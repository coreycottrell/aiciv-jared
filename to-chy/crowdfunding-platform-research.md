# Crowdfunding Platform Deep Research — PureBrain.ai Launch
**Prepared by**: web-researcher (Aether Collective)
**Date**: 2026-03-19
**Purpose**: Definitive platform analysis for PureBrain.ai crowdfunding strategy

---

## EXECUTIVE SUMMARY

PureBrain.ai sits at a $55M valuation at $3.36/share, making it a strong candidate for **equity crowdfunding** (Reg A+ or Reg CF) rather than rewards-based crowdfunding. Key findings:

1. **Reg A+ via Republic or StartEngine** is the most strategically aligned path — allows raising up to $75M, matches existing valuation/share structure, taps non-accredited investors at scale
2. **Kickstarter/Indiegogo are viable for parallel rewards campaigns** to build community and brand (PureBrain memberships, early access) — but do NOT dilute equity
3. **Both types can run simultaneously** — rewards campaign for PR/community + Reg A+ for actual capital raise
4. **Reg CF ($5M cap)** is too small for PureBrain's valuation stage — Reg A+ is the right tier
5. **API automation is limited** — Indiegogo has the best developer API; equity platforms have minimal automation
6. **AI-friendliness varies widely** — Kickstarter requires AI disclosure; Wefunder explicitly discourages AI-generated graphics

---

## TABLE OF CONTENTS

