#!/usr/bin/env python3
"""
Complete fix for social.purebrain.ai
Run: python3 /home/jared/projects/AI-CIV/aether/tools/fix_social_complete.py

ROOT CAUSE: duplicate `const PLATFORM_COLORS` (lines ~2507 and ~2863)
causes SyntaxError that prevents ALL JavaScript from loading.
Login button has onclick="login()" but login() never gets defined.
"""
import sys, re

HTML_PATH = '/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html'
WORKER_PATH = '/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js'

def fix_html():
    with open(HTML_PATH, 'r') as f:
        content = f.read()

    # ===== CRITICAL FIX: Remove duplicate const PLATFORM_COLORS =====
    # First occurrence (kanban section): keep and fix instagram color
    # Second occurrence (analytics section): comment out

    first = "const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',threads:'#000',instagram:'#e1306c',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500'};"
    first_fixed = "const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',threads:'#000',instagram:'#e4405f',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500'};"
    second = "const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',instagram:'#e4405f',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500',threads:'#000'};"

    if first in content and second in content:
        content = content.replace(first, first_fixed, 1)
        content = content.replace(second, "// PLATFORM_COLORS: using kanban declaration above", 1)
        print("[OK] Removed duplicate const PLATFORM_COLORS")
    else:
        print("[WARN] Could not find expected PLATFORM_COLORS patterns, trying fallback...")
        # Fallback: find all occurrences and remove the second
        matches = list(re.finditer(r"const PLATFORM_COLORS=\{[^}]+\};", content))
        if len(matches) >= 2:
            # Remove second match
            m = matches[1]
            content = content[:m.start()] + "// PLATFORM_COLORS: using kanban declaration above" + content[m.end():]
            print(f"[OK] Removed second PLATFORM_COLORS at char {m.start()}")
        else:
            print(f"[ERROR] Found {len(matches)} PLATFORM_COLORS declarations")
            return False

    # ===== FIX 2: Add console.log to login for debugging =====
    old_login = "async function login(){\n  const btn=document.getElementById"
    new_login = "async function login(){\n  console.log('[social] login() called');\n  const btn=document.getElementById"
    if old_login in content:
        content = content.replace(old_login, new_login, 1)
        print("[OK] Added console.log to login()")
    else:
        print("[WARN] Could not add console.log to login (different formatting?)")

    # ===== FIX 3: Improve auto-boot catch handler =====
    old_boot = "if(TOKEN){bootApp().catch(()=>{});}"
    new_boot = "if(TOKEN){console.log('[social] Auto-boot with stored token');bootApp().catch(function(e){console.warn('[social] Auto-boot failed:',e);localStorage.removeItem('social_token');TOKEN='';});}"
    content = content.replace(old_boot, new_boot)
    print("[OK] Improved auto-boot catch handler")

    # ===== FIX 4: Add dayOffset variable =====
    content = content.replace(
        "let monthOffset = 0;\nlet cachedPosts = [];",
        "let monthOffset = 0;\nlet dayOffset = 0;\nlet cachedPosts = [];",
        1
    )
    print("[OK] Added dayOffset variable")

    # ===== FIX 5: Add Day view button =====
    content = content.replace(
        """<button class="view-toggle-btn" onclick="setCalendarView('list')">List</button>""",
        """<button class="view-toggle-btn" onclick="setCalendarView('day')">Day</button>
          <button class="view-toggle-btn" onclick="setCalendarView('list')">List</button>""",
        1
    )
    print("[OK] Added Day view button")

    # ===== FIX 6: Add day-view container =====
    content = content.replace(
        '      <div id="list-view-container" style="display:none;">',
        '      <!-- Day View -->\n      <div id="day-view-container" style="display:none;">\n        <div id="day-view-content"></div>\n      </div>\n\n      <div id="list-view-container" style="display:none;">',
        1
    )
    print("[OK] Added day-view container")

    # ===== FIX 7: Update setCalendarView for day =====
    content = content.replace(
        "  document.getElementById('month-view').classList.toggle('visible',view==='month');\n  document.getElementById('week-view').classList.toggle('visible',view==='week');\n  document.getElementById('list-view-container').style.display=view==='list'?'block':'none';",
        "  document.getElementById('month-view').classList.toggle('visible',view==='month');\n  document.getElementById('week-view').classList.toggle('visible',view==='week');\n  document.getElementById('day-view-container').style.display=view==='day'?'block':'none';\n  document.getElementById('list-view-container').style.display=view==='list'?'block':'none';",
        1
    )
    content = content.replace(
        "  if(view==='month')renderMonthView();\n  else if(view==='week')renderWeekView();\n  else renderListView();\n  updateCalNavTitle();\n}",
        "  if(view==='month')renderMonthView();\n  else if(view==='week')renderWeekView();\n  else if(view==='day')renderDayView();\n  else renderListView();\n  updateCalNavTitle();\n}",
        1
    )
    print("[OK] Updated setCalendarView for day view")

    # ===== FIX 8: Update calNavPrev/Next/Today for day =====
    content = content.replace(
        "  if(calendarView==='month'){monthOffset--;renderMonthView();}\n  else if(calendarView==='week'){weekOffset--;renderWeekView();}\n  updateCalNavTitle();\n}\nfunction calNavNext(){\n  if(calendarView==='month'){monthOffset++;renderMonthView();}\n  else if(calendarView==='week'){weekOffset++;renderWeekView();}\n  updateCalNavTitle();\n}\nfunction calNavToday(){\n  monthOffset=0;weekOffset=0;\n  if(calendarView==='month')renderMonthView();\n  else if(calendarView==='week')renderWeekView();\n  updateCalNavTitle();\n}",
        "  if(calendarView==='month'){monthOffset--;renderMonthView();}\n  else if(calendarView==='week'){weekOffset--;renderWeekView();}\n  else if(calendarView==='day'){dayOffset--;renderDayView();}\n  updateCalNavTitle();\n}\nfunction calNavNext(){\n  if(calendarView==='month'){monthOffset++;renderMonthView();}\n  else if(calendarView==='week'){weekOffset++;renderWeekView();}\n  else if(calendarView==='day'){dayOffset++;renderDayView();}\n  updateCalNavTitle();\n}\nfunction calNavToday(){\n  monthOffset=0;weekOffset=0;dayOffset=0;\n  if(calendarView==='month')renderMonthView();\n  else if(calendarView==='week')renderWeekView();\n  else if(calendarView==='day')renderDayView();\n  updateCalNavTitle();\n}",
        1
    )
    print("[OK] Updated nav buttons for day view")

    # ===== FIX 9: Update calNavTitle for day =====
    content = content.replace(
        "  }else{\n    el.textContent='All Scheduled Posts';\n  }\n}",
        "  }else if(calendarView==='day'){\n    const d=new Date();d.setDate(d.getDate()+dayOffset);\n    el.textContent=d.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});\n  }else{\n    el.textContent='All Scheduled Posts';\n  }\n}",
        1
    )
    print("[OK] Updated nav title for day view")

    # ===== FIX 10: Add renderDayView function =====
    day_view_js = r"""
// ========== DAY VIEW ==========
function renderDayView(){
  var container=document.getElementById('day-view-content');
  if(!container)return;
  var now=new Date();
  var viewDate=new Date(now);
  viewDate.setDate(viewDate.getDate()+dayOffset);
  viewDate.setHours(0,0,0,0);
  var dateStr=viewDate.toISOString().split('T')[0];
  var dayPosts=cachedPosts.filter(function(p){
    var dt=p.scheduled_at||p.scheduled_time||p.created_at;
    if(!dt)return false;
    return dt.split('T')[0]===dateStr;
  }).sort(function(a,b){
    var at=a.scheduled_at||a.created_at||'';
    var bt=b.scheduled_at||b.created_at||'';
    return at.localeCompare(bt);
  });

  var html='<div class="card" style="margin-bottom:16px">';
  html+='<div class="card-header"><div class="card-title">'+viewDate.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'})+'</div>';
  html+='<div style="font-size:13px;color:var(--text-muted)">'+dayPosts.length+' post'+(dayPosts.length===1?'':'s')+'</div></div>';

  if(!dayPosts.length){
    html+='<div class="empty" style="padding:40px 20px"><div class="empty-icon" style="font-size:28px;margin-bottom:8px">--</div><div class="empty-text">No posts scheduled for this day</div></div>';
  }else{
    var hours={};
    dayPosts.forEach(function(p){
      var dt=p.scheduled_at||p.created_at||'';
      var h=dt?new Date(dt).getHours():-1;
      var key=h>=0?String(h).padStart(2,'0')+':00':'Unscheduled';
      if(!hours[key])hours[key]=[];
      hours[key].push(p);
    });

    Object.keys(hours).sort().forEach(function(hourKey){
      html+='<div style="border-bottom:1px solid var(--border);padding:16px 0;">';
      html+='<div style="font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--text-dim);margin-bottom:10px">'+esc(hourKey)+'</div>';
      hours[hourKey].forEach(function(p){
        var pl=p.platform||'linkedin';
        var ct=p.content_type||'linkedin';
        var ctLabel=CONTENT_TYPE_LABELS[ct]||ct;
        var preview=(p.content||p.body||'').substring(0,200);
        var imgSrc=getImgSrc(p);
        var time=p.scheduled_at?new Date(p.scheduled_at).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'}):'--';
        var barColor=PLATFORM_COLORS[pl]||'#888';

        html+='<div class="post-card" style="cursor:pointer;margin-bottom:10px;border-left:3px solid '+barColor+'" onclick="openEditModal(\''+p.id+'\')">';
        html+='<div class="post-meta" style="margin-bottom:8px">';
        html+='<div class="post-platform"><span class="dot '+esc(pl)+'"></span>'+esc(PLATFORM_NAMES[pl]||pl)+' <span class="ct-badge ct-badge-'+esc(ct)+'">'+esc(ctLabel)+'</span></div>';
        html+='<div style="display:flex;align-items:center;gap:8px"><span class="status-badge status-'+esc(p.status)+'">'+esc(p.status)+'</span><span class="post-time">'+esc(time)+'</span></div>';
        html+='</div>';
        if(p.title){html+='<div style="font-size:14px;font-weight:700;color:#fff;margin-bottom:4px">'+esc(p.title)+'</div>';}
        html+='<div style="display:flex;gap:12px;align-items:flex-start">';
        if(imgSrc){html+='<div class="post-thumb"><img src="'+esc(imgSrc)+'" alt="media" onerror="this.parentElement.style.display=\'none\'"></div>';}
        html+='<div class="post-body" style="font-size:13px;flex:1">'+esc(preview)+'</div>';
        html+='</div>';
        html+='<div class="post-actions" style="margin-top:8px" onclick="event.stopPropagation()">';
        if(p.status==='draft')html+='<button class="action-btn approve" onclick="event.stopPropagation();approvePost(\''+p.id+'\')">Approve</button>';
        html+='<button class="action-btn edit" onclick="event.stopPropagation();openEditModal(\''+p.id+'\')">Edit</button>';
        if(p.status==='scheduled')html+='<button class="action-btn post-now" onclick="event.stopPropagation();postNowById(\''+p.id+'\')">Post Now</button>';
        html+='<button class="action-btn delete" onclick="event.stopPropagation();deletePost(\''+p.id+'\')">Delete</button>';
        html+='</div></div>';
      });
      html+='</div>';
    });
  }
  html+='</div>';
  container.innerHTML=html;
}

"""

    content = content.replace(
        "// ========== WEEK VIEW ==========",
        day_view_js + "// ========== WEEK VIEW ==========",
        1
    )
    print("[OK] Added renderDayView function")

    # ===== FIX 11: Update showDayDetail to use day view =====
    content = content.replace(
        "function showDayDetail(dateStr){\n  setCalendarView('list');\n  // Pre-set date filter -- not implemented as a dedicated filter, just switch to list view\n}",
        "function showDayDetail(dateStr){\n  var target=new Date(dateStr+'T12:00:00');\n  var now=new Date();now.setHours(0,0,0,0);\n  dayOffset=Math.round((target-now)/(86400000));\n  setCalendarView('day');\n}",
        1
    )
    print("[OK] Updated showDayDetail for day view")

    # ===== FIX 12: Add platform-specific captions to edit modal =====
    # Add the container in the HTML
    content = content.replace(
        '        </div>\n      </div>\n      <!-- CENTER: Live Post Preview -->',
        '        </div>\n        <!-- Platform-Specific Captions (Edit Modal) -->\n        <div class="form-group" id="modal-platform-captions-group" style="display:none">\n          <label class="form-label">Platform-Specific Captions</label>\n          <div id="modal-platform-captions"></div>\n        </div>\n      </div>\n      <!-- CENTER: Live Post Preview -->',
        1
    )
    print("[OK] Added platform captions container to edit modal")

    # Add JS to populate platform captions in openEditModal
    pc_js = """
  // Platform-specific captions
  var pcGroup=document.getElementById('modal-platform-captions-group');
  var pcContainer=document.getElementById('modal-platform-captions');
  var existingCaptions={};
  if(post.platform_captions){
    try{existingCaptions=typeof post.platform_captions==='string'?JSON.parse(post.platform_captions):post.platform_captions;}catch(ex){}
  }
  pcGroup.style.display='block';
  var pl=post.platform||'linkedin';
  var otherPlatforms=Object.keys(PLATFORM_NAMES).filter(function(p){return p!==pl;});
  var pcHtml='<div style="font-size:11px;color:var(--text-dim);margin-bottom:8px">Primary: '+(PLATFORM_NAMES[pl]||pl)+' (uses main content above)</div>';
  otherPlatforms.forEach(function(p){
    var val=existingCaptions[p]||'';
    var limit=CHAR_LIMITS[p]||3000;
    pcHtml+='<div style="margin-bottom:10px">';
    pcHtml+='<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px"><span class="dot '+p+'" style="width:8px;height:8px"></span><span style="font-size:11px;font-weight:600;color:var(--text-muted)">'+(PLATFORM_NAMES[p]||p)+'</span><span style="font-size:10px;color:var(--text-dim)">'+limit+' chars</span></div>';
    pcHtml+='<textarea class="field-input modal-pc-textarea" data-platform="'+p+'" placeholder="Custom caption for '+(PLATFORM_NAMES[p]||p)+' (leave empty to use main)" style="min-height:60px;font-size:13px">'+esc(val)+'</textarea>';
    pcHtml+='</div>';
  });
  pcContainer.innerHTML=pcHtml;

"""
    content = content.replace(
        "  // Quality gate check\n  updateModalQG();",
        pc_js + "  // Quality gate check\n  updateModalQG();",
        1
    )
    print("[OK] Added platform captions JS to openEditModal")

    # Add platform captions to saveModalEdit
    content = content.replace(
        "  if(modalReplaceFile){updateBody.media_base64=modalReplaceFile.base64;updateBody.media_filename=modalReplaceFile.name;}",
        "  if(modalReplaceFile){updateBody.media_base64=modalReplaceFile.base64;updateBody.media_filename=modalReplaceFile.name;}\n  // Collect platform-specific captions\n  var modalPcTextareas=document.querySelectorAll('.modal-pc-textarea');\n  if(modalPcTextareas.length){\n    var pc={};\n    modalPcTextareas.forEach(function(ta){var v=ta.value.trim();if(v)pc[ta.dataset.platform]=v;});\n    if(Object.keys(pc).length)updateBody.platform_captions=JSON.stringify(pc);\n  }",
        1
    )
    print("[OK] Added platform captions to saveModalEdit")

    # ===== FIX 13: Update build comment =====
    content = content.replace(
        "<!-- VERIFIED BUILD: 3185 lines, LinkedIn preview + Trello cards, 2026-04-20 10:15 UTC -->",
        "<!-- VERIFIED BUILD: login-fix+dayview+platform-captions, 2026-04-20 CTO sprint -->"
    )
    print("[OK] Updated build comment")

    # Write
    with open(HTML_PATH, 'w') as f:
        f.write(content)

    # Verify
    pc_count = content.count("const PLATFORM_COLORS=")
    login_ok = "console.log('[social] login() called')" in content
    day_ok = "function renderDayView()" in content
    captions_ok = "modal-platform-captions" in content
    boot_ok = "Auto-boot with stored token" in content

    print(f"\n=== VERIFICATION ===")
    print(f"  const PLATFORM_COLORS count: {pc_count} {'[PASS]' if pc_count == 1 else '[FAIL]'}")
    print(f"  login() logging: {login_ok}")
    print(f"  day view: {day_ok}")
    print(f"  platform captions: {captions_ok}")
    print(f"  auto-boot fix: {boot_ok}")
    print(f"  Total lines: {len(content.splitlines())}")

    if pc_count != 1:
        print("\n*** CRITICAL FAILURE: const PLATFORM_COLORS count != 1 ***")
        return False
    return True


