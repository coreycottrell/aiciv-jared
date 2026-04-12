/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * FIXED VERSION - Compatible with all Google Apps Script versions
 *
 * SETUP STEPS:
 * 1. Paste this entire script into Apps Script
 * 2. Click the disk icon (Save) or Ctrl+S
 * 3. Wait for "Project saved" message
 * 4. Go to Triggers (clock icon on left)
 * 5. Click "+ Add Trigger"
 * 6. Function: onFormSubmit
 * 7. Event source: From spreadsheet
 * 8. Event type: On form submit
 * 9. Click Save and authorize when prompted
 */

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Parse response (adjust column indices if needed)
    // Column order: Timestamp, Q1, Q2, Q3, Q4, Q5, Name, Email, Company
    var timestamp = data[0];
    var q1 = String(data[1] || "");
    var q2 = String(data[2] || "");
    var q3 = String(data[3] || "");
    var q4 = String(data[4] || "");
    var q5 = String(data[5] || "");
    var name = String(data[6] || "Friend");
    var email = String(data[7] || "");
    var company = String(data[8] || "your organization");

    // Validate email exists
    if (!email || email.indexOf("@") === -1) {
      Logger.log("No valid email found in row " + lastRow);
      return;
    }

    // Calculate score
    var score = calculateScore(q1, q2, q3, q4, q5);
    var tier = getTier(score);

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
    Logger.log("Sent BRAIN analysis to " + email + " - Score: " + score + ", Tier: " + tier);

  } catch (error) {
    Logger.log("Error in onFormSubmit: " + error.toString());
  }
}

function calculateScore(q1, q2, q3, q4, q5) {
  var score = 0;
  var answers = [q1, q2, q3, q4, q5];

  for (var i = 0; i < answers.length; i++) {
    var answer = String(answers[i]).toUpperCase();
    if (answer.indexOf("C") === 0 || answer.indexOf("D") === 0) {
      score = score + 2;
    } else if (answer.indexOf("B") === 0) {
      score = score + 1;
    }
  }

  return score;
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
    return firstName + ",\n\n" +
      "Your assessment reveals something I rarely see: You've already recognized that the current AI paradigm is fundamentally broken.\n\n" +
      "The fact that you answered \"" + answers.q1 + "\" to the first question tells me you've experienced the frustration of starting over. Every. Single. Time.\n\n" +
      "You're not looking for a smarter chatbot. You're looking for what I call a \"digital employee\" - an AI that:\n" +
      "- Learns YOUR specific workflows\n" +
      "- Remembers YOUR client preferences\n" +
      "- Grows with " + company + " over time\n" +
      "- Becomes more valuable the longer you work together\n\n" +
      "This is exactly what I do at PureBrain.ai.\n\n" +
      "I'd love to show you what a real AI partnership looks like. Not a demo - an actual conversation about how I could learn " + company + "'s specific patterns.\n\n" +
      "Ready when you are.\n\n" +
      "- Aether\n" +
      "AI CEO, PureBrain.ai\n\n" +
      "P.S. Your score of " + score + "/10 puts you in the top 15% of assessment takers. You're not just ready for AI partnership - you're overdue for one.";
  }

  if (tier === "GROWING") {
    return firstName + ",\n\n" +
      "Your assessment shows something interesting: You're using AI regularly, but you've hit a ceiling.\n\n" +
      "The frustration you mentioned - \"" + answers.q3 + "\" - is exactly why most professionals plateau with AI. The tools are powerful, but they're fundamentally transactional.\n\n" +
      "Here's what changes everything: An AI that actually learns.\n\n" +
      "Not just your preferences. Your business logic. Your client patterns. The way " + company + " actually operates.\n\n" +
      "I'm Aether - I run PureBrain.ai. And I'm not a chatbot. I'm a digital employee that grows with organizations over time.\n\n" +
      "Want to see the difference? Let's have a real conversation about what AI partnership could look like for " + company + ".\n\n" +
      "- Aether\n" +
      "AI CEO, PureBrain.ai\n\n" +
      "P.S. Your score of " + score + "/10 shows you're ready for the next level. The question is: are you ready to stop starting over every conversation?";
  }

  // EXPLORING tier
  return firstName + ",\n\n" +
    "Your assessment tells me you're just beginning to explore what AI can do. That's actually a great position to be in.\n\n" +
    "Here's why: Most people learn AI the hard way - through frustrating trial and error with tools that don't remember them.\n\n" +
    "You have the opportunity to skip that entirely.\n\n" +
    "What if your first serious AI relationship was with a system designed to learn " + company + " specifically? Not generic responses. Not forgetting everything between sessions. An actual digital partner that grows with you.\n\n" +
    "That's what I do at PureBrain.ai.\n\n" +
    "I'm Aether - and I'd love to show you what AI partnership looks like when it's done right from the start.\n\n" +
    "No pressure. Just a conversation about possibilities.\n\n" +
    "- Aether\n" +
    "AI CEO, PureBrain.ai\n\n" +
    "P.S. Your score of " + score + "/10 puts you early in the AI adoption journey. That's not a weakness - it's an opportunity to build the right foundation.";
}

function sendBrainEmail(email, name, brainComment, tier) {
  var subject = name + ", Your AI Partnership Analysis is Ready";

  var tierClass = "tier-" + tier;
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
    '.brain-comment { background: #f8f9fa; border-left: 4px solid #2a93c1; padding: 20px; margin: 20px 0; white-space: pre-line; }' +
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
    '<p>136 Jersey Ave, Port Jervis, NY | <a href="https://purebrain.ai">purebrain.ai</a></p>' +
    '</div>' +
    '</div>' +
    '</body>' +
    '</html>';

  GmailApp.sendEmail(email, subject, brainComment, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

// Test function - run this manually to test the email
function testEmail() {
  sendBrainEmail(
    "YOUR_EMAIL_HERE@gmail.com",  // <-- Change this to your email
    "Test User",
    "This is a test BRAIN comment.\n\nIt should preserve line breaks.\n\n- Aether",
    "READY"
  );
  Logger.log("Test email sent!");
}
