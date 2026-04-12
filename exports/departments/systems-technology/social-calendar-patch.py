#!/usr/bin/env python3
"""
Social Dashboard Calendar View Rebuild
Patches social.html to add proper Month + Week + List calendar views
with Buffer-inspired grid design.
"""
import re
import sys

def patch_social_html(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # =========================================================
    # 1. INSERT CSS before </style>
    # =========================================================
    calendar_css = """
/* --- CALENDAR VIEWS (Month/Week/List) --- */
.view-toggle {
  display: flex;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}
.view-toggle-btn {
  padding: 7px 16px;
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.view-toggle-btn:hover { color: var(--text); background: var(--surface-hover); }
.view-toggle-btn.active {
  background: var(--blue);
  color: #fff;
}

/* Content type badges */
.ct-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.ct-badge-blog { background: rgba(42,147,193,0.15); color: var(--blue); }
.ct-badge-linkedin { background: rgba(241,66,11,0.15); color: var(--orange); }
.ct-badge-newsletter { background: rgba(34,197,94,0.15); color: var(--green); }
.ct-badge-bluesky { background: rgba(99,102,241,0.15); color: #818cf8; }

/* Calendar navigation bar */
.cal-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}
.cal-nav-center {
  display: flex;
  align-items: center;
  gap: 12px;
}
.cal-nav-title {
  font-size: 18px;
  font-weight: 700;
  min-width: 180px;
  text-align: center;
}
.cal-nav-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.cal-nav-btn:hover { background: var(--surface-hover); border-color: var(--blue); }
.cal-today-btn {
  padding: 6px 14px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-dim);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.cal-today-btn:hover { color: var(--blue); border-color: var(--blue); }

/* ---- MONTH VIEW ---- */
.month-view { display: none; }
.month-view.visible { display: block; }

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface);
}
.month-day-header {
  padding: 10px 4px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-dim);
  background: var(--bg);
  border-bottom: 1px solid var(--border);
}
.month-cell {
  min-height: 110px;
  padding: 6px;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  transition: background 0.15s;
  position: relative;
  overflow: hidden;
}
.month-cell:nth-child(7n) { border-right: none; }
.month-cell:hover { background: var(--surface-hover); }
.month-cell.other-month { opacity: 0.35; }
.month-cell.today {
  background: rgba(42, 147, 193, 0.06);
  box-shadow: inset 0 0 0 2px var(--blue);
}
.month-date {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-dim);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.month-cell.today .month-date {
  color: var(--blue);
}
.month-date-num {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.month-cell.today .month-date-num {
  background: var(--blue);
  color: #fff;
}
.month-card {
  padding: 4px 6px;
  margin-bottom: 3px;
  border-radius: 4px;
  font-size: 11px;
  line-height: 1.3;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-left: 3px solid transparent;
  background: var(--bg);
}
.month-card:hover {
  filter: brightness(1.2);
  transform: translateX(2px);
}
.month-card.type-blog { border-left-color: var(--blue); color: var(--blue); }
.month-card.type-linkedin { border-left-color: var(--orange); color: var(--orange); }
.month-card.type-newsletter { border-left-color: var(--green); color: var(--green); }
.month-card.type-bluesky { border-left-color: #6366f1; color: #818cf8; }
.month-card.type-other { border-left-color: var(--text-dim); color: var(--text-dim); }
.month-card-time {
  font-size: 9px;
  opacity: 0.7;
  font-weight: 600;
}
.month-card-status {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-left: 3px;
  vertical-align: middle;
}
.month-card-status.s-draft { background: var(--yellow); }
.month-card-status.s-approved { background: var(--blue); }
.month-card-status.s-posted { background: var(--green); }
.month-card-status.s-failed { background: var(--red); }
.month-overflow {
  font-size: 10px;
  color: var(--text-dim);
  padding: 2px 6px;
  cursor: pointer;
  font-weight: 600;
}
.month-overflow:hover { color: var(--blue); }

/* ---- WEEK VIEW ---- */
.week-view { display: none; }
.week-view.visible { display: block; }

.week-grid {
  display: grid;
  grid-template-columns: 80px repeat(7, 1fr);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface);
}
.week-header {
  padding: 12px 8px;
  text-align: center;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-dim);
}
.week-header:last-child { border-right: none; }
.week-header.today {
  color: var(--blue);
  background: rgba(42,147,193,0.08);
}
.week-header-date {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  line-height: 1;
  margin-top: 2px;
}
.week-header.today .week-header-date { color: var(--blue); }
.week-slot-label {
  padding: 10px 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-dim);
  background: var(--bg);
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  text-align: center;
  min-height: 80px;
}
.week-cell {
  padding: 6px;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  min-height: 80px;
  background: var(--surface);
  transition: background 0.15s;
}
.week-cell:nth-child(8n) { border-right: none; }
.week-cell:hover { background: var(--surface-hover); }
.week-post-chip {
  padding: 5px 8px;
  margin-bottom: 4px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.15s;
  border-left: 3px solid transparent;
  background: var(--bg);
  line-height: 1.3;
}
.week-post-chip:hover { filter: brightness(1.2); transform: translateX(2px); }
.week-post-chip.blog { border-left-color: var(--blue); color: var(--blue); }
.week-post-chip.linkedin { border-left-color: var(--orange); color: var(--orange); }
.week-post-chip.newsletter { border-left-color: var(--green); color: var(--green); }
.week-post-chip.bluesky { border-left-color: #6366f1; color: #818cf8; }
.week-post-chip.other { border-left-color: var(--text-dim); color: var(--text-dim); }

/* Week legend */
.week-legend {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  flex-wrap: wrap;
}
.week-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-dim);
}
.week-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

/* --- List view (already styled, ensure cal-list toggle works) --- */
#calendar-list { display: block; }

/* Responsive calendar */
@media (max-width: 900px) {
  .month-cell { min-height: 80px; }
  .month-card { font-size: 10px; padding: 3px 4px; }
  .week-grid { grid-template-columns: 60px repeat(7, 1fr); }
  .week-slot-label { font-size: 10px; padding: 6px 4px; }
  .week-post-chip { font-size: 10px; padding: 3px 5px; }
}
@media (max-width: 640px) {
  .month-grid { grid-template-columns: repeat(7, 1fr); }
  .month-cell { min-height: 60px; padding: 3px; }
  .month-card { display: none; }
  .month-date { font-size: 11px; }
  .month-cell.has-posts::after {
    content: '';
    display: block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--blue);
    margin: 4px auto 0;
  }
}

"""

    content = content.replace('</style>', calendar_css + '</style>')

    # =========================================================
    # 2. REPLACE the Calendar tab HTML (panel-calendar)
    # =========================================================
    old_calendar_panel = re.search(
        r'<!-- ={5,} TAB 2: CALENDAR ={5,} -->\s*<div class="tab-panel" id="panel-calendar">.*?</div>\s*(?=<!-- ={5,} TAB 3)',
        content, re.DOTALL
    )

    if not old_calendar_panel:
        print("ERROR: Could not find Calendar panel HTML to replace")
        sys.exit(1)

    new_calendar_panel = """<!-- ===================== TAB 2: CALENDAR ===================== -->
<div class="tab-panel" id="panel-calendar">
  <!-- View Toggle + Nav -->
  <div class="cal-nav">
    <div class="view-toggle">
      <button class="view-toggle-btn active" onclick="setCalendarView('month')">Month</button>
      <button class="view-toggle-btn" onclick="setCalendarView('week')">Week</button>
      <button class="view-toggle-btn" onclick="setCalendarView('list')">List</button>
    </div>
    <div class="cal-nav-center">
      <button class="cal-nav-btn" onclick="calNavPrev()" title="Previous">&lsaquo;</button>
      <span class="cal-nav-title" id="cal-nav-title"></span>
      <button class="cal-nav-btn" onclick="calNavNext()" title="Next">&rsaquo;</button>
      <button class="cal-today-btn" onclick="calNavToday()">Today</button>
    </div>
    <div style="display:flex;gap:8px;align-items:center;">
      <button class="btn btn-ghost btn-sm" onclick="refreshAllData()">Refresh</button>
    </div>
  </div>

  <!-- Month Calendar View (default) -->
  <div class="month-view visible" id="month-view">
    <div class="month-grid" id="month-grid"></div>
    <div class="week-legend" style="margin-top:8px;">
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--blue);"></div> Blog</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--orange);"></div> Standalone</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--green);"></div> Newsletter</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:#6366f1;"></div> Bluesky</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--text-dim);"></div> Other</div>
      <div style="margin-left:auto;display:flex;gap:10px;font-size:11px;color:var(--text-dim);">
        <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--yellow);vertical-align:middle;"></span> Draft</span>
        <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--blue);vertical-align:middle;"></span> Approved</span>
        <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);vertical-align:middle;"></span> Live</span>
        <span><span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--red);vertical-align:middle;"></span> Failed</span>
      </div>
    </div>
  </div>

  <!-- Weekly Calendar View -->
  <div class="week-view" id="week-view">
    <div class="week-grid" id="week-grid"></div>
    <div class="week-legend">
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--blue);"></div> Blog (8-9am ET)</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--orange);"></div> Standalone (1pm ET)</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--green);"></div> Newsletter</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:#6366f1;"></div> Bluesky</div>
      <div class="week-legend-item"><div class="week-legend-dot" style="background:var(--text-dim);"></div> Other</div>
    </div>
  </div>

  <!-- List View Filters -->
  <div class="filter-bar" id="list-filters" style="display:none;">
    <div class="form-group">
      <label class="form-label">Content Type</label>
      <select id="filter-content-type" onchange="renderCalendar()">
        <option value="all">All Types</option>
        <option value="blog">Blog</option>
        <option value="linkedin">Standalone Post</option>
        <option value="newsletter">Newsletter</option>
        <option value="bluesky">Bluesky</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Platform</label>
      <select id="filter-platform">
        <option value="all">All Platforms</option>
        <option value="instagram">Instagram</option>
        <option value="facebook">Facebook</option>
        <option value="linkedin">LinkedIn</option>
        <option value="twitter">X / Twitter</option>
        <option value="bluesky">Bluesky</option>
        <option value="tiktok">TikTok</option>
        <option value="reddit">Reddit</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Status</label>
      <select id="filter-status">
        <option value="all">All Status</option>
        <option value="draft">Draft</option>
        <option value="approved">Approved</option>
        <option value="posted">Posted</option>
        <option value="failed">Failed</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">Date</label>
      <input type="date" id="filter-date">
    </div>
    <div class="form-group" style="flex:0;">
      <label class="form-label">&nbsp;</label>
      <button class="btn btn-ghost" onclick="renderCalendar()">Filter</button>
    </div>
    <div class="form-group" style="flex:0;">
      <label class="form-label">&nbsp;</label>
      <button class="btn btn-primary btn-sm" onclick="refreshAllData()">Refresh</button>
    </div>
  </div>
  <div id="calendar-list" style="display:none;"></div>
</div>

"""

    content = content[:old_calendar_panel.start()] + new_calendar_panel + content[old_calendar_panel.end():]

    # =========================================================
    # 3. REPLACE the calendar JS (view toggle + week + add month)
    # =========================================================

    # Replace the calendarView default and weekOffset
    content = content.replace(
        "let calendarView = 'list';",
        "let calendarView = 'month';"
    )
    content = content.replace(
        "let weekOffset = 0;",
        "let weekOffset = 0;\nlet monthOffset = 0;"
    )

    # Replace setCalendarView function
    old_set_view = re.search(
        r'// ={5,} CALENDAR VIEW TOGGLE ={5,}\s*function setCalendarView\(view\)\s*\{.*?\}',
        content, re.DOTALL
    )
    if not old_set_view:
        # Try alternate pattern
        old_set_view = re.search(
            r'function setCalendarView\(view\)\s*\{.*?^\}',
            content, re.DOTALL | re.MULTILINE
        )

    if old_set_view:
        new_set_view = """// ========== CALENDAR VIEW TOGGLE ==========
function setCalendarView(view) {
  calendarView = view;
  document.querySelectorAll('.view-toggle-btn').forEach(b => {
    b.classList.toggle('active', b.textContent.trim().toLowerCase() === view);
  });
  const monthView = document.getElementById('month-view');
  const weekView = document.getElementById('week-view');
  const listFilters = document.getElementById('list-filters');
  const listView = document.getElementById('calendar-list');

  monthView.classList.remove('visible');
  weekView.classList.remove('visible');
  listFilters.style.display = 'none';
  listView.style.display = 'none';

  if (view === 'month') {
    monthView.classList.add('visible');
    renderMonthView();
  } else if (view === 'week') {
    weekView.classList.add('visible');
    renderWeekView();
  } else {
    listFilters.style.display = '';
    listView.style.display = '';
    renderCalendar();
  }
  updateCalNavTitle();
}"""
        content = content[:old_set_view.start()] + new_set_view + content[old_set_view.end():]

    # Replace weekNavPrev/weekNavNext
    content = content.replace(
        "function weekNavPrev() { weekOffset--; renderWeekView(); }",
        "function weekNavPrev() { weekOffset--; renderWeekView(); updateCalNavTitle(); }"
    )
    content = content.replace(
        "function weekNavNext() { weekOffset++; renderWeekView(); }",
        "function weekNavNext() { weekOffset++; renderWeekView(); updateCalNavTitle(); }"
    )

    # Insert new calendar navigation + month view code before renderWeekView
    week_view_marker = "// ========== WEEKLY CALENDAR VIEW =========="
    if week_view_marker not in content:
        week_view_marker = "function renderWeekView()"

    new_cal_code = """// ========== CALENDAR NAVIGATION ==========
function calNavPrev() {
  if (calendarView === 'month') { monthOffset--; renderMonthView(); }
  else if (calendarView === 'week') { weekOffset--; renderWeekView(); }
  updateCalNavTitle();
}
function calNavNext() {
  if (calendarView === 'month') { monthOffset++; renderMonthView(); }
  else if (calendarView === 'week') { weekOffset++; renderWeekView(); }
  updateCalNavTitle();
}
function calNavToday() {
  monthOffset = 0;
  weekOffset = 0;
  if (calendarView === 'month') renderMonthView();
  else if (calendarView === 'week') renderWeekView();
  updateCalNavTitle();
}
function updateCalNavTitle() {
  const el = document.getElementById('cal-nav-title');
  if (!el) return;
  const now = new Date();
  if (calendarView === 'month') {
    const d = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1);
    el.textContent = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  } else if (calendarView === 'week') {
    const monday = new Date(now);
    monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7) + (weekOffset * 7));
    const sunday = new Date(monday);
    sunday.setDate(sunday.getDate() + 6);
    const fmt = d => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    el.textContent = fmt(monday) + ' - ' + fmt(sunday) + ', ' + sunday.getFullYear();
  } else {
    el.textContent = 'All Scheduled Posts';
  }
}

// ========== MONTHLY CALENDAR VIEW ==========
function renderMonthView() {
  const grid = document.getElementById('month-grid');
  if (!grid) return;

  const posts = getCachedPosts();
  const now = new Date();
  const viewDate = new Date(now.getFullYear(), now.getMonth() + monthOffset, 1);
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // First day of month and last day
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // Start from Monday before (or on) the 1st
  const startDate = new Date(firstDay);
  const dayOfWeek = startDate.getDay();
  const diff = (dayOfWeek === 0) ? -6 : 1 - dayOfWeek;
  startDate.setDate(startDate.getDate() + diff);

  // End on Sunday after (or on) the last day
  const endDate = new Date(lastDay);
  const endDow = endDate.getDay();
  if (endDow !== 0) endDate.setDate(endDate.getDate() + (7 - endDow));

  // Build post lookup by date string
  const postsByDate = {};
  posts.forEach(p => {
    if (!p.scheduled_time) return;
    const dateStr = p.scheduled_time.split('T')[0];
    if (!postsByDate[dateStr]) postsByDate[dateStr] = [];
    postsByDate[dateStr].push(p);
  });

  let html = '';

  // Day headers (Mon-Sun)
  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  dayNames.forEach(d => {
    html += '<div class="month-day-header">' + d + '</div>';
  });

  // Cells
  const cursor = new Date(startDate);
  while (cursor <= endDate) {
    const dateStr = cursor.toISOString().split('T')[0];
    const isToday = cursor.getTime() === today.getTime();
    const isOtherMonth = cursor.getMonth() !== month;
    const dayPosts = postsByDate[dateStr] || [];
    const hasPosts = dayPosts.length > 0;

    let classes = 'month-cell';
    if (isToday) classes += ' today';
    if (isOtherMonth) classes += ' other-month';
    if (hasPosts) classes += ' has-posts';

    html += '<div class="' + classes + '">';
    html += '<div class="month-date"><span class="month-date-num">' + cursor.getDate() + '</span></div>';

    // Show up to 3 post cards per day
    const maxShow = 3;
    dayPosts.slice(0, maxShow).forEach(p => {
      const ct = p.content_type || 'linkedin';
      const typeClass = ['blog', 'linkedin', 'newsletter', 'bluesky'].includes(ct) ? ct : 'other';
      const label = p.title || (p.content || '').substring(0, 25);
      const time = p.scheduled_time ? new Date(p.scheduled_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true }) : '';
      const statusClass = 's-' + (p.status || 'draft');
      html += '<div class="month-card type-' + typeClass + '" onclick="scrollToPost(\\'' + p.id + '\\')" title="' + escapeAttr((p.title || '') + ' - ' + (p.content || '').substring(0, 100)) + '">';
      html += '<span class="month-card-time">' + escapeHtml(time) + '</span> ';
      html += escapeHtml(label);
      html += '<span class="month-card-status ' + statusClass + '"></span>';
      html += '</div>';
    });

    if (dayPosts.length > maxShow) {
      html += '<div class="month-overflow" onclick="showDayDetail(\\'' + dateStr + '\\'")">+' + (dayPosts.length - maxShow) + ' more</div>';
    }

    html += '</div>';
    cursor.setDate(cursor.getDate() + 1);
  }

  grid.innerHTML = html;
  updateCalNavTitle();
}

function showDayDetail(dateStr) {
  // Switch to list view filtered to this date
  document.getElementById('filter-date').value = dateStr;
  setCalendarView('list');
  renderCalendar();
}

function escapeAttr(str) {
  return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;');
}

"""

    content = content.replace(week_view_marker, new_cal_code + week_view_marker)

    # =========================================================
    # 4. Update init() to render month view by default
    # =========================================================
    # Replace the renderWeekView call in init with month view setup
    content = content.replace(
        "  renderCalendar();\n  renderApprovals();\n  renderWeekView();",
        "  renderCalendar();\n  renderApprovals();\n  renderMonthView();\n  updateCalNavTitle();"
    )

    # Also fix scrollToPost to switch to list view
    content = content.replace(
        "function scrollToPost(postId) {\n  setCalendarView('list');",
        "function scrollToPost(postId) {\n  setCalendarView('list');\n  renderCalendar();"
    )

    # Remove old nav label update in renderWeekView since we have updateCalNavTitle now
    # (keep it as fallback but it won't hurt)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"SUCCESS: Patched {filepath}")
    print("  - Added ~250 lines of calendar CSS")
    print("  - Replaced Calendar panel HTML (Month + Week + List views)")
    print("  - Added Month view renderer")
    print("  - Added calendar navigation (prev/next/today)")
    print("  - Default view: Month")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else '/var/www/puresurf/social.html'
    patch_social_html(filepath)