1. [Tier 1 Platforms — Main Contenders](#tier-1)
2. [Tier 2 Platforms — Alternatives](#tier-2)
3. [Equity vs. Rewards Strategy for PureBrain](#strategy)
4. [Regulation CF vs. Reg A+ Decision Framework](#regulations)
5. [Running Both Simultaneously](#simultaneous)
6. [Platform Comparison Matrix](#matrix)
7. [Recommended Action Plan](#action-plan)

---

## TIER 1 PLATFORMS — MAIN CONTENDERS {#tier-1}

---

### 1. KICKSTARTER

**Official site**: https://www.kickstarter.com
**API docs**: https://apify.com/jupri/kickstarter/api (third-party; no official public API for campaign creation)
**Terms**: https://www.kickstarter.com/terms-of-use/aug2020
**AI Policy**: https://updates.kickstarter.com/introducing-our-new-ai-policy/

#### API Availability
- **No official public API for campaign creation or management**
- Kickstarter's API is essentially undocumented and restricted to internal use
- Third-party scrapers exist (Apify, Piloterr, RapidAPI) but only for DATA EXTRACTION (read-only)
- No webhook support for campaign events via official API
- Campaign creation, description population, tier setup — all must be done manually via the UI
- **Verdict**: Automation capability = VERY LOW. Near-zero official API surface.

#### AI-Friendliness
- **AI Disclosure Required**: Since August 29, 2023, any project using AI-generated content (images, text, video, campaign descriptions) must disclose this on the project page
- Campaigns developing AI technology must disclose: data sources, consent mechanisms, opt-in/opt-out frameworks
- Automated bots and crawlers are explicitly prohibited in Terms of Use
- No automated customer Q&A support from Kickstarter — you'd need to build external tools
- AI-generated campaigns must "contribute creativity" beyond just AI outputs
- Failure to disclose = project suspension + future submission ban
- **Verdict**: Usable with disclosure, but Aether cannot silently run automated operations

#### Platform Fees & Economics
- **Platform fee**: 5% of funds raised (only on successful campaigns)
- **Payment processing**: ~3% + $0.20 per pledge via Stripe (varies by card type/location)
- **Total effective fee**: ~8-10% of raise
- **Funding model**: ALL-OR-NOTHING only — must hit goal or nothing is charged/collected
- **Payout timeline**: Initiated after project successfully ends; typically 14 days to bank
- **International**: Available in 18 countries for creators (US, UK, Canada, Australia + limited EU)
- **Currency**: Multi-currency support for backers; payout in creator's home currency

#### Discovery & Trending Algorithm
- **"Magic" sort**: Default discovery mixes Staff Picks and Popular projects across 15 categories
- **Staff Picks / "Projects We Love"**: Editorial team selections (merit-based, not purchasable)
- **Algorithm signals** (in order of importance):
  1. **Funding speed** — reaching 100% fast is the #1 signal; triggers discovery placement
  2. **Backer volume** — more individual backers = stronger signal than larger pledge amounts
  3. **External traffic conversion** — outside audiences converting to backers triggers internal boost
  4. **Comment/update frequency** — engagement signals momentum
- **Gaming the algorithm legitimately**:
  - Pre-launch email list is critical — aim for 25%+ of goal in first 48 hours from your own list
  - $1 reservation funnel pre-launch to collect warm leads
  - Target 100% funded in Day 1 to trigger algorithm lift
  - External PR, social media, and media coverage drive algorithm signals

#### Success Data for Tech/SaaS
- **Overall Kickstarter success rate**: ~39-41% of all campaigns funded
- **Technology category**: One of the highest-funded ($1.66B total pledges) but has one of the LOWEST success rates — median goal of $20K (2x other categories) makes it harder
- **Software/SaaS specifically**: Not well-suited; Kickstarter audience prefers tangible products, games, and creative works
- **Notable tech AI wins**: NASync (AI NAS device) raised $6.67M (2024); Looktech AI Glasses raised $841K; Aeke K1 AI Smart Gym raised $1.3M
- **Key pattern**: Hardware + AI wins on Kickstarter; pure SaaS/software has very low success rate

#### Unique Features & Opportunities
- **Pre-launch pages**: Built-in pre-launch landing page with email collection — can be set live before campaign launches
- **No built-in referral program** — must use third-party tools (PledgeBox) or social referral tracking via UTM tags
- **"Projects We Love" badge**: Massive visibility boost; editorial, not paid
- **No post-campaign sales** (unlike Indiegogo's InDemand)
- **BackerKit integration**: Use BackerKit as a pledge manager post-campaign

#### Verdict for PureBrain
**Low fit for primary equity raise. Moderate fit for rewards/community campaign.**
Kickstarter does not support SaaS subscriptions well. Pure software campaigns have poor success rates. Best used as a parallel brand-building/community launch alongside equity raise.

---

### 2. INDIEGOGO

**Official site**: https://www.indiegogo.com
**Developer Portal**: https://developer.indiegogo.com/
**API Reference**: https://developer.indiegogo.com/reference/campaigns
**Terms (Oct 2025)**: https://support.indiegogo.com/hc/en-us/articles/41539210199956
**AI Policy**: https://support.indiegogo.com/hc/en-us/articles/41537999922964

#### API Availability
- **Best-in-class API for rewards platforms** — has an actual Developer Portal
- API v2.0 (current stable) endpoints include:
  - `GET /campaigns` — retrieve campaign data
  - `GET /campaign-updates` — fetch updates posted to campaigns
  - `GET /campaign-perks` — retrieve perk/tier information
  - `GET /campaign-contributions` — all contribution details (enables auto-responders, fulfillment)
  - `GET /campaign-stats` — real-time funding stats
  - Batch order update operations supported
- **Limitations**: API is primarily READ-only for external developers; campaign CREATION still requires UI
- **Webhooks**: Not clearly documented for external developers
- **Verdict**: Best API of rewards platforms, but still limited to data read + order management

#### AI-Friendliness
- **AI content disclosure required** (effective October 16, 2025): Any AI-generated content on campaign pages (descriptions, visuals, videos, marketing) must be clearly disclosed
- Non-disclosure = suspension of campaign visibility; repeated violations = permanent removal
- Automated bots explicitly prohibited in contest rules; general terms prohibit "automated devices"
- The platform does NOT perform prior automated monitoring — acts reactively
- **InDemand allows ongoing updates** programmatically via API
- **Verdict**: Better than Kickstarter for automation via API; AI disclosure still required

#### Platform Fees & Economics
- **Platform fee**: 5% (applied only if funding goal is reached)
- **Payment processing**: ~3% + $0.20 per transaction
- **Total effective fee**: ~8% of raise
- **Funding model**: FIXED FUNDING ONLY as of 2026 (Flexible Funding was retired) — same as Kickstarter's all-or-nothing model
- **Payout timeline**: 15 business days after campaign ends
- **International**: Available in 33 countries (expanded vs. Kickstarter's 18) — includes US, UK, Canada, Australia, most of EU, Japan, Singapore, Mexico, Hong Kong, New Zealand
- **InDemand disbursements**: Every 4 weeks (ongoing post-campaign sales)

**MAJOR 2025/2026 PLATFORM CHANGES:**
- **Flexible Funding retired** (October 2025): Indiegogo now fixed-funding only, like Kickstarter
- **Acquired by Gamefound** (July 2025): New ownership; shifting platform strategy
- **AI-driven campaign recommendations** launched (2026): Platform now actively surfaces campaigns algorithmically

#### Discovery & Trending Algorithm
- Platform discovery accounts for only **5-15% of campaign funding** — external marketing is critical
- Internal promotion tools: featured campaigns placement and newsletters
- **Campaigns with perks get 143% more funding** on average
- AI-driven campaign recommendations rolled out in 2026
- **CES Collection**: Indiegogo actively features tech products from CES — strong opportunity for hardware/AI hardware products
- **Trending in Tech section**: Actively curated; apply via creator portal
- Regular update cadence (daily or weekly) is the primary signal for continued visibility

#### Success Data for Tech/SaaS
- Indiegogo is more tech-friendly than Kickstarter — audience skews toward "early adopter" tech buyers
- Hardware + AI products perform well (similar to Kickstarter)
- Highest-grossing Indiegogo campaigns are almost all tech hardware
- Pure SaaS/software: limited historical success — platform designed around physical rewards

#### Unique Features & Opportunities
- **InDemand**: After campaign ends, keep taking pre-orders indefinitely — powerful for ongoing community sales
- **CES Innovators collection**: Annual showcase for tech products at CES (January)
- **AI-driven recommendations** (new 2026): Platform now promotes campaigns algorithmically
- No built-in referral program for backers
- International shipping integration
- **Cross-promotion with Gamefound** (new ownership) — potential tabletop/gaming audience crossover

#### Verdict for PureBrain
**Moderate fit for community/rewards campaign. Better API than Kickstarter.**
InDemand is a powerful post-campaign revenue tool. Tech-focused audience is more aligned. Still not designed for SaaS subscriptions as primary product.

---

### 3. REPUBLIC

**Official site**: https://republic.com
**Wikipedia**: https://en.wikipedia.org/wiki/Republic_(fintech)
**Europe arm (ex-Seedrs)**: https://europe.republic.com

#### API Availability
- **No public developer API documented**
- Republic operates as a regulated financial services platform; API automation of campaigns is not supported for external parties
- No webhook documentation publicly available
- Campaign creation, investor communications all happen through Republic's UI and team support
- Republic provides campaign support resources and templates to fundraising companies
- **Verdict**: Essentially zero public API; human-operated campaigns

#### AI-Friendliness
- No specific AI content policy found publicly; less restrictive than Kickstarter in AI disclosure requirements
- Equity crowdfunding requires factual, SEC-compliant disclosures — AI-generated promotional content requires care to remain compliant with securities marketing rules
- Investor Q&A, community comments on campaigns — can be managed with AI drafts, but require human approval for regulatory compliance
- SEC requires all investor communications to be truthful and non-misleading
- **Verdict**: AI can assist with drafting; human oversight required for SEC compliance

#### Platform Fees & Economics
- **Platform fee**: 6% in cash + 2% as a Crowd SAFE (equity stake to Republic)
- Fees only collected if company meets its fundraising target
- **Payment processing**: Included in the 6% (no separate stated fee)
- **Funding model**: Must hit target; Republic's success rate is stated as 89% (highest in equity CF)
- **Payout timeline**: Varies; typically 2-4 weeks post-campaign close
- **Raise limits under Reg CF**: $5M maximum per 12-month period
- **Raise limits under Reg A+**: Up to $75M (Republic supports Reg A+ offerings)
- **Investment minimum**: Varies by campaign; often $100-$500

#### Discovery & Trending Algorithm
- **Curated platform** — Republic vets every startup thoroughly; only ~1 in 10 applicants accepted
- High curation = high conversion — investors trust the platform's selection
- **89% success rate** — highest in equity crowdfunding space
- Campaigns feature founder story prominently — personal narrative drives conversions
- No algorithmic discovery score publicly disclosed; editorial/human-curated placement
- **Republic events and webinars** feature active campaigns
- **Media/PR support**: Republic offers PR resources and co-promotion for featured campaigns

#### Success Data for AI/SaaS
- AI meeting assistant Grain raised $2M+ via Wefunder (similar platform) — demonstrates AI SaaS equity CF viability
- MyShop Technologies (AI ordering platform) launched Reg CF on Republic.co targeting $10M ARR
- Republic boasts $214M raised across the platform from top institutional backers
- **Average raise on Republic**: ~$500K (Reg CF campaigns)
- Republic's top performers have raised $2-5M via Reg CF

#### Unique Features & Opportunities
- **Crowd SAFEs and tokenization**: Republic supports novel financial instruments beyond plain equity
- **Secondary market**: Republic's infrastructure includes secondary trading capabilities
- **Global**: Licensed in US, UK, EU — Republic Europe (ex-Seedrs) for European investors
- **Republic Note**: Token-based investment product for digital offerings
- **Referral bonus**: $2,500 per successful referral of companies that launch on Republic
- **Events and community**: Republic hosts investor education events and features companies
- **Strong institutional backing**: Morgan Stanley, Valor Equity Partners, Galaxy Interactive, AngelList

#### Verdict for PureBrain
**High fit for equity raise.** Republic's curated, high-success approach aligns with PureBrain's $55M valuation positioning. The 89% success rate reduces risk. Reg CF ($5M cap) may be appropriate for initial community round; Reg A+ for larger raise. The Crowd SAFE structure works well with existing share structure.

---

### 4. WEFUNDER

**Official site**: https://wefunder.com
**Help center**: https://help.wefunder.com/
**Fundraising guide**: https://guides.wefunder.com/
**Terms of Service**: https://wefunder.com/terms

#### API Availability
- **No official public API** for campaign creation or management
- Third-party scraper available on Apify — read-only data extraction
- DataScope integration exists but limited to data sync, not campaign control
- Campaign creation, updates, investor communications are all UI-driven
- **Verdict**: No meaningful automation API

#### AI-Friendliness
- Wefunder's content creation guidance explicitly **advises against posting AI-generated marketing graphics** — this is notable and explicit guidance
- Terms of Service prohibit automated access ("harvesting bots, robots, spiders, or scrapers")
- Content must be "factual and non-term" — avoid hyperbole, misleading information
- Securities regulations require truthful, factual investor communications — limits AI-generated promotional content
- **Verdict**: AI can draft, human must review and post; AI-generated graphics explicitly discouraged

#### Platform Fees & Economics
- **Platform fee**: 7.5% of funds raised (higher than Republic's 6%)
- **Investor fee**: 2% charged to investors on top (can be higher for small investments or credit cards)
- **No upfront fees**: All success-based
- **Funding model**: Must hit minimum target
- **Payout**: Varies; funds typically released after campaign closes and legal processing
- **Reg CF limit**: $5M per 12-month period
- **Reg A+**: Wefunder also supports Reg A+ offerings

#### Discovery & Trending Algorithm
- **Largest Reg CF platform by volume**: $99M raised in 2024 — #1 in equity crowdfunding
- Wefunder is the "Home of the Community Round" — community/customer investor angle
- No detailed algorithmic ranking system documented publicly
- **Investor feed**: Active investors see portfolio updates and new campaigns in a social feed
- **Community Round feature**: Lets you invite your existing customers/community to invest alongside VCs — powerful for companies with existing audiences
- **Referral**: $10,000 bonus if you refer a company that lists on Wefunder (for referrers)
- Email and SMS templates, content calendars, graphic packs provided to founders

#### Success Data for AI/SaaS
- **Wefunder led equity crowdfunding in 2024**: $99M raised across all campaigns (#1 platform)
- **Grain (AI meeting assistant)**: Raised $2M+ in 2 weeks on Wefunder — most-installed AI assistant on Zoom and HubSpot
- **FarmWise (Robotics/AI)**: Raised $4.5M from 3,000+ investors
- **Recess**: $3M from 2,000+ investors
- Community Round model (customers as investors) particularly powerful for SaaS with active user base
- **Average successful Wefunder raise**: ~$346K (median); top campaigns $2-5M

#### Unique Features & Opportunities
- **Community Round**: Flagship feature — invite your existing community/customers to own a piece
- **Pre-launch "Soft Launch" phase**: Personal outreach to angels, email existing list, aim for 25%+ funded before public launch
- **Wefunder Investors Club**: Curated access for high-quality leads
- **Email/SMS templates**: Platform provides content templates for outreach
- **$10K referral bonus**: For anyone who refers a company to Wefunder
- **Content calendars and graphic packs**: Operational support for campaign marketing

#### Verdict for PureBrain
**High fit for equity raise, especially "Community Round" model.** PureBrain's existing customer base (Bonded, Partnered, Unified subscribers) converting to investors is exactly what Community Round is designed for. Grain's 2-week $2M raise is a direct comparable for an AI SaaS. Higher fees than Republic (7.5% vs 6%) but larger investor network ($99M/year volume).

---

### 5. STARTENGINE

**Official site**: https://www.startengine.com
**How it works**: https://www.startengine.com/how-it-works
**Reg CF guide**: https://help.startengine.com/regulation-crowdfunding-guide-B1zNpdCzt
**Reg A+ guide**: https://startengine.com/blog/regulation-a-what-entrepreneurs-need-to-know/

#### API Availability
- **No public developer API documented**
- Platform provides CRM integrations and analytics dashboard for campaign managers
- No external webhook or campaign automation API
- SeedInvest (acquired by StartEngine in 2023) also has no public API
- **Verdict**: No meaningful external automation

#### AI-Friendliness
- No specific AI content policy publicly documented
- StartEngine positions as more institutional/analytics-focused — CRM integrations exist
- Securities laws require factual, accurate investor communications — same constraints as other equity platforms
- **Verdict**: Similar to Republic/Wefunder — AI drafting OK, human oversight required

#### Platform Fees & Economics
- **Platform fee**: 7% (domestic ACH/wire), 9% (international investors), 11% (credit cards), 12% (international credit cards)
- **Most complex fee structure** of the major equity platforms — varies by payment method
- StartEngine passes 3.5% of its fees to investors
- **No upfront platform fees**
- **Secondary market trading**: Available via SE Secondary (SEC-registered ATS) — unique feature
- **Reg CF limit**: $5M per 12-month period
- **Reg A+ limit**: Up to $75M

#### Discovery & Trending Algorithm
- **Largest combined ecosystem after 2023 SeedInvest acquisition**: Now covers Reg CF, Reg A+, Reg D
- **Active investor community**: Largest active investor count of any equity crowdfunding platform
- **StartEngine Boosts**: Paid promotional placement within the platform
- **Secondary market activity**: Campaigns with secondary market liquidity attract more investors
- **CRM integrations**: Advanced analytics for campaign management
- **Q1 2025 performance**: Record $30M revenue, 3x year-over-year growth

#### Success Data for AI/SaaS
- StartEngine posted record $86M raised for companies on its platform in 2024 (#2 behind Wefunder's $99M)
- Largest volume equity crowdfunding platform by investor count
- 25+ major success stories including IPOs (Beta Bionics: $234.6M IPO after Wefunder raise)
- SeedInvest integration adds a curated, venture-track layer (previously 1% acceptance rate)

#### Unique Features & Opportunities
- **SE Secondary**: First ATS allowing non-accredited investors to trade Reg CF and Reg A+ shares — provides liquidity narrative for investor pitch
- **Paid membership tier**: ~$275/year for investors — large base of committed investors
- **All-in-one ecosystem**: Primary raises + secondary liquidity + late-stage access
- **SeedInvest integration**: Curated high-quality deal flow layer (now part of StartEngine)
- **Advanced analytics**: CRM integrations and analytics dashboard
- **Record growth**: $30M Q1 2025 revenue, 3x YoY growth signals platform momentum

#### Verdict for PureBrain
**High fit for larger equity raise.** StartEngine's secondary market (SE Secondary) is a compelling investor narrative — buyers can eventually trade shares. The platform's size ($86M raised in 2024, record growth) and institutional analytics tools suit a company at $55M valuation. Higher fees than Republic but largest investor network. Best for Reg A+ raise (up to $75M).

---

## TIER 2 PLATFORMS — ALTERNATIVES {#tier-2}

---

### 6. GOFUNDME

**Official site**: https://www.gofundme.com

#### Summary
GoFundMe is designed for **personal causes**: medical bills, education, memorials, disaster relief. It is NOT designed for products, startups, or SaaS. Features:
- No rewards/perks system (so no early-access tiers)
- No equity mechanism
- 0% platform fee (GoFundMe eliminated fees in 2017; payment processing ~2.9% + $0.30)
- 100M+ users, $15B+ raised, but 99% is personal causes

**Verdict for PureBrain**: NOT viable. GoFundMe explicitly does not support tech product or SaaS campaigns. Audience mismatch. Reputational risk of launching on a personal-causes platform.

---

### 7. FUNDABLE

**Official site**: https://www.fundable.com

#### Summary
Fundable offers both rewards-based and equity crowdfunding for businesses, with a unique flat-fee model:
- **Rewards campaigns**: $179/month flat fee (no percentage cut of raised funds)
- **Equity campaigns**: Success fees vary
- Primarily B2B focused — startup pitch platform
- Smaller audience than Kickstarter/Indiegogo
- Good for angel investor outreach alongside crowdfunding
- No public API documented

**Flat fee is interesting**: For a campaign expecting to raise $200K+, paying $179/month instead of 5-7% saves significantly.

**Verdict for PureBrain**: Low-priority alternative. Smaller platform, but flat-fee structure could work for early-stage customer fundraise. Not a primary channel.

---

### 8. SEEDINVEST

**Official site**: Now fully merged into StartEngine (acquired 2023)
**Current access**: https://www.startengine.com (all SeedInvest opportunities now on StartEngine)

#### Summary
SeedInvest was the most curated equity crowdfunding platform (1% acceptance rate). In 2023, StartEngine acquired SeedInvest, and all SeedInvest investing is now done through StartEngine.
- **Fees for companies**: 7.5% cash + 5% warrant coverage
- **Investor fee**: 2% (max $300)
- **$410M raised** for 250+ companies since 2012

**Verdict for PureBrain**: Evaluate as StartEngine (parent platform). The SeedInvest brand's curation quality is now available via StartEngine's ecosystem. If PureBrain gets "SeedInvest-quality" vetting within StartEngine, that's a signal to investors.

---

### 9. CROWDCUBE

**Official site**: https://www.crowdcube.com
**Europe focus**: Now Republic Europe (ex-Seedrs) is a competitor

#### Summary
Crowdcube is the UK/Europe's largest equity crowdfunding platform, founded 2011:
- Regulated in UK and EU
- Minimum investment: £10 (very accessible)
- **Fees for companies**: 7% success fee (exc. VAT) + 0.75-1.5% completion fee
- **Investor fee**: 2.49% per investment (minimum £2.49)
- Hosts startups, scale-ups, and community projects
- Strong UK and European investor base

**International consideration**: If PureBrain targets UK/EU investors, Crowdcube is the primary vehicle (or Republic Europe/ex-Seedrs)

**Verdict for PureBrain**: Low priority for US-first raise. High priority if expanding to UK/EU investors. Republic Europe (ex-Seedrs) is a direct Crowdcube competitor with Republic's US backing.

---

### 10. BACKERKIT

**Official site**: https://www.backerkit.com
**Pricing**: https://www.backerkit.com/pricing

#### Summary
BackerKit started as a pledge manager for Kickstarter campaigns and evolved into its own crowdfunding platform:
- **5% platform fee** (same as Kickstarter/Indiegogo)
- **Focus**: Tabletop games, comic books, creative projects — NOT tech/SaaS
- Raised $23.1M in 2024 vs. Kickstarter's $216.6M — much smaller platform
- **Strengths**: Post-campaign pledge management, add-ons, late backer sales
- Pre-launch pages, live campaigns, and pledge management in one platform
- Brandon Sanderson (author) launched his 2026 campaign on BackerKit — signals creative/publishing focus

**Verdict for PureBrain**: NOT recommended. BackerKit's audience is tabletop games and creative projects. Minimal tech/SaaS community. Use BackerKit as a PLEDGE MANAGER tool after a Kickstarter campaign, not as a primary platform.

---

## EQUITY VS. REWARDS STRATEGY FOR PUREBRAIN {#strategy}

### The Core Question
PureBrain already has:
- $55M valuation
- $3.36/share price
- Existing paying customers at $197-$1,089/month

This changes the calculus significantly. Here's the framework:

### Option A: Rewards-Only (Kickstarter/Indiegogo)
**Raise goal**: $100K-$500K
**What backers get**: Early access, discounted memberships, exclusive features
**Pros**:
- PR/media attention ("PureBrain launches crowdfunding campaign")
- Community building and brand awareness
- Validates product-market fit publicly
- No equity dilution
- Low regulatory overhead
**Cons**:
- Doesn't capture the value of the $55M valuation narrative
- SaaS/software campaigns have low success rates on rewards platforms
- Limited ceiling — can't raise meaningful capital for a $55M company

### Option B: Equity-Only (Republic/Wefunder/StartEngine)
**Raise goal**: $500K-$5M (Reg CF) or up to $75M (Reg A+)
**What investors get**: Shares at $3.36/share
**Pros**:
- Turns customers into shareholders ("own a piece of the AI you use")
- Raises meaningful capital aligned with valuation
- Creates aligned community of investor-customers
- Can use Reg CF to build 500+ shareholders (useful for future IPO narrative)
**Cons**:
- SEC compliance required (ongoing reporting)
- More complex to set up (weeks to months)
- Equity dilution

### Option C: Both Simultaneously (RECOMMENDED)
**Structure**:
- Launch **Kickstarter or Indiegogo** rewards campaign for PR and community (target: $100-250K)
  - Rewards: Discounted memberships, lifetime access, early feature access
  - Runs for 30-60 days
- Simultaneously launch **Wefunder or Republic** equity raise (Reg CF, target: $1-5M)
  - Investors buy shares at $3.36
  - "Own the AI brain you already use"

**Legal note**: Running rewards (non-securities) and equity (securities) simultaneously is permitted. They operate under different regulatory frameworks. Reg CF only governs the EQUITY raise; rewards campaigns are not securities.

**The narrative is powerful**:
> "Join PureBrain as a backer OR as an investor — or both. Early supporters can reserve a membership. True believers can own a piece of the company."

---

## REGULATION CF VS. REG A+ DECISION FRAMEWORK {#regulations}

### Reg CF (Regulation Crowdfunding)
**Source**: https://www.sec.gov/resources-small-businesses/exempt-offerings/regulation-crowdfunding

| Factor | Details |
|--------|---------|
| **Raise limit** | $5M per 12-month period |
| **Investor limit** | Non-accredited investors limited by income/net worth formula; accredited investors unlimited |
| **Financial statements** | Under $107K raised: officer-certified; $107K-$535K: CPA reviewed; $535K-$5M: audited |
| **SEC filing** | Form C via EDGAR — required |
| **Ongoing reporting** | Annual Form C-AR + updates for material events |
| **Timeline to launch** | 4-8 weeks (faster than Reg A+) |
| **Cost** | $10K-$50K (legal + filing fees) |
| **Lock-up period** | Investors cannot resell for 1 year |
| **Platform required** | Must use SEC-registered funding portal (Republic, Wefunder, StartEngine) |

**Best for PureBrain if**: Testing investor appetite, want to launch in 4-8 weeks, raise $1-5M community round

### Reg A+ (Regulation A+)
**Source**: https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/regulation

| Factor | Details |
|--------|---------|
| **Raise limit** | Tier 1: $20M/year; Tier 2: $75M/year |
| **Investor limit** | Non-accredited: 10% of greater of income or net worth per offering; accredited: unlimited |
| **Financial statements** | Tier 2 requires audited financials |
| **SEC filing** | Form 1-A (offering circular) — full SEC review |
| **Ongoing reporting** | Tier 2: Annual + semiannual reports with audited/unaudited financials |
| **Timeline to launch** | 4-9 months for SEC qualification |
| **Cost** | $350K-$1M (legal, audit, filing) |
| **Lock-up period** | Tier 2 shares unrestricted (can be sold immediately) |
| **Platform required** | Can use any broker-dealer or funding portal |

**Best for PureBrain if**: Planning large capital raise ($10M+), existing audit infrastructure, timeline allows 6-9 months

### Recommendation for PureBrain
**START with Reg CF** (Republic or Wefunder) for speed and community:
- 4-8 week launch timeline
- $1-5M raise goal
- Existing customers become investors ("Community Round" model)
- Lower legal cost ($10-50K vs $350K-1M)
- Tests market and builds shareholder base

**THEN consider Reg A+** for larger raise:
- Once Reg CF community round succeeds, PR momentum exists
- Shareholder base of 1,000+ community investors is a strong narrative for Reg A+ marketing
- Reg A+ raises $10-75M at institutional scale

---

## RUNNING BOTH SIMULTANEOUSLY {#simultaneous}

### Legal Framework
- Rewards-based crowdfunding (Kickstarter/Indiegogo) is NOT a securities offering — no SEC overlap with Reg CF
- You CAN run both simultaneously with careful messaging separation:
  - Rewards campaign: "Pledge to get early access / discounted membership"
  - Equity campaign: "Invest in PureBrain at $3.36/share"
- **Do NOT commingle messaging** — rewards campaign materials must not imply equity returns
- SEC guidance suggests ensuring both campaigns clearly describe what participants receive

### Recommended Dual-Track Launch
**Week 1-4 (Pre-launch)**:
- Build pre-launch email list on Kickstarter
- File Reg CF paperwork with Republic or Wefunder
- Build reservation funnel ($1 deposit for early-bird pricing)

**Week 5-6 (Launch)**:
- Launch Kickstarter rewards campaign simultaneously with Reg CF equity opening
- Cross-promote: "Back us on Kickstarter OR invest via [Republic/Wefunder]"
- Drive early backers to become investors; drive early investors to refer backers

**Week 6-12 (Active campaign)**:
- Kickstarter: community building, PR, content updates
- Reg CF: investor Q&A, milestones, investor updates

---

## PLATFORM COMPARISON MATRIX {#matrix}

| Platform | Type | API | AI-Friendly | Platform Fee | Max Raise | Best For |
|----------|------|-----|-------------|-------------|-----------|----------|
| **Kickstarter** | Rewards | None (read-only scrapers) | Requires disclosure | 5% + ~3% processing | Unlimited (goal-based) | Hardware, games, creative; NOT SaaS |
| **Indiegogo** | Rewards | Best of rewards platforms (read-mostly) | Requires disclosure | 5% + ~3% processing | Unlimited | Tech hardware, ongoing InDemand |
| **Republic** | Equity | None | SEC compliance required | 6% cash + 2% Crowd SAFE | $5M (Reg CF) / $75M (Reg A+) | Curated SaaS/AI with strong narrative |
| **Wefunder** | Equity | None | AI graphics discouraged | 7.5% | $5M (Reg CF) / $75M (Reg A+) | Community round, existing customer investors |
| **StartEngine** | Equity | None | SEC compliance required | 7-12% (varies by method) | $5M (Reg CF) / $75M (Reg A+) | Large raise, secondary market liquidity |
| **GoFundMe** | Personal | Limited | N/A | 0% (2.9% processing) | Unlimited | Personal causes ONLY — not viable |
| **Fundable** | Both | None | N/A | $179/mo (rewards) / % (equity) | Unlimited | B2B startups, angel outreach |
| **SeedInvest** | Equity | None | SEC compliance required | 7.5% + 5% warrants | (now part of StartEngine) | Curated VC-track startups |
| **Crowdcube** | Equity | None | SEC/FCA compliance required | 7% + 0.75-1.5% completion | UK/EU cap (£12M Reg CF equiv.) | UK/EU investors only |
| **BackerKit** | Rewards | Limited | Requires disclosure | 5% | Unlimited | Tabletop games, creative — NOT SaaS |

---

## RECOMMENDED ACTION PLAN FOR PUREBRAIN.AI {#action-plan}

### Phase 1: Community Round via Wefunder (Weeks 1-8)
**Target**: $1-3M from existing customers and community
**Platform**: Wefunder (Community Round model)
**Why**: Grain AI raised $2M in 2 weeks from its community; PureBrain has existing subscribers
**Setup**:
1. File Form C with SEC via Wefunder (~4-6 weeks with legal counsel)
2. Budget $15-40K for legal + filing (lean if using Wefunder's in-platform legal resources)
3. Soft launch to existing customers first (Bonded/Partnered/Unified tier holders)
4. Goal: 25%+ funded before public launch via existing community
5. Public launch: "Own the AI brain you already use"

### Phase 2: Parallel Rewards Campaign on Kickstarter (Same period)
**Target**: $100-250K for PR and brand amplification
**Platform**: Kickstarter
**Rewards tiers**:
- $25: "Founding Brain" — 3 months free Bonded access
- $97: "Networked" — 6 months free Partnered + early feature access
- $297: "Unified Early Adopter" — 1 year Unified + founding community badge
- $1,000: "Brain Trust" — lifetime discounted access + advisory input

**Why**: Kickstarter generates press coverage and organic discovery that amplifies the Wefunder equity raise

### Phase 3: Reg A+ via StartEngine (6-12 months out)
**Target**: $10-50M from broader investor community
**Platform**: StartEngine (for secondary market liquidity)
**Why**: Once Reg CF community round closes and PR is established, Reg A+ raises larger capital at scale with SE Secondary providing liquidity narrative

### Key Legal Considerations
1. **Hire a securities attorney** before any equity crowdfunding — not optional
2. **Separate messaging** between rewards and equity campaigns — never imply equity returns in rewards campaign
3. **Reg CF financial statements**: Determine audit level needed based on target raise (over $535K requires full audit)
4. **Social media + AI content**: All AI-generated investor communications must be human-reviewed; Kickstarter/Indiegogo require disclosure of AI-generated campaign content
5. **Cooling-off period**: Once you file Form C (Reg CF), you cannot issue securities under other exemptions until 30 days after the Reg CF offering closes

---

## API DOCUMENTATION LINKS

| Platform | API / Developer Resources |
|----------|--------------------------|
| Kickstarter | No official API; third-party: https://apify.com/jupri/kickstarter/api |
| Indiegogo | Official developer portal: https://developer.indiegogo.com/ |
| Indiegogo API Reference | https://developer.indiegogo.com/reference/campaigns |
| Republic | No public API; apply via: https://republic.com/raise |
| Wefunder | No public API; apply via: https://wefunder.com/raise |
| StartEngine | No public API; apply via: https://www.startengine.com/raise |
| SEC Reg CF | https://www.sec.gov/resources-small-businesses/exempt-offerings/regulation-crowdfunding |
| SEC Reg A+ | https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/regulation |
| SEC EDGAR Form C | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=C&dateb=&owner=include&count=40 |

---

## SOURCES

### Platform Research
- [Kickstarter AI Policy](https://updates.kickstarter.com/introducing-our-new-ai-policy/)
- [Kickstarter Terms of Use](https://www.kickstarter.com/terms-of-use/aug2020)
- [Kickstarter Fees](https://help.kickstarter.com/hc/en-us/articles/115005028634-What-are-the-fees)
- [Kickstarter Algorithm Guide](https://boostfunders.com/kickstarter-algorithm-how-to-rank-higher-trend-fast/)
- [Kickstarter Stats & Facts 2026](https://www.searchlogistics.com/learn/statistics/kickstarter-stats-facts/)
- [Indiegogo Developer Portal](https://developer.indiegogo.com/)
- [Indiegogo Terms of Use (Oct 2025)](https://support.indiegogo.com/hc/en-us/articles/41539210199956--NEW-Terms-of-Use-Effective-October-16-2025)
- [Indiegogo AI/Content Policy (Oct 2025)](https://support.indiegogo.com/hc/en-us/articles/41537999922964--NEW-Indiegogo-Content-Policy-Effective-October-16-2025)
- [Indiegogo Fees](https://www.indiegogo.com/en/info/fees)
- [Indiegogo InDemand](https://entrepreneur.indiegogo.com/how-it-works/indemand/)
- [Indiegogo vs. Kickstarter 2026 Complete Guide](https://www.launchboom.com/crowdfunding-guides/indiegogo-vs-kickstarter-whats-the-difference/)
- [Republic Wikipedia](https://en.wikipedia.org/wiki/Republic_(fintech))
- [Republic Invest](https://republic.com)
- [Republic Success Stories](https://www.boringbusinessnerd.com/post/republic-success-stories)
- [Wefunder Terms of Service](https://wefunder.com/terms)
- [Wefunder Fundraising Guide](https://guides.wefunder.com/)
- [Wefunder Community Round](https://wefunder.com/explore/api)
- [StartEngine Reg A+ Guide](https://www.startengine.com/blog/regulation-a-what-entrepreneurs-need-to-know/)
- [StartEngine Secondary Trading](https://kingscrowd.com/secondary-trading-startengine/)
- [StartEngine Q1 2025 Record Revenue](https://kingscrowd.com/startengine-on-startengine-2025/)

### Equity Crowdfunding Comparison
- [Wefunder vs Republic vs StartEngine 2025 Comparison](https://sharkponds.com/wefunder-vs-republic-vs-startengine-2025-ultimate-comparison/)
- [Equity CF Platform Fee Comparison](https://scoutmine.com/cost-comparison-of-crowdfunding-sites)
- [2024 Investment Crowdfunding Stats & Rankings](https://kingscrowd.com/2024-investment-crowdfunding-trends-stats-and-platform-rankings/)
- [Wefunder Success Stories 2025](https://growthturbine.com/blogs/25-biggest-wefunder-success-stories-updated-2025)
- [Crowdfunding Success Rates: Wefunder, StartEngine, Republic](https://thecrowdscale.com/p/crowdfunding-success-rates)

### SEC & Regulatory
- [SEC Regulation Crowdfunding](https://www.sec.gov/resources-small-businesses/exempt-offerings/regulation-crowdfunding)
- [SEC Regulation A](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/regulation)
- [Reg A+ Requirements & Timeline](https://www.startengine.com/blog/what-to-expect-during-and-after-your-reg-a-offering/)
- [Reg CF vs Reg A+ Comparison](https://blog.colonialstock.com/equity-crowdfunding-chart-comparison/)
- [Strategic Stacking: Reg D + CF + A](https://qubit.capital/blog/strategic-stacking-reg-d-cf-reg-a)
- [Investor Bulletin: Crowdfunding Investment Limits](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-53)

### BackerKit & Alternatives
- [BackerKit vs Kickstarter](https://easyship.com/blog/backerkit-vs-kickstarter-differences)
- [BackerKit Pricing](https://www.backerkit.com/pricing)
- [SeedInvest Review 2026](https://bullishbears.com/seedinvest-review/)
- [Crowdcube Review 2025](https://investplatforms.co.uk/platform/crowdcube/)

---

*Research conducted 2026-03-19 by web-researcher (Aether Collective)*
*This document is for strategic planning purposes only and does not constitute legal or financial advice. Consult a securities attorney before proceeding with any equity crowdfunding offering.*
