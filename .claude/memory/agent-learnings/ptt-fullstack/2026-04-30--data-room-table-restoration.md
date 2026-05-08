# Data Room V3 Table Restoration

**Date**: 2026-04-30
**Type**: operational
**File**: /home/jared/purebrain-site/data-room/index.html

## What was done
Converted paragraph-formatted tabular data back into proper HTML `<table>` elements across multiple sections of the investor data room V3.

## Sections that needed conversion (had paragraph data that should be tables)
- **use-of-funds**: Allocation Summary, Monthly P&L (6-month), Capital Efficiency comparison, Path to Series-A milestones, Series-A reference
- **financial-model**: 6-Month Ramp Earn vs Burn, Burn Breakdown, Revenue by Stream, EBITDA Summary, Subscriber Growth, PureBrain Revenue Breakdown, Per-Subscriber Costs, Delivery Partner Revenue Share, Infrastructure Cost Model, Headcount, Valuation Context, Key Assumptions
- **executive-summary**: Timeline (Seed-2 to Scale), Ramp period objectives
- **gtm-strategy**: ICP segment profiles (SMB/Mid-Market/Enterprise), Campaign Phases & KPIs, Survival Math, Agent Architecture by Tier, Margin Analysis

## Sections that ALREADY had proper tables (no work needed)
- revenue-projections, unit-economics, ramp-plan, customer-traction, competitive-analysis, team-organization, investment-terms, market-opportunity, product-overview, business-overview

## Key patterns
- Used `<span class="highlight-num">` for dollar amounts
- Used `<span class="highlight-orange">` for negative numbers (CSS already defined)
- Used `<strong>` for total/summary rows
- Used `<th>` for header rows
- The file is a single HTML page with JavaScript template literals containing all content
- File is ~663KB with a large base64 image embedded
- 142 tables total after conversion (properly matched open/close)
