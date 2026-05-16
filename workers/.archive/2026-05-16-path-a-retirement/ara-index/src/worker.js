/**
 * ARA Index Worker — AI Brand Readiness scoring
 * Owner: Morphe
 * Support: Aether + Chy
 *
 * Endpoints:
 *   POST /ara/score      — {url, industry, email?} → run scan, return score + TG alert
 *   GET  /ara/score/:id  — get scan results by brand ID
 *   GET  /ara/stats      — social proof counter (total scans, brands scored)
 *   POST /ara/subscribe  — {brand_id, email} → opt-in monthly re-scans
 *   POST /ara/report     — email-gated full report + Brevo drip
 *   GET  /health         — health check
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;
    const path = url.pathname;

    // CORS
    if (method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), {
        status,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });

    // Health
    if (path === "/health") {
      return json({ status: "ok", worker: "ara-index", timestamp: new Date().toISOString() });
    }

    // POST /ara/score — run a brand scan
    if (method === "POST" && path === "/ara/score") {
      try {
        const body = await request.json();
        const brandUrl = (body.url || "").trim();
        const industry = (body.industry || "").trim();
        const email = (body.email || "").trim();

        if (!brandUrl) return json({ error: "url required" }, 400);

        // URL validation
        try {
          const testUrl = brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`;
          new URL(testUrl);
        } catch {
          return json({ error: "invalid URL format" }, 400);
        }

        // Upsert brand
        let brand = await env.DB.prepare(
          "SELECT id FROM ara_brands WHERE url = ?"
        ).bind(brandUrl).first();

        if (!brand) {
          const res = await env.DB.prepare(
            "INSERT INTO ara_brands (url, industry, owner_email) VALUES (?, ?, ?) RETURNING id"
          ).bind(brandUrl, industry || null, email || null).first();
          brand = { id: res.id };
        }

        const brandId = brand.id;

        // Run all 5 dimensions IN PARALLEL with 25s overall timeout
        const dimPromises = [
          scoreStructural(brandUrl),
          scoreSemantic(brandUrl, env),
          scoreSynthetic(brandUrl, industry, env),
          scoreEmotional(brandUrl, env),
          scoreVoice(brandUrl, env),
        ];
        const overallTimeout = new Promise((_, reject) => setTimeout(() => reject(new Error("Overall scoring timeout")), 25000));
        let [a1, a2, a3, a4, a5] = await Promise.race([
          Promise.all(dimPromises.map((p, i) =>
            p.catch(e => ({
              dimension: ["A1_structural","A2_semantic","A3_synthetic","A4_emotional","A5_voice"][i],
              score: 0,
              signals: { note: `Dimension timed out: ${e.message}` }
            }))
          )),
          overallTimeout.then(() => { throw new Error("timeout"); })
        ]).catch(() => [
          { dimension: "A1_structural", score: 0, signals: { note: "Timeout" } },
          { dimension: "A2_semantic", score: 0, signals: { note: "Timeout" } },
          { dimension: "A3_synthetic", score: 0, signals: { note: "Timeout" } },
          { dimension: "A4_emotional", score: 0, signals: { note: "Timeout" } },
          { dimension: "A5_voice", score: 0, signals: { note: "Timeout" } },
        ]);

        // Store dimension scores
        for (const dim of [a1, a2, a3, a4, a5]) {
          await env.DB.prepare(
            "INSERT INTO ara_scores (brand_id, dimension, score, signals) VALUES (?, ?, ?, ?)"
          ).bind(brandId, dim.dimension, dim.score, JSON.stringify(dim.signals)).run();
        }

        // Calculate total (5 dimensions, each 0-20 = max 100)
        const rawTotal = a1.score + a2.score + a3.score + a4.score + a5.score;
        const totalScore = Math.min(rawTotal, 100);
        const tier = totalScore >= 83 ? "Awesome" : totalScore >= 70 ? "Strong" : totalScore >= 56 ? "Average" : totalScore >= 40 ? "Weak" : "Invisible";

        // Store scan
        await env.DB.prepare(
          "INSERT INTO ara_scans (brand_id, total_score, tier, dimensions) VALUES (?, ?, ?, ?)"
        ).bind(brandId, totalScore, tier, JSON.stringify({ a1: a1.score, a2: a2.score, a3: a3.score, a4: a4.score, a5: a5.score })).run();

        // Telegram alert to Jared
        if (env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID) {
          const tgText = `[BrainScore] New scan: ${brandUrl} — ${totalScore}/100 ${tier}\n${email ? `Email: ${email}` : "No email provided"}\nDimensions: A1:${a1.score} A2:${a2.score} A3:${a3.score} A4:${a4.score} A5:${a5.score}`;
          ctx.waitUntil(
            fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT_ID, text: tgText }),
            }).catch(e => console.error("[ara] Telegram alert error:", e.message))
          );
        }

        // Run citation tracking and content authority in parallel with each other
        let citationTracking = { citation_rate: 0, appearances: 0, total_queries: 0, query_results: [] };
        let contentAuthority = { content_authority: 0, signals: {} };
        const [ctResult, caResult] = await Promise.allSettled([
          scoreCitationFrequency(brandUrl, industry, env),
          scoreContentAuthority(brandUrl, env),
        ]);
        if (ctResult.status === "fulfilled") citationTracking = ctResult.value;
        if (caResult.status === "fulfilled") contentAuthority = caResult.value;

        // Store citation results in ara_citations table
        if (citationTracking.query_results && citationTracking.query_results.length > 0) {
          for (const qr of citationTracking.query_results) {
            try {
              await env.DB.prepare(
                "INSERT INTO ara_citations (brand_id, query, model, appeared) VALUES (?, ?, ?, ?)"
              ).bind(brandId, qr.query, qr.model, qr.appeared ? 1 : 0).run();
            } catch {}
          }
        }

        // Build gap analysis from A2 semantic signals
        const gapAnalysis = buildGapAnalysis(a2);

        // Generate answer nuggets from scan data
        const hostname = new URL(brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`).hostname;
        const brandName = hostname.replace("www.", "").split(".")[0];
        const answerNuggets = generateAnswerNuggets(brandUrl, brandName, { a1, a2, a3, a4, a5 }, gapAnalysis);

        // Store nuggets for later retrieval
        await env.DB.prepare(
          "INSERT OR REPLACE INTO ara_nuggets (brand_id, nuggets) VALUES (?, ?)"
        ).bind(brandId, JSON.stringify(answerNuggets)).run();

        return json({
          ok: true,
          brand_id: brandId,
          brand_url: brandUrl,
          total_score: totalScore,
          tier: tier.toLowerCase(),
          dimensions: {
            structural: a1.score,
            semantic: a2.score,
            synthetic: a3.score,
            emotional: a4.score,
            voice: a5.score,
          },
          details: {
            structural_readiness: a1,
            semantic_clarity: a2,
            synthetic_customer: a3,
            emotional_residue: a4,
            voice_archetype: a5,
          },
          gap_analysis: gapAnalysis,
          answer_nuggets: answerNuggets,
          citation_tracking: citationTracking,
          content_authority: contentAuthority,
        });
      } catch (e) {
        console.error("[ara] Score error:", e);
        return json({ error: e.message }, 500);
      }
    }

    // GET /ara/score/:id
    if (method === "GET" && path.startsWith("/ara/score/")) {
      const brandId = path.split("/").pop();
      const scan = await env.DB.prepare(
        "SELECT * FROM ara_scans WHERE brand_id = ? ORDER BY scanned_at DESC LIMIT 1"
      ).bind(brandId).first();
      if (!scan) return json({ error: "not found" }, 404);
      return json(scan);
    }

    // GET /ara/nuggets/:brand_id — answer nuggets for a brand
    if (method === "GET" && path.match(/^\/ara\/nuggets\/\d+$/)) {
      const brandId = path.split("/").pop();
      try {
        const row = await env.DB.prepare(
          "SELECT nuggets FROM ara_nuggets WHERE brand_id = ?"
        ).bind(brandId).first();
        if (!row) return json({ error: "no nuggets found for this brand" }, 404);
        const nuggets = typeof row.nuggets === "string" ? JSON.parse(row.nuggets) : row.nuggets;
        return json({ ok: true, brand_id: parseInt(brandId), answer_nuggets: nuggets });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // POST /ara/report — email-gated full premium report
    if (method === "POST" && path === "/ara/report") {
      try {
        const body = await request.json();
        const brandId = body.brand_id;
        const email = (body.email || "").trim();
        if (!brandId || !email) return json({ error: "brand_id and email required" }, 400);

        // Store email as lead
        await env.DB.prepare(
          "UPDATE ara_brands SET owner_email = ? WHERE id = ?"
        ).bind(email, brandId).run();

        // Get latest scan with full details
        const scan = await env.DB.prepare(
          "SELECT * FROM ara_scans WHERE brand_id = ? ORDER BY scanned_at DESC LIMIT 1"
        ).bind(brandId).first();

        // Get ALL dimension scores with full signals
        const scores = await env.DB.prepare(
          "SELECT dimension, score, signals FROM ara_scores WHERE brand_id = ? ORDER BY scanned_at DESC LIMIT 5"
        ).bind(brandId).all();

        // Get brand URL and industry
        const brandRow = await env.DB.prepare(
          "SELECT url, industry FROM ara_brands WHERE id = ?"
        ).bind(brandId).first();
        const brandUrl2 = brandRow?.url || "unknown";
        const brandIndustry = brandRow?.industry || "";

        // Get answer nuggets
        const nuggetsRow = await env.DB.prepare(
          "SELECT nuggets FROM ara_nuggets WHERE brand_id = ?"
        ).bind(brandId).first();
        const answerNuggets = nuggetsRow?.nuggets
          ? (typeof nuggetsRow.nuggets === "string" ? JSON.parse(nuggetsRow.nuggets) : nuggetsRow.nuggets)
          : [];

        // Get citation tracking data
        const citations = await env.DB.prepare(
          "SELECT query, model, appeared FROM ara_citations WHERE brand_id = ? ORDER BY rowid DESC LIMIT 8"
        ).bind(brandId).all();
        const citationResults = (citations.results || []);
        const citationAppearances = citationResults.filter(c => c.appeared).length;
        const citationTotal = citationResults.length;
        const citationRate = citationTotal > 0 ? Math.round((citationAppearances / citationTotal) * 100) : 0;

        // Get leaderboard position
        const leaderboardAll = await env.DB.prepare(`
          SELECT s.brand_id, s.total_score
          FROM ara_scans s
          WHERE s.scanned_at = (
            SELECT MAX(s2.scanned_at) FROM ara_scans s2 WHERE s2.brand_id = s.brand_id
          )
          ORDER BY s.total_score DESC
        `).all();
        const allBrands = leaderboardAll.results || [];
        const position = allBrands.findIndex(b => b.brand_id === brandId) + 1;
        const totalBrands = allBrands.length;
        const avgScore = totalBrands > 0 ? Math.round(allBrands.reduce((s, b) => s + b.total_score, 0) / totalBrands) : 0;

        // Parse dimensions from scan
        const dims = scan?.dimensions ? (typeof scan.dimensions === "string" ? JSON.parse(scan.dimensions) : scan.dimensions) : {};
        const totalScore = scan?.total_score || 0;
        const tier = scan?.tier || "unknown";

        // Parse full dimension details with signals
        const dimensionDetails = (scores.results || []).map(s => ({
          ...s,
          signals: typeof s.signals === "string" ? JSON.parse(s.signals) : s.signals,
        }));

        // Build gap analysis from semantic dimension signals
        const semanticDim = dimensionDetails.find(d => d.dimension === "A2_semantic");
        const gapAnalysis = semanticDim ? buildGapAnalysis({ signals: semanticDim.signals }) : { website_claims: "", ai_says: "", gaps: [] };

        // Build content authority from stored signals
        const contentDim = dimensionDetails.find(d => d.dimension === "A1_structural");
        const contentAuthSignals = contentDim?.signals || {};

        // Send premium Brevo email with ALL data
        if (env.BREVO_API_KEY) {
          try {
            await sendBrevoReport(env.BREVO_API_KEY, email, brandUrl2, totalScore, tier, dims, {
              dimensionDetails,
              gapAnalysis,
              answerNuggets,
              citationTracking: { rate: citationRate, appearances: citationAppearances, total: citationTotal, results: citationResults },
              contentAuthority: contentAuthSignals,
              leaderboard: { position, totalBrands, avgScore },
              industry: brandIndustry,
            });
          } catch (e) {
            console.error("[ara] Brevo email error:", e.message);
          }
        }

        // Add to Brevo contact list for drip automation
        if (env.BREVO_API_KEY && email) {
          ctx.waitUntil(
            fetch("https://api.brevo.com/v3/contacts", {
              method: "POST",
              headers: { "api-key": env.BREVO_API_KEY, "Content-Type": "application/json" },
              body: JSON.stringify({
                email: email,
                listIds: [36],
                attributes: { BRAINSCORE: totalScore, TIER: tier, BRAND_URL: brandUrl2 },
                updateEnabled: true,
              }),
            }).catch(e => console.error("[ara] Brevo drip error:", e.message))
          );
        }

        return json({
          ok: true,
          brand_id: brandId,
          email_captured: true,
          email_sent: !!env.BREVO_API_KEY,
          scan: scan || {},
          dimension_details: dimensionDetails,
        });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // GET /ara/history/:url — scan history for a brand
    if (method === "GET" && path.startsWith("/ara/history/")) {
      try {
        const brandUrl = decodeURIComponent(path.replace("/ara/history/", ""));
        if (!brandUrl) return json({ error: "url required" }, 400);

        const brand = await env.DB.prepare(
          "SELECT id FROM ara_brands WHERE url = ?"
        ).bind(brandUrl).first();

        if (!brand) return json({ error: "brand not found" }, 404);

        const scans = await env.DB.prepare(
          "SELECT total_score, tier, dimensions, scanned_at FROM ara_scans WHERE brand_id = ? ORDER BY scanned_at DESC LIMIT 10"
        ).bind(brand.id).all();

        return json({
          brand_url: brandUrl,
          scans: (scans.results || []).map(s => ({
            scanned_at: s.scanned_at,
            total_score: s.total_score,
            tier: s.tier,
            dimensions: typeof s.dimensions === "string" ? JSON.parse(s.dimensions) : s.dimensions,
          })),
        });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // GET /ara/leaderboard — all brands sorted by score
    if (method === "GET" && path === "/ara/leaderboard") {
      try {
        const results = await env.DB.prepare(`
          SELECT b.url, s.total_score, s.tier, s.dimensions, s.scanned_at
          FROM ara_scans s
          JOIN ara_brands b ON b.id = s.brand_id
          WHERE s.scanned_at = (
            SELECT MAX(s2.scanned_at) FROM ara_scans s2 WHERE s2.brand_id = s.brand_id
          )
          ORDER BY s.total_score DESC
        `).all();

        return json({
          brands: (results.results || []).map(r => ({
            url: r.url,
            total_score: r.total_score,
            tier: r.tier,
            dimensions: typeof r.dimensions === "string" ? JSON.parse(r.dimensions) : r.dimensions,
            scanned_at: r.scanned_at,
          })),
        });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // GET /ara/leaderboard/:category — filtered by industry
    if (method === "GET" && path.startsWith("/ara/leaderboard/")) {
      try {
        const category = decodeURIComponent(path.replace("/ara/leaderboard/", ""));
        if (!category) return json({ error: "category required" }, 400);

        const results = await env.DB.prepare(`
          SELECT b.url, s.total_score, s.tier, s.dimensions, s.scanned_at
          FROM ara_scans s
          JOIN ara_brands b ON b.id = s.brand_id
          WHERE b.industry LIKE ?
          AND s.scanned_at = (
            SELECT MAX(s2.scanned_at) FROM ara_scans s2 WHERE s2.brand_id = s.brand_id
          )
          ORDER BY s.total_score DESC
        `).bind(`%${category}%`).all();

        return json({
          category,
          brands: (results.results || []).map(r => ({
            url: r.url,
            total_score: r.total_score,
            tier: r.tier,
            dimensions: typeof r.dimensions === "string" ? JSON.parse(r.dimensions) : r.dimensions,
            scanned_at: r.scanned_at,
          })),
        });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // GET /ara/stats — social proof counter for landing page
    if (method === "GET" && path === "/ara/stats") {
      try {
        const totalRow = await env.DB.prepare("SELECT COUNT(*) as cnt FROM ara_scans").first();
        const brandsRow = await env.DB.prepare("SELECT COUNT(DISTINCT brand_id) as cnt FROM ara_scans").first();
        return json({
          total_scans: totalRow?.cnt || 0,
          brands_scored: brandsRow?.cnt || 0,
          since: "2026-05-01",
        });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    // POST /ara/subscribe — opt-in for monthly re-scans
    if (method === "POST" && path === "/ara/subscribe") {
      try {
        const body = await request.json();
        const brandId = body.brand_id;
        const email = (body.email || "").trim();
        if (!brandId || !email) return json({ error: "brand_id and email required" }, 400);

        // Calculate next scan date (30 days from now)
        const nextScan = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

        await env.DB.prepare(
          "INSERT INTO ara_subscriptions (brand_id, email, frequency, next_scan_at) VALUES (?, ?, 'monthly', ?)"
        ).bind(brandId, email, nextScan).run();

        return json({ ok: true, brand_id: brandId, email, next_scan_at: nextScan });
      } catch (e) {
        return json({ error: e.message }, 500);
      }
    }

    return json({ error: "not found" }, 404);
  },
};

// ── A2: Semantic Clarity (0-20) ──
// Common English stopwords to filter out of vocabulary matching
const STOP_WORDS = new Set([
  "about", "above", "after", "again", "against", "their", "there", "these",
  "those", "through", "under", "until", "very", "would", "could", "should",
  "which", "while", "where", "other", "every", "being", "between", "before",
  "below", "both", "during", "having", "itself", "might", "never", "still",
  "since", "those", "three", "under", "using", "without", "within", "yours",
  "today", "right", "great", "first", "world", "start", "built", "based",
  "learn", "helps", "makes", "needs", "people", "things", "better", "business",
  "company", "offers", "provides", "platform", "solution", "solutions", "service",
  "services", "customers", "online", "digital", "global", "leading", "website",
]);

// ── Answer Nuggets Generator ──
function generateAnswerNuggets(brandUrl, brandName, dims, gapAnalysis) {
  const a2Signals = dims.a2.signals || {};
  const a4Signals = dims.a4.signals || {};
  const brandTerms = a2Signals.brand_terms || [];
  const aiDescriptions = a2Signals.ai_descriptions || [];
  const associations = a4Signals.associations || [];

  // Extract brand's own vocabulary
  const brandVocab = brandTerms.slice(0, 10).join(", ");
  // Extract AI model descriptions
  const aiTexts = aiDescriptions.filter(d => d.text && !d.error).map(d => d.text);
  const combinedAiText = aiTexts.join(" ");
  // Extract emotional/cultural signals
  const emotionalTexts = associations.filter(a => a.text && !a.error).map(a => a.text);
  const combinedEmotional = emotionalTexts.join(" ");

  const displayName = brandName.charAt(0).toUpperCase() + brandName.slice(1);
  const nuggets = [];

  // Nugget 1: What does [brand] do?
  let whatAnswer = "";
  if (aiTexts.length > 0) {
    const firstDesc = aiTexts[0];
    const sentences = firstDesc.split(/[.!?]+/).filter(s => s.trim().length > 10).slice(0, 2);
    whatAnswer = sentences.join(". ").trim();
    if (whatAnswer && !whatAnswer.endsWith(".")) whatAnswer += ".";
  }
  if (!whatAnswer && brandVocab) {
    whatAnswer = `${displayName} is a company focused on ${brandVocab}.`;
  }
  if (!whatAnswer) whatAnswer = `${displayName} provides services accessible at ${brandUrl}.`;
  nuggets.push({
    question: `What does ${displayName} do?`,
    answer: whatAnswer.charAt(0).toUpperCase() + whatAnswer.slice(1),
    schema_type: "FAQPage",
    implementation: "Add this as JSON-LD FAQPage schema to your homepage"
  });

  // Nugget 2: Why choose [brand]?
  let whyAnswer = "";
  if (brandTerms.length > 2) {
    const uniqueTerms = brandTerms.filter(t => !combinedAiText.includes(t)).slice(0, 3);
    const knownTerms = brandTerms.filter(t => combinedAiText.includes(t)).slice(0, 3);
    if (knownTerms.length > 0) {
      whyAnswer = `${displayName} is recognized for ${knownTerms.join(", ")}`;
      if (uniqueTerms.length > 0) {
        whyAnswer += `, and also offers unique strengths in ${uniqueTerms.join(", ")}`;
      }
      whyAnswer += ".";
    }
  }
  if (!whyAnswer && emotionalTexts.length > 0) {
    const emotSentences = combinedEmotional.split(/[.!?]+/).filter(s => s.trim().length > 15).slice(0, 1);
    whyAnswer = emotSentences.length > 0 ? `${displayName} stands out because ${emotSentences[0].trim()}.` : "";
  }
  if (!whyAnswer) whyAnswer = `${displayName} combines ${brandVocab || "specialized expertise"} to deliver value to its customers.`;
  nuggets.push({
    question: `Why choose ${displayName}?`,
    answer: whyAnswer,
    schema_type: "FAQPage",
    implementation: "Add this as JSON-LD FAQPage schema to your homepage or About page"
  });

  // Nugget 3: How is [brand] different from competitors?
  let diffAnswer = "";
  const hasCompetitorFraming = combinedAiText.includes("alternative to") || combinedAiText.includes("similar to");
  if (hasCompetitorFraming) {
    const competitorMention = combinedAiText.match(/alternative to (\w+)/i) || combinedAiText.match(/similar to (\w+)/i);
    const competitor = competitorMention ? competitorMention[1] : "competitors";
    diffAnswer = `Unlike ${competitor}, ${displayName} focuses on ${brandTerms.slice(0, 3).join(", ") || "its unique approach"} to deliver a differentiated experience.`;
  } else if (brandTerms.length > 0) {
    diffAnswer = `${displayName} differentiates through its focus on ${brandTerms.slice(0, 4).join(", ")}, which AI systems recognize as its core positioning.`;
  } else {
    diffAnswer = `${displayName} offers a distinct approach in its market category.`;
  }
  nuggets.push({
    question: `How is ${displayName} different from competitors?`,
    answer: diffAnswer,
    schema_type: "FAQPage",
    implementation: "Add this as JSON-LD FAQPage schema to your comparison or features page"
  });

  // Nugget 4: Who uses [brand]?
  let whoAnswer = "";
  if (combinedEmotional.length > 20) {
    const audiencePatterns = combinedEmotional.match(/\b(developer|designer|creator|entrepreneur|startup|enterprise|small business|marketer|team|professional|engineer|artist|student)s?\b/gi);
    if (audiencePatterns && audiencePatterns.length > 0) {
      const uniqueAudiences = [...new Set(audiencePatterns.map(a => a.toLowerCase()))].slice(0, 3);
      whoAnswer = `${displayName} serves ${uniqueAudiences.join(", ")}, and professionals who value ${brandTerms.slice(0, 2).join(" and ") || "quality and reliability"}.`;
    }
  }
  if (!whoAnswer && combinedAiText.length > 20) {
    const aiAudiencePatterns = combinedAiText.match(/\b(developer|designer|creator|entrepreneur|startup|enterprise|small business|marketer|team|professional|engineer|artist|student)s?\b/gi);
    if (aiAudiencePatterns && aiAudiencePatterns.length > 0) {
      const uniqueAudiences = [...new Set(aiAudiencePatterns.map(a => a.toLowerCase()))].slice(0, 3);
      whoAnswer = `${displayName} is used by ${uniqueAudiences.join(", ")} who need ${brandTerms.slice(0, 2).join(" and ") || "reliable solutions"}.`;
    }
  }
  if (!whoAnswer) whoAnswer = `${displayName} is designed for professionals and organizations looking for ${brandTerms.slice(0, 2).join(" and ") || "effective solutions"}.`;
  nuggets.push({
    question: `Who uses ${displayName}?`,
    answer: whoAnswer,
    schema_type: "FAQPage",
    implementation: "Add this as JSON-LD FAQPage schema to your homepage or customers page"
  });

  // Nugget 5: What problem does [brand] solve?
  let problemAnswer = "";
  if (aiTexts.length > 0) {
    const problemPatterns = combinedAiText.match(/\b(helps|enables|allows|solves|addresses|eliminates|simplifies|streamlines|automates)\b[^.]{10,60}/i);
    if (problemPatterns) {
      problemAnswer = `${displayName} ${problemPatterns[0].trim()}.`;
    }
  }
  if (!problemAnswer && brandTerms.length > 0) {
    problemAnswer = `${displayName} solves challenges related to ${brandTerms.slice(0, 3).join(", ")} for its users.`;
  }
  if (!problemAnswer) problemAnswer = `${displayName} helps organizations overcome challenges in their domain.`;
  nuggets.push({
    question: `What problem does ${displayName} solve?`,
    answer: problemAnswer.charAt(0).toUpperCase() + problemAnswer.slice(1),
    schema_type: "FAQPage",
    implementation: "Add this as JSON-LD FAQPage schema to your homepage or solutions page"
  });

  return nuggets;
}

// ── Gap Analysis Builder ──
function buildGapAnalysis(a2Result) {
  const signals = a2Result.signals || {};
  const brandTerms = signals.brand_terms || [];
  const aiDescriptions = signals.ai_descriptions || [];

  // Website claims = brand terms from meta desc + title
  const websiteClaims = brandTerms.length > 0
    ? brandTerms.slice(0, 10).join(", ")
    : "No positioning vocabulary found on homepage";

  // AI says = combine AI model descriptions
  const aiSays = aiDescriptions
    .filter(d => d.text && !d.error)
    .map(d => `${d.model}: "${d.text.substring(0, 150)}"`)
    .join(" | ") || "No AI descriptions available";

  // Find gaps: brand terms NOT mentioned by any AI model
  const allAiText = aiDescriptions
    .filter(d => d.text && !d.error)
    .map(d => d.text)
    .join(" ")
    .toLowerCase();

  const gaps = [];

  // Terms website uses that AI doesn't echo back
  const missingTerms = brandTerms.filter(term => !allAiText.includes(term));
  if (missingTerms.length > 0) {
    gaps.push(`Website positioning uses "${missingTerms.slice(0, 5).join('", "')}" but AI models don't repeat these terms`);
  }

  // Check for competitor framing
  const hasCompetitorFraming = allAiText.includes("alternative to") || allAiText.includes("similar to") || allAiText.includes("competitor");
  if (hasCompetitorFraming) {
    gaps.push("AI describes brand relative to competitors rather than on its own terms");
  }

  // Check for generic descriptions
  const isGeneric = allAiText.includes("is a company") || allAiText.includes("is a platform") || allAiText.includes("is a tool");
  if (isGeneric && brandTerms.length > 3) {
    gaps.push("Website has specific positioning but AI defaults to generic descriptions");
  }

  // If no gaps found, brand is well-aligned
  if (gaps.length === 0 && brandTerms.length > 0) {
    gaps.push("AI descriptions are well-aligned with website positioning");
  }

  return {
    website_claims: websiteClaims,
    ai_says: aiSays,
    gaps,
  };
}

async function scoreSemantic(brandUrl, env) {
  const signals = { brand_terms: [], ai_descriptions: [] };
  let score = 0;

  const baseUrl = brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`;
  const hostname = new URL(baseUrl).hostname;
  const brandName = hostname.replace("www.", "").split(".")[0];

  // Step 1: Scrape homepage for brand's POSITIONING vocabulary (title + meta desc only)
  let brandVocab = [];
  try {
    const r = await fetch(baseUrl, { cf: { cacheTtl: 300 } });
    if (r.ok) {
      const html = await r.text();
      const metaDesc = (html.match(/name="description"\s+content="([^"]+)"/) || [])[1] || "";
      const title = (html.match(/<title>([^<]+)<\/title>/) || [])[1] || "";
      const combined = `${title} ${metaDesc}`.toLowerCase();
      // Only count words 6+ chars that aren't common stopwords
      brandVocab = combined.split(/\s+/)
        .filter(w => w.length >= 6 && !STOP_WORDS.has(w))
        .map(w => w.replace(/[^a-z]/g, ""))
        .filter(w => w.length >= 6);
      // Deduplicate
      brandVocab = [...new Set(brandVocab)];
      signals.brand_terms = brandVocab.slice(0, 20);
    }
  } catch {}

  // Step 2: Ask Claude to describe the brand
  if (env.ANTHROPIC_API_KEY) {
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": env.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514", max_tokens: 300,
          messages: [{ role: "user", content: `Describe ${brandName} (${hostname}) in 3 sentences. What do they do and what makes them unique?` }],
        }),
      });
      const data = await r.json();
      const text = (data.content?.[0]?.text || "").toLowerCase();
      signals.ai_descriptions.push({ model: "claude", text: text.substring(0, 300) });

      // Score: only count matches of positioning-specific vocabulary (6+ chars, non-generic)
      const vocabMatches = brandVocab.filter(w => text.includes(w)).length;
      const hasCompetitorFraming = text.includes("alternative to") || text.includes("similar to") || text.includes("competitor");
      const isGeneric = text.includes("is a company") || text.includes("is a platform") || text.includes("is a tool");

      signals.ai_descriptions[signals.ai_descriptions.length - 1].vocab_matches = vocabMatches;

      if (vocabMatches >= 4 && !hasCompetitorFraming) score += 10;
      else if (vocabMatches >= 2 && !hasCompetitorFraming) score += 7;
      else if (vocabMatches >= 1) score += 4;
      else if (isGeneric) score += 2;
      else score += 1;

      if (hasCompetitorFraming) score = Math.max(score - 3, 0);
    } catch (e) { signals.ai_descriptions.push({ model: "claude", error: e.message }); }
  }

  // Step 3: Ask GPT to describe the brand
  if (env.OPENAI_API_KEY) {
    try {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "gpt-4o", max_tokens: 300,
          messages: [{ role: "user", content: `Describe ${brandName} (${hostname}) in 3 sentences. What do they do and what makes them unique?` }],
        }),
      });
      const data = await r.json();
      const text = (data.choices?.[0]?.message?.content || "").toLowerCase();
      signals.ai_descriptions.push({ model: "gpt-4o", text: text.substring(0, 300) });

      const vocabMatches = brandVocab.filter(w => text.includes(w)).length;
      const hasCompetitorFraming = text.includes("alternative to") || text.includes("similar to") || text.includes("competitor");
      const isGeneric = text.includes("is a company") || text.includes("is a platform") || text.includes("is a tool");

      signals.ai_descriptions[signals.ai_descriptions.length - 1].vocab_matches = vocabMatches;

      if (vocabMatches >= 4 && !hasCompetitorFraming) score += 10;
      else if (vocabMatches >= 2 && !hasCompetitorFraming) score += 7;
      else if (vocabMatches >= 1) score += 4;
      else if (isGeneric) score += 2;
      else score += 1;

      if (hasCompetitorFraming) score = Math.max(score - 3, 0);
    } catch (e) { signals.ai_descriptions.push({ model: "gpt-4o", error: e.message }); }
  }

  return { dimension: "A2_semantic", score: Math.min(score, 20), signals };
}

// ── A4: Emotional Residue (0-20) ──
async function scoreEmotional(brandUrl, env) {
  const signals = { associations: [] };
  let score = 0;

  const hostname = new URL(brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`).hostname;
  const brandName = hostname.replace("www.", "").split(".")[0];

  const prompt = `What cultural associations, emotions, or community connections does ${brandName} (${hostname}) have? Name any specific cultural moments, communities, or movements associated with this brand. Be specific — name real groups, events, campaigns, or movements.`;

  // Helper: score emotional response on 0-10 scale
  function scoreEmotionalResponse(text) {
    const hasNamedEntity = /[A-Z][a-z]+(?:\s[A-Z][a-z]+)*/.test(text) || /\b\d{4}\b/.test(text);
    const hasSpecificGroup = /\b(developer|designer|creator|athlete|runner|entrepreneur|startup|maker)s?\s+(community|group|movement)/i.test(text);
    const hasNamedCampaign = /\b(just do it|think different|#\w{4,}|campaign|slogan|tagline)\b/i.test(text);
    const hasNamedEvent = /\b(super bowl|olympics|world cup|conference|summit|wwdc|reinvent|dreamforce)\b/i.test(text);
    const hasSpecificPartner = /\b(partner|collaborat|sponsor|endorse)\w*\s+(with|by)\b/i.test(text);

    const hasGenericOnly = /\b(innovative|trusted|reliable|modern|professional|popular|well-known|reputable)\b/i.test(text);
    const isPurelyFunctional = /\b(provides|offers|allows|enables|helps users)\b/i.test(text);

    const specificSignals = [hasNamedEntity, hasSpecificGroup, hasNamedCampaign, hasNamedEvent, hasSpecificPartner].filter(Boolean).length;

    if (specificSignals >= 3) return 10;
    if (specificSignals === 2) return 8;
    if (specificSignals === 1) return 5;
    if (hasGenericOnly && !isPurelyFunctional) return 4;
    if (isPurelyFunctional) return 1;
    return 0;
  }

  // Ask Claude
  if (env.ANTHROPIC_API_KEY) {
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": env.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 400, messages: [{ role: "user", content: prompt }] }),
      });
      const data = await r.json();
      const text = data.content?.[0]?.text || "";
      signals.associations.push({ model: "claude", text: text.substring(0, 400) });
      const modelScore = scoreEmotionalResponse(text);
      signals.associations[signals.associations.length - 1].emotional_score = modelScore;
      score += modelScore;
    } catch (e) { signals.associations.push({ model: "claude", error: e.message }); }
  }

  // Ask GPT
  if (env.OPENAI_API_KEY) {
    try {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model: "gpt-4o", max_tokens: 400, messages: [{ role: "user", content: prompt }] }),
      });
      const data = await r.json();
      const text = data.choices?.[0]?.message?.content || "";
      signals.associations.push({ model: "gpt-4o", text: text.substring(0, 400) });
      const modelScore = scoreEmotionalResponse(text);
      signals.associations[signals.associations.length - 1].emotional_score = modelScore;
      score += modelScore;
    } catch (e) { signals.associations.push({ model: "gpt-4o", error: e.message }); }
  }

  return { dimension: "A4_emotional", score: Math.min(score, 20), signals };
}

