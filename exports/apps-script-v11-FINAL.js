/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 11 - FINAL - CORRECT COLUMN MAPPING
 *
 * YOUR ACTUAL COLUMN LAYOUT:
 * A (0) = Timestamp
 * B (1) = Email Address (Google Forms auto-added)
 * C (2) = Q1 answer
 * D (3) = Q2 answer
 * E (4) = Q3 answer
 * F (5) = Q4 answer
 * G (6) = Q5 answer
 * H (7) = Name
 * I (8) = Email
 * J (9) = Company
 * K (10) = Score
 * L (11) = Tier
 */

// ==================== MAIN FORM HANDLER ====================

function onFormSubmit(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Form Responses 1");
    if (!sheet) {
      Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
      return;
    }
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // CORRECT COLUMN MAPPING (based on your debugColumns output)
    var q1 = String(data[2] || "");   // Column C
    var q2 = String(data[3] || "");   // Column D
    var q3 = String(data[4] || "");   // Column E
    var q4 = String(data[5] || "");   // Column F
    var q5 = String(data[6] || "");   // Column G
    var name = String(data[7] || "Friend");  // Column H
    var email = String(data[8] || "");       // Column I
    var company = String(data[9] || "your organization");  // Column J

    Logger.log("Row " + lastRow + " received:");
    Logger.log("Q1: " + q1);
    Logger.log("Q2: " + q2);
    Logger.log("Q3: " + q3);
    Logger.log("Q4: " + q4);
    Logger.log("Q5: " + q5);
    Logger.log("Name: " + name);
    Logger.log("Email: " + email);

    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found, skipping");
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

// ==================== SCORING ====================

function calculateScore(q1, q2, q3, q4, q5) {
  var score = 0;

  // Q1: Conversation history
  var a1 = q1.toLowerCase();
  if (a1.indexOf("frustrating") !== -1 || a1.indexOf("tried to maintain") !== -1) {
    score += 2;
  } else if (a1.indexOf("look back") !== -1 || a1.indexOf("old chats") !== -1) {
    score += 1;
  }
  // "gone forever" and "don't know" = 0

  // Q2: Current AI usage
  var a2 = q2.toLowerCase();
  if (a2.indexOf("heavily integrated") !== -1 || a2.indexOf("most of my work") !== -1) {
    score += 2;
  } else if (a2.indexOf("occasional") !== -1 || a2.indexOf("regular task") !== -1) {
    score += 1;
  }
  // "not really using" = 0

  // Q3: Biggest frustration
  var a3 = q3.toLowerCase();
  if (a3.indexOf("don't remember") !== -1 || a3.indexOf("generic") !== -1 || a3.indexOf("strangers") !== -1) {
    score += 2;
  }
  // "not sure how" = 0

  // Q4: Ideal relationship
  var a4 = q4.toLowerCase();
  if (a4.indexOf("strategic partner") !== -1 || a4.indexOf("digital employee") !== -1) {
    score += 2;
  } else if (a4.indexOf("reliable assistant") !== -1) {
    score += 1;
  }
  // "search engine" = 0

  // Q5: What would you pay
  var a5 = q5.toLowerCase();
  if (a5.indexOf("200-500") !== -1 || a5.indexOf("isn't cost") !== -1 || a5.indexOf("actually works") !== -1) {
    score += 2;
  } else if (a5.indexOf("100-200") !== -1) {
    score += 1;
  }
  // "nothing" / "free tools" = 0

  Logger.log("Calculated score: " + score + "/10");
  return score;
}

function getTier(score) {
  if (score >= 8) return "READY";
  if (score >= 5) return "GROWING";
  return "EXPLORING";
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
  Logger.log("Headers added: K=Score, L=Tier");
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
  Logger.log("Using CORRECT column mapping: C=Q1, D=Q2, E=Q3, F=Q4, G=Q5");

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 12).getValues()[0];

    // CORRECT indices
    var q1 = String(data[2] || "");
    var q2 = String(data[3] || "");
    var q3 = String(data[4] || "");
    var q4 = String(data[5] || "");
    var q5 = String(data[6] || "");

    Logger.log("Row " + row + ": Q1='" + q1.substring(0,30) + "...'");

    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);
    sheet.getRange(row, 12).setValue(tier);

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Done! All scores recalculated.");
}

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
  Logger.log("Q1 (data[2]): " + data[2]);
  Logger.log("Q2 (data[3]): " + data[3]);
  Logger.log("Q3 (data[4]): " + data[4]);
  Logger.log("Q4 (data[5]): " + data[5]);
  Logger.log("Q5 (data[6]): " + data[6]);
  Logger.log("Name (data[7]): " + data[7]);
  Logger.log("Email (data[8]): " + data[8]);
  Logger.log("Company (data[9]): " + data[9]);

  var score = calculateScore(
    String(data[2] || ""),
    String(data[3] || ""),
    String(data[4] || ""),
    String(data[5] || ""),
    String(data[6] || "")
  );
  Logger.log("CALCULATED: " + score + "/10 → " + getTier(score));
}

/**
 * Test the scoring with known answers
 */
function testScoring() {
  Logger.log("=== Testing Scoring ===");

  // Test EXPLORING (0 points)
  var s1 = calculateScore(
    "It's gone forever - I start fresh each time",
    "I'm not really using AI yet",
    "I'm not sure how to use them effectively",
    "A smart search engine that answers questions quickly",
    "Nothing - free tools work fine for me"
  );
  Logger.log("EXPLORING test: " + s1 + "/10 (expected: 0) → " + getTier(s1));

  // Test GROWING (6 points)
  var s2 = calculateScore(
    "I can look back at old chats if needed",
    "Regular task assistance (writing, research)",
    "They give generic, not-personalized responses",
    "A reliable assistant that knows my preferences",
    "$100-200/month if it saved significant time"
  );
  Logger.log("GROWING test: " + s2 + "/10 (expected: 6) → " + getTier(s2));

  // Test READY (10 points)
  var s3 = calculateScore(
    "I've tried to maintain context but it's frustrating",
    "Heavily integrated into most of my work",
    "They don't remember what I've told them",
    "A digital employee that grows with my organization",
    "The question isn't cost - it's whether it actually works"
  );
  Logger.log("READY test: " + s3 + "/10 (expected: 10) → " + getTier(s3));
}

// ==================== EMAIL FUNCTIONS ====================

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
