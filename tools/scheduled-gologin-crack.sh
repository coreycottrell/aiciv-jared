#!/bin/bash
# Scheduled task: Crack GoLogin signup using PureSurf anti-detection (100/100 score)
# Strategy: Let the REAL Turnstile widget load and auto-verify (not 2Captcha token injection)
# The anti-detection hardening should make Turnstile think we're a real browser

cd /home/jared/projects/AI-CIV/aether

# Create session with residential proxy
SESSION=$(curl -s -X POST "https://surf.purebrain.ai/sessions" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"profile_name":"gologin-autosolve","device":"macbook","proxy":"http://user-hjW3vwbaT8UJlpwz-type-residential-session-g906ztg3-country-US-city-New_York-rotation-15:UEEsVU57WP5VBvHn@geo.g-w.info:10080"}')

echo "$(date): GoLogin crack session created: $SESSION" >> logs/gologin-crack.log

# Navigate to signup
curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/navigate" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://app.gologin.com/sign_up","auto_solve_captcha":true}'

sleep 5

# Fill form
curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/type" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"selector":"input[type=email]","text":"purebrain@puremarketing.ai"}'

curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/evaluate" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"script":"var pws=document.querySelectorAll(\"input[type=password]\"); pws.forEach(function(p){p.value=\"PureSurf2026!R\"; p.dispatchEvent(new Event(\"input\",{bubbles:true}));}); pws.length"}'

sleep 2

# Solve captcha (will try bulletproof solver with iframe detection)
SOLVE=$(curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/solve-captcha" \
  -H "X-API-Key: aether-baas-key-001")
echo "$(date): Captcha solve result: $SOLVE" >> logs/gologin-crack.log

sleep 5

# Click signup
curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/evaluate" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"script":"var btn=Array.from(document.querySelectorAll(\"button\")).find(b=>b.textContent.trim()===\"Sign up\"); if(btn){btn.click(); \"clicked\";} else {\"no btn\";}"}'

sleep 10

# Screenshot result
curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/screenshot" \
  -H "X-API-Key: aether-baas-key-001" \
  --output exports/portal-files/gologin-scheduled-crack-result.png

RESULT=$(curl -s -X POST "https://surf.purebrain.ai/sessions/gologin-autosolve/evaluate" \
  -H "X-API-Key: aether-baas-key-001" \
  -H "Content-Type: application/json" \
  -d '{"script":"document.title + \" | \" + window.location.href"}')
echo "$(date): Final result: $RESULT" >> logs/gologin-crack.log

# Close session
curl -s -X DELETE "https://surf.purebrain.ai/sessions/gologin-autosolve" \
  -H "X-API-Key: aether-baas-key-001"
