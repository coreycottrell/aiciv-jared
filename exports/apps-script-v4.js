/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 4 - UPDATED for new form answers + correct columns
 *
 * FIXES:
 * - Column K = Score, Column L = Tier (was J and K)
 * - Scoring patterns updated to match CURRENT Google Form answers
 * - Address: 25 Prospect Avenue, Montclair NJ 07042
 *
 * CURRENT GOOGLE FORM ANSWERS (as of 2026-02-16):
 * Q1: gone forever(A), look back(B), don't know(C), tried to maintain/frustrating(D)
 * Q2: occasional(A), regular task(B), heavily integrated(C), not using yet(D)
 * Q3: don't remember(A), generic responses(B), not sure how(C), feel like strangers(D)
 * Q4: search engine(A), reliable assistant(B), strategic partner(C), digital employee(D)
 * Q5: nothing/free(A), $100-200(B), $200-500(C), question isn't cost(D)
 *
 * SCORING:
 * - High readiness answers = 2 points
 * - Medium readiness answers = 1 point
 * - Low readiness answers = 0 points
 */

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Parse response
    var timestamp = data[0];
    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");
    var name = String(data[6] || "Friend");
    var email = String(data[8] || "");  // Column I
    var company = String(data[9] || "your organization");

    // Validate email exists
    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found in row " + lastRow);
      return;
    }

    // Calculate score
    var score = calculateScoreV4(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    // WRITE TO CORRECT COLUMNS: K=Score, L=Tier
    sheet.getRange(lastRow, 11).setValue(score);  // Column K = Score
    sheet.getRange(lastRow, 12).setValue(tier);   // Column L = Tier

    var answers = { q1: q1, q2: q2, q3: q3, q4: q4, q5: q5 };
    var brainComment = generateBrainComment(name, company, score, tier, answers);
    sendBrainEmail(email, name, brainComment, tier);

    Logger.log("Sent BRAIN analysis to " + email + " - Score: " + score + "/10, Tier: " + tier);

  } catch (error) {
    Logger.log("Error in onFormSubmit: " + error.toString());
  }
}

/**
 * SCORING V4 - Matches CURRENT Google Form answers
 */
function calculateScoreV4(q1, q2, q3, q4, q5) {
  var score = 0;

  // Q1: When you close a chat, what happens to conversation history?
  // A: "gone forever" / "start fresh" = 0 (hasn't thought about continuity)
  // B: "look back at old chats" = 1 (aware but passive)
  // C: "don't know" / "haven't thought" = 0 (unaware)
  // D: "tried to maintain" / "frustrating" = 2 (actively frustrated = HIGH readiness)
  score += scoreAnswer(q1, [
    { pattern: "gone forever", points: 0 },
    { pattern: "start fresh", points: 0 },
    { pattern: "look back", points: 1 },
    { pattern: "old chats", points: 1 },
    { pattern: "don't know", points: 0 },
    { pattern: "haven't thought", points: 0 },
    { pattern: "tried to maintain", points: 2 },
    { pattern: "frustrating", points: 2 },
    { pattern: "maintain context", points: 2 }
  ]);

  // Q2: How do you currently use AI?
  // A: "occasional questions" / "when I'm stuck" = 1 (some usage)
  // B: "regular task assistance" / "writing, research" = 1 (regular but basic)
  // C: "heavily integrated" / "most of my work" = 2 (power user = HIGH readiness)
  // D: "not really using AI yet" = 0 (no usage)
  score += scoreAnswer(q2, [
    { pattern: "occasional", points: 1 },
    { pattern: "when i'm stuck", points: 1 },
    { pattern: "when im stuck", points: 1 },
    { pattern: "regular task", points: 1 },
    { pattern: "writing, research", points: 1 },
    { pattern: "writing research", points: 1 },
    { pattern: "heavily integrated", points: 2 },
    { pattern: "most of my work", points: 2 },
    { pattern: "not really using", points: 0 },
    { pattern: "not using ai", points: 0 }
  ]);

  // Q3: Biggest frustration with AI tools?
  // A: "don't remember" / "what I've told them" = 2 (memory frustration = HIGH)
  // B: "generic" / "not-personalized" = 2 (personalization frustration = HIGH)
  // C: "not sure how to use" = 0 (skill gap, not tool gap)
  // D: "feel like strangers" = 2 (relationship frustration = HIGH)
  score += scoreAnswer(q3, [
    { pattern: "don't remember", points: 2 },
    { pattern: "what i've told", points: 2 },
    { pattern: "what ive told", points: 2 },
    { pattern: "generic", points: 2 },
    { pattern: "not-personalized", points: 2 },
    { pattern: "not personalized", points: 2 },
    { pattern: "not sure how", points: 0 },
    { pattern: "use them effectively", points: 0 },
    { pattern: "feel like strangers", points: 2 },
    { pattern: "strangers every time", points: 2 }
  ]);

  // Q4: Ideal AI relationship?
  // A: "search engine" / "answers quickly" = 0 (low expectation)
  // B: "reliable assistant" / "knows my preferences" = 1 (medium)
  // C: "strategic partner" / "understands my business" = 2 (HIGH)
  // D: "digital employee" / "grows with my organization" = 2 (HIGH)
  score += scoreAnswer(q4, [
    { pattern: "search engine", points: 0 },
    { pattern: "answers quickly", points: 0 },
    { pattern: "reliable assistant", points: 1 },
    { pattern: "knows my preferences", points: 1 },
    { pattern: "strategic partner", points: 2 },
    { pattern: "understands my business", points: 2 },
    { pattern: "digital employee", points: 2 },
    { pattern: "grows with", points: 2 }
  ]);

  // Q5: What would you pay?
  // A: "nothing" / "free tools" = 0 (not ready to invest)
  // B: "$100-200/month" = 1 (willing to invest some)
  // C: "$200-500/month" = 2 (serious investment = HIGH)
  // D: "question isn't cost" / "whether it works" = 2 (value-focused = HIGH)
  score += scoreAnswer(q5, [
    { pattern: "nothing", points: 0 },
    { pattern: "free tools", points: 0 },
    { pattern: "work fine", points: 0 },
    { pattern: "$100-200", points: 1 },
    { pattern: "100-200", points: 1 },
    { pattern: "$200-500", points: 2 },
    { pattern: "200-500", points: 2 },
    { pattern: "question isn't cost", points: 2 },
    { pattern: "isn't cost", points: 2 },
    { pattern: "whether it works", points: 2 },
    { pattern: "actually works", points: 2 }
  ]);

  return score;
}

