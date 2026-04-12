/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 6 - LEGEND SHEET BASED SCORING
 *
 * This version uses a separate "Legend" sheet for scoring rules
 * Makes it easy to adjust scoring without changing code
 *
 * SETUP INSTRUCTIONS:
 * 1. Create a new sheet tab called "Legend"
 * 2. Set up the Legend sheet like this:
 *
 *    Column A: Question (Q1, Q2, Q3, Q4, Q5)
 *    Column B: Keyword (text to match)
 *    Column C: Points (0, 1, or 2)
 *
 *    Example rows:
 *    Q1    gone forever         0
 *    Q1    start fresh          0
 *    Q1    scroll back          1
 *    Q1    copy/paste           2
 *    Q1    wish                 2
 *    Q1    remembered           2
 *    Q2    don't                0
 *    Q2    curious              0
 *    Q2    occasionally         1
 *    Q2    regularly            2
 *    ...etc
 *
 * 3. Deploy this script
 * 4. Run recalculateAllScores() to apply to existing rows
 */

// Global cache for legend rules
var legendCache = null;

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
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

    Logger.log("Row " + lastRow + " received");
    Logger.log("Q1: " + q1);
    Logger.log("Q2: " + q2);
    Logger.log("Q3: " + q3);
    Logger.log("Q4: " + q4);
    Logger.log("Q5: " + q5);

    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found in row " + lastRow);
      return;
    }

    // Load legend and calculate score
    var legend = loadLegend();
    var score = calculateScoreWithLegend(q1, q2, q3, q4, q5, legend);
    var tier = getTier(score);

    // Write to columns K and L
    sheet.getRange(lastRow, 11).setValue(score);
    sheet.getRange(lastRow, 12).setValue(tier);

    // Send email
    var answers = { q1: q1, q2: q2, q3: q3, q4: q4, q5: q5 };
    var brainComment = generateBrainComment(name, company, score, tier, answers);
    sendBrainEmail(email, name, brainComment, tier);

    Logger.log("SUCCESS: Score=" + score + ", Tier=" + tier + ", Email sent to " + email);

  } catch (error) {
    Logger.log("ERROR: " + error.toString());
  }
}

/**
 * Load scoring rules from Legend sheet
 */
function loadLegend() {
  if (legendCache) return legendCache;

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var legendSheet = ss.getSheetByName("Legend");

  if (!legendSheet) {
    Logger.log("WARNING: No Legend sheet found, using default rules");
    return getDefaultLegend();
  }

  var data = legendSheet.getDataRange().getValues();
  var legend = { Q1: [], Q2: [], Q3: [], Q4: [], Q5: [] };

  for (var i = 1; i < data.length; i++) {  // Skip header row
    var question = String(data[i][0]).toUpperCase().trim();
    var keyword = String(data[i][1]).toLowerCase().trim();
    var points = parseInt(data[i][2]) || 0;

    if (legend.hasOwnProperty(question) && keyword) {
      legend[question].push({ keyword: keyword, points: points });
    }
  }

  legendCache = legend;
  return legend;
}

/**
 * Default scoring rules (used if no Legend sheet exists)
 */
function getDefaultLegend() {
  return {
    Q1: [
      { keyword: "gone forever", points: 0 },
      { keyword: "start fresh", points: 0 },
      { keyword: "scroll back", points: 1 },
      { keyword: "can scroll", points: 1 },
      { keyword: "copy/paste", points: 2 },
      { keyword: "tedious", points: 2 },
      { keyword: "wish", points: 2 },
      { keyword: "remembered", points: 2 },
      { keyword: "preferences", points: 2 }
    ],
    Q2: [
      { keyword: "don't", points: 0 },
      { keyword: "curious", points: 0 },
      { keyword: "haven't started", points: 0 },
      { keyword: "occasionally", points: 1 },
      { keyword: "one-off", points: 1 },
      { keyword: "regularly", points: 2 },
      { keyword: "repeat myself", points: 2 },
      { keyword: "tried to build", points: 2 },
      { keyword: "hit walls", points: 2 }
    ],
    Q3: [
      { keyword: "don't know where", points: 0 },
      { keyword: "where to start", points: 0 },
      { keyword: "generic", points: 2 },
      { keyword: "don't understand", points: 2 },
      { keyword: "prompting", points: 2 },
      { keyword: "more time", points: 2 },
      { keyword: "new intern", points: 2 },
      { keyword: "training", points: 2 },
      { keyword: "every session", points: 2 }
    ],
    Q4: [
      { keyword: "search engine", points: 0 },
      { keyword: "quickly", points: 0 },
      { keyword: "writing assistant", points: 1 },
      { keyword: "drafts", points: 1 },
      { keyword: "team member", points: 2 },
      { keyword: "work history", points: 2 },
      { keyword: "partner", points: 2 },
      { keyword: "anticipates", points: 2 },
      { keyword: "grows", points: 2 }
    ],
    Q5: [
      { keyword: "few hours", points: 1 },
      { keyword: "saving", points: 1 },
      { keyword: "better outputs", points: 1 },
      { keyword: "less editing", points: 1 },
      { keyword: "whole projects", points: 2 },
      { keyword: "handles", points: 2 },
      { keyword: "transformational", points: 2 },
      { keyword: "reimagining", points: 2 },
      { keyword: "entire operation", points: 2 }
    ]
  };
}

