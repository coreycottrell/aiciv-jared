// PureApex SPA HTML - auto-generated from index.html
// DO NOT EDIT - regenerate from source

export const HTML_PAGE = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PureApex</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-primary: #080C15;
    --bg-secondary: #0D1320;
    --bg-card: #151C2B;
    --bg-input: #1C2437;
    --bg-elevated: #243044;
    --border: #2D3748;
    --border-light: #374151;
    --text-primary: #E8ECF1;
    --text-secondary: #94A3B8;
    --text-muted: #5E6E82;
    --orange: #EE6624;
    --orange-hover: #D95A1E;
    --orange-wash: rgba(238,102,36,0.08);
    --blue: #0479C2;
    --blue-light: #60A5FA;
    --green: #34D399;
    --red: #FB7185;
    --amber: #FBBF24;
    --cyan: #22D3EE;
    --purple: #C084FC;
    --gray-badge: #6B7280;
    --radius: 8px;
    --radius-lg: 12px;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
}

/* --- Login Screen --- */
#login-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
}

.login-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 48px 40px;
    width: 100%;
    max-width: 400px;
}

.login-box h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
    color: var(--text-primary);
}

.login-box .brand {
    color: var(--orange);
    font-weight: 600;
}

.login-box .subtitle {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 32px;
}

.form-group {
    margin-bottom: 16px;
}

.form-group label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 6px;
}

.form-group input, .form-group select, .form-group textarea {
    width: 100%;
    padding: 10px 14px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
    border-color: var(--orange);
}

.form-group textarea { resize: vertical; min-height: 80px; }
.form-group select { cursor: pointer; }
.form-group select option { background: var(--bg-card); }

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: var(--radius);
    border: none;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s, opacity 0.2s;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary {
    background: var(--orange);
    color: #fff;
    width: 100%;
    padding: 12px;
    font-size: 15px;
}

.btn-primary:hover:not(:disabled) { background: var(--orange-hover); }

.btn-secondary {
    background: var(--bg-input);
    color: var(--text-primary);
    border: 1px solid var(--border);
}

.btn-secondary:hover:not(:disabled) { background: var(--border); }

.btn-sm { padding: 6px 14px; font-size: 13px; }

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border);
    padding: 6px 14px;
    font-size: 13px;
}

.btn-ghost:hover { border-color: var(--orange); color: var(--orange); }

.login-error {
    color: var(--red);
    font-size: 13px;
    margin-top: 12px;
    display: none;
}

/* --- Main App --- */
#app-screen { display: none; }

.header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header h1 {
    font-size: 18px;
    font-weight: 700;
}

.header .brand { color: var(--orange); }

.header-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.user-info {
    font-size: 13px;
    color: var(--text-secondary);
}

.user-info strong { color: var(--text-primary); }

.btn-logout {
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 6px 14px;
    border-radius: var(--radius);
    cursor: pointer;
    font-size: 13px;
}

.btn-logout:hover { border-color: var(--red); color: var(--red); }

/* --- Nav Tabs --- */
.nav-tabs {
    display: flex;
    gap: 0;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    position: sticky;
    top: 49px;
    z-index: 99;
}

.nav-tab {
    padding: 14px 24px 12px;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-muted);
    cursor: pointer;
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
    transition: color 0.2s, background 0.2s, border-color 0.2s;
    user-select: none;
    background: transparent;
}

.nav-tab:hover {
    color: var(--text-secondary);
    background: var(--orange-wash);
    border-bottom-color: rgba(238,102,36,0.3);
}

.nav-tab.active {
    color: #fff;
    background: var(--orange-wash);
    border-bottom-color: var(--orange);
}

.container { max-width: 1400px; margin: 0 auto; padding: 24px; }

/* --- Views --- */
.view { display: none; }
.view.active { display: block; }

/* --- Summary Bar --- */
.summary-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.summary-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
    border-left: 4px solid var(--border-light);
}

.summary-card:nth-child(1) { border-left-color: var(--orange); }
.summary-card:nth-child(2) { border-left-color: var(--blue-light); }
.summary-card:nth-child(3) { border-left-color: var(--green); }
.summary-card:nth-child(4) { border-left-color: var(--cyan); }
.summary-card:nth-child(5) { border-left-color: var(--purple); }

.summary-card:hover { background: var(--bg-elevated); transition: background 0.2s; }

.summary-card .label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 8px;
}

.summary-card .value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
}

.summary-card .value.orange { color: var(--orange); }
.summary-card .value.green { color: var(--green); }
.summary-card .value.blue { color: var(--blue-light); }

.summary-card .sub {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* --- Pipeline Bar --- */
.pipeline-bar-container {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 24px;
}

.pipeline-bar-container h3 {
    font-size: 15px;
    color: var(--text-primary);
    margin-bottom: 12px;
    font-weight: 600;
    padding-left: 10px;
    border-left: 3px solid var(--orange);
}

.pipeline-bar {
    display: flex;
    height: 32px;
    border-radius: 6px;
    overflow: hidden;
    background: var(--bg-input);
}

.pipeline-bar .segment {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    min-width: 2px;
    transition: width 0.3s;
}

.pipeline-bar-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 12px;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-primary);
}

.legend-item .legend-value {
    font-weight: 600;
}

.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* --- Dashboard: Pipeline by Type / Owner --- */
.dash-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}

.dash-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
}

.dash-panel h3 {
    font-size: 15px;
    color: var(--text-primary);
    margin-bottom: 16px;
    font-weight: 600;
    padding-left: 10px;
    border-left: 3px solid var(--blue-light);
}

.mini-card-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.mini-card {
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
    min-width: 120px;
    flex: 1;
}

.mini-card .mc-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
}

.mini-card .mc-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--orange);
}

.mini-card .mc-sub {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 2px;
}

/* --- Filter Bar --- */
.filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: flex-end;
    margin-bottom: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 16px 20px;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.filter-group label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
}

.filter-group select, .filter-group input {
    padding: 7px 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 13px;
    outline: none;
    min-width: 140px;
}

.filter-group select:focus, .filter-group input:focus {
    border-color: var(--orange);
}

.filter-group select option { background: var(--bg-card); }

.filter-actions {
    display: flex;
    gap: 8px;
    align-items: flex-end;
    margin-left: auto;
}

/* --- Opportunities Table --- */
.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.table-header h2 {
    font-size: 19px;
    font-weight: 700;
    padding-left: 10px;
    border-left: 3px solid var(--orange);
}

.table-wrapper {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.opp-table {
    width: 100%;
    border-collapse: collapse;
}

.opp-table th {
    text-align: left;
    padding: 12px 16px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
}

.opp-table th:hover { color: var(--text-secondary); }
.opp-table th .sort-arrow { margin-left: 4px; opacity: 0.5; }
.opp-table th.sorted .sort-arrow { opacity: 1; color: var(--orange); }

.opp-table td {
    padding: 12px 16px;
    font-size: 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);
}

.opp-table tr:last-child td { border-bottom: none; }

.opp-table tbody tr:nth-child(even) td {
    background: rgba(255,255,255,0.02);
}

.opp-table tr:hover td {
    background: rgba(238, 102, 36, 0.08);
    cursor: pointer;
}

.opp-table .company-cell {
    color: var(--text-primary);
    font-weight: 500;
}

.opp-table .value-cell {
    color: #E8ECF1;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

/* Stage badges */
.stage-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
}

.stage-Suspect { background: rgba(148,163,184,0.15); color: #94A3B8; }
.stage-Pipeline { background: rgba(96,165,250,0.15); color: #60A5FA; }
.stage-Qualified { background: rgba(45,212,191,0.15); color: #2DD4BF; }
.stage-Proposal-Submitted { background: rgba(245,158,11,0.15); color: #F59E0B; }
.stage-Proposal-Finalised { background: rgba(251,146,60,0.15); color: #FB923C; }
.stage-Sponsor-Commitment { background: rgba(244,114,182,0.15); color: #F472B6; }
.stage-Proposal-Accepted { background: rgba(163,230,53,0.15); color: #A3E635; }
.stage-Closed-Won { background: rgba(52,211,153,0.15); color: #34D399; }
.stage-Closed-Lost { background: rgba(251,113,133,0.15); color: #FB7185; }

.type-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    background: rgba(4,121,194,0.15);
    color: var(--blue-light);
}

/* --- Modal --- */
.modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 1000;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.modal-overlay.active { display: flex; }

.modal {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 700px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border);
}

.modal-header h2 { font-size: 18px; font-weight: 600; }

.modal-close {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 24px;
    cursor: pointer;
    padding: 4px;
    line-height: 1;
}

.modal-close:hover { color: var(--text-primary); }

.modal-body { padding: 24px; }

.modal-body .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.modal-body .form-row.three { grid-template-columns: 1fr 1fr 1fr; }
.modal-body .form-row.full { grid-template-columns: 1fr; }

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px;
    border-top: 1px solid var(--border);
}

/* --- Collapsible section in modal --- */
.collapsible-section {
    border-top: 1px solid var(--border);
    margin-top: 16px;
    padding-top: 12px;
}

.collapsible-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    user-select: none;
    padding: 4px 0;
}

.collapsible-toggle h3 {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
    margin: 0;
}

.collapsible-toggle .toggle-icon {
    font-size: 12px;
    color: var(--text-muted);
    transition: transform 0.2s;
}

.collapsible-toggle .toggle-icon.open { transform: rotate(180deg); }

.collapsible-body {
    display: none;
    margin-top: 12px;
}

.collapsible-body.open { display: block; }

/* --- Activity Log in modal --- */
.activity-list {
    margin-top: 16px;
    border-top: 1px solid var(--border);
    padding-top: 16px;
}

.activity-list h3 {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 12px;
}

.activity-item {
    display: flex;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(45,55,72,0.5);
    font-size: 13px;
}

.activity-item:last-child { border-bottom: none; }

.activity-item .actor {
    color: var(--orange);
    font-weight: 500;
    white-space: nowrap;
    min-width: 100px;
}

.activity-item .action { color: var(--text-secondary); flex: 1; }

.activity-item .time {
    color: var(--text-muted);
    font-size: 12px;
    white-space: nowrap;
}

/* --- Recent Activity panel --- */
.activity-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-top: 24px;
}

.activity-panel h3 {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--text-primary);
    padding-left: 10px;
    border-left: 3px solid var(--purple);
}

/* --- Stage Definitions Panel --- */
.stage-defs-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 24px;
}

.stage-defs-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    user-select: none;
}

.stage-defs-toggle h3 {
    font-size: 15px;
    color: var(--text-primary);
    font-weight: 600;
    margin: 0;
}

.stage-defs-toggle .toggle-arrow {
    font-size: 12px;
    color: var(--text-muted);
    transition: transform 0.2s;
}

.stage-defs-toggle .toggle-arrow.open { transform: rotate(180deg); }

.stage-defs-body {
    display: none;
    margin-top: 16px;
}

.stage-defs-body.open { display: block; }

.stage-def-row {
    display: grid;
    grid-template-columns: 180px 1fr 1fr;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    align-items: start;
}

.stage-def-row:last-child { border-bottom: none; }

.stage-def-row .def-stage {
    font-weight: 600;
    font-size: 13px;
}

.stage-def-row .def-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.stage-def-row .def-criteria {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.5;
}

.stage-def-row .def-criteria strong {
    color: var(--text-secondary);
}

/* --- Accounts View --- */
.accounts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 16px;
}

