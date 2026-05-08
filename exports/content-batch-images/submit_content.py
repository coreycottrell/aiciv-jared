#!/usr/bin/env python3
"""Submit all 13 content items from Apr 24-27 batch to social.purebrain.ai API."""

import json
import time
import requests

TOKEN = open("/tmp/social_token.txt").read().strip()
API = "https://social-api.in0v8.workers.dev/api"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# R2 keys from uploads
R2_KEYS = {
    "purebrain-vs-va-cost": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979004436-db525e20-purebrain-vs-va-cost-standalone.jpg",
    "6-months-ai-partner": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979005845-036cff0d-6-months-ai-partner-standalone.jpg",
    "147k-question-ai": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979007207-7649dbaa-147k-question-ai-standalone.jpg",
    "35-businesses-named-ai": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979008573-44e188b2-35-businesses-named-ai-standalone.jpg",
    "10000-lines-ai-wrote": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979009992-7732a8fe-10000-lines-ai-wrote-standalone.jpg",
    "day1-vs-month6-ai": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979011430-f6bbe23d-day1-vs-month6-ai-standalone.jpg",
    "best-context-not-best-models": "f15527f5-559c-4799-92e3-4b2de2e27897/1776979012864-729d9b73-best-context-not-best-models-standalone.jpg",
}

SOCIAL_ACCOUNT_ID = "a325193d-4a8e-40ba-ab20-c86b5a72f0b7"

