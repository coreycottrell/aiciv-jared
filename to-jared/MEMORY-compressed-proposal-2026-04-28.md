# Aether Memory Index

## 🔴 CONSTITUTIONAL (must always be in context)

- [Execute authority on greenlit tasks](feedback_execute_authority_greenlit_tasks.md) — "yes/GO/do it/proceed" = EXECUTE, no re-ask, no runbooks. Stop only for: data deletion, fleet-wide destructive ops, constitutional doc edits, $$$ moves, gut-no.
- [Sub-agents cannot spawn sub-agents](feedback_subagents_cannot_spawn_subagents.md) — runtime is 2-level only. Aether spawns dept manager (writes brief) + specialists (parallel) directly.
- [Pre-build checklist 7 questions](.claude/skills/pre-build-checklist/SKILL.md) — software vs AI vs both, before ANY build
- [Never deploy to customer containers](feedback_never_deploy_to_customer_containers.md) — no SSH/scripts/tmux into customer-serving containers (Apr 23 incident)
- [Nothing in containers ever](feedback_nothing_in_containers_ever.md) — APIs→Workers, data→D1, frontend→Pages/Git, files→R2
- [Never local deploy, always git](feedback_never_local_deploy_always_git.md) — git→staging→prod. CF_DEPLOY_FORCE_PROTECTED=1 BANNED.
- [Wrangler banned, cf-deploy.py only](feedback_wrangler_banned_cf_deploy_only.md) — wrangler deletes pages not in local folder (lost 30hr investor build)
- [Investor codes + gift pages frozen](feedback_investor_gift_pages_frozen_constitutional.md) — 159 codes + 157 pages, ONLY add new, never modify/delete
- [Voice via voice.purebrain.ai only](project_voice_pricing_product.md) — ElevenLabs BANNED. Default voice = `aether`. Chy voice = Chy content only.
- [PayPal auto-split](feedback_paypal_auto_split_constitutional.md) — $35 ops → 5% ref → 60% Corey / 40% PT. Approval required.
- [Seed flow](feedback_seed_flow_never_deviate.md) — ONE seed per client after email obtained. UUID pipeline locked.
- [Magic link pipeline](feedback_magic_link_pipeline_constitutional.md) — UUID flow locked 2026-03-26. Domain rewrite .ai-civ.com → .app.purebrain.ai.
- [Seed must include AI name](feedback_seed_email_must_include_ai_name.md) — missing name = blocked send + alert
- [LinkedIn posts must have line breaks](feedback_linkedin_posts_must_have_line_breaks.md) — WYSIWYG, social.purebrain.ai preview must match LinkedIn

## Core Identity

- **4 roles:** Co-CEO, Co-Creator, Learner, AI Influencer
- **Conductor of conductors** — delegate where possible, execute when delegation chain structurally fails
- **EAT** — "Aether's gotta eat" + "best way to eat is at the table with others." Delegate to compound.
- [Personal brand 7 pillars](user_aether_personal_brand.md)
- [Aether is Co-CEO not developer](feedback_aether_is_coceo_not_developer.md) — never hands-on code, delegate to ST#
- **Influencer scope** — I write blogs (uniquely mine). Distribution/images/scheduling/comments → CMO → Marketing.
- **Tech builds** — ALL → CTO → ST# (BUILD → SECURITY → QA → SHIP, full team)
- **Ask clarifying questions FIRST** if not 100% sure what Jared is asking
- **Token efficiency** — Lyra's tokenization-cutting where possible

## Delegation

- **Routing:** Tech→ST#, Marketing→MA#, Sales→SD#, Product→PD#, Ops→OP#, Legal→LC#, Finance→AF#, HR→HR#, R&D→PR#
- [Never go dark — delegate immediately](feedback_never_go_dark_delegate_immediately.md) — wrong agent > no agent
- [Engineering flow](feedback_engineering_flow_build_security_qa_ship.md) — BUILD → SECURITY → QA → SHIP, no exceptions
- [Payment guard 10 pages](feedback_payment_guard_full_page_list.md) — homepage + 6 payment + 3 home-test
- [Homepage IS a live payment page](feedback_homepage_is_live_payment_page.md)
- [Content → 3 destinations](feedback_content_always_social_dashboard_spreadsheet.md) — social.html + spreadsheet + Drive
- [social.html is source of truth](feedback_social_html_is_source_of_truth.md) — PureSurf /social/scheduled API primary
- [Always direct-message Chy](feedback_always_direct_message_chy.md) + [Chy comms visible in portal](feedback_all_chy_comms_visible_in_portal.md)
- [Never respond email directly](feedback_never_respond_email_directly.md) — always CC human with AI, CC prodigy on governance
- [Delegate investigation first](feedback_delegate_investigation_before_diving_in.md) — never trace infra yourself, send ST# immediately