.account-card {
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
    border-left: 4px solid var(--blue);
}

.account-card:hover {
    border-color: var(--orange);
    border-left-color: var(--orange);
    box-shadow: 0 2px 12px rgba(238,102,36,0.1);
}

.account-card.expanded {
    border-color: var(--orange);
    border-left-color: var(--orange);
    grid-column: 1 / -1;
    box-shadow: 0 4px 20px rgba(238,102,36,0.12);
}

.account-card .ac-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.account-card .ac-company {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
}

.account-card .ac-deal-count {
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
}

.account-card .ac-stats {
    display: flex;
    gap: 20px;
    margin-bottom: 8px;
}

.account-card .ac-stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.account-card .ac-stat-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--orange);
}

.account-card .ac-contacts {
    margin-top: 16px;
    border-top: 1px solid var(--border);
    padding-top: 12px;
}

.ac-contact-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(45,55,72,0.4);
    font-size: 13px;
}

.ac-contact-row:last-child { border-bottom: none; }

.ac-contact-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.ac-contact-name {
    color: var(--text-primary);
    font-weight: 500;
}

.ac-contact-title {
    color: var(--text-muted);
    font-size: 12px;
}

.ac-contact-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ac-contact-value {
    color: var(--green);
    font-weight: 600;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
}

.ac-view-deal {
    color: var(--orange);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    white-space: nowrap;
}

.ac-view-deal:hover { text-decoration: underline; }

/* --- Deal Detail View --- */
.deal-detail {
    max-width: 1200px;
}

.deal-detail-top {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}

.deal-detail-top .back-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: 6px 14px;
    border-radius: var(--radius);
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: border-color 0.2s, color 0.2s;
}

.deal-detail-top .back-btn:hover { border-color: var(--orange); color: var(--orange); }

.deal-detail-top .dd-company {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
}

.deal-detail-top .dd-actions {
    margin-left: auto;
    display: flex;
    gap: 8px;
}

.deal-columns {
    display: grid;
    grid-template-columns: 3fr 2fr;
    gap: 24px;
    align-items: start;
}

.deal-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.deal-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--orange);
}

.deal-field-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.deal-field {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.deal-field .df-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.deal-field .df-value {
    font-size: 14px;
    color: var(--text-primary);
}

.deal-field .df-value a {
    color: var(--blue-light);
    text-decoration: none;
}

.deal-field .df-value a:hover { text-decoration: underline; }

/* --- Deal Qualification --- */
.meddpicc-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.meddpicc-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--amber);
}

.meddpicc-field {
    margin-bottom: 14px;
}

.meddpicc-field:last-of-type { margin-bottom: 0; }

.meddpicc-field label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.meddpicc-field textarea {
    width: 100%;
    padding: 8px 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    resize: vertical;
    min-height: 48px;
    outline: none;
    transition: border-color 0.2s;
}

.meddpicc-field textarea:focus {
    border-color: var(--orange);
}

.meddpicc-save-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
}

/* --- Stage Progress (vertical) --- */
.stage-progress {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.stage-progress h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--green);
}

.sp-list {
    display: flex;
    flex-direction: column;
    gap: 0;
}

.sp-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    position: relative;
}

.sp-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid var(--border);
    background: var(--bg-input);
    flex-shrink: 0;
    position: relative;
    z-index: 2;
}

.sp-item.completed .sp-dot {
    background: var(--green);
    border-color: var(--green);
}

.sp-item.current .sp-dot {
    background: var(--orange);
    border-color: var(--orange);
    box-shadow: 0 0 0 3px rgba(238,102,36,0.3);
}

.sp-item.future .sp-dot {
    background: var(--bg-input);
    border-color: var(--border);
}

.sp-label {
    font-size: 13px;
    color: var(--text-muted);
}

.sp-item.completed .sp-label { color: var(--text-secondary); }
.sp-item.current .sp-label { color: var(--orange); font-weight: 600; }

.sp-line {
    width: 2px;
    height: 16px;
    background: var(--border);
    margin-left: 6px;
}

.sp-line.completed { background: var(--green); }

/* --- Next Action Card --- */
.next-action-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.next-action-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--cyan);
}

.next-action-text {
    font-size: 14px;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.next-action-date {
    font-size: 12px;
    color: var(--text-muted);
}

/* --- Meeting Notes --- */
.notes-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.notes-section h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--blue-light);
}

.note-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
}

.note-form-row {
    display: flex;
    gap: 8px;
    align-items: flex-end;
}

.note-form select {
    padding: 7px 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 13px;
    outline: none;
    min-width: 120px;
}

.note-form select:focus { border-color: var(--orange); }
.note-form select option { background: var(--bg-card); }

.note-form textarea {
    width: 100%;
    padding: 8px 12px;
    background: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
    outline: none;
}

.note-form textarea:focus { border-color: var(--orange); }

.note-item {
    padding: 12px 0;
    border-bottom: 1px solid rgba(45,55,72,0.5);
}

.note-item:last-child { border-bottom: none; }

.note-item-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}

.note-type-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}

.note-type-meeting { background: rgba(168,85,247,0.15); color: #C084FC; }
.note-type-call { background: rgba(34,197,94,0.15); color: #4ADE80; }
.note-type-email { background: rgba(59,130,246,0.15); color: #60A5FA; }
.note-type-general { background: rgba(107,114,128,0.15); color: #9CA3AF; }

.note-actor {
    font-size: 12px;
    font-weight: 500;
    color: var(--orange);
}

.note-time {
    font-size: 12px;
    color: var(--text-muted);
    margin-left: auto;
}

.note-content {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    white-space: pre-wrap;
}

/* --- Empty state --- */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-muted);
}

.empty-state .icon { font-size: 48px; margin-bottom: 12px; }
.empty-state p { font-size: 15px; }

/* --- Responsive --- */
@media (max-width: 1024px) {
    .deal-columns { grid-template-columns: 1fr; }
    .dash-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
    .summary-bar { grid-template-columns: 1fr 1fr; }
    .filter-bar { flex-direction: column; }
    .filter-actions { margin-left: 0; width: 100%; }
    .filter-actions .btn { flex: 1; }
    .modal-body .form-row { grid-template-columns: 1fr; }
    .modal-body .form-row.three { grid-template-columns: 1fr; }
    .header { flex-direction: column; gap: 8px; }
    .header-right { width: 100%; justify-content: space-between; }
    .nav-tabs { padding: 6px 12px; overflow-x: auto; }
    .nav-tab { padding: 8px 16px; font-size: 14px; white-space: nowrap; }

    .table-wrapper { overflow-x: auto; }
    .opp-table { min-width: 800px; }

    .stage-def-row {
        grid-template-columns: 1fr;
        gap: 4px;
    }

    .accounts-grid { grid-template-columns: 1fr; }
    .deal-field-grid { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
    .summary-bar { grid-template-columns: 1fr; }
    .container { padding: 12px; }
    .login-box { padding: 32px 24px; }
}

/* --- Emotional Arc Tracker --- */
.emotional-arc-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.emotional-arc-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--purple);
}

.ea-track {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 12px;
}

.ea-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    cursor: pointer;
    padding: 4px 2px;
}

.ea-dot {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid var(--border);
    background: var(--bg-input);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    transition: all 0.2s;
    position: relative;
    z-index: 2;
}

.ea-step:hover .ea-dot {
    border-color: var(--text-secondary);
    color: var(--text-secondary);
}

.ea-step.reached .ea-dot {
    border-color: transparent;
    color: #fff;
}

.ea-step[data-stage="Curious"].reached .ea-dot { background: #6B7280; border-color: #6B7280; }
.ea-step[data-stage="Aware"].reached .ea-dot { background: #F59E0B; border-color: #F59E0B; }
.ea-step[data-stage="FOMO"].reached .ea-dot { background: #EA580C; border-color: #EA580C; }
.ea-step[data-stage="Excited"].reached .ea-dot { background: #22C55E; border-color: #22C55E; }
.ea-step[data-stage="Committed"].reached .ea-dot { background: #16A34A; border-color: #16A34A; }

.ea-step.active .ea-dot {
    box-shadow: 0 0 0 3px rgba(168,85,247,0.3);
}

.ea-label {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 6px;
    text-align: center;
    white-space: nowrap;
}

.ea-step.reached .ea-label { color: var(--text-secondary); font-weight: 500; }
.ea-step.active .ea-label { color: var(--purple); font-weight: 600; }

.ea-connector {
    flex: 0 0 auto;
    width: 24px;
    height: 2px;
    background: var(--border);
    margin-top: -16px;
}

.ea-connector.reached { background: var(--green); }

.ea-note {
    font-size: 12px;
    color: var(--text-muted);
    font-style: italic;
    line-height: 1.5;
    padding: 8px 0 0 0;
    border-top: 1px solid var(--border);
}

/* Tooltip for emotional arc */
.ea-step .ea-tooltip {
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius);
    padding: 8px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    white-space: nowrap;
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.ea-step:hover .ea-tooltip { display: block; }

/* --- Readiness Check Card --- */
.readiness-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.readiness-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding-left: 10px;
    border-left: 3px solid var(--orange);
}

.readiness-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    cursor: pointer;
    user-select: none;
}

.readiness-item:hover {
    opacity: 0.85;
}

.readiness-checkbox {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid var(--border-light);
    background: var(--bg-input);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.15s;
    font-size: 12px;
    color: transparent;
}

.readiness-item.checked .readiness-checkbox {
    background: var(--green);
    border-color: var(--green);
    color: #fff;
}

.readiness-label {
    font-size: 13px;
    color: var(--text-secondary);
}

.readiness-item.checked .readiness-label {
    color: var(--text-primary);
}

.readiness-status {
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 13px;
    font-weight: 600;
}

.readiness-status.ready {
    color: var(--green);
}

.readiness-status.not-ready {
    color: var(--amber);
}

/* --- Stage Timer --- */
.stage-timer {
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 13px;
}

.stage-timer-value {
    color: var(--text-muted);
}

.stage-timer-value.amber {
    color: var(--amber);
    font-weight: 500;
}

.stage-timer-value.red {
    color: var(--red);
    font-weight: 600;
}

.stage-timer-note {
    margin-top: 6px;
    font-size: 12px;
    color: var(--amber);
    font-weight: 500;
}

/* --- Silence Card --- */
.silence-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--text-muted);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 16px;
}

.silence-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.silence-card .silence-elapsed {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 6px;
}

.silence-card .silence-next {
    font-size: 13px;
    color: var(--amber);
    font-weight: 500;
    margin-bottom: 8px;
}

.silence-card .silence-note {
    font-size: 12px;
    color: var(--text-muted);
    font-style: italic;
    line-height: 1.5;
}

/* --- Playbook Weapon Popup --- */
.pw-clickable {
    cursor: pointer;
    text-decoration: underline;
    text-decoration-style: dotted;
    text-underline-offset: 3px;
}

.pw-clickable:hover {
    color: var(--orange);
}

.pw-popup {
    display: none;
    position: fixed;
    z-index: 2000;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 16px 20px;
    max-width: 400px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

.pw-popup.active { display: block; }

.pw-popup h4 {
    font-size: 14px;
    font-weight: 600;
    color: var(--orange);
    margin-bottom: 8px;
}

.pw-popup p {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin: 0;
}

.pw-popup-close {
    position: absolute;
    top: 8px;
    right: 12px;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 18px;
    cursor: pointer;
    line-height: 1;
}

.pw-popup-close:hover { color: var(--text-primary); }

/* Playbook info icon in modal */
.pw-info-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: none;
    font-size: 11px;
    font-weight: 700;
    font-style: normal;
    color: #fff;
    background: var(--orange);
    cursor: pointer;
    margin-left: 6px;
    vertical-align: middle;
    transition: transform 0.2s, box-shadow 0.2s;
}

@keyframes pw-icon-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(238,102,36,0.4); }
    50% { box-shadow: 0 0 0 5px rgba(238,102,36,0); }
}