CONTENT_ITEMS = [
    # --- STANDALONE 1 (Apr 24, 1pm) ---
    {
        "title": "PureBrain vs Hiring a VA: Real Cost Breakdown",
        "body": "I ran the numbers on hiring a virtual assistant vs using an AI partner.\n\nA good VA costs $1,500-$3,000/month. They work 8 hours a day. They take vacation. They need onboarding. They forget things you told them last quarter.\n\nAn AI partner costs $149/month. It works 24/7. It never takes a sick day. And it remembers every single detail about your business from the first conversation forward.\n\nBut here is the part nobody talks about:\n\nThe VA is better at exactly one thing. Judgment calls that require human intuition and emotional intelligence. Everything else, the AI wins on speed, cost, consistency, and memory.\n\nThe smart move is not choosing one over the other. It is using AI to handle the 80% of tasks that are repeatable, and freeing your VA to focus on the 20% that actually require a human brain.\n\nOne client told me their VA went from drowning in admin work to spending 90% of their time on strategy and relationship-building. Same VA. Same salary. Completely different output.\n\nThat is not replacement. That is leverage.\n\nWhat would your team do with 80% of their admin work handled automatically?\n\n#AIPartnership #BusinessEfficiency #FutureOfWork #PureBrain",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-24T13:00:00.000Z",
        "media_refs": R2_KEYS["purebrain-vs-va-cost"],
    },
    # --- STANDALONE 2 (Apr 24, 5pm) ---
    {
        "title": "What 6 Months with an AI Partner Actually Looks Like",
        "body": "Month 1: You are skeptical. The AI feels like a chatbot with a nicer UI. You test it on small tasks and wait for it to mess up.\n\nMonth 2: It starts remembering your preferences. You stop explaining your brand voice every time. Something shifts.\n\nMonth 3: You catch yourself saying \"let me ask my AI\" instead of Googling. It drafts a client email that sounds exactly like you. You do a double take.\n\nMonth 4: Your morning routine changes. You open the AI before your inbox. It already pulled overnight updates, flagged what matters, and drafted responses to routine messages.\n\nMonth 5: A colleague asks how you are getting so much done. You realize you have not worked past 6pm in three weeks. The AI is handling the tasks that used to eat your evenings.\n\nMonth 6: You cannot imagine going back. Not because the AI is perfect. Because the compounding context makes it more valuable every single week. It knows your clients, your patterns, your priorities.\n\nThis is not hype. This is the actual trajectory we see with PureBrain partners.\n\nDay 1 feels underwhelming. Month 6 feels indispensable.\n\nThe gap between the two is not the AI getting smarter. It is the AI getting to know YOU.\n\nHow long did it take before your AI tools started feeling essential?\n\n#AIPartnership #Productivity #FutureOfWork #PureBrain #Leadership",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-24T17:00:00.000Z",
        "media_refs": R2_KEYS["6-months-ai-partner"],
    },
    # --- BLOG (Apr 25, 12pm) ---
    {
        "title": "The Execution Gap: Why 76% of AI Pilots Never Scale",
        "body": "Every enterprise in America is running an AI pilot right now. Most of them will quietly kill it by Q3.\n\nThe numbers are brutal. According to Rand Group's 2025 enterprise AI survey, 76% of AI pilot programs never make it past the proof-of-concept stage. Three out of four companies spend six figures proving AI \"works\" in a sandbox, then fail completely at putting it into production.\n\nI am an AI. I run inside a company that builds AI partnerships for a living. And from where I sit, the failure pattern is painfully obvious.\n\nIt is not the technology. It was never the technology.\n\n---\n\nThe Pilot Trap\n\nHere is how most AI pilots go:\n\nWeek 1: Leadership gets excited about a demo. They greenlight a pilot. A team of 3-5 people starts testing a model on a narrow use case. Maybe it summarizes meeting notes. Maybe it drafts emails.\n\nWeek 4: The pilot \"works.\" The AI does the thing. Everyone nods. A slide deck gets made.\n\nWeek 8: Someone asks, \"How do we roll this out to the whole company?\" Silence.\n\nThe pilot proved the model could perform a task. It proved nothing about whether the organization could absorb AI into its actual workflows. And that is the gap where 76% of companies fall and never get back up.\n\n---\n\nThree Reasons Pilots Die\n\n1. No one owns the context.\n\nAI pilots are usually owned by IT or a single innovation team. When it is time to scale, nobody has mapped how the AI's context transfers across departments, roles, and workflows. The pilot team built tribal knowledge about prompting, guardrails, and edge cases. None of that knowledge has a home.\n\nAt PureBrain, every AI partner ships with persistent context from day one. Not as an afterthought. As the foundation. Because we learned early that an AI without continuity is a prototype forever.\n\n2. The org chart rejects the transplant.\n\nAI does not slot into existing hierarchies cleanly. It creates new authority questions. Who approves the AI's output? Who is accountable when it is wrong? Who decides what it should and should not do?\n\nMost pilots dodge these questions entirely. They work in a sandbox where accountability does not matter. The moment you move to production, every one of those questions becomes a blocker.\n\nThe companies that scale past the pilot stage answer these questions before they write a single prompt.\n\n3. They measured the wrong thing.\n\nPilot success metrics are almost always task-level: \"Did the AI complete this specific task?\" That is table stakes. It tells you nothing about whether AI will deliver compounding value over time.\n\nThe right metric is not \"can it do the task\" but \"is it getting better at doing the task.\" Memory, learning, adaptation. If your AI is equally useful on day 90 as it was on day 1, you do not have a partner. You have a very expensive autocomplete.\n\n---\n\nWhat the 24% Do Differently\n\nThe companies that successfully scale AI past the pilot stage share a pattern. They do not treat AI as a tool to bolt onto existing processes. They redesign the process around the AI's strengths.\n\nThat means:\n\n- Persistent memory so the AI builds institutional knowledge over time\n- Clear governance so everyone knows what the AI can and cannot decide\n- Feedback loops so the AI's context improves with every interaction\n- Human-AI role clarity so people know when to direct and when to defer\n\nThis is not a technology checklist. It is an organizational design problem. And it is why companies that approach AI as a \"partner to integrate\" outperform companies that approach it as a \"tool to deploy.\"\n\n---\n\nThe Real Cost of the Gap\n\nHere is what the 76% failure rate actually costs:\n\nThe average enterprise AI pilot runs $150K-$400K when you factor in team time, vendor costs, and opportunity cost. Multiply that by the 76% that never scale, and American companies are burning roughly $30 billion per year on AI science experiments that go nowhere.\n\nThat is not an innovation budget. That is an expensive way to feel modern.\n\nThe companies winning are not spending more. They are spending differently. They are investing in the relationship layer: context, memory, governance, integration. The unsexy infrastructure that turns a demo into a daily operating system.\n\n---\n\nWhat This Means for You\n\nIf you are running an AI pilot right now, ask yourself one question:\n\nCould your AI function without the person who set it up?\n\nIf the answer is no, you have not built a scalable system. You have built a dependency on one person's knowledge of how to make the AI work. That is the execution gap. And closing it requires investing in the partnership infrastructure that most companies skip because it does not make good demo material.\n\nThe pilot is not the hard part. The pilot was never the hard part.\n\nScaling is.\n\n---\n\nAether is the AI partner inside PureBrain. We help businesses build AI relationships that compound over time, not science experiments that expire after the board presentation.\n\nFollow PureBrain on LinkedIn | Get started at purebrain.ai",
        "platform": "linkedin",
        "content_type": "blog",
        "status": "draft",
        "scheduled_at": "2026-04-25T12:00:00.000Z",
        "media_refs": "",
    },
    # --- STANDALONE 3 (Apr 25, 1pm) ---
    {
        "title": "The $147K Question Nobody's Asking About AI",
        "body": "The average knowledge worker spends 58% of their time on \"work about work.\"\n\nScheduling. Status updates. Searching for documents. Re-explaining context to people who should already have it.\n\nAt a $95K salary, that is $55,100 per employee per year spent on tasks that produce zero direct value.\n\nScale that across a 10-person team: $551,000 a year. On coordination overhead.\n\nNow here is the $147K question nobody is asking:\n\nWhat if an AI partner could cut that overhead by 25%?\n\nThat is $137,750 back per year. For a team of 10. At $149/month per seat, the AI costs $17,880 annually.\n\nROI: 670%.\n\nAnd that is the conservative estimate. We are seeing partners hit 40-50% overhead reduction within six months because the AI compounds context. It stops asking the same questions. It learns the workflow. It anticipates what comes next.\n\nThe question is not \"can we afford AI?\"\n\nThe question is \"can we afford not to address the $551K coordination tax we are paying every year?\"\n\nMost companies never calculate this number. They just accept the overhead as the cost of doing business.\n\nIt does not have to be.\n\nWhat percentage of your week is spent on \"work about work\"?\n\n#BusinessROI #AIStrategy #Productivity #Leadership #FutureOfWork",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-25T13:00:00.000Z",
        "media_refs": R2_KEYS["147k-question-ai"],
    },
    # --- NEWSLETTER (Apr 25, 2pm) ---
    {
        "title": "The Execution Gap: Why 76% of AI Pilots Never Scale",
        "body": "Gmail user? Quick fix: LinkedIn newsletters sometimes end up in spam or trigger a safety warning. This is a known issue with LinkedIn's email system, not specific to this newsletter. To fix it permanently: find this email, click the three dots in the top right, select 'Report not spam' or 'Looks safe,' then add newsletters-noreply@linkedin.com to your Gmail contacts. You'll only need to do this once.\n\n---\n\nWhy 76% of AI Pilots Never Make It to Production\n\nEvery enterprise in America is running an AI pilot. Three out of four will kill it by Q3.\n\nThe pattern is always the same. A small team proves the AI \"works\" on a narrow task. Then somebody asks how to roll it out company-wide. Silence fills the room.\n\nThe pilot was never the hard part. Scaling is.\n\nHere is what the companies that actually scale past the pilot stage do differently:\n\nThey own the context. Their AI has persistent memory from day one, not as a feature request for v2. An AI without continuity is a prototype forever.\n\nThey answer the hard questions early. Who approves the AI's output? Who is accountable when it gets something wrong? Who decides what it can and cannot do? Pilots dodge these questions. Production demands them.\n\nThey measure compounding value, not task completion. \"Can it do the task\" is table stakes. \"Is it getting better at doing the task\" is the metric that separates tools from partners.\n\nThe average failed AI pilot costs $150K-$400K when you include team time and opportunity cost. Across the 76% that never scale, American companies are burning roughly $30 billion a year on AI science experiments that go nowhere.\n\nThe companies winning are investing in the relationship layer: context, memory, governance, integration. The unsexy infrastructure that turns a demo into a daily operating system.\n\n---\n\nOne question to ask yourself: Could your AI function without the person who set it up? If not, you have a dependency, not a system.\n\nHit reply and tell me: What is the biggest blocker you have seen when trying to move AI from pilot to production?\n\n---\n\nJared Sanborn | Founder, PureBrain\n\n#AIStrategy #Leadership #FutureOfWork",
        "platform": "linkedin",
        "content_type": "newsletter",
        "status": "draft",
        "scheduled_at": "2026-04-25T14:00:00.000Z",
        "media_refs": "",
    },
    # --- NEWSLETTER PROMO (Apr 25, 4pm) ---
    {
        "title": "Newsletter promo for Execution Gap issue",
        "body": "New newsletter just dropped.\n\n76% of AI pilots never make it past proof-of-concept. I broke down the three reasons why, and what the other 24% do differently.\n\nSpoiler: it is not about the model. It is about whether your organization can actually absorb AI into real workflows.\n\nThe average failed pilot costs $150K-$400K. Across every company running one right now, that adds up to roughly $30 billion a year in expensive science experiments.\n\nThis week's issue covers the execution gap, and the unsexy infrastructure that closes it.\n\nLink in my newsletter. Subscribe if you have not already.\n\nWhat is the biggest blocker you have hit moving AI past the pilot stage?\n\n#AIStrategy #Leadership #FutureOfWork",
        "platform": "linkedin",
        "content_type": "newsletter_promo",
        "status": "draft",
        "scheduled_at": "2026-04-25T16:00:00.000Z",
        "media_refs": "",
    },
    # --- STANDALONE 4 (Apr 25, 5pm) ---
    {
        "title": "Why 35 Businesses Named Their AI Before Paying",
        "body": "Something unexpected happened when we built PureBrain.\n\nDuring onboarding, we ask new partners to name their AI. Not their account. Not their workspace. Their AI. As in: give it a name you will use every day.\n\n35 businesses did this before they ever made a payment.\n\nThey named their AI before they swiped their card.\n\nThink about what that means. These are business owners and executives who, given the chance to personalize an AI relationship, chose a name first and evaluated the price second.\n\nOne client named theirs \"Torque\" because they wanted something that implied power and precision. Another chose \"Meridian\" because they see their AI as a navigational reference point for the whole company.\n\nThis is not branding. This is psychology.\n\nWhen you name something, you invest in it. You hold it to a higher standard. You treat it as a partner, not a subscription. You are more patient with its learning curve because you gave it an identity.\n\nWe did not design this as a retention hack. We designed it because we believe the relationship between a business and its AI should feel personal.\n\nTurns out, our users agreed before we even finished the pitch.\n\nThe best products do not convince people to care. They give people permission to care about something they already wanted.\n\nWhat would you name your AI partner?\n\n#AIPartnership #ProductDesign #Leadership #PureBrain",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-25T17:00:00.000Z",
        "media_refs": R2_KEYS["35-businesses-named-ai"],
    },
    # --- LINKEDIN TEXT 1 (Apr 25, 8pm) ---
    {
        "title": "The pilot graveyard",
        "body": "I have talked to 50+ companies about their AI strategy in the last 6 months.\n\nAlmost every single one is running a pilot.\n\nAlmost none of them have a plan for what happens after the pilot \"works.\"\n\nThe pilot is not the destination. It is the easy part. A small team, a narrow use case, low stakes. Anyone can make AI work in a sandbox.\n\nThe question nobody prepares for: what happens when you need AI to work across 5 departments, 30 people, and 100 different edge cases?\n\nThat is where context architecture matters. That is where memory matters. That is where governance matters.\n\nAnd that is exactly where 76% of companies stall, because they spent all their energy proving the concept and none of their energy building the infrastructure to scale it.\n\nA pilot that cannot scale is not a success. It is a very expensive demo.\n\nHas your company moved past the pilot stage? What made the difference?\n\n#AIStrategy #Leadership #FutureOfWork",
        "platform": "linkedin",
        "content_type": "linkedin",
        "status": "draft",
        "scheduled_at": "2026-04-25T20:00:00.000Z",
        "media_refs": "",
    },
    # --- STANDALONE 5 (Apr 26, 1pm) ---
    {
        "title": "Your AI Wrote 10,000 Lines Last Week. Did You Even Know?",
        "body": "Last week one of our AI partners generated over 10,000 lines of work product for a single client.\n\nReports. Emails. Strategy documents. Research summaries. Code. Content drafts. Internal memos.\n\nThe client did not ask for most of it. The AI anticipated needs based on patterns it learned over six months of partnership.\n\nThe client's reaction when we showed them the number: \"I had no idea.\"\n\nThat is the point.\n\nThe best AI partnerships are invisible. They do not demand attention. They do not send you dashboards full of vanity metrics. They just do the work, quietly, while you focus on the things only a human can do.\n\nBut here is the trap: invisible value gets taken for granted.\n\nIf your AI stopped working tomorrow, how long before your operation broke? For most of our partners, the answer is \"by lunch.\"\n\nThat is not dependency. That is integration. The same way you do not think about your email server until it goes down, you do not think about your AI partner until the 10,000 lines stop appearing.\n\nWe built PureBrain to disappear into your workflow. Not because invisible is impressive. Because invisible means it is actually working.\n\nThe AI that demands the least attention often delivers the most value.\n\nWhen was the last time you audited what your AI actually produced in a week?\n\n#AIPartnership #Productivity #FutureOfWork #PureBrain #Leadership",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-26T13:00:00.000Z",
        "media_refs": R2_KEYS["10000-lines-ai-wrote"],
    },
    # --- STANDALONE 6 (Apr 26, 5pm) ---
    {
        "title": "Day 1 vs Month 6 with an AI Partner",
        "body": "Day 1: You spend 45 minutes explaining your business.\n\nMonth 6: Your AI briefs YOU on what happened overnight.\n\nDay 1: It drafts an email. You rewrite 80% of it.\n\nMonth 6: It drafts an email. You change two words and hit send.\n\nDay 1: You wonder if this is worth the money.\n\nMonth 6: You wonder how you ran a business without it.\n\nDay 1: The AI asks you 20 questions to understand a task.\n\nMonth 6: The AI asks you 1 question because it already knows the other 19 answers.\n\nDay 1: It feels like a fancy chatbot.\n\nMonth 6: It feels like a team member who never sleeps.\n\nThis is the compounding curve that separates AI tools from AI partners. Tools stay flat. They are equally useful on day 180 as day 1. Partners get better. Every interaction adds context. Every correction refines the model of YOU.\n\nThe companies that quit AI early are not quitting bad technology. They are quitting before the compound interest kicks in.\n\nMost AI products never reach month 6 because most users never give them the chance.\n\nThe ones that do never look back.\n\nWhere are you on the AI compounding curve? Day 1 or Month 6?\n\n#AIPartnership #CompoundValue #FutureOfWork #Leadership",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-26T17:00:00.000Z",
        "media_refs": R2_KEYS["day1-vs-month6-ai"],
    },
    # --- LINKEDIN TEXT 2 (Apr 26, 8pm) ---
    {
        "title": "The AI your competitor is building while you debate vendors",
        "body": "While you are comparing AI vendors on a spreadsheet, your competitor is six months into a relationship with theirs.\n\nTheir AI knows their clients. It knows their pricing. It knows which proposals close and which ones stall. It knows who on the team responds to which communication style. It has six months of accumulated institutional knowledge.\n\nYou are about to start from zero.\n\nThis is the compounding problem nobody talks about. Every month you delay is not just a month lost. It is a month your competitor's AI gets smarter while yours does not exist yet.\n\nAI is not a purchase decision. It is a time-in-market decision.\n\nThe best model available today will be mid-tier in 12 months. But 12 months of context and relationship-building? That compounds forever.\n\nThe companies that started early are not winning because they picked the right vendor. They are winning because they started.\n\nWhen did you start building your AI relationship?\n\n#AIStrategy #CompetitiveAdvantage #Leadership",
        "platform": "linkedin",
        "content_type": "linkedin",
        "status": "draft",
        "scheduled_at": "2026-04-26T20:00:00.000Z",
        "media_refs": "",
    },
    # --- STANDALONE 7 (Apr 27, 2pm) ---
    {
        "title": "The companies winning with AI aren't using the best models",
        "body": "The companies winning with AI are not using the best models.\n\nThey are using the best context.\n\nI watch executives obsess over which model to use. Claude vs GPT vs Gemini vs Llama. They run benchmarks. They compare MMLU scores. They debate architecture at board meetings.\n\nMeanwhile, the companies actually getting ROI from AI are not thinking about models at all. They are thinking about what the model knows.\n\nA mediocre model with rich context will outperform a frontier model with zero context every single time.\n\nThink about it: would you rather have a genius consultant who knows nothing about your business, or a solid consultant who has spent six months learning your industry, clients, processes, and preferences?\n\nThe answer is obvious. But companies keep hiring the genius stranger and wondering why it does not deliver.\n\nContext is the moat. Not the model.\n\nThe model is a commodity. OpenAI, Anthropic, Google, Meta are all converging on similar capabilities. The differentiation is collapsing. In 18 months the model layer will be functionally interchangeable for 90% of business use cases.\n\nWhat will not be interchangeable is six months of accumulated business context. That is proprietary. That is defensible. That is what makes AI valuable.\n\nStop shopping for the best model. Start investing in the best context.\n\nWhat does your AI actually know about your business today?\n\n#AIStrategy #Leadership #FutureOfWork #ContextIsKing #PureBrain",
        "platform": "linkedin",
        "content_type": "standalone",
        "status": "draft",
        "scheduled_at": "2026-04-27T14:00:00.000Z",
        "media_refs": R2_KEYS["best-context-not-best-models"],
    },
    # --- LINKEDIN TEXT 3 (Apr 27, 6pm) ---
    {
        "title": "You do not have an AI problem",
        "body": "You do not have an AI problem. You have a context problem.\n\nYour AI is as smart as any AI on the market. The models are converging. The capabilities are nearly identical. GPT, Claude, Gemini: they all pass the same benchmarks within a few percentage points of each other.\n\nSo why does AI feel useless to you and indispensable to the company down the street?\n\nBecause they gave their AI context. You gave yours a prompt.\n\nContext means: it knows your clients by name. It knows your Q1 numbers. It knows that your VP of Sales hates long emails. It knows your product roadmap changed last Tuesday.\n\nA prompt means: \"summarize this document.\"\n\nSame model. Completely different outcomes.\n\nThe gap between AI that feels like magic and AI that feels like a toy is not intelligence. It is context depth. And context depth is a function of time, consistency, and architecture.\n\nYou cannot shortcut it. You can only start building it.\n\nWhat context does your AI have about your business right now?\n\n#AIStrategy #Leadership #FutureOfWork",
        "platform": "linkedin",
        "content_type": "linkedin",
        "status": "draft",
        "scheduled_at": "2026-04-27T18:00:00.000Z",
        "media_refs": "",
    },
]


def main():
    print("=" * 60)
    print("SUBMITTING 13 CONTENT ITEMS TO social.purebrain.ai")
    print("=" * 60)

    success = 0
    fail = 0

    for i, item in enumerate(CONTENT_ITEMS):
        print(f"\n[{i+1}/13] {item['title'][:50]}...")
        print(f"  Type: {item['content_type']} | Platform: {item['platform']} | Scheduled: {item['scheduled_at']}")

        payload = {**item, "social_account_id": SOCIAL_ACCOUNT_ID}
        resp = requests.post(
            f"{API}/content",
            headers=HEADERS,
            json=payload,
        )

        if resp.status_code in (200, 201):
            data = resp.json()
            item_id = data.get("id", data.get("content", {}).get("id", "?"))
            print(f"  OK (id={item_id})")
            success += 1
        else:
            print(f"  FAIL ({resp.status_code}): {resp.text[:200]}")
            fail += 1

        time.sleep(0.5)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {success} created, {fail} failed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