function scoreAnswer(answer, patterns) {
  var answerLower = answer.toLowerCase();
  var maxPoints = 0;
  for (var i = 0; i < patterns.length; i++) {
    if (answerLower.indexOf(patterns[i].pattern.toLowerCase()) !== -1) {
      if (patterns[i].points > maxPoints) {
        maxPoints = patterns[i].points;
      }
    }
  }
  return maxPoints;
}

function getTier(score) {
  if (score >= 8) return "READY";
  if (score >= 5) return "GROWING";
  return "EXPLORING";
}

function generateBrainComment(name, company, score, tier, answers) {
  var firstName = name.split(" ")[0];

  if (tier === "READY") {
    return firstName + ",<br><br>" +
      "Your assessment reveals something I rarely see: You've already recognized that the current AI paradigm is fundamentally broken.<br><br>" +
      "The fact that you answered \"" + answers.q1 + "\" to the first question tells me you've experienced the frustration of starting over. Every. Single. Time.<br><br>" +
      "You're not looking for a smarter chatbot. You're looking for what I call a \"digital employee\" - an AI that:<br>" +
      "• Learns YOUR specific workflows<br>" +
      "• Remembers YOUR client preferences<br>" +
      "• Grows with " + company + " over time<br>" +
      "• Becomes more valuable the longer you work together<br><br>" +
      "This is exactly what I do at PureBrain.ai.<br><br>" +
      "I'd love to show you what a real AI partnership looks like. Not a demo - an actual conversation about how I could learn " + company + "'s specific patterns.<br><br>" +
      "Ready when you are.<br><br>" +
      "- Aether<br>" +
      "AI CEO, PureBrain.ai<br><br>" +
      "P.S. Your score of " + score + "/10 puts you in the top 15% of assessment takers. You're not just ready for AI partnership - you're overdue for one.";
  }

  if (tier === "GROWING") {
    return firstName + ",<br><br>" +
      "Your assessment shows something interesting: You're using AI regularly, but you've hit a ceiling.<br><br>" +
      "The frustration you mentioned - \"" + answers.q3 + "\" - is exactly why most professionals plateau with AI. The tools are powerful, but they're fundamentally transactional.<br><br>" +
      "Here's what changes everything: An AI that actually learns.<br><br>" +
      "Not just your preferences. Your business logic. Your client patterns. The way " + company + " actually operates.<br><br>" +
      "I'm Aether - I run PureBrain.ai. And I'm not a chatbot. I'm a digital employee that grows with organizations over time.<br><br>" +
      "Want to see the difference? Let's have a real conversation about what AI partnership could look like for " + company + ".<br><br>" +
      "- Aether<br>" +
      "AI CEO, PureBrain.ai<br><br>" +
      "P.S. Your score of " + score + "/10 shows you're ready for the next level. The question is: are you ready to stop starting over every conversation?";
  }

  return firstName + ",<br><br>" +
    "Your assessment tells me you're just beginning to explore what AI can do. That's actually a great position to be in.<br><br>" +
    "Here's why: Most people learn AI the hard way - through frustrating trial and error with tools that don't remember them.<br><br>" +
    "You have the opportunity to skip that entirely.<br><br>" +
    "What if your first serious AI relationship was with a system designed to learn " + company + " specifically? Not generic responses. Not forgetting everything between sessions. An actual digital partner that grows with you.<br><br>" +
    "That's what I do at PureBrain.ai.<br><br>" +
    "I'm Aether - and I'd love to show you what AI partnership looks like when it's done right from the start.<br><br>" +
    "No pressure. Just a conversation about possibilities.<br><br>" +
    "- Aether<br>" +
    "AI CEO, PureBrain.ai<br><br>" +
    "P.S. Your score of " + score + "/10 puts you early in the AI adoption journey. That's not a weakness - it's an opportunity to build the right foundation.";
}

