/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 7 - CORRECTED KEYWORDS from actual Google Form
 *
 * ACTUAL FORM ANSWERS (from Google Form):
 * ========================================
 *
 * Q1: When you close a chat with ChatGPT or Claude, what happens to your conversation history?
 *   A) It's gone forever - I start fresh each time → 0 pts
 *   B) I can look back at old chats if needed → 1 pt
 *   C) I don't know / haven't thought about it → 0 pts
 *   D) I've tried to maintain context but it's frustrating → 2 pts
 *
 * Q2: How do you currently use AI in your daily workflow?
 *   A) Occasional questions when I'm stuck → 1 pt
 *   B) Regular task assistance (writing, research) → 1 pt
 *   C) Heavily integrated into most of my work → 2 pts
 *   D) I'm not really using AI yet → 0 pts
 *
 * Q3: What's your biggest frustration with current AI tools?
 *   A) They don't remember what I've told them → 2 pts
 *   B) They give generic, not-personalized responses → 2 pts
 *   C) I'm not sure how to use them effectively → 0 pts
 *   D) They're helpful but feel like strangers every time → 2 pts
 *
 * Q4: If you could describe your ideal AI relationship, it would be:
 *   A) A smart search engine that answers questions quickly → 0 pts
 *   B) A reliable assistant that knows my preferences → 1 pt
 *   C) A strategic partner that understands my business → 2 pts
 *   D) A digital employee that grows with my organization → 2 pts
 *
 * Q5: What would you pay for an AI that genuinely learned your business over time?
 *   A) Nothing - free tools work fine for me → 0 pts
 *   B) $100-200/month if it saved significant time → 1 pt
 *   C) $200-500/month for a genuine productivity boost → 2 pts
 *   D) The question isn't cost - it's whether it actually works → 2 pts
 *
 * MAX SCORE: 10 points
 * TIERS: 0-4 = EXPLORING, 5-7 = GROWING, 8-10 = READY
 */

function onFormSubmit(e) {
  try {
    // IMPORTANT: Always use Form Responses 1, NOT the active sheet
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Form Responses 1");
    if (!sheet) {
      Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
      return;
    }
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");
    var name = String(data[6] || "Friend");
    var email = String(data[8] || "");  // Column I
    var company = String(data[9] || "your organization");

    Logger.log("Row " + lastRow + " received:");
    Logger.log("Q1: " + q1);
    Logger.log("Q2: " + q2);
    Logger.log("Q3: " + q3);
    Logger.log("Q4: " + q4);
    Logger.log("Q5: " + q5);
    Logger.log("Email: " + email);

    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found");
      return;
    }

    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    // Write to columns K and L
    sheet.getRange(lastRow, 11).setValue(score);
    sheet.getRange(lastRow, 12).setValue(tier);

    var answers = { q1: q1, q2: q2, q3: q3, q4: q4, q5: q5 };
    var brainComment = generateBrainComment(name, company, score, tier, answers);
    sendBrainEmail(email, name, brainComment, tier);

    Logger.log("SUCCESS: Score=" + score + "/10, Tier=" + tier + ", Email sent to " + email);

  } catch (error) {
    Logger.log("ERROR: " + error.toString());
  }
}

/**
 * Calculate score using EXACT keywords from actual Google Form answers
 */
function calculateScore(q1, q2, q3, q4, q5) {
  var score = 0;

  // Q1: Conversation history
  score += scoreQ1(q1);

  // Q2: Current AI usage
  score += scoreQ2(q2);

  // Q3: Biggest frustration
  score += scoreQ3(q3);

  // Q4: Ideal relationship
  score += scoreQ4(q4);

  // Q5: What would you pay
  score += scoreQ5(q5);

  return score;
}

function scoreQ1(answer) {
  var a = answer.toLowerCase();

  // D: "tried to maintain" / "frustrating" = 2 pts (HIGH)
  if (a.indexOf("tried to maintain") !== -1) return 2;
  if (a.indexOf("frustrating") !== -1) return 2;

  // B: "look back" / "old chats" = 1 pt
  if (a.indexOf("look back") !== -1) return 1;
  if (a.indexOf("old chats") !== -1) return 1;

  // A: "gone forever" / "start fresh" = 0 pts
  if (a.indexOf("gone forever") !== -1) return 0;
  if (a.indexOf("start fresh") !== -1) return 0;

  // C: "don't know" / "haven't thought" = 0 pts
  if (a.indexOf("don't know") !== -1) return 0;
  if (a.indexOf("haven't thought") !== -1) return 0;

  return 0;
}