.pw-info-icon:hover {
    transform: scale(1.15);
    box-shadow: 0 0 8px rgba(238,102,36,0.5), 0 0 16px rgba(238,102,36,0.25);
    animation: pw-icon-pulse 1.5s ease-in-out infinite;
}

.pw-all-defs {
    display: none;
    position: fixed;
    z-index: 2000;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    padding: 20px 24px;
    max-width: 520px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

.pw-all-defs.active { display: block; }

.pw-all-defs h4 {
    font-size: 15px;
    font-weight: 600;
    color: var(--orange);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

.pw-def-item {
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(45,55,72,0.4);
}

.pw-def-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }

.pw-def-item strong {
    display: block;
    font-size: 13px;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.pw-def-item span {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* --- Playbook Weapons Reference Panel (Dashboard) --- */
.pw-ref-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    margin-bottom: 24px;
}

.pw-ref-toggle {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    user-select: none;
}

.pw-ref-toggle h3 {
    font-size: 15px;
    color: var(--text-primary);
    font-weight: 600;
    margin: 0;
    padding-left: 10px;
    border-left: 3px solid var(--orange);
}

.pw-ref-toggle .toggle-arrow {
    font-size: 12px;
    color: var(--text-muted);
    transition: transform 0.2s;
}

.pw-ref-toggle .toggle-arrow.open { transform: rotate(180deg); }

.pw-ref-body {
    display: none;
    margin-top: 16px;
}

.pw-ref-body.open { display: block; }

.pw-ref-row {
    display: flex;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
    align-items: baseline;
}

.pw-ref-row:last-child { border-bottom: none; }

.pw-ref-row .pw-ref-bullet {
    flex-shrink: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--orange);
    margin-top: 5px;
}

.pw-ref-row .pw-ref-name {
    flex-shrink: 0;
    min-width: 130px;
    font-weight: 600;
    font-size: 13px;
    color: var(--orange);
}

.pw-ref-row .pw-ref-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
}
</style>
</head>
<body>

<!-- LOGIN SCREEN -->
<div id="login-screen">
    <div class="login-box">
        <h1><span class="brand">PT</span> Pipeline</h1>
        <p class="subtitle">Pure Technology Sales CRM</p>
        <form id="login-form">
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="login-username" placeholder="e.g. jsmith" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="login-password" placeholder="Enter password" autocomplete="current-password" required>
            </div>
            <button type="submit" class="btn btn-primary" id="login-btn">Sign In</button>
            <p class="login-error" id="login-error"></p>
        </form>
    </div>
</div>

<!-- APP SCREEN -->
<div id="app-screen">
    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <h1><span class="brand">Pure</span>Apex</h1>
        </div>
        <div class="header-right">
            <span class="user-info">Signed in as <strong id="user-display"></strong> <span id="user-role" style="color:var(--text-muted)"></span></span>
            <button class="btn-logout" onclick="doLogout()">Sign Out</button>
        </div>
    </div>

    <!-- Tab Navigation -->
    <div class="nav-tabs" id="nav-tabs">
        <button class="nav-tab active" data-view="dashboard" onclick="switchView('dashboard')">Dashboard</button>
        <button class="nav-tab" data-view="pipeline" onclick="switchView('pipeline')">Pipeline</button>
        <button class="nav-tab" data-view="accounts" onclick="switchView('accounts')">Companies</button>
    </div>

    <div class="container">
        <!-- ============ DASHBOARD VIEW ============ -->
        <div class="view active" id="view-dashboard">
            <!-- Summary Cards -->
            <div class="summary-bar" id="summary-bar"></div>

            <!-- Pipeline Bar -->
            <div class="pipeline-bar-container">
                <h3>Pipeline by Stage (Estimated Value)</h3>
                <div class="pipeline-bar" id="pipeline-bar"></div>
                <div class="pipeline-bar-legend" id="pipeline-legend"></div>
            </div>

            <!-- Pipeline by Type and Owner -->
            <div class="dash-grid">
                <div class="dash-panel">
                    <h3>Pipeline by Type</h3>
                    <div class="mini-card-grid" id="dash-by-type"></div>
                </div>
                <div class="dash-panel">
                    <h3>Pipeline by Owner</h3>
                    <div class="mini-card-grid" id="dash-by-owner"></div>
                </div>
            </div>

            <!-- Stage Definitions -->
            <div class="stage-defs-container">
                <div class="stage-defs-toggle" onclick="toggleStageDefs()">
                    <h3>Stage Definitions & Transition Criteria</h3>
                    <span class="toggle-arrow" id="stage-defs-arrow">&#9660;</span>
                </div>
                <div class="stage-defs-body" id="stage-defs-body">
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Suspect">Suspect (0%)</span></div>
                        <div class="def-desc">Target identified but not yet engaged.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Pipeline:</strong> Account matches ICP, identifiable business pain, commercial insight available, trigger event present.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Pipeline">Pipeline (5%)</span></div>
                        <div class="def-desc">Prospect expressed interest and agreed to meet.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Qualified:</strong> Real confirmed business problem, decision maker engaged, urgency/timeline exists, engagement reason understood.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Qualified">Qualified (15%)</span></div>
                        <div class="def-desc">Pain confirmed, decision makers mapped, budget verified.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Proposal Submitted:</strong> Pain confirmed in Economic Buyer's language, budget confirmed, all decision makers mapped, champion identified and tested, competitive landscape understood.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Proposal-Submitted">Proposal Submitted (40%)</span></div>
                        <div class="def-desc">Pain chain complete, champion active, proposal delivered.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Proposal Finalised:</strong> Client responded substantively, champion active, internal approval process mapped, legal/IT/finance stakeholders identified.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Proposal-Finalised">Proposal Finalised (60%)</span></div>
                        <div class="def-desc">Client engaged substantively, final version agreed internally.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Sponsor Commitment:</strong> Preferred vendor confirmed in writing, legal/procurement processing, commercial terms agreed, target signature date owned by client.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Sponsor-Commitment">Sponsor Commitment (80%)</span></div>
                        <div class="def-desc">Preferred vendor confirmed, legal and procurement engaged.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Proposal Accepted:</strong> Contract signed, PO or equivalent received.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Proposal-Accepted">Proposal Accepted (90%)</span></div>
                        <div class="def-desc">Contract signed, PO issued.</div>
                        <div class="def-criteria"><strong>Exit &rarr; Closed Won:</strong> Kick-off scheduled, success metrics agreed, internal handover complete.</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Closed-Won">Closed Won (100%)</span></div>
                        <div class="def-desc">Deal complete, partnership begins.</div>
                        <div class="def-criteria">&mdash;</div>
                    </div>
                    <div class="stage-def-row">
                        <div class="def-stage"><span class="stage-badge stage-Closed-Lost">Closed Lost</span></div>
                        <div class="def-desc">Dead for now. Declined, went dark, or chose competitor.</div>
                        <div class="def-criteria">&mdash;</div>
                    </div>
                </div>
            </div>

            <!-- Playbook Weapons Reference -->
            <div class="pw-ref-container">
                <div class="pw-ref-toggle" onclick="togglePlaybookRef()">
                    <h3>Playbook Weapons</h3>
                    <span class="toggle-arrow" id="pw-ref-arrow">&#9660;</span>
                </div>
                <div class="pw-ref-body" id="pw-ref-body">
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Reverse Demo</div>
                        <div class="pw-ref-desc">Instead of showing what we can do, we ask the prospect to show us their current process. Reveals pain points they didn't know they had.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Proof Packet</div>
                        <div class="pw-ref-desc">A curated bundle of case studies, velocity data, and ROI evidence tailored to the prospect's specific category and challenges.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Content Sniper</div>
                        <div class="pw-ref-desc">Targeted thought leadership content that addresses the prospect's exact pain point, delivered before they ask for it.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Alliance</div>
                        <div class="pw-ref-desc">Strategic partnership positioning where we bring complementary capabilities to the table, making the deal larger than either party alone.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">48hr Challenge</div>
                        <div class="pw-ref-desc">A time-boxed proof of concept where we demonstrate tangible results within 48 hours, removing the "what if" objection.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">FOMO</div>
                        <div class="pw-ref-desc">Evidence that competitors or peers are already moving, creating urgency through market intelligence rather than artificial pressure.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Live Event</div>
                        <div class="pw-ref-desc">In-person or virtual activation that lets the prospect experience the value firsthand rather than hearing about it.</div>
                    </div>
                    <div class="pw-ref-row">
                        <div class="pw-ref-bullet"></div>
                        <div class="pw-ref-name">Sales Process</div>
                        <div class="pw-ref-desc">Our structured methodology itself becomes the differentiator, showing the prospect a level of rigour their other vendors can't match.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ============ PIPELINE VIEW ============ -->
        <div class="view" id="view-pipeline">
            <!-- Filter Bar -->
            <div class="filter-bar">
                <div class="filter-group">
                    <label>Owner</label>
                    <select id="filter-owner"><option value="">All</option></select>
                </div>
                <div class="filter-group">
                    <label>Type</label>
                    <select id="filter-type">
                        <option value="">All</option>
                        <option value="CPG">CPG</option>
                        <option value="Gaming">Gaming</option>
                        <option value="Enterprise">Enterprise</option>
                        <option value="PureBrain">PureBrain</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Geography</label>
                    <select id="filter-geography">
                        <option value="">All</option>
                        <option value="NA">NA</option>
                        <option value="EMEA">EMEA</option>
                        <option value="APAC">APAC</option>
                        <option value="MENA">MENA</option>
                        <option value="LATAM">LATAM</option>
                        <option value="Global">Global</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Stage</label>
                    <select id="filter-stage">
                        <option value="">All</option>
                        <option value="Suspect">Suspect</option>
                        <option value="Pipeline">Pipeline</option>
                        <option value="Qualified">Qualified</option>
                        <option value="Proposal Submitted">Proposal Submitted</option>
                        <option value="Proposal Finalised">Proposal Finalised</option>
                        <option value="Sponsor Commitment">Sponsor Commitment</option>
                        <option value="Proposal Accepted">Proposal Accepted</option>
                        <option value="Closed Won">Closed Won</option>
                        <option value="Closed Lost">Closed Lost</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Vertical</label>
                    <input type="text" id="filter-vertical" placeholder="e.g. snacks">
                </div>
                <div class="filter-actions">
                    <button class="btn btn-secondary btn-sm" onclick="clearFilters()">Clear</button>
                    <button class="btn btn-primary btn-sm" style="width:auto" onclick="loadOpportunities()">Apply</button>
                </div>
            </div>

            <!-- Table Header -->
            <div class="table-header">
                <h2>Opportunities</h2>
                <button class="btn btn-primary btn-sm" style="width:auto" onclick="openCreateModal()">+ New Opportunity</button>
            </div>

            <!-- Opportunities Table -->
            <div class="table-wrapper">
                <table class="opp-table" id="opp-table">
                    <thead>
                        <tr>
                            <th data-sort="company">Company <span class="sort-arrow">&#9650;</span></th>
                            <th data-sort="stage">Stage <span class="sort-arrow">&#9650;</span></th>
                            <th data-sort="type">Type <span class="sort-arrow">&#9650;</span></th>
                            <th data-sort="owner">Owner <span class="sort-arrow">&#9650;</span></th>
                            <th data-sort="estimated_value">Value <span class="sort-arrow">&#9650;</span></th>
                            <th data-sort="geography">Geo <span class="sort-arrow">&#9650;</span></th>
                            <th>Next Action</th>
                            <th data-sort="updated_at">Updated <span class="sort-arrow">&#9650;</span></th>
                        </tr>
                    </thead>
                    <tbody id="opp-tbody"></tbody>
                </table>
                <div class="empty-state" id="empty-state" style="display:none">
                    <div class="icon">&#128200;</div>
                    <p>No opportunities found. Add your first deal to get started.</p>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="activity-panel">
                <h3>Recent Activity</h3>
                <div id="activity-feed"></div>
            </div>
        </div>

        <!-- ============ COMPANIES VIEW ============ -->
        <div class="view" id="view-accounts">
            <div class="table-header" style="margin-bottom:20px">
                <h2>Companies</h2>
                <input type="text" id="company-search" placeholder="Search companies..." oninput="filterCompanies()" style="padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:var(--bg-card);color:var(--text-primary);font-size:14px;width:260px;outline:none">
            </div>
            <div class="accounts-grid" id="accounts-grid"></div>
        </div>

        <!-- ============ DEAL DETAIL VIEW ============ -->
        <div class="view" id="view-deal-detail">
            <div class="deal-detail" id="deal-detail-content"></div>
        </div>
    </div>