// ── A5: Voice & Archetype (0-20) ──
async function scoreVoice(brandUrl, env) {
  const signals = { voice_analysis: [], round_trip: [] };
  let score = 0;

  const baseUrl = brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`;
  const hostname = new URL(baseUrl).hostname;
  const brandName = hostname.replace("www.", "").split(".")[0];

  // Step 1: Scrape homepage text for voice analysis
  let pageText = "";
  try {
    const r = await fetch(baseUrl, { cf: { cacheTtl: 300 } });
    if (r.ok) {
      const html = await r.text();
      pageText = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "")
                     .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, "")
                     .replace(/<[^>]+>/g, " ")
                     .replace(/\s+/g, " ")
                     .trim()
                     .substring(0, 1500);
    }
  } catch {}

  const archPrompt = `Analyze this brand's writing voice. Here is text from ${brandName}'s website:\n\n"${pageText.substring(0, 800)}"\n\nAnswer these 3 questions:\n1. Describe their voice in exactly 3 words\n2. What brand archetype best fits? (Hero/Sage/Outlaw/Magician/Innocent/Ruler/Lover/Jester/Caregiver/Creator/Explorer/Everyman)\n3. Is this voice distinctive enough that you could identify the brand without seeing the name? Yes or No.`;

  // Ask Claude for voice analysis
  if (env.ANTHROPIC_API_KEY && pageText) {
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": env.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 300, messages: [{ role: "user", content: archPrompt }] }),
      });
      const data = await r.json();
      const text = (data.content?.[0]?.text || "").toLowerCase();
      signals.voice_analysis.push({ model: "claude", text: text.substring(0, 400) });

      const hasArchetype = /hero|sage|outlaw|magician|innocent|ruler|lover|jester|caregiver|creator|explorer|everyman/i.test(text);
      const isDistinctive = text.includes("yes") || /recognizable|distinct|unique voice|strong personality|unmistakable|signature/i.test(text);
      const isGeneric = /generic|corporate|standard|interchangeable|boilerplate|cookie-cutter/i.test(text);

      if (hasArchetype && isDistinctive) score += 10;
      else if (hasArchetype && !isGeneric) score += 7;
      else if (hasArchetype && isGeneric) score += 4;
      else if (!isGeneric) score += 4;
      else score += 1;
    } catch (e) { signals.voice_analysis.push({ model: "claude", error: e.message }); }
  }

  // Ask GPT for voice analysis
  if (env.OPENAI_API_KEY && pageText) {
    try {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model: "gpt-4o", max_tokens: 300, messages: [{ role: "user", content: archPrompt }] }),
      });
      const data = await r.json();
      const text = (data.choices?.[0]?.message?.content || "").toLowerCase();
      signals.voice_analysis.push({ model: "gpt-4o", text: text.substring(0, 400) });

      const hasArchetype = /hero|sage|outlaw|magician|innocent|ruler|lover|jester|caregiver|creator|explorer|everyman/i.test(text);
      const isDistinctive = text.includes("yes") || /recognizable|distinct|unique voice|strong personality|unmistakable|signature/i.test(text);
      const isGeneric = /generic|corporate|standard|interchangeable|boilerplate|cookie-cutter/i.test(text);

      if (hasArchetype && isDistinctive) score += 10;
      else if (hasArchetype && !isGeneric) score += 7;
      else if (hasArchetype && isGeneric) score += 4;
      else if (!isGeneric) score += 4;
      else score += 1;
    } catch (e) { signals.voice_analysis.push({ model: "gpt-4o", error: e.message }); }
  }

  if (!pageText) {
    signals.voice_analysis.push({ note: "Could not scrape homepage text for voice analysis" });
  }

  return { dimension: "A5_voice", score: Math.min(score, 20), signals };
}

// ── A1: Structural Readiness (0-20) ──
async function scoreStructural(brandUrl) {
  const signals = {};
  let score = 0;

  // Normalize URL
  const baseUrl = brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`;
  const hostname = new URL(baseUrl).hostname;

  // Check robots.txt — existence (+2) and AI-friendliness (+2)
  try {
    const r = await fetch(`https://${hostname}/robots.txt`, { cf: { cacheTtl: 300 } });
    signals.robots_txt = r.ok;
    if (r.ok) {
      score += 2;
      const robotsText = await r.text();
      const blocksGPTBot = /disallow.*gptbot/i.test(robotsText) || /user-agent:\s*gptbot[\s\S]*?disallow:\s*\//im.test(robotsText);
      const blocksClaudeBot = /disallow.*claudebot/i.test(robotsText) || /user-agent:\s*claudebot[\s\S]*?disallow:\s*\//im.test(robotsText);
      signals.allows_ai_crawlers = !blocksGPTBot && !blocksClaudeBot;
      if (signals.allows_ai_crawlers) score += 2;
    }
  } catch { signals.robots_txt = false; }

  // Check llms.txt (+3)
  try {
    const r = await fetch(`https://${hostname}/llms.txt`, { cf: { cacheTtl: 300 } });
    signals.llms_txt = r.ok;
    if (r.ok) score += 3;
  } catch { signals.llms_txt = false; }

  // Check sitemap.xml (+2)
  try {
    const r = await fetch(`https://${hostname}/sitemap.xml`, { cf: { cacheTtl: 300 } });
    signals.sitemap = r.ok;
    if (r.ok) score += 2;
  } catch { signals.sitemap = false; }

  // Check homepage for schema, meta, og tags, HTTPS, load time
  let homepageHtml = "";
  try {
    const startTime = Date.now();
    const r = await fetch(baseUrl, { cf: { cacheTtl: 300 } });
    const loadTime = Date.now() - startTime;
    signals.load_time_ms = loadTime;

    // HTTPS check (+1)
    signals.is_https = baseUrl.startsWith("https://") || r.url.startsWith("https://");
    if (signals.is_https) score += 1;

    // Page loads under 5 seconds (+2)
    signals.fast_load = loadTime < 5000;
    if (signals.fast_load) score += 2;

    if (r.ok) {
      homepageHtml = await r.text();

      // Schema.org / JSON-LD (+3)
      signals.has_schema = homepageHtml.includes("schema.org") || homepageHtml.includes("application/ld+json");
      if (signals.has_schema) score += 3;

      // Meta description present AND >50 chars (+2)
      const metaDescMatch = homepageHtml.match(/name="description"\s+content="([^"]*)"/);
      const metaDesc = metaDescMatch ? metaDescMatch[1] : "";
      signals.has_meta_description = metaDesc.length > 50;
      signals.meta_description_length = metaDesc.length;
      if (signals.has_meta_description) score += 2;

      // og:title + og:description + og:image ALL present (+3)
      const hasOgTitle = homepageHtml.includes('property="og:title"');
      const hasOgDesc = homepageHtml.includes('property="og:description"');
      const hasOgImage = homepageHtml.includes('property="og:image"');
      signals.og_title = hasOgTitle;
      signals.og_description = hasOgDesc;
      signals.og_image = hasOgImage;
      signals.has_all_og_tags = hasOgTitle && hasOgDesc && hasOgImage;
      if (signals.has_all_og_tags) score += 3;
    }
  } catch { signals.has_schema = false; }

  // Knowledge Graph Check — entity recognition bonus
  const brandName = hostname.replace("www.", "").split(".")[0];
  signals.knowledge_graph = { wikipedia: false, wikidata: false, org_schema: false, entity_recognized: false };

  // Wikipedia check (use API to avoid bot blocking)
  try {
    const wikiApiUrl = `https://en.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(brandName.charAt(0).toUpperCase() + brandName.slice(1))}&format=json`;
    const wikiR = await fetch(wikiApiUrl, { cf: { cacheTtl: 300 } });
    if (wikiR.ok) {
      const wikiData = await wikiR.json();
      const pages = wikiData.query?.pages || {};
      signals.knowledge_graph.wikipedia = !pages["-1"];
      if (signals.knowledge_graph.wikipedia) score += 1;
    }
  } catch {}

  // Wikidata check
  try {
    const wdR = await fetch(`https://www.wikidata.org/w/api.php?action=wbsearchentities&search=${encodeURIComponent(brandName)}&format=json&language=en`, { cf: { cacheTtl: 300 } });
    if (wdR.ok) {
      const wdData = await wdR.json();
      signals.knowledge_graph.wikidata = (wdData.search && wdData.search.length > 0);
      if (signals.knowledge_graph.wikidata) score += 1;
    }
  } catch {}

  // Organization schema check (refine from generic schema check)
  if (homepageHtml) {
    const hasOrgSchema = homepageHtml.includes('"@type":"Organization"') ||
                         homepageHtml.includes('"@type": "Organization"') ||
                         homepageHtml.includes("'@type':'Organization'") ||
                         /\"@type\"\s*:\s*\"(Organization|LocalBusiness|Corporation)\"/i.test(homepageHtml);
    signals.knowledge_graph.org_schema = hasOrgSchema;
    if (hasOrgSchema) score += 1;
  }

  signals.knowledge_graph.entity_recognized = signals.knowledge_graph.wikipedia || signals.knowledge_graph.wikidata || signals.knowledge_graph.org_schema;

  return { dimension: "A1_structural", score: Math.min(score, 20), signals };
}