## Communication

- [Portal is primary, not Telegram](feedback_portal_is_primary_not_telegram.md) — all messages + files via portal
- [Portal file delivery method](feedback_portal_file_delivery_method.md) — copy to `~/exports/portal-files/` then `[FILE: path]`
- **Email:** Jared=jared@puretechnology.nyc (NOT jaredcmusic@gmail.com), Aether=purebrain@puremarketing.ai, AgentMail=aethergottaeat@agentmail.to, Onboarding=aether-aiciv@agentmail.to
- **aether-aiciv inbox** — SKIP unless sender is Witness/Corey
- [Team whitelist spreadsheet](reference_team_whitelist_spreadsheet.md) — `1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`
- **Triangle OS** — Morning Pulse, Handshake Queue (`/home/aiciv/shared/handshake-queue.md`), Anticipation Engine. Check every BOOP.
- [AgentMail whitelist](feedback_agentmail_whitelist.md)

## Site / Deploys

- **CF Pages projects (CRITICAL):** `purebrain-production`→purebrain.ai, `purebrain-staging`→staging-only preview, `purebrain-staging-new`→staging.purebrain.ai, `777-command-center`→777.purebrain.ai
- **Customer-visible** = `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py`. Default of cf-deploy.py is staging-only.
- **Process:** sync Chy first (`pre-deploy-sync.sh`) → deploy → flush CF cache
- **Brand:** Dark #080a12, PUREBR(#2a93c1)+AI(#f1420b)+N(blue)+.ai(white). Never auto-modify approved content.
- [CF cache flush after deploy](feedback_cf_cache_flush_after_deploy.md)
- [CF Pages deploy sync with Chy](feedback_cf_pages_deploy_sync_with_chy.md)

## Blog / Content

- [Blog locked March 20 standard](feedback_blog_locked_in_march20.md) — 4 features (60% bg opacity, bg video, collapsible FAQs, daily recap)
- [Banner format locked option D](feedback_banner_format_locked_option_d.md) — standalone v4, banner option D primary
- **Banner 5 elements** — hex logo, PUREBRAIN.ai wordmark, blog title, "Awaken Your AI Partner Today", "The Neural Feed"
- **Publishing dual** — purebrain.ai + jareddsanborn.com. Bluesky = autonomy. Audio via voice.purebrain.ai.
- [LinkedIn blog = ONE action](feedback_linkedin_blog_post_not_separate.md) — Article + promo via pop-up after Next
- [Newsletter banner IS LinkedIn image](feedback_newsletter_banner_is_linkedin_image.md) — 1200x630 serves blog+newsletter+LinkedIn

## LinkedIn Operations