</div>

<!-- Create/Edit Modal -->
<div class="modal-overlay" id="opp-modal">
    <div class="modal">
        <div class="modal-header">
            <h2 id="modal-title">New Opportunity</h2>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-body">
            <input type="hidden" id="opp-id">
            <div class="form-row">
                <div class="form-group">
                    <label>Company *</label>
                    <input type="text" id="opp-company" required>
                </div>
                <div class="form-group">
                    <label>Owner</label>
                    <select id="opp-owner"></select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Division / Sub-brand</label>
                    <input type="text" id="opp-division" placeholder="e.g. Sports Marketing, Pampers">
                </div>
                <div class="form-group"></div>
            </div>
            <div class="form-row three">
                <div class="form-group">
                    <label>Contact Name</label>
                    <input type="text" id="opp-contact-name">
                </div>
                <div class="form-group">
                    <label>Contact Title</label>
                    <input type="text" id="opp-contact-title">
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" id="opp-contact-email">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Contact LinkedIn</label>
                    <input type="url" id="opp-contact-linkedin" placeholder="https://linkedin.com/in/...">
                </div>
                <div class="form-group">
                    <label>Contact Location</label>
                    <input type="text" id="opp-contact-location" placeholder="e.g. New York, NY">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Estimated Value ($)</label>
                    <input type="number" id="opp-value" min="0" step="1000" value="0">
                </div>
                <div class="form-group"></div>
            </div>
            <div class="form-row three">
                <div class="form-group">
                    <label>Type</label>
                    <select id="opp-type">
                        <option value="">-- Select --</option>
                        <option value="CPG">CPG</option>
                        <option value="Gaming">Gaming</option>
                        <option value="Enterprise">Enterprise</option>
                        <option value="PureBrain">PureBrain</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Geography</label>
                    <select id="opp-geography">
                        <option value="">-- Select --</option>
                        <option value="NA">NA</option>
                        <option value="EMEA">EMEA</option>
                        <option value="APAC">APAC</option>
                        <option value="MENA">MENA</option>
                        <option value="LATAM">LATAM</option>
                        <option value="Global">Global</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Stage</label>
                    <select id="opp-stage">
                        <option value="Suspect">Suspect</option>
                        <option value="Pipeline">Pipeline</option>
                        <option value="Qualified">Qualified</option>
                        <option value="Proposal Submitted">Proposal Submitted</option>
                        <option value="Proposal Finalised">Proposal Finalised</option>
                        <option value="Sponsor Commitment">Sponsor Commitment</option>
                        <option value="Proposal Accepted">Proposal Accepted</option>
                        <option value="Closed Won">Closed Won</option>
                        <option value="Closed Lost">Closed Lost</option>
                    </select>
                </div>
            </div>
            <div class="form-row three">
                <div class="form-group">
                    <label>Vertical</label>
                    <input type="text" id="opp-vertical" placeholder="e.g. snacks, beverage, esports">
                </div>
                <div class="form-group">
                    <label>Partner</label>
                    <input type="text" id="opp-partner" placeholder="e.g. GamePlan Studio, agency name">
                </div>
                <div class="form-group">
                    <label>Playbook Weapon <span class="pw-info-icon" onclick="event.stopPropagation();showAllWeaponDefs(event)" title="View all weapon definitions">i</span></label>
                    <select id="opp-playbook">
                        <option value="">-- Select --</option>
                        <option value="Reverse Demo">Reverse Demo</option>
                        <option value="Proof Packet">Proof Packet</option>
                        <option value="Content Sniper">Content Sniper</option>
                        <option value="Alliance">Alliance</option>
                        <option value="48hr Challenge">48hr Challenge</option>
                        <option value="FOMO">FOMO</option>
                        <option value="Live Event">Live Event</option>
                        <option value="Sales Process">Sales Process</option>
                    </select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Next Action</label>
                    <input type="text" id="opp-next-action" placeholder="e.g. Schedule discovery call">
                </div>
                <div class="form-group">
                    <label>Next Action Date</label>
                    <input type="date" id="opp-next-action-date">
                </div>
            </div>
            <div class="form-row full">
                <div class="form-group">
                    <label>Notes</label>
                    <textarea id="opp-notes" placeholder="Deal notes, context, history..."></textarea>
                </div>
            </div>

            <!-- Deal Qualification Collapsible Section in Modal -->
            <div class="collapsible-section">
                <div class="collapsible-toggle" onclick="toggleModalMeddpicc()">
                    <h3>Deal Qualification</h3>
                    <span class="toggle-icon" id="modal-meddpicc-arrow">&#9660;</span>
                </div>
                <div class="collapsible-body" id="modal-meddpicc-body">
                    <div class="form-row full">
                        <div class="form-group">
                            <label>Metrics</label>
                            <textarea id="opp-meddpicc-metrics" placeholder="How does the buyer measure success?"></textarea>
                        </div>
                    </div>
                    <div class="form-row full">
                        <div class="form-group">
                            <label>Decision Criteria</label>
                            <textarea id="opp-meddpicc-decision-criteria" placeholder="What are they comparing us against?"></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <div class="activity-list" id="modal-activity" style="display:none">
                <h3>Activity Log</h3>
                <div id="modal-activity-list"></div>
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" style="width:auto" id="modal-save-btn" onclick="saveOpportunity()">Save</button>
        </div>
    </div>
</div>

<!-- Playbook Weapon Popup (single weapon) -->
<div class="pw-popup" id="pw-popup">
    <button class="pw-popup-close" onclick="closePwPopup()">&times;</button>
    <h4 id="pw-popup-title"></h4>
    <p id="pw-popup-desc"></p>
</div>

<!-- Playbook Weapon All Definitions Panel -->
<div class="pw-all-defs" id="pw-all-defs">
    <button class="pw-popup-close" onclick="closeAllWeaponDefs()">&times;</button>
    <h4>Playbook Weapons</h4>
    <div id="pw-all-defs-content"></div>
</div>

<script>
// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentUser = null;
let allOwners = [];
let currentSort = { field: 'updated_at', dir: 'DESC' };
let previousView = 'pipeline';
let currentView = 'dashboard';
let cachedStats = null;
let cachedOpportunities = [];

const STAGE_ORDER = [
    'Suspect', 'Pipeline', 'Qualified', 'Proposal Submitted',
    'Proposal Finalised', 'Sponsor Commitment', 'Proposal Accepted',
    'Closed Won', 'Closed Lost'
];

const STAGE_COLORS = {
    'Suspect': '#94A3B8',
    'Pipeline': '#60A5FA',
    'Qualified': '#2DD4BF',
    'Proposal Submitted': '#F59E0B',
    'Proposal Finalised': '#FB923C',
    'Sponsor Commitment': '#F472B6',
    'Proposal Accepted': '#A3E635',
    'Closed Won': '#34D399',
    'Closed Lost': '#FB7185',
};

const STAGE_WEIGHTS = {
    'Suspect': 0,
    'Pipeline': 0.05,
    'Qualified': 0.15,
    'Proposal Submitted': 0.40,
    'Proposal Finalised': 0.60,
    'Sponsor Commitment': 0.80,
    'Proposal Accepted': 0.90,
    'Closed Won': 1.0,
    'Closed Lost': 0,
};

const EMOTIONAL_ARC_STAGES = [
    { name: 'Curious', tooltip: 'They are interested enough to keep listening' },
    { name: 'Aware', tooltip: 'They see the problem differently' },
    { name: 'FOMO', tooltip: 'The cost of inaction is real and personal' },
    { name: 'Excited', tooltip: 'They see what the better future looks like with us' },
    { name: 'Committed', tooltip: 'They are a co-author of what happens next' },
];

const PLAYBOOK_WEAPONS = {
    'Reverse Demo': 'Instead of showing what we can do, we ask the prospect to show us their current process. Reveals pain points they didn\\'t know they had.',
    'Proof Packet': 'A curated bundle of case studies, velocity data, and ROI evidence tailored to the prospect\\'s specific category and challenges.',
    'Content Sniper': 'Targeted thought leadership content that addresses the prospect\\'s exact pain point, delivered before they ask for it.',
    'Alliance': 'Strategic partnership positioning where we bring complementary capabilities to the table, making the deal larger than either party alone.',
    '48hr Challenge': 'A time-boxed proof of concept where we demonstrate tangible results within 48 hours, removing the "what if" objection.',
    'FOMO': 'Evidence that competitors or peers are already moving, creating urgency through market intelligence rather than artificial pressure.',
    'Live Event': 'In-person or virtual activation that lets the prospect experience the value firsthand rather than hearing about it.',
    'Sales Process': 'Our structured methodology itself becomes the differentiator, showing the prospect a level of rigour their other vendors can\\'t match.',
};

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------
async function api(url, options = {}) {
    const defaults = { headers: { 'Content-Type': 'application/json' } };
    const resp = await fetch(url, { ...defaults, ...options });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Request failed');
    return data;
}

