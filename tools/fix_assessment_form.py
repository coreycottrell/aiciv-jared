#!/usr/bin/env python3
"""
Fix PureBrain Assessment Form - Uses hidden iframe method
that matches the working puremarketing.ai form pattern
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# WordPress credentials
WP_URL = "https://purebrain.ai"
WP_USER = os.getenv('PUREBRAIN_WP_USER', 'Aether')
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

PAGE_ID = 253  # Assessment page

# The CORRECT Google Form URL
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfJ4VGlPt_3RDc4x32hS8d7e1He8L3gnSYpsMLuGHzEzSdeIg/formResponse"

# Entry IDs from Jared's Google Form
ENTRY_IDS = {
    'q1': 'entry.1041511953',
    'q2': 'entry.801023928',
    'q3': 'entry.1787427457',
    'q4': 'entry.739814423',
    'q5': 'entry.1984896605',
    'name': 'entry.1763938619',
    'email': 'entry.1619091608',
    'company': 'entry.414048438'
}

# The HTML content with hidden iframe method (proven pattern from puremarketing.ai)
PAGE_CONTENT = '''
<!-- Hidden iframe for form submission -->
<iframe name="hidden_iframe" id="hidden_iframe" style="display:none !important; width:0; height:0; border:none;"></iframe>

<!-- Hidden form that submits to Google Forms via iframe -->
<form id="googleForm" action="''' + GOOGLE_FORM_URL + '''" method="POST" target="hidden_iframe" style="display:none;">
  <input type="hidden" name="''' + ENTRY_IDS['q1'] + '''" id="gf_q1">
  <input type="hidden" name="''' + ENTRY_IDS['q2'] + '''" id="gf_q2">
  <input type="hidden" name="''' + ENTRY_IDS['q3'] + '''" id="gf_q3">
  <input type="hidden" name="''' + ENTRY_IDS['q4'] + '''" id="gf_q4">
  <input type="hidden" name="''' + ENTRY_IDS['q5'] + '''" id="gf_q5">
  <input type="hidden" name="''' + ENTRY_IDS['name'] + '''" id="gf_name">
  <input type="hidden" name="''' + ENTRY_IDS['email'] + '''" id="gf_email">
  <input type="hidden" name="''' + ENTRY_IDS['company'] + '''" id="gf_company">
</form>

<style>
.assessment-container{max-width:800px;margin:0 auto;padding:40px 20px;font-family:'Plus Jakarta Sans',sans-serif}
.progress-container{margin-bottom:30px;text-align:center}
.progress-text{font-size:14px;color:#666;margin-bottom:10px}
.progress-bar{height:6px;background:#e0e0e0;border-radius:3px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,#2a93c1,#f1420b);transition:width 0.3s ease}
.question{display:none;animation:fadeIn 0.3s ease}
.question.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.question h2{font-size:24px;color:#1a1a1a;margin-bottom:30px;line-height:1.4}
.options{display:flex;flex-direction:column;gap:12px}
.option{display:flex;align-items:center;padding:16px 20px;border:2px solid #e0e0e0;border-radius:12px;cursor:pointer;transition:all 0.2s ease;background:#fff}
.option:hover{border-color:#2a93c1;background:#f8fbfc}
.option.selected{border-color:#2a93c1;background:#e8f4f8}
.option-letter{width:32px;height:32px;display:flex;align-items:center;justify-content:center;background:#f0f0f0;border-radius:8px;font-weight:600;color:#666;margin-right:16px;flex-shrink:0}
.option.selected .option-letter{background:#2a93c1;color:#fff}
.option-text{font-size:16px;color:#333}
.nav-buttons{display:flex;gap:12px;margin-top:30px}
.btn{padding:14px 28px;border-radius:8px;font-size:16px;font-weight:600;cursor:pointer;transition:all 0.2s ease;border:none}
.btn-secondary{background:#f0f0f0;color:#666}
.btn-secondary:hover{background:#e0e0e0}
.btn-primary{background:linear-gradient(135deg,#2a93c1,#f1420b);color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(42,147,193,0.3)}
.btn-primary:disabled{opacity:0.5;cursor:not-allowed;transform:none}
.contact-form{margin-top:20px}
.contact-form h3{font-size:20px;color:#1a1a1a;margin-bottom:20px}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:14px;color:#666;margin-bottom:6px}
.form-group input{width:100%;padding:12px 16px;border:2px solid #e0e0e0;border-radius:8px;font-size:16px;transition:border-color 0.2s ease}
.form-group input:focus{outline:none;border-color:#2a93c1}
#results{display:none;text-align:center;padding:40px 20px}
#results.active{display:block}
#results h2{font-size:28px;color:#1a1a1a;margin-bottom:16px}
#results p{font-size:18px;color:#666;margin-bottom:30px}
.cta-button{display:inline-block;padding:16px 32px;background:linear-gradient(135deg,#f1420b,#2a93c1);color:#fff;text-decoration:none;border-radius:8px;font-size:18px;font-weight:600;transition:transform 0.2s ease}
.cta-button:hover{transform:translateY(-2px)}
</style>

<div class="assessment-container">
<div class="progress-container">
<div class="progress-text">Question <span id="currentQ">1</span> of 6</div>
<div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:16.67%"></div></div>
</div>

<div class="question active" data-question="1">
<h2>When you close a chat with ChatGPT or Claude, what happens to your conversation history?</h2>
<div class="options">
<div class="option" onclick="selectOption(this)"><span class="option-letter">A</span><span class="option-text">It's gone forever – I start fresh each time</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">B</span><span class="option-text">I can look back at old chats if needed</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">C</span><span class="option-text">I don't know / haven't thought about it</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">D</span><span class="option-text">I've tried to maintain context but it's frustrating</span></div>
</div>
<div class="nav-buttons"><button class="btn btn-primary" onclick="nextQuestion()" disabled>Continue</button></div>
</div>

<div class="question" data-question="2">
<h2>How do you currently use AI in your daily workflow?</h2>
<div class="options">
<div class="option" onclick="selectOption(this)"><span class="option-letter">A</span><span class="option-text">Occasional questions when I'm stuck</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">B</span><span class="option-text">Regular task assistance (writing, research)</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">C</span><span class="option-text">Heavily integrated into most of my work</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">D</span><span class="option-text">I'm not really using AI yet</span></div>
</div>
<div class="nav-buttons"><button class="btn btn-secondary" onclick="prevQuestion()">Back</button><button class="btn btn-primary" onclick="nextQuestion()" disabled>Continue</button></div>
</div>

<div class="question" data-question="3">
<h2>What's your biggest frustration with current AI tools?</h2>
<div class="options">
<div class="option" onclick="selectOption(this)"><span class="option-letter">A</span><span class="option-text">They don't remember what I've told them</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">B</span><span class="option-text">They give generic, not-personalized responses</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">C</span><span class="option-text">I'm not sure how to use them effectively</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">D</span><span class="option-text">Every conversation feels like talking to strangers</span></div>
</div>
<div class="nav-buttons"><button class="btn btn-secondary" onclick="prevQuestion()">Back</button><button class="btn btn-primary" onclick="nextQuestion()" disabled>Continue</button></div>
</div>

<div class="question" data-question="4">
<h2>What would an ideal AI relationship look like for you?</h2>
<div class="options">
<div class="option" onclick="selectOption(this)"><span class="option-letter">A</span><span class="option-text">A smart search engine that answers questions quickly</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">B</span><span class="option-text">A reliable assistant that knows my preferences</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">C</span><span class="option-text">A strategic partner that helps me think bigger</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">D</span><span class="option-text">A digital employee that grows with my organization</span></div>
</div>
<div class="nav-buttons"><button class="btn btn-secondary" onclick="prevQuestion()">Back</button><button class="btn btn-primary" onclick="nextQuestion()" disabled>Continue</button></div>
</div>

<div class="question" data-question="5">
<h2>What would you pay monthly for an AI that actually learns how your business runs?</h2>
<div class="options">
<div class="option" onclick="selectOption(this)"><span class="option-letter">A</span><span class="option-text">Nothing – free tools work fine for me</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">B</span><span class="option-text">$100-200/month if it saved significant time</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">C</span><span class="option-text">$200-500/month for a real productivity multiplier</span></div>
<div class="option" onclick="selectOption(this)"><span class="option-letter">D</span><span class="option-text">The question isn't cost – it's whether it actually works</span></div>
</div>
<div class="nav-buttons"><button class="btn btn-secondary" onclick="prevQuestion()">Back</button><button class="btn btn-primary" onclick="nextQuestion()" disabled>Continue</button></div>
</div>

<div class="question" data-question="6">
<h2>Almost done! Where should we send your results?</h2>
<div class="contact-form">
<div class="form-group"><label>Your Name *</label><input type="text" id="name" placeholder="Enter your name" required></div>
<div class="form-group"><label>Email Address *</label><input type="email" id="email" placeholder="your@email.com" required></div>
<div class="form-group"><label>Company/Organization</label><input type="text" id="company" placeholder="Your company (optional)"></div>
</div>
<div class="nav-buttons"><button class="btn btn-secondary" onclick="prevQuestion()">Back</button><button class="btn btn-primary" onclick="submitForm()">Get My Results</button></div>
</div>

<div id="results">
<h2 id="resultTitle">Your Results</h2>
<p id="resultDesc">Check your email for your personalized AI Partnership Analysis from Aether.</p>
<a href="https://purebrain.ai" class="cta-button">Explore PureBrain.ai →</a>
</div>
</div>

<script>
var currentQuestion=1,totalQuestions=6,answers={};

function selectOption(e){
  var t=e.closest(".question");
  t.querySelectorAll(".option").forEach(function(e){e.classList.remove("selected")});
  e.classList.add("selected");
  var n=t.dataset.question;
  var answerText=e.querySelector(".option-text").textContent;
  answers[n]=answerText;
  var o=t.querySelector(".btn-primary");
  if(o){o.disabled=false}
}

function nextQuestion(){
  if(currentQuestion<totalQuestions){
    document.querySelector('.question[data-question="'+currentQuestion+'"]').classList.remove("active");
    currentQuestion++;
    document.querySelector('.question[data-question="'+currentQuestion+'"]').classList.add("active");
    updateProgress();
  }
}

function prevQuestion(){
  if(currentQuestion>1){
    document.querySelector('.question[data-question="'+currentQuestion+'"]').classList.remove("active");
    currentQuestion--;
    document.querySelector('.question[data-question="'+currentQuestion+'"]').classList.add("active");
    updateProgress();
  }
}

function updateProgress(){
  document.getElementById("currentQ").textContent=currentQuestion;
  var e=currentQuestion/totalQuestions*100;
  document.getElementById("progressFill").style.width=e+"%";
}

function calculateResult(){
  var score=0;
  var a1=(answers["1"]||"").toLowerCase();
  if(a1.indexOf("frustrating")!==-1||a1.indexOf("tried to maintain")!==-1){score+=2;}
  else if(a1.indexOf("look back")!==-1){score+=1;}
  var a2=(answers["2"]||"").toLowerCase();
  if(a2.indexOf("heavily integrated")!==-1){score+=2;}
  else if(a2.indexOf("occasional")!==-1||a2.indexOf("regular task")!==-1){score+=1;}
  var a3=(answers["3"]||"").toLowerCase();
  if(a3.indexOf("don't remember")!==-1||a3.indexOf("generic")!==-1||a3.indexOf("strangers")!==-1){score+=2;}
  var a4=(answers["4"]||"").toLowerCase();
  if(a4.indexOf("strategic partner")!==-1||a4.indexOf("digital employee")!==-1){score+=2;}
  else if(a4.indexOf("reliable assistant")!==-1){score+=1;}
  var a5=(answers["5"]||"").toLowerCase();
  if(a5.indexOf("200-500")!==-1||a5.indexOf("isn't cost")!==-1||a5.indexOf("actually works")!==-1){score+=2;}
  else if(a5.indexOf("100-200")!==-1){score+=1;}
  return score;
}

function submitForm(){
  var userName=document.getElementById("name").value;
  var userEmail=document.getElementById("email").value;
  var userCompany=document.getElementById("company").value;

  if(!userName){alert("Please enter your name");return;}
  if(!userEmail){alert("Please enter your email");return;}
  if(!userCompany){userCompany="your organization";}

  // Populate the hidden form fields
  document.getElementById("gf_q1").value=answers["1"]||"";
  document.getElementById("gf_q2").value=answers["2"]||"";
  document.getElementById("gf_q3").value=answers["3"]||"";
  document.getElementById("gf_q4").value=answers["4"]||"";
  document.getElementById("gf_q5").value=answers["5"]||"";
  document.getElementById("gf_name").value=userName;
  document.getElementById("gf_email").value=userEmail;
  document.getElementById("gf_company").value=userCompany;

  // Submit the form via hidden iframe (proven pattern from puremarketing.ai)
  document.getElementById("googleForm").submit();
  console.log("Form submitted via hidden iframe to Google Forms");

  // Show results
  var score=calculateResult();
  var title,desc;
  if(score>=7){title="You're Ready for AI Partnership!";desc="You've outgrown generic AI tools and are ready for a real AI partnership. Check your email for your personalized analysis from Aether.";}
  else if(score>=4){title="You've Felt the Friction";desc="You know AI can do more – you just haven't found the right approach yet. Check your email for your personalized analysis from Aether.";}
  else{title="You're at the Starting Line";desc="This is actually the perfect time to build your AI foundation the right way. Check your email for your personalized analysis from Aether.";}

  document.getElementById("resultTitle").textContent=title;
  document.getElementById("resultDesc").textContent=desc;
  document.querySelectorAll(".question").forEach(function(e){e.classList.remove("active")});
  document.getElementById("results").classList.add("active");
  document.querySelector(".progress-container").style.display="none";
}
</script>
'''


def update_assessment_page():
    """Update the PureBrain assessment page with the hidden iframe form method"""

    print("=" * 60)
    print("Updating PureBrain Assessment Page")
    print("=" * 60)

    # First, get current page to verify we have access
    print("\n[1] Fetching current page...")
    response = requests.get(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
        auth=(WP_USER, WP_APP_PASSWORD)
    )

    if response.status_code != 200:
        print(f"ERROR: Could not fetch page. Status: {response.status_code}")
        print(response.text)
        return False

    current = response.json()
    print(f"  Current title: {current.get('title', {}).get('rendered', 'Unknown')}")

    # Update the page
    print("\n[2] Updating page with hidden iframe form method...")

    update_data = {
        'content': PAGE_CONTENT
    }

    response = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
        auth=(WP_USER, WP_APP_PASSWORD),
        json=update_data
    )

    if response.status_code == 200:
        print("  SUCCESS: Page updated!")
        print(f"\n[3] View at: {WP_URL}/assessment/")
        return True
    else:
        print(f"  ERROR: Could not update page. Status: {response.status_code}")
        print(response.text)
        return False


if __name__ == "__main__":
    success = update_assessment_page()

    if success:
        print("\n" + "=" * 60)
        print("FIX APPLIED: Hidden Iframe Form Method")
        print("=" * 60)
        print("""
The assessment page now uses the PROVEN pattern from puremarketing.ai:

1. Hidden iframe: <iframe name="hidden_iframe" style="display:none">
2. Real form: <form action="...formResponse" target="hidden_iframe" method="POST">
3. Hidden inputs: <input type="hidden" name="entry.XXXX">
4. Native submit: form.submit() → goes to iframe → no page reload

This bypasses CORS/CSP restrictions because:
- Native browser form POST to different origin is allowed
- Iframe target prevents page redirect
- No JavaScript fetch/XHR needed

TEST IT:
1. Go to https://purebrain.ai/assessment/
2. Answer all questions
3. Fill in name/email
4. Click "Get My Results"
5. Check Google Sheet for new row

If row appears → SUCCESS!
""")