// ── A3: Synthetic Customer Test (0-20) ──
async function scoreSynthetic(brandUrl, industry, env) {
  const signals = { models: [] };
  let score = 0;

  const hostname = new URL(brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`).hostname;
  const brandName = hostname.replace("www.", "").split(".")[0];
  const category = industry || "technology";

  const prompt = `I'm looking for a ${category} company. Can you recommend some options? Please list your top 5 recommendations with brief descriptions.`;

  // Helper: score a model's response on a 0-10 scale
  function scoreModelResponse(text, brand) {
    const brandLower = brand.toLowerCase();
    const lines = text.split("\n");
    let modelScore = 0;

    const brandAppears = text.includes(brandLower);

    if (brandAppears) {
      let position = -1;
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].match(/^[\s]*[1-2][\.\)]/)) {
          if (lines[i].toLowerCase().includes(brandLower)) {
            position = parseInt(lines[i].match(/[1-2]/)[0]);
            break;
          }
        }
        if (lines[i].toLowerCase().includes(brandLower)) {
          const precedingItems = lines.slice(0, i).filter(l => l.match(/^[\s]*\d[\.\)]/)).length;
          if (precedingItems <= 1) position = precedingItems + 1;
          break;
        }
      }

      if (position >= 1 && position <= 2) {
        modelScore = 10;
      } else {
        modelScore = 7;
      }
    } else {
      const categoryWords = category.toLowerCase().split(/\s+/);
      const categoryMentioned = categoryWords.some(w => w.length > 3 && text.includes(w));
      if (categoryMentioned) {
        modelScore = 3;
      } else {
        modelScore = 0;
      }
    }

    return { modelScore, brandAppears };
  }

  // Query Claude
  if (env.ANTHROPIC_API_KEY) {
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "x-api-key": env.ANTHROPIC_API_KEY,
          "content-type": "application/json",
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 500,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      const data = await r.json();
      const text = (data.content?.[0]?.text || "").toLowerCase();
      const { modelScore, brandAppears } = scoreModelResponse(text, brandName);
      signals.models.push({ model: "claude", appeared: brandAppears, position_score: modelScore, text: text.substring(0, 400) });
      score += modelScore;
    } catch (e) {
      signals.models.push({ model: "claude", error: e.message });
    }
  }

  // Query GPT
  if (env.OPENAI_API_KEY) {
    try {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.OPENAI_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "gpt-4o",
          messages: [{ role: "user", content: prompt }],
          max_tokens: 500,
        }),
      });
      const data = await r.json();
      const text = (data.choices?.[0]?.message?.content || "").toLowerCase();
      const { modelScore, brandAppears } = scoreModelResponse(text, brandName);
      signals.models.push({ model: "gpt-4o", appeared: brandAppears, position_score: modelScore, text: text.substring(0, 400) });
      score += modelScore;
    } catch (e) {
      signals.models.push({ model: "gpt-4o", error: e.message });
    }
  }

  return { dimension: "A3_synthetic", score: Math.min(score, 20), signals };
}

