/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 3 - FIXED SCORING + Spreadsheet logging
 *
 * FIXES:
 * - Scoring now works with full answer text (not just A/B/C/D)
 * - Writes Score and Tier to columns J and K in spreadsheet
 * - Address: 25 Prospect Avenue, Montclair NJ 07042
 *
 * SCORING LOGIC:
 * - Answers indicating frustration/readiness (C, D options) = 2 points
 * - Answers indicating moderate use (B options) = 1 point
 * - Answers indicating minimal use (A options) = 0 points
 * - Total possible: 10 points
 * - READY: 8-10, GROWING: 5-7, EXPLORING: 0-4
 */

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Parse response - adjust indices based on your column order
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

    // Calculate score using FIXED scoring method
    var score = calculateScoreFixed(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    // WRITE SCORE AND TIER TO SPREADSHEET (Columns J and K)
    sheet.getRange(lastRow, 10).setValue(score);  // Column J = Score
    sheet.getRange(lastRow, 11).setValue(tier);   // Column K = Tier

    // Create answers object
    var answers = {
      q1: q1,
      q2: q2,
      q3: q3,
      q4: q4,
      q5: q5
    };

    // Generate personalized BRAIN comment
    var brainComment = generateBrainComment(name, company, score, tier, answers);

    // Send email
    sendBrainEmail(email, name, brainComment, tier);

    // Log for tracking
    Logger.log("Sent BRAIN analysis to " + email + " - Score: " + score + "/10, Tier: " + tier);

  } catch (error) {
    Logger.log("Error in onFormSubmit: " + error.toString());
  }
}

/**
 * FIXED SCORING - Works with full answer text
 *
 * Each question maps to specific answer patterns:
 * - Q1: Memory/context frustration
 * - Q2: Current AI usage level
 * - Q3: Biggest frustration
 * - Q4: Ideal AI relationship
 * - Q5: Willingness to pay
 */
function calculateScoreFixed(q1, q2, q3, q4, q5) {
  var score = 0;

  // Q1: When you close a chat, what happens to conversation history?
  // A (0): "gone forever" / "start fresh"
  // B (1): "scroll back" / "doesn't remember"
  // C (2): "copy/paste" / "tedious"
  // D (2): "wish it remembered" / "preferences"
  score += scoreAnswer(q1, [
    { pattern: "gone forever", points: 0 },
    { pattern: "start fresh", points: 0 },
    { pattern: "scroll back", points: 1 },
    { pattern: "doesn't remember", points: 1 },
    { pattern: "copy/paste", points: 2 },
    { pattern: "copy paste", points: 2 },
    { pattern: "tedious", points: 2 },
    { pattern: "wish it remembered", points: 2 },
    { pattern: "preferences", points: 2 },
    { pattern: "past decisions", points: 2 }
  ]);

  // Q2: How do you currently use AI?
  // A (0): "don't" / "haven't started"
  // B (1): "occasionally" / "one-off"
  // C (2): "regularly" / "repeat myself"
  // D (2): "tried to build" / "hit walls"
  score += scoreAnswer(q2, [
    { pattern: "don't", points: 0 },
    { pattern: "haven't started", points: 0 },
    { pattern: "curious but", points: 0 },
    { pattern: "occasionally", points: 1 },
    { pattern: "one-off", points: 1 },
    { pattern: "regularly", points: 2 },
    { pattern: "repeat myself", points: 2 },
    { pattern: "tried to build", points: 2 },
    { pattern: "hit walls", points: 2 },
    { pattern: "build systems", points: 2 }
  ]);

  // Q3: Biggest frustration with AI tools?
  // A (0): "don't know where to start"
  // B (1): "generic" / "don't understand my business"
  // C (2): "prompting" / "more time prompting"
  // D (2): "training a new intern" / "every session"
  score += scoreAnswer(q3, [
    { pattern: "don't know where", points: 0 },
    { pattern: "where to start", points: 0 },
    { pattern: "generic", points: 1 },
    { pattern: "don't understand my business", points: 1 },
    { pattern: "understand my business", points: 1 },
    { pattern: "prompting", points: 2 },
    { pattern: "more time", points: 2 },
    { pattern: "intern", points: 2 },
    { pattern: "every session", points: 2 },
    { pattern: "training a new", points: 2 }
  ]);

  // Q4: Ideal AI relationship?
  // A (0): "search engine" / "answers quickly"
  // B (1): "writing assistant" / "drafts content"
  // C (2): "team member" / "work history" / "preferences"
  // D (2): "partner" / "anticipates" / "grows with me"
  score += scoreAnswer(q4, [
    { pattern: "search engine", points: 0 },
    { pattern: "answers quickly", points: 0 },
    { pattern: "writing assistant", points: 1 },
    { pattern: "drafts content", points: 1 },
    { pattern: "team member", points: 2 },
    { pattern: "work history", points: 2 },
    { pattern: "knows my", points: 2 },
    { pattern: "partner", points: 2 },
    { pattern: "anticipates", points: 2 },
    { pattern: "grows with", points: 2 }
  ]);

  // Q5: What would you pay?
  // A (0): "nothing" / "free tools"
  // B (1): "small monthly fee" / "saved time"
  // C (2): "valuable team member" / "if it delivered"
  // D (2): "isn't cost" / "whether it works"
  score += scoreAnswer(q5, [
    { pattern: "nothing", points: 0 },
    { pattern: "free tools", points: 0 },
    { pattern: "good enough", points: 0 },
    { pattern: "small monthly", points: 1 },
    { pattern: "saved me", points: 1 },
    { pattern: "significant time", points: 1 },
    { pattern: "team member", points: 2 },
    { pattern: "if it delivered", points: 2 },
    { pattern: "isn't cost", points: 2 },
    { pattern: "whether it", points: 2 },
    { pattern: "actually works", points: 2 }
  ]);

  return score;
}