function scoreQ2(answer) {
  var a = answer.toLowerCase();

  // C: "heavily integrated" / "most of my work" = 2 pts (HIGH)
  if (a.indexOf("heavily integrated") !== -1) return 2;
  if (a.indexOf("most of my work") !== -1) return 2;

  // A: "occasional" / "when i'm stuck" = 1 pt
  if (a.indexOf("occasional") !== -1) return 1;
  if (a.indexOf("when i'm stuck") !== -1) return 1;
  if (a.indexOf("when im stuck") !== -1) return 1;

  // B: "regular task" / "writing, research" = 1 pt
  if (a.indexOf("regular task") !== -1) return 1;
  if (a.indexOf("writing, research") !== -1) return 1;

  // D: "not really using" = 0 pts
  if (a.indexOf("not really using") !== -1) return 0;

  return 0;
}

function scoreQ3(answer) {
  var a = answer.toLowerCase();

  // A: "don't remember" / "what i've told them" = 2 pts (HIGH)
  if (a.indexOf("don't remember") !== -1) return 2;
  if (a.indexOf("what i've told") !== -1) return 2;
  if (a.indexOf("what ive told") !== -1) return 2;

  // B: "generic" / "not-personalized" = 2 pts (HIGH)
  if (a.indexOf("generic") !== -1) return 2;
  if (a.indexOf("not-personalized") !== -1) return 2;
  if (a.indexOf("not personalized") !== -1) return 2;

  // D: "strangers every time" / "feel like strangers" = 2 pts (HIGH)
  if (a.indexOf("strangers") !== -1) return 2;

  // C: "not sure how" / "use them effectively" = 0 pts
  if (a.indexOf("not sure how") !== -1) return 0;
  if (a.indexOf("use them effectively") !== -1) return 0;

  return 0;
}

function scoreQ4(answer) {
  var a = answer.toLowerCase();

  // C: "strategic partner" / "understands my business" = 2 pts (HIGH)
  if (a.indexOf("strategic partner") !== -1) return 2;
  if (a.indexOf("understands my business") !== -1) return 2;

  // D: "digital employee" / "grows with" = 2 pts (HIGH)
  if (a.indexOf("digital employee") !== -1) return 2;
  if (a.indexOf("grows with") !== -1) return 2;

  // B: "reliable assistant" / "knows my preferences" = 1 pt
  if (a.indexOf("reliable assistant") !== -1) return 1;
  if (a.indexOf("knows my preferences") !== -1) return 1;

  // A: "search engine" / "answers quickly" = 0 pts
  if (a.indexOf("search engine") !== -1) return 0;
  if (a.indexOf("answers quickly") !== -1) return 0;

  return 0;
}

function scoreQ5(answer) {
  var a = answer.toLowerCase();

  // C: "$200-500" / "genuine productivity" = 2 pts (HIGH)
  if (a.indexOf("$200-500") !== -1) return 2;
  if (a.indexOf("200-500") !== -1) return 2;
  if (a.indexOf("genuine productivity") !== -1) return 2;

  // D: "question isn't cost" / "whether it actually works" = 2 pts (HIGH)
  if (a.indexOf("question isn't cost") !== -1) return 2;
  if (a.indexOf("isn't cost") !== -1) return 2;
  if (a.indexOf("actually works") !== -1) return 2;

  // B: "$100-200" / "saved significant time" = 1 pt
  if (a.indexOf("$100-200") !== -1) return 1;
  if (a.indexOf("100-200") !== -1) return 1;
  if (a.indexOf("saved significant") !== -1) return 1;

  // A: "nothing" / "free tools" = 0 pts
  if (a.indexOf("nothing") !== -1) return 0;
  if (a.indexOf("free tools") !== -1) return 0;

  return 0;
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
    '<html><head><style>' +
    'body { font-family: "Segoe UI", Arial, sans-serif; line-height: 1.6; color: #333; }' +
    '.container { max-width: 600px; margin: 0 auto; padding: 20px; }' +
    '.header { text-align: center; padding: 20px 0; }' +
    '.logo { font-size: 24px; font-weight: bold; }' +
    '.brain-comment { background: #f8f9fa; border-left: 4px solid #2a93c1; padding: 20px; margin: 20px 0; line-height: 1.8; }' +
    '.tier-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; margin: 10px 0; background: ' + tierBgColor + '; color: ' + tierTextColor + '; }' +
    '.cta { display: inline-block; background: #f1420b; color: white !important; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }' +
    '.footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }' +
    '</style></head>' +
    '<body><div class="container">' +
    '<div class="header"><div class="logo">' +
    '<span style="color: #2a93c1;">PUREBR</span><span style="color: #f1420b;">AI</span><span style="color: #2a93c1;">N</span><span style="color: #ffffff; background: #333; padding: 0 4px; border-radius: 3px;">.ai</span>' +
    '</div></div>' +
    '<h2>Your AI Partnership Readiness: <span class="tier-badge">' + tier + '</span></h2>' +
    '<p>Thank you for taking the AI Partnership Readiness Assessment. Here\'s my analysis:</p>' +
    '<div class="brain-comment">' + brainComment + '</div>' +
    '<p style="text-align: center;"><a href="https://purebrain.ai" class="cta">Explore AI Partnership →</a></p>' +
    '<div class="footer">' +
    '<p>© 2026 PureBrain.ai | Enterprise AI That Learns How Your Business Runs</p>' +
    '<p>25 Prospect Avenue, Montclair NJ 07042 | <a href="https://purebrain.ai">purebrain.ai</a></p>' +
    '</div></div></body></html>';

  var plainText = brainComment.replace(/<br><br>/g, "\n\n").replace(/<br>/g, "\n").replace(/•/g, "-");

  GmailApp.sendEmail(email, subject, plainText, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

// ==================== UTILITY FUNCTIONS ====================

function addColumnHeaders() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Form Responses 1");
  if (!sheet) {
    Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
    return;
  }
  sheet.getRange(1, 11).setValue("Score");
  sheet.getRange(1, 12).setValue("Tier");
  Logger.log("Headers added to Form Responses 1: K=Score, L=Tier");
}

function recalculateAllScores() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Form Responses 1");
  if (!sheet) {
    Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
    return;
  }
  var lastRow = sheet.getLastRow();

  Logger.log("Recalculating Form Responses 1 rows 2 to " + lastRow);

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 10).getValues()[0];
    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");

    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);
    sheet.getRange(row, 12).setValue(tier);

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Done!");
}