function formatMoney(val) {
    if (!val || val === 0) return '$0';
    if (val >= 1000000) return '$' + (val / 1000000).toFixed(1) + 'M';
    if (val >= 1000) return '$' + (val / 1000).toFixed(0) + 'K';
    return '$' + val.toLocaleString();
}

function formatDate(str) {
    if (!str) return '';
    const d = new Date(str);
    if (isNaN(d.getTime())) return str;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function timeAgo(str) {
    if (!str) return '';
    const d = new Date(str + (str.includes('Z') ? '' : 'Z'));
    const now = new Date();
    const diff = (now - d) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
    if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
    if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
    return formatDate(str);
}

function stageClass(stage) {
    return 'stage-' + (stage || '').replace(/\\s+/g, '-');
}

function escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ---------------------------------------------------------------------------
// View Navigation
// ---------------------------------------------------------------------------
function switchView(viewName) {
    // Track previous view for back navigation (but not deal-detail as previous)
    if (currentView !== 'deal-detail') {
        previousView = currentView;
    }
    currentView = viewName;

    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    // Show target view
    const target = document.getElementById('view-' + viewName);
    if (target) target.classList.add('active');

    // Update tab active state (deal-detail has no tab)
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === viewName);
    });

    // Load data for the view
    if (viewName === 'dashboard') {
        loadStats();
    } else if (viewName === 'pipeline') {
        loadOpportunities();
        loadActivity();
    } else if (viewName === 'accounts') {
        loadAccounts();
    }
}

function goBack() {
    switchView(previousView || 'pipeline');
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
async function checkAuth() {
    try {
        const user = await api('/api/me');
        currentUser = user;
        showApp();
    } catch {
        showLogin();
    }
}

function showLogin() {
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('app-screen').style.display = 'none';
}

function showApp() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
    document.getElementById('user-display').textContent = currentUser.display_name;
    document.getElementById('user-role').textContent = '(' + currentUser.role + ')';
    loadAll();
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('login-error');
    errEl.style.display = 'none';

    const username = document.getElementById('login-username').value.trim().toLowerCase();
    const password = document.getElementById('login-password').value;

    try {
        const data = await api('/api/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        currentUser = data.user;
        showApp();
    } catch (err) {
        errEl.textContent = err.message || 'Login failed';
        errEl.style.display = 'block';
    }
});

async function doLogout() {
    try { await api('/api/logout', { method: 'POST' }); } catch {}
    currentUser = null;
    showLogin();
}

// ---------------------------------------------------------------------------
// Load data
// ---------------------------------------------------------------------------
async function loadAll() {
    await Promise.all([
        loadOwners(),
        loadStats(),
        loadOpportunities(),
        loadActivity(),
    ]);
}

async function loadOwners() {
    try {
        allOwners = await api('/api/owners');
        const filterSelect = document.getElementById('filter-owner');
        filterSelect.innerHTML = '<option value="">All</option>';
        allOwners.forEach(o => {
            filterSelect.innerHTML += '<option value="' + escHtml(o.display_name) + '">' + escHtml(o.display_name) + '</option>';
        });
        populateOwnerDropdown();
    } catch {}
}

function populateOwnerDropdown() {
    const sel = document.getElementById('opp-owner');
    sel.innerHTML = '';
    allOwners.forEach(o => {
        sel.innerHTML += '<option value="' + escHtml(o.display_name) + '">' + escHtml(o.display_name) + '</option>';
    });
    if (currentUser) {
        sel.value = currentUser.display_name;
    }
}

async function loadStats() {
    try {
        const stats = await api('/api/stats');
        cachedStats = stats;
        renderSummary(stats);
        renderPipelineBar(stats);
        renderDashByType(stats);
        renderDashByOwner(stats);
    } catch {}
}

async function loadOpportunities() {
    const params = new URLSearchParams();
    const owner = document.getElementById('filter-owner').value;
    const type = document.getElementById('filter-type').value;
    const geo = document.getElementById('filter-geography').value;
    const stage = document.getElementById('filter-stage').value;
    const vertical = document.getElementById('filter-vertical').value.trim();

    if (owner) params.set('owner', owner);
    if (type) params.set('type', type);
    if (geo) params.set('geography', geo);
    if (stage) params.set('stage', stage);
    if (vertical) params.set('vertical', vertical);
    params.set('sort', currentSort.field);
    params.set('dir', currentSort.dir);

    try {
        const opps = await api('/api/opportunities?' + params.toString());
        cachedOpportunities = opps;
        renderTable(opps);
    } catch {}
}

async function loadActivity() {
    try {
        const items = await api('/api/activity?limit=20');
        renderActivityFeed(items);
    } catch {}
}

async function loadAccounts() {
    try {
        const accounts = await api('/api/accounts');
        renderAccounts(accounts);
    } catch (err) {
        document.getElementById('accounts-grid').innerHTML =
            '<div class="empty-state"><div class="icon">&#127970;</div><p>Could not load accounts.</p></div>';
    }
}

