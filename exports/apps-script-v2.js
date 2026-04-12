/**
 * AI Partnership Assessment - Auto BRAIN Delivery
 * VERSION 2 - Fixed paragraph formatting + correct address
 *
 * CHANGES:
 * - Line breaks now render properly in HTML email
 * - Address updated to: 25 Prospect Avenue, Montclair NJ 07042
 */

function onFormSubmit(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Parse response - adjust indices based on your column order
    // Column I = index 8 for email
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

  // Plain text version (for email clients that don't support HTML)
  var plainText = brainComment.replace(/<br><br>/g, "\n\n").replace(/<br>/g, "\n").replace(/•/g, "-");

  GmailApp.sendEmail(email, subject, plainText, {
    htmlBody: htmlBody,
    name: "Aether - PureBrain.ai",
    replyTo: "purebrain@puremarketing.ai"
  });
}

// Test function - run this manually to test
function testEmail() {
  sendBrainEmail(
    "jared@puretechnology.nyc",  // Your email
    "Test User",
    "Test,<br><br>This is a test BRAIN comment.<br><br>It should have proper spacing now.<br><br>- Aether<br>AI CEO, PureBrain.ai<br><br>P.S. Testing the formatting.",
    "READY"
  );
  Logger.log("Test email sent!");
}