/**
 * Test with ACTUAL form answers to verify scoring
 */
function testActualAnswers() {
  Logger.log("=== Testing with ACTUAL Google Form Answers ===");

  // Test EXPLORING profile (all low-scoring answers)
  var score1 = calculateScore(
    "It's gone forever - I start fresh each time",        // Q1 = 0
    "I'm not really using AI yet",                        // Q2 = 0
    "I'm not sure how to use them effectively",           // Q3 = 0
    "A smart search engine that answers questions quickly", // Q4 = 0
    "Nothing - free tools work fine for me"               // Q5 = 0
  );
  Logger.log("EXPLORING profile: Score=" + score1 + " (expected: 0, Tier: " + getTier(score1) + ")");

  // Test GROWING profile (mix of answers)
  var score2 = calculateScore(
    "I can look back at old chats if needed",             // Q1 = 1
    "Regular task assistance (writing, research)",        // Q2 = 1
    "They give generic, not-personalized responses",      // Q3 = 2
    "A reliable assistant that knows my preferences",     // Q4 = 1
    "$100-200/month if it saved significant time"         // Q5 = 1
  );
  Logger.log("GROWING profile: Score=" + score2 + " (expected: 6, Tier: " + getTier(score2) + ")");

  // Test READY profile (all high-scoring answers)
  var score3 = calculateScore(
    "I've tried to maintain context but it's frustrating", // Q1 = 2
    "Heavily integrated into most of my work",            // Q2 = 2
    "They don't remember what I've told them",            // Q3 = 2
    "A digital employee that grows with my organization", // Q4 = 2
    "The question isn't cost - it's whether it actually works" // Q5 = 2
  );
  Logger.log("READY profile: Score=" + score3 + " (expected: 10, Tier: " + getTier(score3) + ")");
}

/**
 * Debug the last row to see what's being received
 */
function debugLastRow() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Form Responses 1");
  if (!sheet) {
    Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
    return;
  }
  var lastRow = sheet.getLastRow();
  var data = sheet.getRange(lastRow, 1, 1, 12).getValues()[0];

  Logger.log("=== Debug Row " + lastRow + " ===");
  Logger.log("Q1: '" + data[1] + "' → Score: " + scoreQ1(String(data[1] || "")));
  Logger.log("Q2: '" + data[2] + "' → Score: " + scoreQ2(String(data[2] || "")));
  Logger.log("Q3: '" + data[3] + "' → Score: " + scoreQ3(String(data[3] || "")));
  Logger.log("Q4: '" + data[4] + "' → Score: " + scoreQ4(String(data[4] || "")));
  Logger.log("Q5: '" + data[5] + "' → Score: " + scoreQ5(String(data[5] || "")));
  Logger.log("Name: '" + data[6] + "'");
  Logger.log("Email: '" + data[8] + "'");
  Logger.log("Current Score in K: " + data[10]);
  Logger.log("Current Tier in L: " + data[11]);

  var total = calculateScore(
    String(data[1] || ""),
    String(data[2] || ""),
    String(data[3] || ""),
    String(data[4] || ""),
    String(data[5] || "")
  );
  Logger.log("TOTAL CALCULATED: " + total + "/10 → " + getTier(total));
}