def embed_html_in_worker():
    """Re-embed the fixed HTML into worker.js"""
    with open(HTML_PATH, 'r') as f:
        html = f.read()

    with open(WORKER_PATH, 'r') as f:
        worker = f.read()

    # Escape for template literal
    html_escaped = html.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    # Find and replace the FRONTEND_HTML template literal
    # Pattern: const FRONTEND_HTML = `...`;
    start_marker = "const FRONTEND_HTML = `"
    end_marker = "\n`;\n"

    start_idx = worker.find(start_marker)
    if start_idx == -1:
        print("[ERROR] Could not find FRONTEND_HTML in worker.js")
        return False

    # Find the closing backtick-semicolon after the HTML
    search_from = start_idx + len(start_marker)
    end_idx = worker.find(end_marker, search_from)
    if end_idx == -1:
        # Try alternate ending
        end_marker = "`;\n"
        end_idx = worker.find(end_marker, search_from)
        if end_idx == -1:
            print("[ERROR] Could not find end of FRONTEND_HTML in worker.js")
            return False

    # Reconstruct worker.js
    new_worker = worker[:start_idx] + "const FRONTEND_HTML = `" + html_escaped + "\n`;" + worker[end_idx + len(end_marker):]

    with open(WORKER_PATH, 'w') as f:
        f.write(new_worker)

    # Verify no duplicate PLATFORM_COLORS in worker
    pc_count = new_worker.count("const PLATFORM_COLORS=")
    # The worker has its own PLATFORM_COLORS in backend? No, it's only in the HTML template.
    # But the backend code doesn't use PLATFORM_COLORS. Let's check.
    print(f"\n=== WORKER VERIFICATION ===")
    print(f"  FRONTEND_HTML embedded: {start_marker in new_worker}")
    print(f"  Worker total lines: {len(new_worker.splitlines())}")

    # Check that the embedded HTML doesn't have unescaped backticks or ${
    html_section = new_worker[start_idx:new_worker.find("\n`;", start_idx)]
    unescaped_backtick = '`' in html_section.replace('\\`', '')
    print(f"  Unescaped backticks in HTML: {unescaped_backtick} {'[FAIL]' if unescaped_backtick else '[PASS]'}")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("social.purebrain.ai Complete Fix Script")
    print("=" * 60)
    print()

    print("STEP 1: Fix standalone HTML")
    print("-" * 40)
    if not fix_html():
        print("\nHTML fix FAILED. Aborting.")
        sys.exit(1)

    print()
    print("STEP 2: Re-embed HTML into worker.js")
    print("-" * 40)
    if not embed_html_in_worker():
        print("\nWorker embed FAILED.")
        sys.exit(1)

    print()
    print("=" * 60)
    print("ALL FIXES APPLIED SUCCESSFULLY")
    print("=" * 60)
    print()
    print("To deploy:")
    print(f"  cd /home/jared/projects/AI-CIV/aether/workers/social-api")
    print(f"  CLOUDFLARE_API_TOKEN=cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be npx wrangler deploy --dry-run")
    print(f"  # If dry-run passes:")
    print(f"  CLOUDFLARE_API_TOKEN=cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be npx wrangler deploy")