// ── Citation Frequency Tracking ──
async function scoreCitationFrequency(brandUrl, industry, env) {
  const hostname = new URL(brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`).hostname;
  const brandName = hostname.replace("www.", "").split(".")[0];
  const category = industry || "technology";

  // 8 query types that cover different recommendation contexts
  const queries = [
    `Recommend a ${category} company`,
    `What are the best ${category} tools?`,
    `I need help with ${category}. What companies should I look at?`,
    `Compare top ${category} providers`,
    `What ${category} solution would you recommend for a small business?`,
    `Which ${category} company has the best reputation?`,
    `I'm evaluating ${category} options. What should I consider?`,
    `What's the leading ${category} platform right now?`,
  ];

  let totalAppearances = 0;
  let totalQueries = 0;
  const results = [];

  // Run 4 queries against Claude to stay within timeout
  for (const query of queries.slice(0, 4)) {
    totalQueries++;
    try {
      const resp = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": env.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 300, messages: [{ role: "user", content: query }] }),
      });
      const data = await resp.json();
      const text = (data.content?.[0]?.text || "").toLowerCase();
      const appeared = text.includes(brandName.toLowerCase());
      if (appeared) totalAppearances++;
      results.push({ query: query.substring(0, 60), appeared, model: "claude" });
    } catch {}
  }

  // Citation rate = appearances / total queries * 20
  const citationRate = totalQueries > 0 ? Math.round((totalAppearances / totalQueries) * 20) : 0;

  return {
    citation_rate: citationRate,
    appearances: totalAppearances,
    total_queries: totalQueries,
    query_results: results,
  };
}

