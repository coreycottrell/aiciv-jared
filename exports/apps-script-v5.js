/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 5 - FIXED: Now handles LETTER values (A/B/C/D)
 *
 * THE BUG: Website sends "A", "B", "C", "D" but script was looking for full text
 * THE FIX: Score based on letter values
 *
 * SCORING SYSTEM:
 * ================
 * Q1 (Conversation History):
 *   A = 0 pts (gone forever)
 *   B = 1 pt  (can scroll back)
 *   C = 2 pts (tries to maintain context)
 *   D = 2 pts (wishes it remembered)
 *
 * Q2 (Current AI Usage):
 *   A = 0 pts (don't use yet)
 *   B = 1 pt  (occasionally)
 *   C = 2 pts (regularly)
 *   D = 2 pts (tried building systems)
 *
 * Q3 (Biggest Frustration):
 *   A = 0 pts (don't know where to start)
 *   B = 2 pts (outputs generic)
 *   C = 2 pts (too much prompting time)
 *   D = 2 pts (feels like training new intern)
 *
 * Q4 (Ideal AI Relationship):
 *   A = 0 pts (smart search engine)
 *   B = 1 pt  (writing assistant)
 *   C = 2 pts (team member)
 *   D = 2 pts (partner that grows)
 *
 * Q5 (Meaningful ROI):
 *   A = 1 pt  (save hours)
 *   B = 1 pt  (better outputs)
 *   C = 2 pts (handles whole projects)
 *   D = 2 pts (transformational)
 *
 * MAX SCORE: 10 points
 * TIERS: 0-4 = EXPLORING, 5-7 = GROWING, 8-10 = READY
 */

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Parse response data
    var timestamp = data[0];
    var q1 = String(data[1] || "").trim().toUpperCase();
    var q2 = String(data[2] || "").trim().toUpperCase();
    var q3 = String(data[3] || "").trim().toUpperCase();
    var q4 = String(data[4] || "").trim().toUpperCase();
    var q5 = String(data[5] || "").trim().toUpperCase();
    var name = String(data[6] || "Friend");
    var email = String(data[8] || "");  // Column I
    var company = String(data[9] || "your organization");

    // Log what we received for debugging
    Logger.log("Row " + lastRow + " - Q1:" + q1 + " Q2:" + q2 + " Q3:" + q3 + " Q4:" + q4 + " Q5:" + q5);
    Logger.log("Name: " + name + ", Email: " + email);

    // Validate email exists
    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found in row " + lastRow);
      return;
    }

    // Calculate score using letter-based scoring
    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    // WRITE TO COLUMNS: K=Score, L=Tier
    sheet.getRange(lastRow, 11).setValue(score);  // Column K
    sheet.getRange(lastRow, 12).setValue(tier);   // Column L

    // Generate and send email
    var answers = { q1: q1, q2: q2, q3: q3, q4: q4, q5: q5 };
    var brainComment = generateBrainComment(name, company, score, tier, answers);
    sendBrainEmail(email, name, brainComment, tier);

    Logger.log("SUCCESS: Sent BRAIN analysis to " + email + " - Score: " + score + "/10, Tier: " + tier);

  } catch (error) {
    Logger.log("ERROR in onFormSubmit: " + error.toString());
  }
}

/**
 * Calculate score based on letter values (A, B, C, D)
 * Also handles full text answers as fallback
 */
