/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 10 - FIXED COLUMN MAPPING
 *
 * BUG FIX: v9 had wrong column indices. This version:
 * 1. Includes debugColumns() to show actual sheet layout
 * 2. Uses CORRECT column indices based on your Form Responses 1 layout
 *
 * SETUP:
 * 1. Paste this code
 * 2. Run debugColumns() FIRST to verify column layout
 * 3. Run createLegendSheet() if Legend doesn't exist
 * 4. Run recalculateAllScores()
 */

// ==================== DEBUG - RUN THIS FIRST ====================

/**
 * RUN THIS FIRST to see your actual column layout
 */
function debugColumns() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Form Responses 1");
  if (!sheet) {
    Logger.log("ERROR: Could not find 'Form Responses 1' sheet!");
    return;
  }

  // Get headers (row 1)
  var headers = sheet.getRange(1, 1, 1, 15).getValues()[0];
  Logger.log("=== COLUMN HEADERS ===");
  for (var i = 0; i < headers.length; i++) {
    if (headers[i]) {
      Logger.log("Column " + String.fromCharCode(65 + i) + " (index " + i + "): " + headers[i]);
    }
  }

  // Get first data row (row 2)
  var lastRow = sheet.getLastRow();
  if (lastRow >= 2) {
    var data = sheet.getRange(2, 1, 1, 15).getValues()[0];
    Logger.log("\n=== FIRST DATA ROW (Row 2) ===");
    for (var i = 0; i < data.length; i++) {
      if (data[i]) {
        Logger.log("Column " + String.fromCharCode(65 + i) + " (index " + i + "): " + data[i]);
      }
    }
  }
}

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

    // COLUMN MAPPING - Adjust these based on debugColumns() output
    // Standard Google Form layout:
    // A=Timestamp, B=Q1, C=Q2, D=Q3, E=Q4, F=Q5, G=Name, H=Source, I=Email, J=Company
    //
    // If your form has different columns, adjust the indices below:
    var q1 = String(data[1] || "");   // Column B
    var q2 = String(data[2] || "");   // Column C
    var q3 = String(data[3] || "");   // Column D
    var q4 = String(data[4] || "");   // Column E
    var q5 = String(data[5] || "");   // Column F
    var name = String(data[6] || "Friend");  // Column G
    var email = String(data[8] || "");       // Column I
    var company = String(data[9] || "your organization");  // Column J

    Logger.log("Row " + lastRow + " - Q1: " + q1.substring(0, 30) + "...");

    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found");
      return;
    }

    var score = calculateScoreFromLegend(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(lastRow, 11).setValue(score);
    sheet.getRange(lastRow, 12).setValue(tier);

    var answers = { q1: q1, q2: q2, q3: q3, q4: q4, q5: q5 };
    var brainComment = generateBrainComment(name, company, score, tier, answers);
    sendBrainEmail(email, name, brainComment, tier);

    Logger.log("SUCCESS: Score=" + score + "/10, Tier=" + tier);

  } catch (error) {
    Logger.log("ERROR: " + error.toString());
  }
}

// ==================== LEGEND-BASED SCORING ====================

function getLegendMap() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var legend = ss.getSheetByName("Legend");
  if (!legend) {
    Logger.log("WARNING: Legend sheet not found, using hardcoded scores");
    return null;
  }

  var data = legend.getDataRange().getValues();
  var map = {};

  for (var i = 1; i < data.length; i++) {
    var question = String(data[i][0] || "").trim();
    var answer = String(data[i][1] || "").trim().toLowerCase();
    var score = parseInt(data[i][2]) || 0;

    if (question && answer) {
      if (!map[question]) map[question] = {};
      map[question][answer] = score;
    }
  }

  return map;
}

function calculateScoreFromLegend(q1, q2, q3, q4, q5) {
  var legendMap = getLegendMap();

  if (!legendMap) {
    return calculateScoreHardcoded(q1, q2, q3, q4, q5);
  }

  var score = 0;

  score += lookupScore(legendMap, "Q1", q1);
  score += lookupScore(legendMap, "Q2", q2);
  score += lookupScore(legendMap, "Q3", q3);
  score += lookupScore(legendMap, "Q4", q4);
  score += lookupScore(legendMap, "Q5", q5);

  Logger.log("Legend-based score: " + score + "/10");
  return score;
}

function lookupScore(legendMap, question, answer) {
  if (!legendMap[question]) {
    Logger.log("WARNING: No legend entries for " + question);
    return 0;
  }

  var answerLower = String(answer).trim().toLowerCase();

  // Exact match
  if (legendMap[question][answerLower] !== undefined) {
    return legendMap[question][answerLower];
  }

  // Partial match - check if answer contains any legend keyword
  for (var legendAnswer in legendMap[question]) {
    // Check both directions for partial match
    if (answerLower.indexOf(legendAnswer) !== -1) {
      return legendMap[question][legendAnswer];
    }
    // Also check if legend contains the answer (for shorter matches)
    if (legendAnswer.indexOf(answerLower) !== -1 && answerLower.length > 10) {
      return legendMap[question][legendAnswer];
    }
  }

  Logger.log("WARNING: No match found for " + question + ": '" + answer + "'");
  return 0;
}