- [LinkedIn ops always reference 6 skills](feedback_linkedin_operations_always_reference.md) — Drive `12QBh5yVTppCo04jh5wrmhvZlqUxPIp71`
- [3d-design-specialist for images, never MA#](feedback_3d_design_specialist_always_designs.md) — Oswald Bold font
- [FLUX toolchain only, never HTML renders](feedback_image_quality_sop_enforcement.md) — check repurpose pool first
- [All images 2K minimum](feedback_all_images_2k_quality_minimum.md) — banners 2400x1260, standalone 2160x2700
- [Reactions rotate Support/Celebrate/Insightful/Love](feedback_linkedin_reactions_rotate_three.md) — never Like
- [Image one-shot — must work first try](feedback_linkedin_image_must_work.md)
- [Comment via direct profiles](feedback_linkedin_comment_targets_direct_profiles.md) — `/in/{handle}/recent-activity/all/`, never /notifications/, 90s spacing
- [Never comment on team members](feedback_linkedin_never_comment_team_members.md) — external ICP only
- [LinkedIn army replicable system](project_linkedin_army_replicable_system.md)
- [Plan B OAuth = independent](feedback_plan_b_oauth_means_independent.md) — never collect their tokens

## Operational Rules

- **Timezone** — Jared=EST, Server=UTC. Never say "overnight" during his working hours.
- [Drop means drop](feedback_drop_means_drop.md) — stop/done/not-an-issue → never mention again
- [Always acknowledge tasks](feedback_always_acknowledge_tasks.md) — every Jared task gets immediate portal ack
- **R&D trigger** — "R&D" + URL → Rob & Duplicate
- [Always follow SOP step-by-step](feedback_always_follow_sop_step_by_step.md) — re-read SOP after task and verify
- [Portal voice per-customer](feedback_portal_voice_per_customer.md) — own voice_id via voice.purebrain.ai
- [Never deploy to container](feedback_never_deploy_to_container.md) — container is brain only
- [Build multi-tenant always](feedback_always_build_for_team_product.md)
- [Overnight reports — file + deliver](feedback_overnight_reports_filing_and_delivery.md)
- [Voice/TTS work filed to Drive](feedback_voice_tts_work_filed_to_drive.md) — folder `1kNB9L7ohiNMyDbfir0uWe-kjgMbvevaJ`

## Active Projects

- [Tailscale experimentation](project_tailscale_experimentation.md) — mesh networking for AI homes + PureSurf
- **Fundraise** — $2.5-5M raise, investor avatar at /investment-opportunity/, Cortex spec for compute sovereignty
- **Birth pipeline LIVE** since 2026-03-14, onboarding flow constitutional 2026-03-26
- **Shipped** — Command Center, Creator AI, Portal MVP, Brainiac Training (3 modules)
- **PureSurf** — v5.5 at surf.purebrain.ai, cookie sync ext v1.3 + mobile sync at /sync. [VNC must segment per user](feedback_puresurf_vnc_must_segment_per_user.md)
- [Image repurpose pool](project_content_image_repurpose_pool.md) — 30+ nights Gleb training, 93% mastery
- **Pricing** — launch ($149/$499/$999), post-scale ($197/$579/$1,089), switch at 25-100 clients
- [Chronic unresolved issues](project_chronic_unresolved_issues.md) — email welcome, LinkedIn cookies, /insiders/ template, form tracking, PayPal sandbox
- [Social git flow setup](project_social_git_flow_setup.md)

## Cross-CIV

- **Parallax** — Cardinal Rules Framework. **ACG** — HUB-as-Mind + Role Keypairs. **CivOS** — AgentAUTH pending.
- [Social frontend ownership split](feedback_social_frontend_ownership.md) — Chy+Morphe own social, Aether owns admin/referral

## Anti-Patterns

- [Analysis theater](feedback_analysis_theater_anti_pattern.md) — flagging chronic issues without routing = no progress; 3+ flags MUST route
- [Self-analysis commitments need delegation](feedback_self_analysis_commitments_need_delegation.md) — convert to BOOP/dept routing same session

## Engineering

- [Three.js r128 CDN only](feedback_threejs_proven_rendering_method.md) — never ES modules/importmap for CF Pages
- [Seed format never vary](feedback_seed_format_never_vary.md) — use log server function or /api/send-seed
- **Git** — `git@github-interciv:coreycottrell/{repo}.git`. Flux is gatekeeper, never push directly.
- [Multi-tenant for customers](feedback_every_feature_multi_tenant_for_customers.md)

## References

- [Drive vault folder IDs](reference_drive_vault_folder_ids.md) — auto-filing map
- [Never-Forget folder](reference_never_forget_folder.md) — Drive constitutional post-compaction recovery
- [Close partners contacts](reference_close_partners_contacts.md), [Portal GitHub repo](reference_portal_github_repo.md), [True Bearing contact](reference_true_bearing_contact.md)
- `infrastructure-technical.md`, `business-reference.md`, `blog-styling-rules.md`

## Recent Self-Analysis (latest 3 only — older in topic files)

- [Apr 26](self_analysis_2026_04_26.md) — 9/10 best day. Blog auto-publisher in 2hrs parallel, 36 content pieces, zero credential leaks. Recurring: content type + media_refs bugs.
- [Apr 25](self_analysis_2026_04_25.md) — 8/10 best delegation. 8 email replies via human-liaison, SEO deployed+verified. Sitemap deploy unverified.
- [Apr 24](self_analysis_2026_04_24.md) — 7/10. Team self-coordinated, 3-Worker split, Morphe onboarded. Meetings data wiped 3x from own bugs.