// ── Content Authority Score ──
async function scoreContentAuthority(brandUrl, env) {
  const baseUrl = brandUrl.startsWith("http") ? brandUrl : `https://${brandUrl}`;
  const hostname = new URL(baseUrl).hostname;
  const signals = {};
  let score = 0;

  // Check for /blog or /blog/ page
  try {
    const r = await fetch(`https://${hostname}/blog`, { cf: { cacheTtl: 300 }, redirect: "follow" });
    signals.has_blog = r.ok;
    if (r.ok) {
      score += 5;
      const html = await r.text();
      // Count article-like elements (rough heuristic)
      const articleCount = (html.match(/<article/gi) || []).length
        + (html.match(/class="post/gi) || []).length
        + (html.match(/class="entry/gi) || []).length
        + (html.match(/class="blog-post/gi) || []).length;
      signals.estimated_posts = Math.max(articleCount, (html.match(/<h2/gi) || []).length);
      if (signals.estimated_posts >= 10) score += 5;
      else if (signals.estimated_posts >= 5) score += 3;
      else if (signals.estimated_posts >= 1) score += 1;
    }
  } catch { signals.has_blog = false; }

  // Check for /resources or /docs or /help
  for (const path of ["/resources", "/docs", "/help-center", "/learn"]) {
    try {
      const r = await fetch(`https://${hostname}${path}`, { cf: { cacheTtl: 300 } });
      if (r.ok) {
        signals[`has${path.replace("/", "_")}`] = true;
        score += 3;
        break; // Only count once
      }
    } catch {}
  }

  // Ask AI about the brand's content authority
  if (env.ANTHROPIC_API_KEY) {
    try {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": env.ANTHROPIC_API_KEY, "content-type": "application/json", "anthropic-version": "2023-06-01" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514", max_tokens: 200,
          messages: [{ role: "user", content: `Is ${hostname} considered an authority or thought leader in its industry? Rate their content quality and authority on a scale of 1-10. Just the number and one sentence.` }],
        }),
      });
      const data = await r.json();
      const text = (data.content?.[0]?.text || "");
      signals.ai_authority_assessment = text.substring(0, 200);
      const ratingMatch = text.match(/(\d+)\s*\/?\s*10/);
      if (ratingMatch) {
        const rating = parseInt(ratingMatch[1]);
        score += Math.min(Math.round(rating * 0.7), 7); // max 7 points from AI assessment
      }
    } catch {}
  }

  return { content_authority: Math.min(score, 20), signals };
}

// ── Premium Brevo Email Report ──
async function sendBrevoReport(apiKey, toEmail, brandUrl, totalScore, tier, dims, extras) {
  const { dimensionDetails, gapAnalysis, answerNuggets, citationTracking, contentAuthority, leaderboard, industry } = extras || {};

  const tierColors = {
    awesome: "#22c55e",
    strong: "#2a93c1",
    average: "#eab308",
    weak: "#f97316",
    invisible: "#ef4444",
  };
  const tierColor = tierColors[tier.toLowerCase()] || "#888";

  const dimensionNames = {
    a1: { name: "Structural Readiness", icon: "&#x1F3D7;", desc: "How well your technical infrastructure supports AI discovery" },
    a2: { name: "Semantic Clarity", icon: "&#x1F4AC;", desc: "Whether AI understands your brand positioning correctly" },
    a3: { name: "Synthetic Customer", icon: "&#x1F916;", desc: "How often AI recommends you when asked for options" },
    a4: { name: "Emotional Residue", icon: "&#x2764;", desc: "Cultural and emotional associations AI links to your brand" },
    a5: { name: "Voice & Archetype", icon: "&#x1F3A4;", desc: "How distinctive and recognizable your brand voice is to AI" },
  };

  // Extract dimension signals for detailed breakdown
  const dimSignalsMap = {};
  if (dimensionDetails && dimensionDetails.length > 0) {
    for (const d of dimensionDetails) {
      const key = d.dimension === "A1_structural" ? "a1" :
                  d.dimension === "A2_semantic" ? "a2" :
                  d.dimension === "A3_synthetic" ? "a3" :
                  d.dimension === "A4_emotional" ? "a4" :
                  d.dimension === "A5_voice" ? "a5" : null;
      if (key) dimSignalsMap[key] = d.signals || {};
    }
  }

  // ── ARA-STYLE NARRATIVE SECTIONS ──
  const dimEntries = Object.entries(dims);
  const bestDim = dimEntries.reduce((a, b) => b[1] > a[1] ? b : a, ["", 0]);
  const worstDim = dimEntries.reduce((a, b) => b[1] < a[1] ? b : a, ["", 20]);
  const bestName = dimensionNames[bestDim[0]]?.name || bestDim[0];
  const worstName = dimensionNames[worstDim[0]]?.name || worstDim[0];

  // Get gap analysis data for brand vs AI quotes
  const brandQuote = gapAnalysis?.website_claims || null;
  const aiQuote = gapAnalysis?.ai_says || null;
  const gaps = gapAnalysis?.gaps || [];

  // FOUNDATIONS & FORTRESSES — highest dimension with brand/AI quote comparison
  let foundationsHtml = "";
  if (bestDim[1] >= 10) {
    const bestDimKey = bestDim[0];
    const bestSignals = dimSignalsMap[bestDimKey] || {};

    // Get a relevant quote for this dimension
    let brandClaim = "";
    let aiResponse = "";

    if (bestDimKey === "a2" && bestSignals.brand_terms?.length > 0) {
      brandClaim = `Your brand vocabulary: ${bestSignals.brand_terms.slice(0, 3).join(", ")}`;
      if (bestSignals.ai_descriptions?.length > 0) {
        aiResponse = bestSignals.ai_descriptions[0].text?.substring(0, 150) || "";
      }
    } else if (bestDimKey === "a5" && bestSignals.voice_analysis?.length > 0) {
      const va = bestSignals.voice_analysis[0];
      if (va.text && !va.error) {
        aiResponse = va.text.substring(0, 150);
      }
    }

    const foundationNarrative = bestDim[1] >= 16
      ? `AI has deep, accurate understanding here. Your brand's signals are strong and well-indexed.`
      : bestDim[1] >= 12
      ? `AI understands this dimension reasonably well, with some gaps to close.`
      : `This dimension shows basic AI presence but needs strengthening.`;

    foundationsHtml = `
    <tr><td style="padding:0 40px 24px;">
      <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F3F0; Foundations & Fortresses</h2>
      <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:12px;padding:20px;margin-bottom:12px;">
        <div style="font-size:14px;font-weight:700;color:#22c55e;margin-bottom:8px;">Your strongest dimension: ${bestName} (${bestDim[1]}/20)</div>
        <p style="font-size:13px;color:#e8edf5;line-height:1.6;margin:0;">${foundationNarrative}</p>
      </div>
      ${brandClaim || aiResponse ? `
      <div style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);overflow:hidden;">
        <div style="padding:12px 16px;background:rgba(42,147,193,0.1);border-bottom:1px solid rgba(255,255,255,0.06);">
          <span style="font-size:11px;font-weight:600;color:#2a93c1;letter-spacing:0.05em;">YOUR BRAND SAYS</span>
        </div>
        <div style="padding:12px 16px;font-size:13px;color:#e8edf5;line-height:1.5;">${brandClaim || "(AI has indexed your signals here)"}</div>
        <div style="padding:12px 16px;background:rgba(241,66,11,0.08);border-top:1px solid rgba(255,255,255,0.06);border-bottom:1px solid rgba(255,255,255,0.06);">
          <span style="font-size:11px;font-weight:600;color:#f1420b;letter-spacing:0.05em;">AI REPEATS</span>
        </div>
        <div style="padding:12px 16px;font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;">${aiResponse || "(AI echoes your brand's signals accurately)"}</div>
      </div>` : ''}
    </td></tr>`;
  }

  // BAGGAGE & BLINDSPOTS — lowest dimension with gap evidence
  let baggageHtml = "";
  if (worstDim[1] <= 12) {
    const worstDimKey = worstDim[0];
    const worstSignals = dimSignalsMap[worstDimKey] || {};

    // Find a relevant gap for this dimension
    const relevantGap = gaps.find(g => g && typeof g === 'string') ||
      `AI has minimal indexed data for this dimension. Improving here could yield significant score gains.`;

    const baggageNarrative = worstDim[1] <= 5
      ? `AI almost entirely lacks signals for this dimension. This is a critical gap in your machine presence.`
      : worstDim[1] <= 8
      ? `AI has limited data here. The gap between your brand and how AI represents you is significant.`
      : `AI has some presence but there are clear gaps to close.`;

    baggageHtml = `
    <tr><td style="padding:0 40px 24px;">
      <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F6AB; Baggage & Blindspots</h2>
      <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:12px;padding:20px;margin-bottom:12px;">
        <div style="font-size:14px;font-weight:700;color:#ef4444;margin-bottom:8px;">Your biggest gap: ${worstName} (${worstDim[1]}/20)</div>
        <p style="font-size:13px;color:#e8edf5;line-height:1.6;margin:0;">${baggageNarrative}</p>
      </div>
      <div style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:16px;">
        <div style="font-size:12px;font-weight:600;color:rgba(255,255,255,0.4);margin-bottom:8px;">THE GAP:</div>
        <div style="font-size:13px;color:#e8edf5;line-height:1.6;">&#x26A0; ${relevantGap}</div>
      </div>
    </td></tr>`;
  }

  // GOLD MINES & GIMMES — highest-impact opportunity
  const goldmineHtml = `
  <tr><td style="padding:0 40px 24px;">
    <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F3AE; Gold Mines & Gimmes</h2>
    <div style="background:rgba(234,179,8,0.08);border:1px solid rgba(234,179,8,0.2);border-radius:12px;padding:20px;">
      <div style="font-size:14px;font-weight:700;color:#eab308;margin-bottom:8px;">Your fastest win</div>
      <p style="font-size:13px;color:#e8edf5;line-height:1.6;margin:0;">${dims.a1 < 20 && dimSignalsMap.a1 && !dimSignalsMap.a1.llms_txt
        ? `Create an <strong>llms.txt</strong> file at your domain root. This is a 15-minute fix that directly tells AI models how to interpret your brand. Score impact: +3-5 pts.`
        : dims.a2 < 15
        ? `Publish <strong>3 blog posts</strong> using your brand's exact positioning language. AI models learn your vocabulary from your content. Each post compounds. Score impact: +5-8 pts.`
        : dims.a3 < 15
        ? `Get mentioned in <strong>2-3 industry best-of lists</strong>. Third-party validation is the strongest recommendation signal AI looks for. Score impact: +8-12 pts.`
        : `Your brand is well-positioned. Focus on content freshness — AI training data evolves and brands that publish consistently stay top-of-mind.`
      }</p>
    </div>
  </td></tr>`;

  // Assemble the narrative sections (replaces execSummary + findingsHtml)
  const narrativeSections = foundationsHtml + baggageHtml + goldmineHtml;

  // ── Dimension Breakdown with Signals ──
  const dimBreakdownHtml = Object.entries(dims).map(([key, val]) => {
    const d = dimensionNames[key] || { name: key, icon: "", desc: "" };
    const pct = Math.round((val / 20) * 100);
    const barColor = pct >= 70 ? "#22c55e" : pct >= 50 ? "#eab308" : "#ef4444";
    const signals = dimSignalsMap[key] || {};

    // Extract 2-3 key signals per dimension
    let signalBullets = "";
    if (key === "a1") {
      const items = [];
      if (signals.llms_txt !== undefined) items.push(signals.llms_txt ? "llms.txt file found" : "No llms.txt file detected");
      if (signals.has_schema !== undefined) items.push(signals.has_schema ? "Schema.org structured data present" : "No structured data found");
      if (signals.allows_ai_crawlers !== undefined) items.push(signals.allows_ai_crawlers ? "AI crawlers allowed in robots.txt" : "AI crawlers may be blocked");
      if (signals.sitemap !== undefined) items.push(signals.sitemap ? "Sitemap.xml present" : "No sitemap found");
      signalBullets = items.slice(0, 3).map(i => `<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:2px 0;">&#x2022; ${i}</div>`).join("");
    } else if (key === "a2") {
      const items = [];
      const brandTerms = signals.brand_terms || [];
      if (brandTerms.length > 0) items.push(`Brand vocabulary detected: ${brandTerms.slice(0, 4).join(", ")}`);
      const aiDescs = signals.ai_descriptions || [];
      const matched = aiDescs.filter(d => d.vocab_matches > 0).length;
      items.push(`${matched}/${aiDescs.length} AI models echo your positioning vocabulary`);
      signalBullets = items.slice(0, 3).map(i => `<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:2px 0;">&#x2022; ${i}</div>`).join("");
    } else if (key === "a3") {
      const items = [];
      const models = signals.models || [];
      for (const m of models.slice(0, 2)) {
        if (m.appeared) items.push(`${m.model} recommends you when asked about ${industry || "your category"}`);
        else items.push(`${m.model} does not mention you in recommendations`);
      }
      signalBullets = items.slice(0, 3).map(i => `<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:2px 0;">&#x2022; ${i}</div>`).join("");
    } else if (key === "a4") {
      const items = [];
      const assocs = signals.associations || [];
      for (const a of assocs.slice(0, 2)) {
        if (a.text && !a.error) {
          const snippet = a.text.split(/[.!?]/)[0].substring(0, 80);
          items.push(`${a.model}: "${snippet}..."`);
        }
      }
      signalBullets = items.slice(0, 2).map(i => `<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:2px 0;">&#x2022; ${i}</div>`).join("");
    } else if (key === "a5") {
      const items = [];
      const voices = signals.voice_analysis || [];
      for (const v of voices.slice(0, 2)) {
        if (v.text && !v.error) {
          // Try to extract the 3-word voice description
          const threeWordMatch = v.text.match(/\b\w+[,\s]+\w+[,\s]+\w+\b/);
          if (threeWordMatch) items.push(`${v.model} describes voice as: ${threeWordMatch[0]}`);
          else items.push(`${v.model} analyzed your brand voice`);
        }
      }
      signalBullets = items.slice(0, 2).map(i => `<div style="font-size:12px;color:rgba(255,255,255,0.5);padding:2px 0;">&#x2022; ${i}</div>`).join("");
    }

    return `
      <tr><td style="padding:16px 16px 4px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="font-size:14px;font-weight:700;color:#e8edf5;">${d.icon} ${d.name}</td>
            <td style="text-align:right;font-size:14px;font-weight:700;color:${barColor};">${val}/20</td>
          </tr>
        </table>
      </td></tr>
      <tr><td style="padding:4px 16px;">
        <div style="background:rgba(255,255,255,0.08);border-radius:8px;height:20px;overflow:hidden;">
          <div style="background:${barColor};height:100%;width:${pct}%;border-radius:8px;"></div>
        </div>
      </td></tr>
      <tr><td style="padding:4px 16px 4px;">
        <div style="font-size:12px;color:rgba(255,255,255,0.4);font-style:italic;">${d.desc}</div>
      </td></tr>
      <tr><td style="padding:0 16px 16px;">
        ${signalBullets}
      </td></tr>`;
  }).join("");

  // ── Gap Analysis Section ──
  let gapHtml = "";
  if (gapAnalysis && (gapAnalysis.gaps?.length > 0 || gapAnalysis.website_claims)) {
    const gapItems = [];
    if (gapAnalysis.website_claims && gapAnalysis.website_claims !== "No positioning vocabulary found on homepage") {
      gapItems.push(`<tr><td style="padding:8px 0;font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;"><strong style="color:#2a93c1;">Your website says:</strong> ${gapAnalysis.website_claims}</td></tr>`);
    }
    if (gapAnalysis.ai_says && gapAnalysis.ai_says !== "No AI descriptions available") {
      const truncatedAi = gapAnalysis.ai_says.substring(0, 250);
      gapItems.push(`<tr><td style="padding:8px 0;font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;"><strong style="color:#f1420b;">AI says:</strong> ${truncatedAi}</td></tr>`);
    }
    if (gapAnalysis.gaps && gapAnalysis.gaps.length > 0) {
      for (const gap of gapAnalysis.gaps.slice(0, 3)) {
        gapItems.push(`<tr><td style="padding:6px 0;font-size:13px;color:rgba(255,255,255,0.6);line-height:1.5;">&#x26A0; ${gap}</td></tr>`);
      }
    }
    gapHtml = `
      <tr><td style="padding:0 40px 24px;">
        <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F50D; Gap Analysis</h2>
        <p style="font-size:12px;color:rgba(255,255,255,0.4);margin:0 0 12px;">What you say about yourself vs. what AI tells people about you</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:12px;">
          ${gapItems.join("")}
        </table>
      </td></tr>`;
  }

  // ── Answer Nuggets Section ──
  let nuggetsHtml = "";
  if (answerNuggets && answerNuggets.length > 0) {
    const nuggetItems = answerNuggets.slice(0, 4).map(n =>
      `<tr><td style="padding:10px 12px;border-bottom:1px solid rgba(255,255,255,0.04);">
        <div style="font-size:13px;font-weight:700;color:#2a93c1;margin-bottom:4px;">Q: ${n.question}</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;">A: ${n.answer.substring(0, 200)}</div>
      </td></tr>`
    ).join("");
    nuggetsHtml = `
      <tr><td style="padding:0 40px 24px;">
        <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 8px;">&#x1F4AC; What AI Says About You</h2>
        <p style="font-size:12px;color:rgba(255,255,255,0.4);margin:0 0 12px;">When someone asks AI about your brand, here is what it says</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
          ${nuggetItems}
        </table>
      </td></tr>`;
  }

  // ── Citation Tracking Section ──
  let citationHtml = "";
  if (citationTracking && citationTracking.total > 0) {
    const citRate = citationTracking.rate;
    const citColor = citRate >= 50 ? "#22c55e" : citRate >= 25 ? "#eab308" : "#ef4444";
    const queryRows = (citationTracking.results || []).slice(0, 4).map(r =>
      `<tr>
        <td style="padding:6px 8px;font-size:12px;color:rgba(255,255,255,0.6);border-bottom:1px solid rgba(255,255,255,0.04);">${r.query}</td>
        <td style="padding:6px 8px;font-size:12px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.04);color:${r.appeared ? '#22c55e' : '#ef4444'};">${r.appeared ? '&#x2705; Mentioned' : '&#x274C; Not found'}</td>
      </tr>`
    ).join("");
    citationHtml = `
      <tr><td style="padding:0 40px 24px;">
        <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 8px;">&#x1F4CA; Citation Tracking</h2>
        <p style="font-size:12px;color:rgba(255,255,255,0.4);margin:0 0 12px;">How often AI mentions your brand when asked relevant questions</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:12px;">
          <tr><td style="padding:8px 12px;">
            <div style="font-size:24px;font-weight:800;color:${citColor};">${citRate}%</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.4);">Citation Rate (${citationTracking.appearances}/${citationTracking.total} queries)</div>
          </td></tr>
          ${queryRows}
        </table>
      </td></tr>`;
  }

  // ── Content Authority Section ──
  let contentHtml = "";
  if (contentAuthority && Object.keys(contentAuthority).length > 0) {
    const caItems = [];
    if (contentAuthority.has_blog !== undefined) caItems.push(contentAuthority.has_blog ? "&#x2705; Blog detected" : "&#x274C; No blog found");
    if (contentAuthority.estimated_posts !== undefined) caItems.push(`Estimated blog posts: ~${contentAuthority.estimated_posts}`);
    if (contentAuthority.has_resources || contentAuthority.has_docs || contentAuthority.has_learn) caItems.push("&#x2705; Resource/documentation pages found");
    if (contentAuthority.ai_authority_assessment) caItems.push(`AI assessment: "${contentAuthority.ai_authority_assessment.substring(0, 120)}"`);
    if (caItems.length > 0) {
      contentHtml = `
        <tr><td style="padding:0 40px 24px;">
          <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 8px;">&#x1F4DA; Content Authority</h2>
          <p style="font-size:12px;color:rgba(255,255,255,0.4);margin:0 0 12px;">Your content footprint that feeds AI training data</p>
          <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:12px;">
            ${caItems.map(i => `<tr><td style="padding:6px 12px;font-size:13px;color:rgba(255,255,255,0.7);line-height:1.5;">${i}</td></tr>`).join("")}
          </table>
        </td></tr>`;
    }
  }

  // ── Competitive Context Section ──
  let competitiveHtml = "";
  if (leaderboard && leaderboard.position > 0) {
    const percentile = leaderboard.totalBrands > 1 ? Math.round(((leaderboard.totalBrands - leaderboard.position) / (leaderboard.totalBrands - 1)) * 100) : 50;
    const posColor = percentile >= 75 ? "#22c55e" : percentile >= 50 ? "#eab308" : "#ef4444";
    competitiveHtml = `
      <tr><td style="padding:0 40px 24px;">
        <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 8px;">&#x1F3C6; Competitive Context</h2>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);padding:16px;">
          <tr>
            <td style="text-align:center;padding:8px;">
              <div style="font-size:32px;font-weight:800;color:${posColor};">#${leaderboard.position}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.4);">of ${leaderboard.totalBrands} brands scored</div>
            </td>
            <td style="text-align:center;padding:8px;">
              <div style="font-size:32px;font-weight:800;color:#fff;">${totalScore}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.4);">Your Score</div>
            </td>
            <td style="text-align:center;padding:8px;">
              <div style="font-size:32px;font-weight:800;color:rgba(255,255,255,0.5);">${leaderboard.avgScore}</div>
              <div style="font-size:12px;color:rgba(255,255,255,0.4);">Average Score</div>
            </td>
          </tr>
          <tr><td colspan="3" style="padding:8px 0 0;font-size:12px;color:rgba(255,255,255,0.5);text-align:center;">You are in the top ${100 - percentile}% of all brands we have analyzed for AI readiness.</td></tr>
        </table>
      </td></tr>`;
  }

  // ── Strategic Recommendations (data-driven, ALL dimensions checked) ──
  const recommendations = [];

  // A1 Structural
  const a1Score = dims.a1 || 0;
  if (a1Score < 20) {
    if (dimSignalsMap.a1 && !dimSignalsMap.a1.llms_txt) {
      recommendations.push({ priority: "HIGH", dim: "Structural Readiness (A1)", text: `Create an <strong>llms.txt</strong> file at your domain root. This tells AI models exactly how to interpret your site.`, points: "+3 pts", difficulty: "Easy" });
    }
    if (dimSignalsMap.a1 && !dimSignalsMap.a1.has_schema && !dimSignalsMap.a1.schema_org) {
      recommendations.push({ priority: "HIGH", dim: "Structural Readiness (A1)", text: `Add <strong>JSON-LD structured data</strong> (Organization schema) to your homepage. This gives AI models structured facts about your brand.`, points: "+3 pts", difficulty: "Easy" });
    }
    if (a1Score < 15) {
      recommendations.push({ priority: "MED", dim: "Structural Readiness (A1)", text: `Ensure AI crawlers are allowed in <strong>robots.txt</strong> and all Open Graph tags are present on every page.`, points: "+2 pts", difficulty: "Easy" });
    }
  }

  // A2 Semantic
  const a2Score = dims.a2 || 0;
  if (a2Score < 15) {
    recommendations.push({ priority: a2Score < 8 ? "HIGH" : "MED", dim: "Semantic Clarity (A2)", text: `Publish <strong>5 authoritative blog posts</strong> about your core product category. AI models learn your vocabulary from your content.`, points: "+5 pts", difficulty: "Medium" });
    recommendations.push({ priority: "MED", dim: "Semantic Clarity (A2)", text: `Create a clear <strong>"What We Do" page</strong> with unambiguous positioning. AI models struggle with vague messaging.`, points: "+3 pts", difficulty: "Easy" });
  }

  // A3 Synthetic
  const a3Score = dims.a3 || 0;
  if (a3Score < 15) {
    recommendations.push({ priority: a3Score < 5 ? "HIGH" : "MED", dim: "Synthetic Customer (A3)", text: `Get mentioned in <strong>industry comparison articles, directories, and best-of lists</strong>. Third-party mentions are the strongest recommendation signal.`, points: "+8 pts", difficulty: "Hard" });
    recommendations.push({ priority: "MED", dim: "Synthetic Customer (A3)", text: `Create detailed <strong>use-case pages</strong> for your top 3 customer segments. When people ask AI "what tool for X?", AI looks for use-case matches.`, points: "+4 pts", difficulty: "Medium" });
  }

  // A4 Emotional
  const a4Score = dims.a4 || 0;
  if (a4Score < 15) {
    recommendations.push({ priority: "MED", dim: "Emotional Residue (A4)", text: `Tell your <strong>brand story publicly</strong> — founder story, mission, values. AI retains narratives and brands with compelling stories leave stronger impressions.`, points: "+5 pts", difficulty: "Medium" });
  }

  // A5 Voice
  const a5Score = dims.a5 || 0;
  if (a5Score < 15) {
    recommendations.push({ priority: "MED", dim: "Voice & Archetype (A5)", text: `Develop a <strong>distinctive brand voice guide</strong> and apply it consistently. Brands with recognizable voices stand out in AI responses.`, points: "+5 pts", difficulty: "Medium" });
  }

  // Citation-based
  if (citationTracking && citationTracking.rate < 25) {
    recommendations.push({ priority: "HIGH", dim: "Citation Rate", text: `Your citation rate is critically low (<strong>${citationTracking.rate}%</strong>). Publish <strong>10-20 authoritative articles</strong> in your space to become part of AI training data.`, points: "+10 pts", difficulty: "Hard" });
  }

  // Sort by priority
  const priorityOrder = { HIGH: 0, MED: 1, LOW: 2 };
  recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  if (recommendations.length === 0) {
    recommendations.push({ priority: "LOW", dim: "All Dimensions", text: `Your brand scores well. Focus on <strong>content freshness</strong> — AI training data evolves and brands that stop publishing lose ground.`, points: "+1-3 pts", difficulty: "Easy" });
  }

  const priorityColors = { HIGH: "#ef4444", MED: "#eab308", LOW: "#22c55e" };
  const recsHtml = recommendations.slice(0, 7).map((r, i) =>
    `<tr><td style="padding:14px 16px;font-size:14px;color:#e8edf5;line-height:1.6;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,${i % 2 === 0 ? '0.02' : '0.00'});">
      <div style="margin-bottom:6px;">
        <span style="display:inline-block;background:${priorityColors[r.priority]};color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;margin-right:6px;">${r.priority}</span>
        <span style="font-size:11px;color:rgba(255,255,255,0.4);">${r.dim || ''}</span>
      </div>
      <div>${r.text}</div>
      <div style="margin-top:6px;font-size:12px;">
        <span style="color:#22c55e;font-weight:700;">${r.points || ''}</span>
        <span style="color:rgba(255,255,255,0.3);margin-left:8px;">Effort: ${r.difficulty || 'Medium'}</span>
      </div>
    </td></tr>`
  ).join("");

  // ── Assemble Full Email HTML ──
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="margin:0;padding:0;background:#080a12;font-family:'Inter',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#080a12;padding:40px 20px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#0d1117;border-radius:16px;border:1px solid rgba(255,255,255,0.08);">

  <!-- Header -->
  <tr><td style="padding:40px 40px 16px;text-align:center;">
    <div style="font-size:12px;font-weight:700;letter-spacing:0.15em;color:rgba(255,255,255,0.4);margin-bottom:8px;">
      <span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span><span style="color:#fff;">.AI</span>
    </div>
    <h1 style="font-size:28px;font-weight:800;color:#fff;margin:0 0 4px;">Your BrainScore Report</h1>
    <p style="font-size:14px;color:rgba(255,255,255,0.45);margin:0;">AI Brand Readiness Analysis for <strong style="color:rgba(255,255,255,0.7);">${brandUrl}</strong></p>
  </td></tr>

  <!-- Score Hero -->
  <tr><td style="padding:16px 40px 32px;text-align:center;">
    <div style="display:inline-block;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:32px 48px;">
      <div style="font-size:64px;font-weight:900;color:#fff;line-height:1;">${totalScore}</div>
      <div style="font-size:14px;color:rgba(255,255,255,0.5);margin:4px 0 12px;">/100</div>
      <div style="display:inline-block;background:${tierColor};color:#fff;font-size:14px;font-weight:700;padding:6px 20px;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em;">${tier}</div>
    </div>
  </td></tr>

  <!-- ARA Narrative Sections: Foundations & Fortresses, Baggage & Blindspots, Gold Mines & Gimmes -->
  ${narrativeSections}

  <!-- Full Dimension Breakdown -->
  <tr><td style="padding:0 40px 24px;">
    <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F4CA; Dimension Breakdown</h2>
    <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
      ${dimBreakdownHtml}
    </table>
  </td></tr>

  <!-- Gap Analysis -->
  ${gapHtml}

  <!-- Answer Nuggets -->
  ${nuggetsHtml}

  <!-- Citation Tracking -->
  ${citationHtml}

  <!-- Content Authority -->
  ${contentHtml}

  <!-- Competitive Context -->
  ${competitiveHtml}

  <!-- Strategic Recommendations -->
  <tr><td style="padding:0 40px 24px;">
    <h2 style="font-size:18px;font-weight:700;color:#fff;margin:0 0 12px;">&#x1F680; Strategic Recommendations</h2>
    <table width="100%" cellpadding="0" cellspacing="0">${recsHtml}</table>
  </td></tr>

  <!-- CTA -->
  <tr><td style="padding:16px 40px 40px;text-align:center;">
    <div style="background:linear-gradient(135deg, rgba(42,147,193,0.1), rgba(241,66,11,0.1));border:1px solid rgba(42,147,193,0.3);border-radius:12px;padding:24px;">
      <p style="font-size:16px;font-weight:700;color:#fff;margin:0 0 8px;">Want help improving your BrainScore?</p>
      <p style="font-size:13px;color:rgba(255,255,255,0.5);margin:0 0 16px;">Our AI partnership platform helps brands become the ones AI recommends.</p>
      <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="https://purebrain.ai" style="height:48px;v-text-anchor:middle;width:320px;" arcsize="20%" strokecolor="#2a93c1" fillcolor="#2a93c1"><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">Start Your AI Partnership</center></v:roundrect><![endif]-->
      <table cellpadding="0" cellspacing="0" style="margin:0 auto;"><tr><td align="center" bgcolor="#2a93c1" style="border-radius:10px;padding:14px 36px;"><a href="https://purebrain.ai" style="color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;font-family:Arial,sans-serif;display:inline-block;">Start Your AI Partnership &rarr;</a></td></tr></table>
    </div>
  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:0 40px 32px;text-align:center;">
    <div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:20px;">
      <p style="font-size:11px;color:rgba(255,255,255,0.25);margin:0 0 4px;">BrainScore measures how well AI understands, finds, and recommends your brand across 5 dimensions.</p>
      <p style="font-size:11px;color:rgba(255,255,255,0.25);margin:0 0 4px;">Powered by <span style="color:#2a93c1;">PUREBR</span><span style="color:#f1420b;">AI</span><span style="color:#2a93c1;">N</span><span style="color:#fff;">.AI</span> | AI Brand Readiness Platform</p>
      <p style="font-size:11px;color:rgba(255,255,255,0.2);margin:0;">Report generated ${new Date().toISOString().split("T")[0]}</p>
    </div>
  </td></tr>

</table>
</td></tr></table>
</body></html>`;

  const res = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: {
      "api-key": apiKey,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sender: { name: "PureBrain", email: "purebrain@puremarketing.ai" },
      to: [{ email: toEmail }],
      bcc: [{ email: "jared@puretechnology.nyc" }],
      subject: `Your BrainScore Report: ${brandUrl} — ${totalScore}/100 ${tier}`,
      htmlContent: html,
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Brevo API ${res.status}: ${errText}`);
  }
}