function calculateScoreHardcoded(q1, q2, q3, q4, q5) {
  var score = 0;

  var a1 = q1.toLowerCase();
  if (a1.indexOf("frustrating") !== -1 || a1.indexOf("tried to maintain") !== -1) score += 2;
  else if (a1.indexOf("look back") !== -1) score += 1;

  var a2 = q2.toLowerCase();
  if (a2.indexOf("heavily integrated") !== -1) score += 2;
  else if (a2.indexOf("occasional") !== -1 || a2.indexOf("regular task") !== -1) score += 1;

  var a3 = q3.toLowerCase();
  if (a3.indexOf("don't remember") !== -1 || a3.indexOf("generic") !== -1 || a3.indexOf("strangers") !== -1) score += 2;

  var a4 = q4.toLowerCase();
  if (a4.indexOf("strategic partner") !== -1 || a4.indexOf("digital employee") !== -1) score += 2;
  else if (a4.indexOf("reliable assistant") !== -1) score += 1;

  var a5 = q5.toLowerCase();
  if (a5.indexOf("200-500") !== -1 || a5.indexOf("isn't cost") !== -1 || a5.indexOf("actually works") !== -1) score += 2;
  else if (a5.indexOf("100-200") !== -1) score += 1;

  return score;
}

function getTier(score) {
  if (score >= 8) return "READY";
  if (score >= 5) return "GROWING";
  return "EXPLORING";
}

// ==================== CREATE LEGEND SHEET ====================

function createLegendSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  var existing = ss.getSheetByName("Legend");
  if (existing) {
    ss.deleteSheet(existing);
    Logger.log("Deleted old Legend sheet");
  }

  var legend = ss.insertSheet("Legend");

  legend.getRange(1, 1, 1, 3).setValues([["Question", "Answer", "Score"]]);
  legend.getRange(1, 1, 1, 3).setFontWeight("bold");

  // EXACT answers from Google Form (lowercase for matching)
  var legendData = [
    // Q1: Conversation history
    ["Q1", "it's gone forever - i start fresh each time", 0],
    ["Q1", "i can look back at old chats if needed", 1],
    ["Q1", "i don't know / haven't thought about it", 0],
    ["Q1", "i've tried to maintain context but it's frustrating", 2],

    // Q2: Current AI usage
    ["Q2", "occasional questions when i'm stuck", 1],
    ["Q2", "regular task assistance (writing, research)", 1],
    ["Q2", "heavily integrated into most of my work", 2],
    ["Q2", "i'm not really using ai yet", 0],

    // Q3: Biggest frustration
    ["Q3", "they don't remember what i've told them", 2],
    ["Q3", "they give generic, not-personalized responses", 2],
    ["Q3", "i'm not sure how to use them effectively", 0],
    ["Q3", "they're helpful but feel like strangers every time", 2],

    // Q4: Ideal relationship
    ["Q4", "a smart search engine that answers questions quickly", 0],
    ["Q4", "a reliable assistant that knows my preferences", 1],
    ["Q4", "a strategic partner that understands my business", 2],
    ["Q4", "a digital employee that grows with my organization", 2],

    // Q5: What would you pay
    ["Q5", "nothing - free tools work fine for me", 0],
    ["Q5", "$100-200/month if it saved significant time", 1],
    ["Q5", "$200-500/month for a genuine productivity boost", 2],
    ["Q5", "the question isn't cost - it's whether it actually works", 2]
  ];

  legend.getRange(2, 1, legendData.length, 3).setValues(legendData);

  legend.setColumnWidth(1, 80);
  legend.setColumnWidth(2, 400);
  legend.setColumnWidth(3, 60);

  Logger.log("Legend sheet created with " + legendData.length + " answer mappings!");
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

    // Log what we're reading to debug column issues
    Logger.log("Row " + row + " raw data:");
    Logger.log("  [1]=" + String(data[1]).substring(0, 40));
    Logger.log("  [2]=" + String(data[2]).substring(0, 40));
    Logger.log("  [3]=" + String(data[3]).substring(0, 40));
    Logger.log("  [4]=" + String(data[4]).substring(0, 40));
    Logger.log("  [5]=" + String(data[5]).substring(0, 40));

    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");

    var score = calculateScoreFromLegend(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);
    sheet.getRange(row, 12).setValue(tier);

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Done!");
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
  for (var i = 0; i < 12; i++) {
    Logger.log("Column " + String.fromCharCode(65 + i) + " (index " + i + "): " + data[i]);
  }

  var total = calculateScoreFromLegend(
    String(data[1] || ""),
    String(data[2] || ""),
    String(data[3] || ""),
    String(data[4] || ""),
    String(data[5] || "")
  );
  Logger.log("CALCULATED: " + total + "/10 → " + getTier(total));
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