/**
 * Score a single answer by checking for pattern matches
 */
function scoreAnswer(answer, patterns) {
  var answerLower = answer.toLowerCase();

  // Find the highest matching score
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
  if (score >= 8) {
    return "READY";
  }
  if (score >= 5) {
    return "GROWING";
  }
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

  // Plain text version
  var plainText = brainComment.replace(/<br><br>/g, "\n\n").replace(/<br>/g, "\n").replace(/•/g, "-");

  GmailApp.sendEmail(email, subject, plainText, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

/**
 * ADD COLUMN HEADERS - Run this once to set up your spreadsheet
 */
function addColumnHeaders() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.getRange(1, 10).setValue("Score");  // Column J
  sheet.getRange(1, 11).setValue("Tier");   // Column K
  Logger.log("Column headers added: J=Score, K=Tier");
}

/**
 * RECALCULATE ALL SCORES - Run this to update existing rows
 */
function recalculateAllScores() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  for (var row = 2; row <= lastRow; row++) {
    var data = sheet.getRange(row, 1, 1, 9).getValues()[0];

    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");

    var score = calculateScoreFixed(q1, q2, q3, q4, q5);
    var tier = getTier(score);

    sheet.getRange(row, 10).setValue(score);  // Column J
    sheet.getRange(row, 11).setValue(tier);   // Column K

    Logger.log("Row " + row + ": Score=" + score + ", Tier=" + tier);
  }

  Logger.log("Recalculation complete!");
}

/**
 * TEST SCORING - Run this to test the scoring logic
 */
function testScoring() {
  // Test each tier
  var testCases = [
    // Should be EXPLORING (0-4)
    { q1: "It's gone forever", q2: "I don't", q3: "I don't know where to start", q4: "A search engine", q5: "Nothing - free tools" },
    // Should be GROWING (5-7)
    { q1: "I can scroll back", q2: "Occasionally for one-off tasks", q3: "The outputs feel generic", q4: "A writing assistant", q5: "A small monthly fee" },
    // Should be READY (8-10)
    { q1: "I wish it remembered my preferences", q2: "I've tried to build systems but hit walls", q3: "Every session feels like training a new intern", q4: "A partner who anticipates needs and grows with me", q5: "The question isn't cost - it's whether it actually works" }
  ];

  for (var i = 0; i < testCases.length; i++) {
    var tc = testCases[i];
    var score = calculateScoreFixed(tc.q1, tc.q2, tc.q3, tc.q4, tc.q5);
    var tier = getTier(score);
    Logger.log("Test " + (i+1) + ": Score=" + score + ", Tier=" + tier);
  }
}