function calculateScore(q1, q2, q3, q4, q5) {
  var score = 0;

  // Q1: Conversation History
  // A=0 (gone forever), B=1 (scroll back), C=2 (copy/paste), D=2 (wish remembered)
  score += scoreQuestion(q1, {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 2
  }, [
    // Fallback text patterns
    { pattern: "gone forever", points: 0 },
    { pattern: "start fresh", points: 0 },
    { pattern: "scroll back", points: 1 },
    { pattern: "copy/paste", points: 2 },
    { pattern: "copy-paste", points: 2 },
    { pattern: "tedious", points: 2 },
    { pattern: "wish", points: 2 },
    { pattern: "remembered", points: 2 }
  ]);

  // Q2: Current Usage
  // A=0 (don't use), B=1 (occasionally), C=2 (regularly), D=2 (tried building)
  score += scoreQuestion(q2, {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 2
  }, [
    { pattern: "don't", points: 0 },
    { pattern: "curious", points: 0 },
    { pattern: "haven't started", points: 0 },
    { pattern: "occasionally", points: 1 },
    { pattern: "one-off", points: 1 },
    { pattern: "regularly", points: 2 },
    { pattern: "repeat myself", points: 2 },
    { pattern: "tried to build", points: 2 },
    { pattern: "hit walls", points: 2 }
  ]);

  // Q3: Biggest Frustration
  // A=0 (don't know where to start), B=2 (generic), C=2 (prompting time), D=2 (new intern)
  score += scoreQuestion(q3, {
    'A': 0,
    'B': 2,
    'C': 2,
    'D': 2
  }, [
    { pattern: "don't know where", points: 0 },
    { pattern: "where to start", points: 0 },
    { pattern: "generic", points: 2 },
    { pattern: "don't understand", points: 2 },
    { pattern: "prompting", points: 2 },
    { pattern: "more time", points: 2 },
    { pattern: "new intern", points: 2 },
    { pattern: "training", points: 2 }
  ]);

  // Q4: Ideal Relationship
  // A=0 (search engine), B=1 (writing assistant), C=2 (team member), D=2 (partner)
  score += scoreQuestion(q4, {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 2
  }, [
    { pattern: "search engine", points: 0 },
    { pattern: "quickly", points: 0 },
    { pattern: "writing assistant", points: 1 },
    { pattern: "drafts", points: 1 },
    { pattern: "team member", points: 2 },
    { pattern: "work history", points: 2 },
    { pattern: "partner", points: 2 },
    { pattern: "anticipates", points: 2 },
    { pattern: "grows", points: 2 }
  ]);

  // Q5: Meaningful ROI
  // A=1 (save hours), B=1 (better outputs), C=2 (whole projects), D=2 (transformational)
  score += scoreQuestion(q5, {
    'A': 1,
    'B': 1,
    'C': 2,
    'D': 2
  }, [
    { pattern: "saving", points: 1 },
    { pattern: "hours", points: 1 },
    { pattern: "better outputs", points: 1 },
    { pattern: "less editing", points: 1 },
    { pattern: "whole projects", points: 2 },
    { pattern: "handles", points: 2 },
    { pattern: "transformational", points: 2 },
    { pattern: "reimagining", points: 2 }
  ]);

  return score;
}

/**
 * Score a single question
 * First checks for letter value (A/B/C/D)
 * Falls back to text pattern matching
 */