/**
 * Calculate score using legend rules
 */
function calculateScoreWithLegend(q1, q2, q3, q4, q5, legend) {
  var score = 0;

  score += scoreAnswerWithLegend(q1, legend.Q1);
  score += scoreAnswerWithLegend(q2, legend.Q2);
  score += scoreAnswerWithLegend(q3, legend.Q3);
  score += scoreAnswerWithLegend(q4, legend.Q4);
  score += scoreAnswerWithLegend(q5, legend.Q5);

  return score;
}

/**
 * Score a single answer against legend rules
 */
function scoreAnswerWithLegend(answer, rules) {
  var answerLower = answer.toLowerCase();
  var maxPoints = 0;

  for (var i = 0; i < rules.length; i++) {
    if (answerLower.indexOf(rules[i].keyword) !== -1) {
      if (rules[i].points > maxPoints) {
        maxPoints = rules[i].points;
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
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 11).setValue("Score");
  sheet.getRange(1, 12).setValue("Tier");
  Logger.log("Headers added: K=Score, L=Tier");
}

function recalculateAllScores() {
  legendCache = null;  // Clear cache to reload
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var legend = loadLegend();
  var lastRow = sheet.getLastRow();

  Logger.log("Recalculating " + (lastRow - 1) + " rows using legend");

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 10).getValues()[0];
    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");

    var score = calculateScoreWithLegend(q1, q2, q3, q4, q5, legend);
    var tier = getTier(score);

    sheet.getRange(row, 11).setValue(score);
    sheet.getRange(row, 12).setValue(tier);

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }
  Logger.log("Done!");
}

function createLegendSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var existing = ss.getSheetByName("Legend");

  if (existing) {
    Logger.log("Legend sheet already exists");
    return;
  }

  var legend = ss.insertSheet("Legend");

  // Headers
  legend.getRange(1, 1, 1, 3).setValues([["Question", "Keyword", "Points"]]);
  legend.getRange(1, 1, 1, 3).setFontWeight("bold");

  // Q1 rules
  var rules = [
    ["Q1", "gone forever", 0],
    ["Q1", "start fresh", 0],
    ["Q1", "scroll back", 1],
    ["Q1", "can scroll", 1],
    ["Q1", "copy/paste", 2],
    ["Q1", "tedious", 2],
    ["Q1", "wish", 2],
    ["Q1", "remembered", 2],
    ["Q1", "preferences", 2],
    ["Q2", "don't", 0],
    ["Q2", "curious", 0],
    ["Q2", "haven't started", 0],
    ["Q2", "occasionally", 1],
    ["Q2", "one-off", 1],
    ["Q2", "regularly", 2],
    ["Q2", "repeat myself", 2],
    ["Q2", "tried to build", 2],
    ["Q2", "hit walls", 2],
    ["Q3", "don't know where", 0],
    ["Q3", "where to start", 0],
    ["Q3", "generic", 2],
    ["Q3", "don't understand", 2],
    ["Q3", "prompting", 2],
    ["Q3", "more time", 2],
    ["Q3", "new intern", 2],
    ["Q3", "training", 2],
    ["Q3", "every session", 2],
    ["Q4", "search engine", 0],
    ["Q4", "quickly", 0],
    ["Q4", "writing assistant", 1],
    ["Q4", "drafts", 1],
    ["Q4", "team member", 2],
    ["Q4", "work history", 2],
    ["Q4", "partner", 2],
    ["Q4", "anticipates", 2],
    ["Q4", "grows", 2],
    ["Q5", "few hours", 1],
    ["Q5", "saving", 1],
    ["Q5", "better outputs", 1],
    ["Q5", "less editing", 1],
    ["Q5", "whole projects", 2],
    ["Q5", "handles", 2],
    ["Q5", "transformational", 2],
    ["Q5", "reimagining", 2],
    ["Q5", "entire operation", 2]
  ];

  legend.getRange(2, 1, rules.length, 3).setValues(rules);

  // Format
  legend.setColumnWidth(1, 80);
  legend.setColumnWidth(2, 200);
  legend.setColumnWidth(3, 80);

  Logger.log("Legend sheet created with " + rules.length + " rules!");
}

function debugLastRow() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();
  var data = sheet.getRange(lastRow, 1, 1, 12).getValues()[0];

  Logger.log("=== Debug Row " + lastRow + " ===");
  Logger.log("Q1: '" + data[1] + "'");
  Logger.log("Q2: '" + data[2] + "'");
  Logger.log("Q3: '" + data[3] + "'");
  Logger.log("Q4: '" + data[4] + "'");
  Logger.log("Q5: '" + data[5] + "'");
  Logger.log("Name: '" + data[6] + "'");
  Logger.log("Email: '" + data[8] + "'");
  Logger.log("Current Score: " + data[10]);
  Logger.log("Current Tier: " + data[11]);

  var legend = loadLegend();
  var score = calculateScoreWithLegend(
    String(data[1] || ""),
    String(data[2] || ""),
    String(data[3] || ""),
    String(data[4] || ""),
    String(data[5] || ""),
    legend
  );

  Logger.log("Calculated Score: " + score);
  Logger.log("Calculated Tier: " + getTier(score));
}
