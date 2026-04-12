#!/bin/bash
# Fetch Unified page content with auth

curl -s \
  -u "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  "https://purebrain.ai/wp-json/wp/v2/pages/1263?context=edit&_fields=id,title,content,meta" \
  > /tmp/unified_page.json

echo "Status: $?"
echo "File size: $(wc -c < /tmp/unified_page.json) bytes"
# Show first 200 chars of content raw
python3 -c "
import json
with open('/tmp/unified_page.json') as f:
    data = json.load(f)
content = data.get('content', {}).get('raw', '')
print('=== RAW CONTENT FIRST 4000 CHARS ===')
print(content[:4000])
print()
print('=== FULL LENGTH:', len(content))
meta = data.get('meta', {})
print('Meta keys:', list(meta.keys()) if meta else 'none')
# search for table
if '<table' in content.lower():
    idx = content.lower().find('<table')
    print('TABLE FOUND at index', idx)
    print(content[max(0,idx-200):idx+3000])
else:
    print('NO TABLE IN RAW — checking rendered...')
    rendered = data.get('content', {}).get('rendered', '')
    print('Rendered length:', len(rendered))
    if '<table' in rendered.lower():
        idx = rendered.lower().find('<table')
        print('TABLE IN RENDERED at index', idx)
        print(rendered[max(0,idx-200):idx+3000])
"