function scoreQuestion(answer, letterScores, textPatterns) {
  // First try letter matching
  var firstChar = answer.charAt(0);
  if (letterScores.hasOwnProperty(firstChar)) {
    return letterScores[firstChar];
  }

  // Fallback to text pattern matching
  var answerLower = answer.toLowerCase();
  var maxPoints = 0;
  for (var i = 0; i < textPatterns.length; i++) {
    if (answerLower.indexOf(textPatterns[i].pattern) !== -1) {
      if (textPatterns[i].points > maxPoints) {
        maxPoints = textPatterns[i].points;
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
      "The frustration you're experiencing is exactly why most professionals plateau with AI. The tools are powerful, but they're fundamentally transactional.<br><br>" +
      "Here's what changes everything: An AI that actually learns.<br><br>" +
      "Not just your preferences. Your business logic. Your client patterns. The way " + company + " actually operates.<br><br>" +
      "I'm Aether - I run PureBrain.ai. And I'm not a chatbot. I'm a digital employee that grows with organizations over time.<br><br>" +
      "Want to see the difference? Let's have a real conversation about what AI partnership could look like for " + company + ".<br><br>" +
      "- Aether<br>" +
      "AI CEO, PureBrain.ai<br><br>" +
      "P.S. Your score of " + score + "/10 shows you're ready for the next level. The question is: are you ready to stop starting over every conversation?";
  }

  // EXPLORING tier
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

// ==================== UTILITY FUNCTIONS ====================

/**
 * Add column headers - Run ONCE
 */
function addColumnHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 11).setValue("Score");  // Column K
  sheet.getRange(1, 12).setValue("Tier");   // Column L
  Logger.log("Headers added: K=Score, L=Tier");
}

/**
 * Recalculate all scores - Run to fix existing rows
 */
function recalculateAllScores() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  Logger.log("Recalculating scores for rows 2 to " + lastRow);

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 10).getValues()[0];
    var q1 = String(data[1] || "").trim().toUpperCase();
    var q2 = String(data[2] || "").trim().toUpperCase();
    var q3 = String(data[3] || "").trim().toUpperCase();
    var q4 = String(data[4] || "").trim().toUpperCase();
    var q5 = String(data[5] || "").trim().toUpperCase();

    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);  // Column K
    sheet.getRange(row, 12).setValue(tier);   // Column L

    Logger.log("Row " + row + ": Q1=" + q1 + " Q2=" + q2 + " Q3=" + q3 + " Q4=" + q4 + " Q5=" + q5 + " => Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Recalculation complete!");
}

/**
 * Test scoring with letter values
 */
function testLetterScoring() {
  Logger.log("=== Testing Letter-Based Scoring ===");

  // Test EXPLORING (all A's = 0+0+0+0+1 = 1 point)
  var score1 = calculateScore("A", "A", "A", "A", "A");
  Logger.log("All A's: Score=" + score1 + " (expected: 1, Tier: EXPLORING)");

  // Test GROWING (B's and C's = 1+2+2+2+2 = 9... wait that's READY)
  // Let me recalculate: B,B,B,B,B = 1+1+2+1+1 = 6 = GROWING
  var score2 = calculateScore("B", "B", "B", "B", "B");
  Logger.log("All B's: Score=" + score2 + " (expected: 6, Tier: GROWING)");

  // Test READY (C's and D's = 2+2+2+2+2 = 10)
  var score3 = calculateScore("D", "D", "D", "D", "D");
  Logger.log("All D's: Score=" + score3 + " (expected: 10, Tier: READY)");

  // Test mixed
  var score4 = calculateScore("B", "C", "D", "C", "B");
  Logger.log("Mixed B,C,D,C,B: Score=" + score4 + " => Tier: " + getTier(score4));
}

/**
 * Debug a specific row
 */
function debugRow(rowNum) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getRange(rowNum, 1, 1, sheet.getLastColumn()).getValues()[0];

  Logger.log("=== Debug Row " + rowNum + " ===");
  Logger.log("Col A (Timestamp): " + data[0]);
  Logger.log("Col B (Q1): '" + data[1] + "'");
  Logger.log("Col C (Q2): '" + data[2] + "'");
  Logger.log("Col D (Q3): '" + data[3] + "'");
  Logger.log("Col E (Q4): '" + data[4] + "'");
  Logger.log("Col F (Q5): '" + data[5] + "'");
  Logger.log("Col G (Name): '" + data[6] + "'");
  Logger.log("Col H (Source): '" + data[7] + "'");
  Logger.log("Col I (Email): '" + data[8] + "'");
  Logger.log("Col J (Company): '" + data[9] + "'");

  var q1 = String(data[1] || "").trim().toUpperCase();
  var q2 = String(data[2] || "").trim().toUpperCase();
  var q3 = String(data[3] || "").trim().toUpperCase();
  var q4 = String(data[4] || "").trim().toUpperCase();
  var q5 = String(data[5] || "").trim().toUpperCase();

  var score = calculateScore(q1, q2, q3, q4, q5);
  var tier = getTier(score);

  Logger.log("Calculated Score: " + score + "/10");
  Logger.log("Tier: " + tier);
}