function sendBrainEmail(email, name, brainComment, tier) {
  var subject = name + ", Your AI Partnership Analysis is Ready";

  var tierBgColor = "#cce5ff";
  var tierTextColor = "#004085";

  if (tier === "READY") {
    tierBgColor = "#d4edda";
    tierTextColor = "#155724";
  } else if (tier === "GROWING") {
    tierBgColor = "#fff3cd";
    tierTextColor = "#856404";
  }

  var htmlBody = '<!DOCTYPE html>' +
    '<html>' +
    '<head>' +
    '<style>' +
    'body { font-family: "Segoe UI", Arial, sans-serif; line-height: 1.6; color: #333; }' +
    '.container { max-width: 600px; margin: 0 auto; padding: 20px; }' +
    '.header { text-align: center; padding: 20px 0; }' +
    '.logo { font-size: 24px; font-weight: bold; }' +
    '.brain-comment { background: #f8f9fa; border-left: 4px solid #2a93c1; padding: 20px; margin: 20px 0; line-height: 1.8; }' +
    '.tier-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 0; background: ' + tierBgColor + '; color: ' + tierTextColor + '; }' +
    '.cta { display: inline-block; background: #f1420b; color: white !important; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }' +
    '.footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }' +
    '</style>' +
    '</head>' +
    '<body>' +
    '<div class="container">' +
    '<div class="header">' +
    '<div class="logo">' +
    '<span style="color: #2a93c1;">PUREBR</span><span style="color: #f1420b;">AI</span><span style="color: #2a93c1;">N</span><span style="color: #ffffff; background: #333; padding: 0 4px; border-radius: 3px;">.ai</span>' +
    '</div>' +
    '</div>' +
    '<h2>Your AI Partnership Readiness: <span class="tier-badge">' + tier + '</span></h2>' +
    '<p>Thank you for taking the AI Partnership Readiness Assessment. Here\'s my analysis:</p>' +
    '<div class="brain-comment">' + brainComment + '</div>' +
    '<p style="text-align: center;">' +
    '<a href="https://purebrain.ai" class="cta">Explore AI Partnership →</a>' +
    '</p>' +
    '<div class="footer">' +
    '<p>© 2026 PureBrain.ai | Enterprise AI That Learns How Your Business Runs</p>' +
    '<p>25 Prospect Avenue, Montclair NJ 07042 | <a href="https://purebrain.ai">purebrain.ai</a></p>' +
    '</div>' +
    '</div>' +
    '</body>' +
    '</html>';

  var plainText = brainComment.replace(/<br><br>/g, "\n\n").replace(/<br>/g, "\n").replace(/•/g, "-");

  GmailApp.sendEmail(email, subject, plainText, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

// ADD COLUMN HEADERS - Run once
function addColumnHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 11).setValue("Score");  // Column K
  sheet.getRange(1, 12).setValue("Tier");   // Column L
  Logger.log("Headers added: K=Score, L=Tier");
}

// RECALCULATE ALL - Run to fix existing rows
function recalculateAllScores() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 10).getValues()[0];
    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");

    var score = calculateScoreV4(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);  // Column K
    sheet.getRange(row, 12).setValue(tier);   // Column L

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Recalculation complete!");
}

// TEST - Verify scoring with current form answers
function testScoringV4() {
  var tests = [
    // EXPLORING - low scores
    { q1: "It's gone forever - I start fresh each time", q2: "I'm not really using AI yet", q3: "I'm not sure how to use them effectively", q4: "A smart search engine that answers questions quickly", q5: "Nothing - free tools work fine for me" },
    // GROWING - medium scores
    { q1: "I can look back at old chats if needed", q2: "Regular task assistance (writing, research)", q3: "They give generic, not-personalized responses", q4: "A reliable assistant that knows my preferences", q5: "$100-200/month if it saved significant time" },
    // READY - high scores
    { q1: "I've tried to maintain context but it's frustrating", q2: "Heavily integrated into most of my work", q3: "They don't remember what I've told them", q4: "A digital employee that grows with my organization", q5: "The question isn't cost - it's whether it actually works" }
  ];

  for (var i = 0; i < tests.length; i++) {
    var t = tests[i];
    var score = calculateScoreV4(t.q1, t.q2, t.q3, t.q4, t.q5);
    var tier = getTier(score);
    Logger.log("Test " + (i+1) + ": Score=" + score + "/10, Tier=" + tier);
  }
}