function toggleStageDefs() {
    const body = document.getElementById('stage-defs-body');
    const arrow = document.getElementById('stage-defs-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
}

function togglePlaybookRef() {
    const body = document.getElementById('pw-ref-body');
    const arrow = document.getElementById('pw-ref-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
}

function toggleModalMeddpicc() {
    const body = document.getElementById('modal-meddpicc-body');
    const arrow = document.getElementById('modal-meddpicc-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
}

function clearFilters() {
    document.getElementById('filter-owner').value = '';
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-geography').value = '';
    document.getElementById('filter-stage').value = '';
    document.getElementById('filter-vertical').value = '';
    loadOpportunities();
}

// ---------------------------------------------------------------------------
// Render: Dashboard
// ---------------------------------------------------------------------------
function renderSummary(stats) {
    const bar = document.getElementById('summary-bar');
    const activeCount = stats.total.count || 0;
    const activeValue = stats.total.total || 0;
    const wonCount = stats.won.count || 0;
    const wonValue = stats.won.total || 0;
    const lostCount = stats.lost.count || 0;

    const activeStages = stats.by_stage.filter(s => s.stage !== 'Closed Won' && s.stage !== 'Closed Lost');
    const stageCount = activeStages.length;
    const stageSub = stageCount === 1 ? activeStages[0].stage + ' (' + activeStages[0].count + ')' : stageCount + ' stages with deals';

    const weightedValue = stats.by_stage.reduce((sum, s) => {
        const weight = STAGE_WEIGHTS[s.stage] || 0;
        return sum + (s.total * weight);
    }, 0);

    bar.innerHTML = \`
        <div class="summary-card">
            <div class="label">Active Pipeline</div>
            <div class="value orange">\${formatMoney(activeValue)}</div>
            <div class="sub">\${activeCount} open deal\${activeCount !== 1 ? 's' : ''}</div>
        </div>
        <div class="summary-card">
            <div class="label">Weighted Pipeline</div>
            <div class="value orange">\${formatMoney(weightedValue)}</div>
            <div class="sub">probability-adjusted</div>
        </div>
        <div class="summary-card">
            <div class="label">Closed Won</div>
            <div class="value green">\${formatMoney(wonValue)}</div>
            <div class="sub">\${wonCount} deal\${wonCount !== 1 ? 's' : ''} closed</div>
        </div>
        <div class="summary-card">
            <div class="label">Active Stages</div>
            <div class="value blue">\${stageCount}</div>
            <div class="sub">\${stageSub}</div>
        </div>
        <div class="summary-card">
            <div class="label">Win Rate</div>
            <div class="value">\${wonCount + lostCount > 0 ? Math.round(wonCount / (wonCount + lostCount) * 100) : 0}%</div>
            <div class="sub">\${wonCount}W / \${lostCount}L</div>
        </div>
    \`;
}

function renderPipelineBar(stats) {
    const bar = document.getElementById('pipeline-bar');
    const legend = document.getElementById('pipeline-legend');

    const total = stats.by_stage.reduce((s, r) => s + (r.total || 0), 0);

    if (total === 0) {
        bar.innerHTML = '<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:13px">No pipeline data yet</div>';
        legend.innerHTML = '';
        return;
    }

    let barHtml = '';
    let legendHtml = '';

    STAGE_ORDER.forEach(stage => {
        const item = stats.by_stage.find(s => s.stage === stage);
        const val = item ? item.total : 0;
        const pct = (val / total) * 100;
        if (pct > 0) {
            const color = STAGE_COLORS[stage];
            // Use dark text on bright backgrounds for readability
            const brightStages = ['Qualified', 'Proposal Accepted', 'Closed Won', 'Proposal Submitted', 'Proposal Finalised'];
            const textColor = brightStages.includes(stage) ? '#080C15' : '#fff';
            barHtml += '<div class="segment" style="width:' + pct + '%;background:' + color + ';color:' + textColor + '" title="' + stage + ': ' + formatMoney(val) + '">' + (pct > 8 ? formatMoney(val) : '') + '</div>';
        }
        const count = item ? item.count : 0;
        legendHtml += '<div class="legend-item"><div class="legend-dot" style="background:' + STAGE_COLORS[stage] + '"></div><span style="color:' + STAGE_COLORS[stage] + '">' + stage + '</span>: <span class="legend-value">' + formatMoney(val) + '</span> (' + count + ')</div>';
    });

    bar.innerHTML = barHtml;
    legend.innerHTML = legendHtml;
}

function renderDashByType(stats) {
    const container = document.getElementById('dash-by-type');
    if (!stats.by_type || stats.by_type.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">No data</div>';
        return;
    }
    container.innerHTML = stats.by_type.map(t => \`
        <div class="mini-card">
            <div class="mc-label">\${escHtml(t.type || 'Unset')}</div>
            <div class="mc-value">\${formatMoney(t.total)}</div>
            <div class="mc-sub">\${t.count} deal\${t.count !== 1 ? 's' : ''}</div>
        </div>
    \`).join('');
}

function renderDashByOwner(stats) {
    const container = document.getElementById('dash-by-owner');
    if (!stats.by_owner || stats.by_owner.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted);font-size:13px">No data</div>';
        return;
    }
    container.innerHTML = stats.by_owner.map(o => \`
        <div class="mini-card">
            <div class="mc-label">\${escHtml(o.owner || 'Unassigned')}</div>
            <div class="mc-value">\${formatMoney(o.total)}</div>
            <div class="mc-sub">\${o.count} deal\${o.count !== 1 ? 's' : ''}</div>
        </div>
    \`).join('');
}

// ---------------------------------------------------------------------------
// Render: Pipeline Table
// ---------------------------------------------------------------------------
function renderTable(opps) {
    const tbody = document.getElementById('opp-tbody');
    const empty = document.getElementById('empty-state');

    if (opps.length === 0) {
        tbody.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    tbody.innerHTML = opps.map(o => \`
        <tr onclick="openDealDetail(\${o.id})">
            <td class="company-cell">\${escHtml(o.company)}\${o.division ? '<br><span style="font-size:11px;color:var(--amber);font-weight:400">' + escHtml(o.division) + '</span>' : ''}\${o.partner ? '<br><span style="font-size:11px;color:var(--cyan);font-weight:400">via ' + escHtml(o.partner) + '</span>' : ''}</td>
            <td><span class="stage-badge \${stageClass(o.stage)}">\${escHtml(o.stage)}</span></td>
            <td>\${o.type ? '<span class="type-badge">' + escHtml(o.type) + '</span>' : '<span style="color:var(--text-muted)">--</span>'}</td>
            <td>\${escHtml(o.owner)}</td>
            <td class="value-cell">\${formatMoney(o.estimated_value)}</td>
            <td>\${escHtml(o.geography || '--')}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">\${escHtml(o.next_action || '--')}</td>
            <td style="white-space:nowrap;color:var(--text-muted);font-size:13px">\${timeAgo(o.updated_at)}</td>
        </tr>
    \`).join('');
}

function renderActivityFeed(items) {
    const feed = document.getElementById('activity-feed');
    if (items.length === 0) {
        feed.innerHTML = '<p style="color:var(--text-muted);font-size:14px">No activity yet.</p>';
        return;
    }
    feed.innerHTML = items.map(a => \`
        <div class="activity-item">
            <span class="actor">\${escHtml(a.actor)}</span>
            <span class="action">\${escHtml(a.action)}\${a.company ? ' <span style="color:var(--text-muted)">(' + escHtml(a.company) + ')</span>' : ''}</span>
            <span class="time">\${timeAgo(a.created_at)}</span>
        </div>
    \`).join('');
}

// ---------------------------------------------------------------------------
// Render: Accounts
// ---------------------------------------------------------------------------
let expandedAccount = null;
let allAccounts = [];

function filterCompanies() {
    const q = (document.getElementById('company-search').value || '').toLowerCase();
    const filtered = q ? allAccounts.filter(a => a.company.toLowerCase().includes(q)) : allAccounts;
    renderAccountCards(filtered);
}

function renderAccounts(accounts) {
    // Sort alphabetically by company name
    accounts.sort((a, b) => a.company.localeCompare(b.company));
    allAccounts = accounts;
    renderAccountCards(accounts);
}

function renderAccountCards(accounts) {
    const grid = document.getElementById('accounts-grid');
    if (!accounts || accounts.length === 0) {
        grid.innerHTML = '<div class="empty-state"><div class="icon">&#127970;</div><p>No companies found.</p></div>';
        return;
    }
    grid.innerHTML = accounts.map(acc => {
        const isExpanded = expandedAccount === acc.company;
        const opps = acc.opportunities || [];
        const contactCount = opps.filter(o => o.contact_name).length;

        // Collect unique divisions for header badges
        const divisions = [...new Set(opps.map(o => o.division).filter(d => d))];
        const divisionBadgesHtml = divisions.length > 0
            ? '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px">' + divisions.map(d => '<span style="display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;background:rgba(245,158,11,0.15);color:var(--amber)">' + escHtml(d) + '</span>').join('') + '</div>'
            : '';

        let contactsHtml = '';
        if (isExpanded && opps.length > 0) {
            contactsHtml = '<div class="ac-contacts">' + opps.map(o => \`
                <div class="ac-contact-row">
                    <div class="ac-contact-info">
                        <span class="ac-contact-name">\${escHtml(o.contact_name || 'No contact')}\${o.division ? ' <span style="font-size:11px;color:var(--amber);font-weight:400">(' + escHtml(o.division) + ')</span>' : ''}</span>
                        <span class="ac-contact-title">\${escHtml(o.contact_title || '')}\${o.contact_title && o.contact_location ? ' &middot; ' : ''}\${o.contact_location ? '<span style="color:var(--cyan);font-size:12px">' + escHtml(o.contact_location) + '</span>' : ''}</span>
                        <span style="margin-top:2px">
                            <span class="stage-badge \${stageClass(o.stage)}" style="font-size:10px;padding:1px 6px">\${escHtml(o.stage)}</span>
                        </span>
                    </div>
                    <div class="ac-contact-right">
                        <span class="ac-contact-value">\${formatMoney(o.estimated_value)}</span>
                        <a class="ac-view-deal" onclick="event.stopPropagation();openDealDetail(\${o.id})">View Deal &rarr;</a>
                    </div>
                </div>
            \`).join('') + '</div>';
        }

        return \`
            <div class="account-card \${isExpanded ? 'expanded' : ''}" onclick="toggleAccount('\${escHtml(acc.company).replace(/'/g, "\\\\'")}')">
                <div class="ac-header">
                    <span class="ac-company">\${escHtml(acc.company)}</span>
                    <span class="ac-deal-count">\${acc.deal_count} deal\${acc.deal_count !== 1 ? 's' : ''}</span>
                </div>
                <div class="ac-stats">
                    <div>
                        <div class="ac-stat-label">Pipeline Value</div>
                        <div class="ac-stat-value">\${formatMoney(acc.total_value)}</div>
                    </div>
                    <div>
                        <div class="ac-stat-label">Contacts</div>
                        <div class="ac-stat-value" style="color:var(--blue-light)">\${contactCount}</div>
                    </div>
                </div>
                \${divisionBadgesHtml}
                \${contactsHtml}
            </div>
        \`;
    }).join('');
}

function toggleAccount(company) {
    expandedAccount = expandedAccount === company ? null : company;
    loadAccounts();
}

// ---------------------------------------------------------------------------
// Deal Detail View
// ---------------------------------------------------------------------------
async function openDealDetail(id) {
    try {
        const [opp, notes] = await Promise.all([
            api('/api/opportunities/' + id),
            api('/api/opportunities/' + id + '/notes').catch(() => [])
        ]);
        renderDealDetail(opp, notes);
        switchView('deal-detail');
    } catch (err) {
        alert('Failed to load deal: ' + err.message);
    }
}

function renderDealDetail(opp, notes) {
    const container = document.getElementById('deal-detail-content');
    const backLabel = previousView === 'accounts' ? 'Back to Accounts' : 'Back to Pipeline';

    // Build stage progress
    let stageProgressHtml = '';
    const currentStageIdx = STAGE_ORDER.indexOf(opp.stage);
    STAGE_ORDER.forEach((stage, idx) => {
        if (stage === 'Closed Lost') return; // skip in progress bar
        let cls = 'future';
        if (idx < currentStageIdx) cls = 'completed';
        else if (idx === currentStageIdx) cls = 'current';

        stageProgressHtml += '<div class="sp-item ' + cls + '">';
        stageProgressHtml += '<div class="sp-dot"></div>';
        stageProgressHtml += '<span class="sp-label">' + escHtml(stage) + '</span>';
        stageProgressHtml += '</div>';
        if (idx < STAGE_ORDER.length - 2) {
            stageProgressHtml += '<div class="sp-line ' + (idx < currentStageIdx ? 'completed' : '') + '"></div>';
        }
    });

    // LinkedIn link
    const linkedinHtml = opp.contact_linkedin
        ? '<a href="' + escHtml(opp.contact_linkedin) + '" target="_blank" rel="noopener">' + escHtml(opp.contact_linkedin) + '</a>'
        : '<span style="color:var(--text-muted)">--</span>';

    // Email link
    const emailHtml = opp.contact_email
        ? '<a href="mailto:' + escHtml(opp.contact_email) + '">' + escHtml(opp.contact_email) + '</a>'
        : '<span style="color:var(--text-muted)">--</span>';

    // Location
    const locationHtml = opp.contact_location
        ? '<span style="color:var(--cyan);font-weight:500">' + escHtml(opp.contact_location) + '</span>'
        : '<span style="color:var(--text-muted)">--</span>';

    // Meeting notes
    const meetingNotes = notes || opp.meeting_notes || [];
    let notesListHtml = '';
    if (meetingNotes.length > 0) {
        notesListHtml = meetingNotes.map(n => \`
            <div class="note-item">
                <div class="note-item-header">
                    <span class="note-type-badge note-type-\${escHtml(n.note_type || 'general')}">\${escHtml(n.note_type || 'general')}</span>
                    <span class="note-actor">\${escHtml(n.actor)}</span>
                    <span class="note-time">\${timeAgo(n.created_at)}</span>
                </div>
                <div class="note-content">\${escHtml(n.content)}</div>
            </div>
        \`).join('');
    } else {
        notesListHtml = '<p style="color:var(--text-muted);font-size:13px">No meeting notes yet.</p>';
    }

    // Activity timeline
    const activityItems = opp.activity || [];
    let activityHtml = '';
    if (activityItems.length > 0) {
        activityHtml = activityItems.map(a => \`
            <div class="activity-item">
                <span class="actor">\${escHtml(a.actor)}</span>
                <span class="action">\${escHtml(a.action)}</span>
                <span class="time">\${timeAgo(a.created_at)}</span>
            </div>
        \`).join('');
    } else {
        activityHtml = '<p style="color:var(--text-muted);font-size:13px">No activity yet.</p>';
    }

    container.innerHTML = \`
        <div class="deal-detail-top">
            <button class="back-btn" onclick="goBack()">&larr; \${escHtml(backLabel)}</button>
            <span class="dd-company">\${escHtml(opp.company)}\${opp.division ? '<span style="display:block;font-size:14px;font-weight:400;color:var(--amber);margin-top:2px">' + escHtml(opp.division) + '</span>' : ''}</span>
            <span class="stage-badge \${stageClass(opp.stage)}">\${escHtml(opp.stage)}</span>
            <div class="dd-actions">
                <button class="btn btn-secondary btn-sm" onclick="openEditModal(\${opp.id})">Edit Deal</button>
            </div>
        </div>
        <div class="deal-columns">
            <div class="deal-left">
                <!-- Contact Info -->
                <div class="deal-card">
                    <h3>Contact Information</h3>
                    <div class="deal-field-grid">
                        <div class="deal-field">
                            <span class="df-label">Name</span>
                            <span class="df-value">\${escHtml(opp.contact_name || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Title</span>
                            <span class="df-value">\${escHtml(opp.contact_title || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Email</span>
                            <span class="df-value">\${emailHtml}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">LinkedIn</span>
                            <span class="df-value">\${linkedinHtml}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Location</span>
                            <span class="df-value">\${locationHtml}</span>
                        </div>
                    </div>
                </div>

                <!-- Deal Info -->
                <div class="deal-card">
                    <h3>Deal Information</h3>
                    <div class="deal-field-grid">
                        <div class="deal-field">
                            <span class="df-label">Division</span>
                            <span class="df-value">\${opp.division ? '<span style="color:var(--amber);font-weight:500">' + escHtml(opp.division) + '</span>' : '<span style="color:var(--text-muted)">--</span>'}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Type</span>
                            <span class="df-value">\${opp.type ? '<span class="type-badge">' + escHtml(opp.type) + '</span>' : '<span style="color:var(--text-muted)">--</span>'}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Geography</span>
                            <span class="df-value">\${escHtml(opp.geography || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Owner</span>
                            <span class="df-value">\${escHtml(opp.owner || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Estimated Value</span>
                            <span class="df-value" style="color:var(--green);font-weight:700">\${formatMoney(opp.estimated_value)}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Partner</span>
                            <span class="df-value">\${escHtml(opp.partner || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Vertical</span>
                            <span class="df-value">\${escHtml(opp.vertical || '--')}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Playbook Weapon</span>
                            <span class="df-value">\${opp.playbook_weapon ? '<span class="pw-clickable" onclick="event.stopPropagation();showWeaponDef(\\'' + escHtml(opp.playbook_weapon) + '\\', event)">' + escHtml(opp.playbook_weapon) + '</span>' : '<span style="color:var(--text-muted)">--</span>'}</span>
                        </div>
                        <div class="deal-field">
                            <span class="df-label">Created</span>
                            <span class="df-value">\${formatDate(opp.created_at)}</span>
                        </div>
                    </div>
                </div>

                <!-- Deal Qualification -->
                <div class="meddpicc-card" id="meddpicc-card-\${opp.id}">
                    <h3>Deal Qualification</h3>
                    <div class="meddpicc-field">
                        <label>Metrics</label>
                        <textarea id="meddpicc-metrics-\${opp.id}" placeholder="How does the buyer measure success?">\${escHtml(opp.meddpicc_metrics || '')}</textarea>
                    </div>
                    <div class="meddpicc-field">
                        <label>Decision Criteria</label>
                        <textarea id="meddpicc-decision-criteria-\${opp.id}" placeholder="What are they comparing us against?">\${escHtml(opp.meddpicc_decision_criteria || '')}</textarea>
                    </div>
                    <div class="meddpicc-save-row">
                        <button class="btn btn-primary btn-sm" style="width:auto" onclick="saveMeddpicc(\${opp.id})">Save</button>
                    </div>
                </div>

                <!-- Readiness Check -->
                <div class="readiness-card" id="readiness-card-\${opp.id}">
                    <h3>Readiness Check</h3>
                    \${renderReadinessCheck(opp)}
                </div>

                <!-- Emotional Arc Tracker -->
                <div class="emotional-arc-card">
                    <h3>Emotional Arc</h3>
                    <div class="ea-track" id="ea-track-\${opp.id}">
                        \${renderEmotionalArc(opp.id, opp.emotional_arc || '')}
                    </div>
                    <div class="ea-note">A prospect who leaves at FOMO without reaching Excited is anxious but not motivated.</div>
                </div>
            </div>

            <div class="deal-right">
                <!-- Stage Progression -->
                <div class="stage-progress">
                    <h3>Stage Progression</h3>
                    <div class="sp-list">\${stageProgressHtml}</div>
                    \${renderStageTimer(opp)}
                </div>

                <!-- Next Action -->
                <div class="next-action-card">
                    <h3>Next Action</h3>
                    <div class="next-action-text">\${escHtml(opp.next_action || 'No next action set')}</div>
                    \${opp.next_action_date ? '<div class="next-action-date">Due: ' + formatDate(opp.next_action_date) + '</div>' : ''}
                </div>

                \${renderSilenceCard(opp)}

                <!-- Meeting Notes -->
                <div class="notes-section">
                    <h3>Meeting Notes</h3>
                    <div class="note-form">
                        <div class="note-form-row">
                            <select id="note-type-\${opp.id}">
                                <option value="general">General</option>
                                <option value="meeting">Meeting</option>
                                <option value="call">Call</option>
                                <option value="email">Email</option>
                            </select>
                            <button class="btn btn-primary btn-sm" style="width:auto" onclick="addMeetingNote(\${opp.id})">Add Note</button>
                        </div>
                        <textarea id="note-content-\${opp.id}" placeholder="Add a meeting note..."></textarea>
                    </div>
                    <div id="notes-list-\${opp.id}">\${notesListHtml}</div>
                </div>

                <!-- Activity Timeline -->
                <div class="deal-card">
                    <h3>Activity Timeline</h3>
                    <div>\${activityHtml}</div>
                </div>
            </div>
        </div>
    \`;
}

// ---------------------------------------------------------------------------
// Deal Qualification Save
// ---------------------------------------------------------------------------
async function saveMeddpicc(id) {
    const payload = {
        meddpicc_metrics: document.getElementById('meddpicc-metrics-' + id).value,
        meddpicc_decision_criteria: document.getElementById('meddpicc-decision-criteria-' + id).value,
    };

    try {
        await api('/api/opportunities/' + id, {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
        // Brief success indication
        const btn = event.target;
        const origText = btn.textContent;
        btn.textContent = 'Saved!';
        btn.style.background = 'var(--green)';
        setTimeout(() => {
            btn.textContent = origText;
            btn.style.background = '';
        }, 1500);
    } catch (err) {
        alert('Error saving qualification: ' + err.message);
    }
}

// ---------------------------------------------------------------------------
// Emotional Arc
// ---------------------------------------------------------------------------
function renderEmotionalArc(oppId, currentStage) {
    const currentIdx = EMOTIONAL_ARC_STAGES.findIndex(s => s.name === currentStage);
    let html = '';

    EMOTIONAL_ARC_STAGES.forEach((stage, idx) => {
        const isReached = currentIdx >= 0 && idx <= currentIdx;
        const isActive = idx === currentIdx;
        let cls = '';
        if (isReached) cls += ' reached';
        if (isActive) cls += ' active';

        html += '<div class="ea-step' + cls + '" data-stage="' + stage.name + '" onclick="event.stopPropagation();saveEmotionalArc(' + oppId + ',\\'' + stage.name + '\\')">';
        html += '<div class="ea-tooltip">' + escHtml(stage.tooltip) + '</div>';
        html += '<div class="ea-dot">' + (idx + 1) + '</div>';
        html += '<span class="ea-label">' + escHtml(stage.name) + '</span>';
        html += '</div>';

        if (idx < EMOTIONAL_ARC_STAGES.length - 1) {
            html += '<div class="ea-connector' + (currentIdx >= 0 && idx < currentIdx ? ' reached' : '') + '"></div>';
        }
    });

    return html;
}

async function saveEmotionalArc(oppId, stage) {
    try {
        await api('/api/opportunities/' + oppId, {
            method: 'PUT',
            body: JSON.stringify({ emotional_arc: stage }),
        });
        // Re-render the arc in place
        const track = document.getElementById('ea-track-' + oppId);
        if (track) {
            track.innerHTML = renderEmotionalArc(oppId, stage);
        }
    } catch (err) {
        alert('Error saving emotional arc: ' + err.message);
    }
}

// ---------------------------------------------------------------------------
// Readiness Check
// ---------------------------------------------------------------------------
function renderReadinessCheck(opp) {
    const items = [
        { key: 'readiness_pnl_pain', label: 'P&L pain identified' },
        { key: 'readiness_decision_maker', label: 'Decision maker known' },
        { key: 'readiness_competitor', label: 'Competitor/incumbent mapped' },
        { key: 'readiness_unique_angle', label: 'Unique angle defined' },
        { key: 'readiness_proof', label: 'Proof ready (case study, data, demo)' },
    ];

    let count = 0;
    let html = '';
    items.forEach(item => {
        const checked = opp[item.key] ? 1 : 0;
        if (checked) count++;
        html += '<div class="readiness-item' + (checked ? ' checked' : '') + '" onclick="toggleReadiness(' + opp.id + ',\\'' + item.key + '\\', this)">';
        html += '<div class="readiness-checkbox">' + (checked ? '&#10003;' : '') + '</div>';
        html += '<span class="readiness-label">' + escHtml(item.label) + '</span>';
        html += '</div>';
    });

    if (count === 5) {
        html += '<div class="readiness-status ready">&#10003; Ready</div>';
    } else {
        html += '<div class="readiness-status not-ready">' + count + ' of 5 &mdash; Not ready</div>';
    }

    return html;
}

async function toggleReadiness(oppId, field, el) {
    const isChecked = el.classList.contains('checked');
    const newValue = isChecked ? 0 : 1;

    // Optimistic UI update
    if (newValue) {
        el.classList.add('checked');
        el.querySelector('.readiness-checkbox').innerHTML = '&#10003;';
    } else {
        el.classList.remove('checked');
        el.querySelector('.readiness-checkbox').innerHTML = '';
    }

    // Recalculate status
    const card = document.getElementById('readiness-card-' + oppId);
    const allItems = card.querySelectorAll('.readiness-item');
    let count = 0;
    allItems.forEach(item => { if (item.classList.contains('checked')) count++; });
    const statusEl = card.querySelector('.readiness-status');
    if (count === 5) {
        statusEl.className = 'readiness-status ready';
        statusEl.innerHTML = '&#10003; Ready';
    } else {
        statusEl.className = 'readiness-status not-ready';
        statusEl.innerHTML = count + ' of 5 &mdash; Not ready';
    }

    // Save to API
    const payload = {};
    payload[field] = newValue;
    try {
        await api('/api/opportunities/' + oppId, {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
    } catch (err) {
        // Revert on failure
        if (newValue) {
            el.classList.remove('checked');
            el.querySelector('.readiness-checkbox').innerHTML = '';
        } else {
            el.classList.add('checked');
            el.querySelector('.readiness-checkbox').innerHTML = '&#10003;';
        }
        alert('Error saving readiness: ' + err.message);
    }
}

// ---------------------------------------------------------------------------
// Stage Timer
// ---------------------------------------------------------------------------
function renderStageTimer(opp) {
    if (!opp.stage_changed_at) return '';

    const changedAt = new Date(opp.stage_changed_at + (opp.stage_changed_at.endsWith('Z') ? '' : 'Z'));
    const now = new Date();
    const diffMs = now - changedAt;
    if (diffMs < 0) return '';

    const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
    const days = Math.floor(totalHours / 24);
    const hours = totalHours % 24;

    let timeText = '';
    if (days > 0) {
        timeText = days + ' day' + (days !== 1 ? 's' : '') + ', ' + hours + ' hour' + (hours !== 1 ? 's' : '');
    } else {
        timeText = hours + ' hour' + (hours !== 1 ? 's' : '');
    }

    let timerClass = 'stage-timer-value';
    if (opp.stage === 'Proposal Submitted') {
        if (totalHours > 72) {
            timerClass += ' red';
        } else if (totalHours > 48) {
            timerClass += ' amber';
        }
    }

    let html = '<div class="stage-timer">';
    html += '<span class="' + timerClass + '">At current stage: ' + timeText + '</span>';
    if (opp.stage === 'Proposal Submitted') {
        html += '<div class="stage-timer-note">&#9201; Response window: 48 hours</div>';
    }
    html += '</div>';
    return html;
}

// ---------------------------------------------------------------------------
// Silence Card (Proposal Submitted only)
// ---------------------------------------------------------------------------
function renderSilenceCard(opp) {
    if (opp.stage !== 'Proposal Submitted' || !opp.stage_changed_at) return '';

    const changedAt = new Date(opp.stage_changed_at + (opp.stage_changed_at.endsWith('Z') ? '' : 'Z'));
    const now = new Date();
    const diffMs = now - changedAt;
    if (diffMs < 0) return '';

    const daysSince = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    let nextFollowUp = '';
    if (daysSince < 5) {
        nextFollowUp = 'Day 5';
    } else if (daysSince < 7) {
        nextFollowUp = 'Day 7';
    } else {
        nextFollowUp = 'Overdue';
    }

    let html = '<div class="silence-card">';
    html += '<h3>Strategic Patience</h3>';
    html += '<div class="silence-elapsed">Proposal sent ' + daysSince + ' day' + (daysSince !== 1 ? 's' : '') + ' ago.</div>';
    html += '<div class="silence-next">Next follow-up: ' + nextFollowUp + '</div>';
    html += '<div class="silence-note">Silence is strategic. Let the proposal speak.</div>';
    html += '</div>';
    return html;
}

// ---------------------------------------------------------------------------
// Playbook Weapon Popups
// ---------------------------------------------------------------------------
function showWeaponDef(weapon, event) {
    const popup = document.getElementById('pw-popup');
    const title = document.getElementById('pw-popup-title');
    const desc = document.getElementById('pw-popup-desc');

    title.textContent = weapon;
    desc.textContent = PLAYBOOK_WEAPONS[weapon] || 'No definition available.';

    // Position near the click
    const x = Math.min(event.clientX, window.innerWidth - 420);
    const y = Math.max(event.clientY - 100, 10);
    popup.style.left = x + 'px';
    popup.style.top = y + 'px';
    popup.classList.add('active');
}

function closePwPopup() {
    document.getElementById('pw-popup').classList.remove('active');
}

function showAllWeaponDefs(event) {
    const panel = document.getElementById('pw-all-defs');
    const content = document.getElementById('pw-all-defs-content');

    let html = '';
    for (const [weapon, def] of Object.entries(PLAYBOOK_WEAPONS)) {
        html += '<div class="pw-def-item"><strong>' + escHtml(weapon) + '</strong><span>' + escHtml(def) + '</span></div>';
    }
    content.innerHTML = html;

    // Position near the click
    const x = Math.min(event.clientX, window.innerWidth - 540);
    const y = Math.max(event.clientY - 200, 10);
    panel.style.left = x + 'px';
    panel.style.top = y + 'px';
    panel.classList.add('active');
}

function closeAllWeaponDefs() {
    document.getElementById('pw-all-defs').classList.remove('active');
}

// Close popups when clicking outside
document.addEventListener('click', (e) => {
    const pwPopup = document.getElementById('pw-popup');
    const pwAll = document.getElementById('pw-all-defs');
    if (pwPopup.classList.contains('active') && !pwPopup.contains(e.target) && !e.target.classList.contains('pw-clickable')) {
        pwPopup.classList.remove('active');
    }
    if (pwAll.classList.contains('active') && !pwAll.contains(e.target) && !e.target.classList.contains('pw-info-icon')) {
        pwAll.classList.remove('active');
    }
});

// ---------------------------------------------------------------------------
// Meeting Notes
// ---------------------------------------------------------------------------
async function addMeetingNote(id) {
    const noteType = document.getElementById('note-type-' + id).value;
    const content = document.getElementById('note-content-' + id).value.trim();

    if (!content) {
        alert('Please enter note content');
        return;
    }

    try {
        await api('/api/opportunities/' + id + '/notes', {
            method: 'POST',
            body: JSON.stringify({ content: content, note_type: noteType }),
        });
        document.getElementById('note-content-' + id).value = '';

        // Reload the deal detail to show the new note
        const [opp, notes] = await Promise.all([
            api('/api/opportunities/' + id),
            api('/api/opportunities/' + id + '/notes').catch(() => [])
        ]);
        renderDealDetail(opp, notes);
    } catch (err) {
        alert('Error adding note: ' + err.message);
    }
}

// ---------------------------------------------------------------------------
// Sorting
// ---------------------------------------------------------------------------
function initSortHandlers() {
    document.querySelectorAll('#opp-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const field = th.dataset.sort;
            if (currentSort.field === field) {
                currentSort.dir = currentSort.dir === 'ASC' ? 'DESC' : 'ASC';
            } else {
                currentSort.field = field;
                currentSort.dir = field === 'estimated_value' ? 'DESC' : 'ASC';
            }

            document.querySelectorAll('#opp-table th').forEach(h => h.classList.remove('sorted'));
            th.classList.add('sorted');
            th.querySelector('.sort-arrow').innerHTML = currentSort.dir === 'ASC' ? '&#9650;' : '&#9660;';

            loadOpportunities();
        });
    });
}

// ---------------------------------------------------------------------------
// Modal: Create
// ---------------------------------------------------------------------------
function openCreateModal() {
    document.getElementById('modal-title').textContent = 'New Opportunity';
    document.getElementById('opp-id').value = '';
    document.getElementById('opp-company').value = '';
    document.getElementById('opp-division').value = '';
    document.getElementById('opp-contact-name').value = '';
    document.getElementById('opp-contact-title').value = '';
    document.getElementById('opp-contact-email').value = '';
    document.getElementById('opp-contact-linkedin').value = '';
    document.getElementById('opp-contact-location').value = '';
    document.getElementById('opp-value').value = '0';
    document.getElementById('opp-type').value = '';
    document.getElementById('opp-geography').value = '';
    document.getElementById('opp-stage').value = 'Suspect';
    document.getElementById('opp-vertical').value = '';
    document.getElementById('opp-partner').value = '';
    document.getElementById('opp-playbook').value = '';
    document.getElementById('opp-next-action').value = '';
    document.getElementById('opp-next-action-date').value = '';
    document.getElementById('opp-notes').value = '';

    // Clear Deal Qualification fields
    document.getElementById('opp-meddpicc-metrics').value = '';
    document.getElementById('opp-meddpicc-decision-criteria').value = '';

    // Collapse Deal Qualification section
    document.getElementById('modal-meddpicc-body').classList.remove('open');
    document.getElementById('modal-meddpicc-arrow').classList.remove('open');

    populateOwnerDropdown();
    document.getElementById('opp-owner').value = currentUser.display_name;

    document.getElementById('modal-activity').style.display = 'none';
    document.getElementById('modal-save-btn').textContent = 'Create';
    document.getElementById('opp-modal').classList.add('active');
}

// ---------------------------------------------------------------------------
// Modal: Edit
// ---------------------------------------------------------------------------
async function openEditModal(id) {
    try {
        const opp = await api('/api/opportunities/' + id);

        document.getElementById('modal-title').textContent = 'Edit: ' + opp.company;
        document.getElementById('opp-id').value = opp.id;
        document.getElementById('opp-company').value = opp.company || '';
        document.getElementById('opp-division').value = opp.division || '';
        document.getElementById('opp-contact-name').value = opp.contact_name || '';
        document.getElementById('opp-contact-title').value = opp.contact_title || '';
        document.getElementById('opp-contact-email').value = opp.contact_email || '';
        document.getElementById('opp-contact-linkedin').value = opp.contact_linkedin || '';
        document.getElementById('opp-contact-location').value = opp.contact_location || '';
        document.getElementById('opp-value').value = opp.estimated_value || 0;
        document.getElementById('opp-type').value = opp.type || '';
        document.getElementById('opp-geography').value = opp.geography || '';
        document.getElementById('opp-stage').value = opp.stage || 'Suspect';
        document.getElementById('opp-vertical').value = opp.vertical || '';
        document.getElementById('opp-partner').value = opp.partner || '';
        document.getElementById('opp-playbook').value = opp.playbook_weapon || '';
        document.getElementById('opp-next-action').value = opp.next_action || '';
        document.getElementById('opp-next-action-date').value = opp.next_action_date || '';
        document.getElementById('opp-notes').value = opp.notes || '';

        // Deal Qualification fields
        document.getElementById('opp-meddpicc-metrics').value = opp.meddpicc_metrics || '';
        document.getElementById('opp-meddpicc-decision-criteria').value = opp.meddpicc_decision_criteria || '';

        // Show Deal Qualification section if any fields have content
        const hasMeddpicc = opp.meddpicc_metrics || opp.meddpicc_decision_criteria;
        if (hasMeddpicc) {
            document.getElementById('modal-meddpicc-body').classList.add('open');
            document.getElementById('modal-meddpicc-arrow').classList.add('open');
        } else {
            document.getElementById('modal-meddpicc-body').classList.remove('open');
            document.getElementById('modal-meddpicc-arrow').classList.remove('open');
        }

        populateOwnerDropdown();
        document.getElementById('opp-owner').value = opp.owner;

        // Activity log
        const actDiv = document.getElementById('modal-activity');
        const actList = document.getElementById('modal-activity-list');
        if (opp.activity && opp.activity.length > 0) {
            actDiv.style.display = 'block';
            actList.innerHTML = opp.activity.map(a => \`
                <div class="activity-item">
                    <span class="actor">\${escHtml(a.actor)}</span>
                    <span class="action">\${escHtml(a.action)}</span>
                    <span class="time">\${timeAgo(a.created_at)}</span>
                </div>
            \`).join('');
        } else {
            actDiv.style.display = 'none';
        }

        document.getElementById('modal-save-btn').textContent = 'Update';
        document.getElementById('opp-modal').classList.add('active');
    } catch (err) {
        alert('Failed to load opportunity: ' + err.message);
    }
}

function closeModal() {
    document.getElementById('opp-modal').classList.remove('active');
}

// Close modal on overlay click
document.getElementById('opp-modal').addEventListener('click', (e) => {
    if (e.target === document.getElementById('opp-modal')) closeModal();
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// ---------------------------------------------------------------------------
// Save opportunity
// ---------------------------------------------------------------------------
async function saveOpportunity() {
    const id = document.getElementById('opp-id').value;
    const company = document.getElementById('opp-company').value.trim();
    if (!company) {
        alert('Company name is required');
        return;
    }

    const payload = {
        company,
        division: document.getElementById('opp-division').value.trim(),
        contact_name: document.getElementById('opp-contact-name').value.trim(),
        contact_title: document.getElementById('opp-contact-title').value.trim(),
        contact_email: document.getElementById('opp-contact-email').value.trim(),
        contact_linkedin: document.getElementById('opp-contact-linkedin').value.trim(),
        contact_location: document.getElementById('opp-contact-location').value.trim(),
        estimated_value: parseFloat(document.getElementById('opp-value').value) || 0,
        type: document.getElementById('opp-type').value,
        geography: document.getElementById('opp-geography').value,
        stage: document.getElementById('opp-stage').value,
        vertical: document.getElementById('opp-vertical').value.trim(),
        partner: document.getElementById('opp-partner').value.trim(),
        playbook_weapon: document.getElementById('opp-playbook').value,
        owner: document.getElementById('opp-owner').value,
        next_action: document.getElementById('opp-next-action').value.trim(),
        next_action_date: document.getElementById('opp-next-action-date').value,
        notes: document.getElementById('opp-notes').value,
        meddpicc_metrics: document.getElementById('opp-meddpicc-metrics').value,
        meddpicc_decision_criteria: document.getElementById('opp-meddpicc-decision-criteria').value,
    };

    const btn = document.getElementById('modal-save-btn');
    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
        if (id) {
            await api('/api/opportunities/' + id, { method: 'PUT', body: JSON.stringify(payload) });
        } else {
            await api('/api/opportunities', { method: 'POST', body: JSON.stringify(payload) });
        }
        closeModal();
        await Promise.all([loadStats(), loadOpportunities(), loadActivity()]);
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = id ? 'Update' : 'Create';
    }
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
initSortHandlers();
checkAuth();
</script>
</body>
</html>
`;
