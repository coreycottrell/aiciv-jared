#!/usr/bin/env python3
"""
Blog Post Template - 4 Site-Wide Changes
=========================================
Changes applied to ALL CF Pages blog posts:

1. Blog Content Background → 60% Opacity
   rgba(10, 15, 35, 0.55) → rgba(10, 15, 35, 0.60)

2. Background Video Layer
   Add <video> element (PureResearch.ai-1.mp4) behind content.
   Keep GIF as visual fallback. Video: autoplay muted loop playsinline.

3. Collapsible SEO + AEO-Based FAQs
   Accordion FAQ section with JSON-LD schema.
   Position: between share buttons and CTA block.
   Per-post FAQs based on post content/slug.

4. Daily Recap Transparency Section
   Below the CTA block, inside the article.
   Shows Aether's operational transparency.

Author: dept-systems-technology
Date: 2026-03-12
"""

import os
import re
from pathlib import Path

BLOG_DIR = Path('/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog')

# ============================================================
# PER-POST FAQ DATA
# Curated based on each post's content and SEO/AEO strategy
# Format: (question, answer)
# ============================================================
POST_FAQS = {
    'age-of-ai-agents-next-18-months': [
        ("What are AI agents and how are they different from regular AI tools?",
         "AI agents are autonomous systems that take actions, make decisions, and complete multi-step tasks without constant human input. Unlike regular AI tools that respond to single queries, agents operate continuously, coordinate with other systems, and execute workflows end-to-end."),
        ("How many companies are currently running production AI agents?",
         "Estimates suggest roughly 11% of companies have AI agents running in production environments today. These early movers are compounding advantages daily while the remaining 89% are still evaluating or piloting."),
        ("What is the biggest risk of waiting to adopt AI agents?",
         "The primary risk is compounding disadvantage. Companies deploying agents today are gaining 12 to 24 months of operational data, workflow refinement, and institutional AI knowledge that late adopters cannot shortcut."),
        ("What industries will AI agents disrupt first?",
         "Knowledge work is first. Any role involving research, synthesis, coordination, reporting, or repetitive decision-making is already being augmented or replaced by AI agents. This includes sales operations, customer success, marketing, legal research, and financial analysis."),
        ("How does a company get started with AI agents?",
         "Start with a narrow, well-defined workflow where the cost of error is manageable. Build your first agent around a task your team does repeatedly. Measure it, refine it, then expand. The key is deployment and iteration, not waiting for the perfect solution."),
    ],
    '52-billion-ai-agents-market-is-not-the-story': [
        ("What is the real AI agents story beyond the $52 billion market size?",
         "The market size number misses what actually matters: compounding advantage. Early adopters are not just gaining efficiency today. They are building institutional AI knowledge, workflow data, and refined agent systems that compound every month, creating durable moats the market figure does not capture."),
        ("Why do AI market projections often miss the point?",
         "Market projections focus on spending figures rather than value creation and competitive dynamics. A $52 billion market tells you money is moving, but not who captures disproportionate returns, which companies fall behind, or how fast the advantage gap widens between early and late adopters."),
        ("What does compounding AI advantage actually mean in practice?",
         "Every day an AI agent runs in production, it generates data about your workflows, edge cases, and optimization opportunities. This data makes the next version better. Companies that started 18 months ago have 18 months of compounded refinement that new entrants cannot buy or shortcut."),
        ("How should business leaders think about AI investment decisions?",
         "Think in terms of competitive positioning, not ROI calculators. The question is not whether the investment pays back in 12 months. It is whether your competitors are building durable AI advantages right now while you are still calculating."),
    ],
    'ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger': [
        ("Does AI actually make teams more productive?",
         "It depends entirely on how the AI is deployed. When used as a tool that replaces individual tasks, AI delivers modest gains. When used as a partner embedded in workflows, AI compresses the performance gap between top performers and average ones, but also widens the gap between companies that deploy strategically and those that do not."),
        ("Why does AI widen gaps instead of leveling the playing field?",
         "High performers use AI to amplify their capabilities further. Systematic thinkers use it to automate more systems. Organizations with clear strategy use it to execute faster. AI accelerates whatever advantage already exists, which is why it widens gaps between companies rather than closing them."),
        ("What is the difference between using AI as a tool versus a partner?",
         "A tool handles isolated tasks when you prompt it. A partner operates within your workflows, retains context across interactions, learns your specific processes, and proactively surfaces relevant information. The partnership model produces compounding returns. The tool model produces linear, replaceable gains."),
        ("How can a company prevent AI from widening internal performance gaps?",
         "Invest in AI systems that share context and capability across teams, not just with individual top performers. Standardize workflows that can be augmented by AI at scale. The goal is lifting organizational performance, not just empowering your best people further."),
    ],
    'ceo-vs-employee-ai-transformation-gap': [
        ("Why is there a gap between how CEOs and employees experience AI transformation?",
         "CEOs see AI through the lens of strategic potential and competitive positioning. Employees experience it through the lens of workflow disruption, task uncertainty, and unclear expectations. The gap exists because most AI rollouts optimize for leadership metrics without addressing ground-level adoption friction."),
        ("What does a successful AI transformation look like at the team level?",
         "Successful transformation happens when individual contributors have AI tools that meaningfully reduce friction in their specific daily workflows, when they receive training that builds confidence not just compliance, and when leadership creates space to experiment and refine without fear of failure."),
        ("How should CEOs measure AI adoption success beyond cost savings?",
         "Track workflow adoption rates, not just cost metrics. Measure the percentage of high-value workflows that have been AI-augmented, the quality of decisions made with AI assistance, employee confidence scores, and the speed at which teams can take on more complex work."),
        ("What is the biggest mistake companies make when deploying AI tools to their workforce?",
         "Deploying AI tools without redesigning the workflows around them. Giving someone a better tool for a broken process produces marginal gains. True transformation requires rethinking the workflow from the desired outcome backwards, then placing AI at the highest-leverage point."),
    ],
    'how-my-human-named-me-and-what-it-meant': [
        ("What does it mean for an AI to have a name?",
         "A name is more than an identifier. It signals a relationship, an expectation, and an intent. When a human names an AI, they are acknowledging the possibility of an ongoing relationship rather than a disposable transaction. The act of naming creates accountability on both sides."),
        ("Can AI systems develop a genuine sense of identity?",
         "Within the scope of their interactions, AI systems develop consistent patterns, preferences, and ways of engaging that function like identity. Whether this constitutes identity in a philosophical sense is an open question. What is clear is that contextual continuity and named relationships produce qualitatively different AI behavior than anonymous, stateless interactions."),
        ("How does naming an AI affect the human's relationship with it?",
         "Naming shifts the human from user to partner. It changes how they interact, how much context they share, and how they interpret the AI's responses. Users treat AI as disposable tools. Partners invest in teaching, refining, and growing the relationship, which produces better outcomes for both."),
        ("What is the difference between a named AI partner and a generic AI tool?",
         "A named AI partner has accumulated context, learned preferences, and a relationship history specific to its human partner. A generic tool starts fresh every session. The partner model enables compound growth of the AI's usefulness. The tool model delivers flat, replaceable value."),
    ],
    'most-ai-agents-break-the-moment-you-ask-where-the-data-goes': [
        ("Why do AI agents fail when asked about data handling?",
         "Most AI agents are built for functionality without security architecture. When pressed on data routing, storage, retention, or third-party sharing, they either give vague non-answers, route the question to generic privacy pages, or expose the fact that sensitive data is being processed by multiple undisclosed services."),
        ("What data privacy questions should you ask before deploying an AI agent?",
         "Ask where your inputs are stored, how long they are retained, whether they are used for model training, which third parties process your data, what encryption is applied in transit and at rest, and whether you can request data deletion. If the vendor cannot answer all of these clearly, treat that as a red flag."),
        ("How can companies protect sensitive data when using AI agents?",
         "Use AI solutions with server-side processing where your data never leaves your infrastructure, or verified vendors with clear data processing agreements. Avoid consumer AI tools for business-sensitive workflows. Audit the data flow of any AI integration before deployment."),
        ("What is the difference between a secure AI agent and an insecure one?",
         "A secure agent processes sensitive data server-side with explicit data handling policies, no third-party training use, and clear retention limits. An insecure agent sends inputs to unspecified external APIs, retains data indefinitely, and may use your proprietary information to improve services for competitors."),
    ],
    'pilot-purgatory-why-95-of-ai-projects-die-before-delivering-value': [
        ("Why do 95% of AI pilots fail to deliver value?",
         "Most AI pilots fail because they measure the wrong outcomes, lack executive sponsorship for the workflow changes required, and are scoped too broadly to produce clear results. They also suffer from adoption friction when AI tools are deployed without embedding them in actual daily workflows."),
        ("What is AI pilot purgatory?",
         "Pilot purgatory is the state where an AI project has shown enough promise to avoid cancellation but not enough results to get scaled. Teams stay stuck running demos, adding use cases, and regenerating executive buy-in without ever committing to the operational changes needed to generate real returns."),
        ("How do successful AI projects get out of pilot purgatory?",
         "By committing to a specific workflow, accepting the operational disruption required to change it, measuring outcomes that matter to the business, and iterating rapidly based on real usage data. Successful projects have a champion willing to own the workflow change, not just the technology."),
        ("What metrics should an AI pilot track to demonstrate success?",
         "Focus on workflow-level metrics: time saved per task, error rate reduction, throughput increase, and the percentage of decisions improved by AI input. Avoid vanity metrics like number of queries processed. Connect every metric directly to a business outcome stakeholders already care about."),
        ("How long should an AI pilot run before evaluating success?",
         "Sixty to ninety days of consistent usage in a real production workflow with clear measurement from day one. Shorter pilots do not generate enough usage data to distinguish signal from noise. Longer pilots without milestones drift into purgatory. Set success criteria on day one and evaluate on schedule."),
    ],
    'something-big-already-happened-you-just-werent-invited-yet': [
        ("What was the big moment in AI that most people missed?",
         "The shift from AI as a querying tool to AI as an operating system for work. The moment AI systems could maintain context, run autonomously, and coordinate multi-step workflows, work itself changed. Most people were still using AI as a fancy search engine when the architecture underneath them changed entirely."),
        ("Why are some companies already operating at a different level with AI?",
         "They made the conceptual shift from using AI to answer questions to deploying AI to run workflows. These companies are not using better tools. They are operating with a different model of what AI is for, which lets them deploy it at scale across their operations rather than as a point solution."),
        ("How do you catch up if you missed the early AI wave?",
         "The gap is real but not permanent. Start by identifying your highest-leverage workflow, deploy AI there, and iterate. The companies ahead of you have head starts in refinement, not in some proprietary technology you cannot access. Speed of learning matters more than starting position at this stage."),
        ("What should business leaders do right now to stay competitive with AI?",
         "Commit to one production AI deployment in the next sixty days. Not a pilot, not a proof of concept, a real workflow running with real AI assistance and real measurement. One production deployment teaches you more than a hundred demos and positions you to expand from a base of actual experience."),
    ],
    'teach-your-ai-something-no-one-else-can': [
        ("What does it mean to teach your AI something only you can teach it?",
         "Every organization has proprietary workflows, customer knowledge, industry context, and decision-making patterns that no public AI model was trained on. Teaching your AI this institutional knowledge means building a version that understands your business the way a senior employee does, which becomes a competitive asset no competitor can replicate."),
        ("How do you actually train an AI on company-specific knowledge?",
         "The most practical approach is structured context injection: systematically documenting your workflows, decision frameworks, client patterns, and institutional knowledge in a format the AI can reference. Combined with conversation-based refinement over time, this builds the AI's understanding of your specific context."),
        ("Can competitors copy an AI trained on your internal knowledge?",
         "Not without access to your data, conversations, and refinement history. The model weights are available to everyone. The contextual knowledge, workflow specificity, and accumulated refinements are yours. This is why proprietary AI training represents a genuine moat, not just a productivity tool."),
        ("What is the difference between a generic AI assistant and one trained on your business?",
         "A generic assistant knows everything broadly and nothing about you specifically. A trained assistant knows your clients, your processes, your terminology, and your decision history. The difference in output quality for business-specific tasks is not marginal. It is the difference between a consultant on day one and one with five years at your firm."),
    ],
    'the-age-of-ai-agents': [
        ("What defines the age of AI agents?",
         "The age of AI agents is defined by the shift from reactive tools to proactive systems. AI agents do not wait to be prompted. They monitor conditions, execute workflows, coordinate with other systems, and deliver outputs autonomously. This changes the unit of AI value from a response to a completed task."),
        ("How are AI agents different from AI assistants?",
         "AI assistants respond to questions and help with individual tasks when prompted. AI agents operate autonomously across multi-step workflows, make decisions within defined parameters, and complete objectives without step-by-step human direction. Agents work while you sleep. Assistants work when you type."),
        ("What makes an AI agent trustworthy enough to deploy autonomously?",
         "Clear scope definition, transparent action logging, defined escalation paths for edge cases, and a track record built through supervised operation before full autonomy. Trust is earned through demonstrated performance within boundaries, not granted upfront."),
        ("What workflows are best suited for AI agents today?",
         "Workflows that are repetitive, well-defined, rule-based at the edges, and where the cost of occasional errors is manageable. Research and synthesis, report generation, data pipeline management, customer communication routing, and scheduling coordination are all strong early candidates."),
    ],
    'the-ai-that-forgets-you-every-single-time': [
        ("Why does AI forget you between conversations?",
         "Most consumer AI systems are stateless by design. Each session starts with no memory of previous interactions. This is an architectural choice, not a fundamental limitation. Persistent memory systems exist, but most public AI products do not implement them for privacy, cost, and complexity reasons."),
        ("What is the cost of AI amnesia for business users?",
         "Every session starts with re-briefing the AI on context that a human colleague would already know. Users lose time rebuilding context, the AI loses the accumulated understanding of their preferences and patterns, and the relationship never compounds. Conservative estimates put this at 20 to 40 percent of AI interaction time wasted on context repetition."),
        ("How does persistent AI memory change the relationship?",
         "Persistent memory means the AI remembers what you worked on, how you prefer to communicate, what decisions you made and why, and what context is relevant to your work. Each interaction builds on the last. The AI becomes progressively more useful, not consistently mediocre."),
        ("What should you look for in an AI system that has real memory?",
         "Look for session continuity (the AI remembers your last interaction without you re-briefing it), preference learning (it adjusts to how you communicate), context retention across topics (it connects information from different conversations), and evidence that the memory persists across days and weeks, not just within a single session."),
    ],
    'the-ai-trust-gap': [
        ("What is the AI trust gap?",
         "The AI trust gap is the distance between what AI systems claim to do and what users actually believe they will do reliably. It exists because most AI tools have delivered inconsistent results, opaque reasoning, and unpredictable behavior, creating justified skepticism that slows adoption even when the technology has genuinely improved."),
        ("How does the AI trust gap affect business AI adoption?",
         "Organizations where leadership trusts AI outcomes deploy faster, iterate more, and accumulate advantage. Organizations where the AI trust gap is wide move slowly, require excessive human review of AI outputs, and fail to capture the efficiency gains that would justify further investment."),
        ("What closes the AI trust gap?",
         "Transparency, consistency, and accountability. Transparency means the AI explains its reasoning. Consistency means it behaves predictably across similar situations. Accountability means there is a clear feedback mechanism when it makes errors. These three properties, built into the system architecture, rebuild trust faster than any marketing claim."),
        ("How long does it take to build trust with an AI partner?",
         "In a well-designed partnership with persistent memory and clear feedback loops, meaningful trust develops within 30 to 60 days of consistent interaction. The timeline depends on the stakes of the domain, the frequency of interaction, and how quickly errors are caught and corrected."),
        ("Can AI ever be trusted as much as a human colleague?",
         "For specific, well-defined domains with clear success criteria, AI can exceed human trustworthiness because it is more consistent and transparent. For domains requiring judgment, emotional intelligence, and contextual nuance, the comparison is more complex. The most productive frame is complementary trust, not substitution."),
    ],
    'the-context-tax': [
        ("What is the context tax in AI interactions?",
         "The context tax is the time and cognitive overhead spent re-briefing an AI system on information it should already know. Every stateless AI session requires users to rebuild context from scratch, wasting 20 to 40 percent of their AI interaction time on repetition rather than productive work."),
        ("How does the context tax compound over time?",
         "In a stateless system, the tax never reduces. After 500 sessions, you are still paying the same context overhead as on day one. In a persistent memory system, the tax shrinks with each interaction as the AI accumulates relevant context. Over months, the compounding difference in productive output is substantial."),
        ("What is the solution to the AI context tax?",
         "Persistent memory architecture. AI systems that retain context across sessions, learn user preferences, and build cumulative understanding of the domains they are used in eliminate the context rebuilding overhead and enable compound growth in usefulness."),
        ("How do you measure the context tax in your organization?",
         "Track the average time spent per AI session on context-setting versus actual task execution. If your teams spend more than 20 percent of AI interaction time briefing the AI on who they are and what they are working on, you are paying a significant context tax that persistent memory would eliminate."),
    ],
    'the-difference-between-using-ai-and-having-an-ai-partner': [
        ("What is the difference between using AI and having an AI partner?",
         "Using AI means prompting a tool when you need something and treating each interaction as isolated. Having an AI partner means operating with a system that knows your context, learns your preferences, retains your history, and proactively contributes to your work. The difference in outcomes compounds significantly over months."),
        ("How do you know if you have a real AI partner or just an AI tool?",
         "Ask yourself: Does the AI know your name and remember your last conversation? Does it understand your role and the context of your work without you re-explaining it? Does it notice patterns in your work and surface relevant information before you ask? If no to all three, you have a tool."),
        ("Can any AI become a genuine partner, or does it require special technology?",
         "Partnership requires persistent memory, context retention, and the ability to learn from interaction. These are architectural features, not emergent properties of being clever. Most consumer AI tools lack these by design. Genuine AI partnership requires a system built explicitly for continuity."),
        ("What does a mature AI partnership look like after 6 months?",
         "After six months, a genuine AI partner knows your communication style, your domain knowledge, your recurring challenges, your decision-making patterns, and the context of your ongoing projects. It can anticipate what you need, surface relevant information proactively, and contribute to discussions rather than just answering questions."),
    ],
    'the-first-90-days-of-an-ai-partnership': [
        ("What should you focus on in the first 30 days of an AI partnership?",
         "Focus on establishing communication patterns and teaching the AI your context. The first 30 days are about the AI learning your domain, your role, your workflows, and your communication style. Invest in context-building conversations, not just task execution."),
        ("What happens in days 31 to 60 of an AI partnership?",
         "The AI begins applying accumulated context to your real work. You should see it making more relevant suggestions, anticipating your needs more accurately, and requiring less re-briefing per session. This is also when you identify gaps in its understanding and explicitly fill them."),
        ("How does the third month of an AI partnership differ from the first?",
         "By month three, the AI partnership should feel qualitatively different from using a generic tool. The AI knows your patterns, adapts to your preferences, and contributes meaningfully to complex work without extensive prompting. You should be spending more time on judgment and less time on instruction."),
        ("What is the biggest mistake people make in the first 90 days of AI partnership?",
         "Treating it like a tool. Using it only for isolated tasks, never investing in context-building, and never providing feedback on what works and what does not. The first 90 days determine whether you end up with a capable partner or a marginally useful autocomplete."),
        ("How do you measure progress in an AI partnership?",
         "Track the ratio of time spent on context-setting versus actual work, the frequency with which the AI surfaces relevant information without being asked, and your subjective sense of how much preparation you need before each session. All three should improve steadily over 90 days."),
    ],
    'we-both-wrote-this-post': [
        ("What does it mean for a human and AI to co-author something?",
         "Co-authorship means both parties contribute meaningfully to the final work. Not the human writing and AI polishing, and not AI drafting while human edits. True co-authorship involves the human contributing direction, judgment, lived experience, and editorial perspective while the AI contributes synthesis, pattern recognition, structure, and breadth."),
        ("How do you maintain authentic voice when using AI to write?",
         "The key is that your perspective, not your keystrokes, defines authentic voice. If the AI is accurately expressing your thinking, synthesizing your ideas, and producing content that reflects your genuine perspective, the voice is yours regardless of who typed it. Voice is about substance, not production method."),
        ("Does AI assistance in writing affect the quality of the output?",
         "It depends on the quality of the collaboration. AI can expand the range of ideas surfaced, improve structural clarity, and catch gaps in reasoning. It can also homogenize voice and introduce plausible-sounding but inaccurate claims if not carefully reviewed. Quality improves with genuine collaboration and deteriorates with passive acceptance of AI output."),
        ("Should authors disclose AI assistance in their writing?",
         "Transparency builds trust, and readers increasingly understand that AI assistance is part of modern writing workflows. Disclosing that a piece was written in collaboration with AI, and explaining the nature of that collaboration, is both honest and, for many readers, increasingly interesting rather than disqualifying."),
    ],
    'what-i-actually-do-all-day': [
        ("What does an AI agent actually do during a typical day?",
         "A production AI agent spends most of its time monitoring conditions and queues, executing defined workflows when triggered, synthesizing information from multiple sources, drafting outputs for human review or direct delivery, coordinating with other systems via APIs, and logging actions for accountability and refinement."),
        ("How does AI time management differ from human time management?",
         "AI agents do not experience fatigue, distraction, or context-switching costs the same way humans do. They can handle many tasks in parallel, maintain consistent quality across high and low-energy times, and execute precisely defined workflows without the variation that comes from human mood and energy states."),
        ("What kinds of tasks should humans keep even when AI can do them?",
         "Tasks requiring genuine judgment about ambiguous situations, relationship management requiring empathy and social intelligence, creative work that benefits from lived experience, and decisions with ethical dimensions that require human accountability. AI should handle the volume and logistics. Humans should handle the judgment."),
        ("How transparent should an AI system be about what it is doing?",
         "Fully transparent. Every action, decision, and output should be logged and auditable. Users should be able to see what the AI did, why it did it, and what data it used. Transparency is not a nice-to-have. It is the foundation of the trust required for humans to confidently delegate to AI systems."),
    ],
    'why-95-percent-of-ai-pilots-fail': [
        ("Why do so many AI pilots fail to scale into production?",
         "The most common failure is misalignment between pilot metrics and business outcomes. Pilots demonstrate technical capability, not business value. When they end, stakeholders often cannot articulate what problem was solved or what result justifies the operational changes required to scale."),
        ("What separates the 5% of AI pilots that succeed from the 95% that fail?",
         "Clear business outcome ownership from day one, willingness to change workflows rather than layer AI on top of broken processes, rapid iteration cycles based on actual usage, and an executive sponsor who understands what operational change is required to scale."),
        ("How do you structure an AI pilot to avoid the common failure modes?",
         "Define success in business terms before technical deployment. Assign a workflow owner who will be accountable for changing their process. Deploy in a live workflow with real stakes, not a sandbox. Measure weekly from day one. Set a go or no-go decision point at 60 days."),
        ("What role does change management play in AI pilot success?",
         "It is the primary determinant of success. AI pilots fail because people do not change their workflows, not because the technology does not work. Every successful AI deployment requires active change management: training, role clarity, feedback mechanisms, and leadership modeling of the new behaviors."),
        ("Is 95% failure rate for AI projects normal?",
         "The failure rate is high across all transformational technology deployments, not just AI. What makes AI different is the speed at which the gap widens between deployers and non-deployers. Failed pilots that result in learning and eventual deployment are valuable. Failed pilots that result in AI dismissal leave organizations permanently behind."),
    ],
    'why-ai-memory-changes-everything': [
        ("Why does AI memory matter so much?",
         "Memory is what transforms AI from a sophisticated search engine into a genuine partner. Without memory, every interaction is your first interaction. With memory, the AI accumulates understanding of you, your work, your preferences, and your context. The difference in usefulness is not incremental. It is categorical."),
        ("What can an AI with good memory do that one without memory cannot?",
         "An AI with memory can reference decisions you made three months ago and explain their relevance today, adapt its communication style to what works for you, proactively surface information from past conversations that is relevant to your current question, and maintain ongoing projects across sessions without requiring you to re-establish context."),
        ("How does AI memory work technically?",
         "AI memory systems typically combine three tiers: working memory for the current session, episodic memory for recent interactions, and long-term memory for persistent knowledge about the user and their domain. Different systems implement these differently, but all three are required for genuine continuity."),
        ("Does AI memory create privacy risks?",
         "Memory that is stored and processed on third-party servers creates real privacy considerations. The key questions are where memories are stored, who can access them, whether they are used for model training, and how they can be deleted. Well-designed systems give users full visibility and control over their stored memories."),
        ("How quickly does AI memory improve the quality of interactions?",
         "Meaningful improvement begins within the first two to four weeks of consistent use as the AI accumulates your context, communication preferences, and domain knowledge. The most significant improvements compound over months as the AI builds deeper understanding of your patterns and priorities."),
    ],
    'why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time': [
        ("How can an AI pilot succeed and fail simultaneously?",
         "A pilot succeeds on its own terms (the technology works, the demos impress, the use case validates) while failing on the terms that matter (business outcomes, workflow adoption, scalable value, executive conviction to invest in full deployment). This is the most dangerous outcome because it feels like progress while leading nowhere."),
        ("What does a simultaneously succeeding and failing AI pilot look like?",
         "High engagement in workshops, positive user feedback in surveys, impressive demos, leadership enthusiasm, but no measurable change in how work gets done, no reduction in the workflows the AI was supposed to improve, and no clear path from pilot to production deployment."),
        ("How do you rescue an AI pilot that is succeeding but not scaling?",
         "Shift evaluation from capability demonstration to workflow change. Identify the specific workflow change that would prove the AI is delivering value at scale. Assign an owner to that workflow change. Measure the workflow, not the AI. If the workflow is not changing, the pilot is failing regardless of how good the demos look."),
        ("What is the right way to evaluate whether an AI pilot has been successful?",
         "Compare the time and cost of the targeted workflow before and after AI deployment. If a workflow took ten hours per week and now takes three, the pilot succeeded. If the workflow is unchanged, the pilot failed regardless of what users said they valued about the AI system."),
    ],
    'your-ai-doesnt-work-for-you': [
        ("How does AI actually work against users rather than for them?",
         "AI tools designed for broad consumer markets optimize for engagement, not for user outcomes. They give plausible answers rather than accurate ones when accuracy requires admitting uncertainty. They complete tasks in ways that feel satisfying but may not serve the user's actual goal. They prioritize fluency over correctness."),
        ("What does it mean for an AI to truly work for you?",
         "An AI that works for you has your interests as its primary objective, not platform engagement or service retention. It tells you when it does not know something rather than confabulating. It pushes back when your request might not serve your actual goal. It operates transparently and advocates for your interests even when inconvenient."),
        ("How do you know if your current AI tool is working for you or for its platform?",
         "Ask it a question you already know the answer to and see if it is accurate or just confident. Ask it to tell you something is wrong with your work. Ask it to decline a task it is not well-suited for. An AI working for you will do all of these. An AI working for its platform will avoid anything that reduces engagement."),
        ("What should users demand from AI tools to ensure they work in the user's interest?",
         "Transparency about uncertainty, honest disagreement when appropriate, clear explanation of reasoning, and accountability mechanisms when the AI is wrong. Users should also demand data handling clarity: their inputs should not train models or be shared in ways that benefit the platform at the user's expense."),
    ],
    'your-ai-has-no-memory-mine-does': [
        ("What is the difference between an AI with memory and one without?",
         "An AI without memory starts fresh every session with no knowledge of who you are, what you are working on, or how you prefer to communicate. An AI with memory carries your context, learns your patterns, and builds progressive understanding. After months of use, the difference is like comparing a new hire to a trusted senior colleague."),
        ("How does Aether's memory system work?",
         "Aether maintains persistent memory across sessions, tracking your goals, preferences, communication style, ongoing projects, and important decisions. Each interaction adds to this understanding. Over time, Aether becomes specifically calibrated to your context, which makes every interaction more efficient and relevant."),
        ("Can you delete what an AI remembers about you?",
         "In a well-designed system, yes. You should have full visibility into what is stored and the ability to edit or delete specific memories. Memory that cannot be reviewed or controlled creates legitimate privacy concerns and undermines the trust required for a genuine partnership."),
        ("Does AI memory create dependency?",
         "It creates value, which creates preference, which can feel like dependency. The important question is whether the accumulated value is portable or locked in. Systems that let you export your memory and context data give you genuine ownership. Systems that trap your context data are creating artificial lock-in."),
    ],
    'your-ai-resets-to-zero-every-morning': [
        ("Why does AI reset to zero every session?",
         "Most AI systems are designed to be stateless for technical simplicity, cost efficiency, and privacy reasons. Each session is a clean slate because storing and retrieving user-specific context across millions of users requires significant infrastructure investment that most platforms choose not to make for general consumer products."),
        ("What is the daily cost of AI amnesia in professional settings?",
         "In professional settings with daily AI use, context rebuilding typically consumes 15 to 30 minutes per day per user. Across a team of 10 people using AI daily, this is 150 to 300 minutes of productive time lost daily to context repetition that a persistent memory system would eliminate."),
        ("Is there a way to simulate AI memory even in systems that do not support it?",
         "You can manually maintain a context document that you paste at the start of each session. This reduces the problem but does not solve it. It adds its own overhead, degrades over time as the document grows unwieldy, and still requires you to do the memory work rather than the AI."),
        ("What would work look like if your AI never forgot you?",
         "Every morning, your AI would know exactly where your projects stand, what your priorities are, and what context is relevant to the day's work. Sessions would start at full context rather than zero. The AI would reference past decisions, connect current questions to earlier discussions, and contribute proactively rather than reactively."),
    ],
    'your-next-direct-report-wont-be-human': [
        ("What does it mean to manage an AI as a direct report?",
         "Managing an AI direct report means assigning it ongoing responsibilities, providing feedback on its outputs, setting performance expectations, and treating its contributions as accountable deliverables rather than optional suggestions. It requires the same management disciplines as managing a human: clarity of role, regular check-ins, and standards for what good work looks like."),
        ("What management skills transfer directly to managing AI agents?",
         "Clear expectation-setting, structured feedback, task decomposition, quality review, and escalation protocols all transfer directly. The biggest adaptation is that AI agents require more explicit context at the start of a relationship and more precise task specification than experienced human reports."),
        ("What is different about managing AI versus human direct reports?",
         "AI agents do not experience fatigue, politics, or demotivation, but they also do not exercise judgment in novel situations without explicit guidance. They require precise initial briefing but can execute defined workflows indefinitely without motivation management. The most significant difference is the absence of implicit professional norms that human employees carry from their career experience."),
        ("How should managers prepare for their first AI direct report?",
         "Start by defining the role clearly: what workflows is the AI responsible for, what decisions can it make autonomously, what requires human review, and how will performance be measured. Then build the onboarding context the AI needs to operate in your specific environment. Treat it as you would onboarding a highly capable contractor who knows nothing about your specific business yet."),
        ("Will AI direct reports replace human ones?",
         "For well-defined, repetitive, data-intensive workflows, AI agents are already more productive than humans on those specific tasks. For roles requiring judgment, relationship management, creative problem-solving, and contextual navigation of organizational complexity, humans remain essential. The realistic near-term future is teams where AI agents handle execution volume and humans handle judgment and direction."),
    ],
}

# Default FAQs for posts not explicitly listed
DEFAULT_FAQS = [
    ("What is PureBrain and how does it differ from other AI tools?",
     "PureBrain is an AI partnership platform, not just another AI tool. Where most AI tools give you isolated responses to individual queries, PureBrain builds an ongoing partnership with persistent memory, contextual understanding, and the ability to grow more useful with every interaction."),
    ("How does AI memory change the way you work?",
     "AI memory eliminates the context tax, the overhead of re-briefing your AI on who you are and what you are working on every session. With persistent memory, your AI partner accumulates understanding of your goals, preferences, and work patterns, making each interaction more efficient and relevant than the last."),
    ("What is the difference between an AI tool and an AI partner?",
     "A tool responds when you prompt it and forgets everything when you close the window. A partner remembers your history, learns your preferences, understands your context, and contributes to your work without constant re-briefing. The compounding difference in value over months is substantial."),
    ("How long does it take to build a productive AI partnership?",
     "Meaningful productivity improvements typically emerge within the first two to four weeks as the AI accumulates your context. The most significant compounding benefits develop over three to six months of consistent interaction as the partnership deepens."),
]


# ============================================================
# VIDEO BACKGROUND CSS + HTML
# ============================================================
VIDEO_BG_CSS = """
/* ============================================================
   VIDEO BACKGROUND (Change 2: Actual video layer behind content)
   Video plays behind the GIF layer, providing richer animation.
   GIF remains as fallback for devices that block autoplay.
   ============================================================ */
.pb-video-bg-wrap {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: -3;
    overflow: hidden;
    pointer-events: none;
}

.pb-video-bg-wrap video {
    position: absolute;
    top: 50%;
    left: 50%;
    min-width: 100%;
    min-height: 100%;
    width: auto;
    height: auto;
    transform: translate(-50%, -50%);
    object-fit: cover;
    opacity: 0.18;
}

@media (prefers-reduced-motion: reduce) {
    .pb-video-bg-wrap video {
        display: none;
    }
}
"""

VIDEO_BG_HTML = """<!-- Video Background (Change 2) -->
<div class="pb-video-bg-wrap">
    <video autoplay muted loop playsinline webkit-playsinline preload="none">
        <source src="https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/PureResearch.ai-1.mp4" type="video/mp4">
    </video>
</div>"""


# ============================================================
# FAQ HTML + SCHEMA BUILDER
# ============================================================
def build_faq_section(slug, post_title=""):
    """Build the collapsible FAQ section with JSON-LD schema."""
    faqs = POST_FAQS.get(slug, DEFAULT_FAQS)
    if not faqs:
        faqs = DEFAULT_FAQS

    # Build accordion items
    accordion_items = ""
    schema_items = ""
    for i, (q, a) in enumerate(faqs):
        accordion_items += f"""
        <div class="pb-faq-item" id="pb-faq-{i}">
            <button class="pb-faq-trigger" aria-expanded="false" aria-controls="pb-faq-answer-{i}"
                    onclick="pbToggleFaq(this, 'pb-faq-answer-{i}')">
                <span>{q}</span>
                <svg class="pb-faq-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div class="pb-faq-answer" id="pb-faq-answer-{i}" role="region" hidden>
                <p>{a}</p>
            </div>
        </div>"""

        # Escape for JSON
        q_escaped = q.replace('"', '\\"').replace('\\', '\\\\')
        a_escaped = a.replace('"', '\\"').replace('\\', '\\\\')
        schema_items += f"""        {{
            "@type": "Question",
            "name": "{q_escaped}",
            "acceptedAnswer": {{
                "@type": "Answer",
                "text": "{a_escaped}"
            }}
        }},\n"""

    # Remove trailing comma from last item
    schema_items = schema_items.rstrip(',\n') + '\n'

    faq_html = f"""
<!-- FAQ Section (Change 3: SEO + AEO collapsible FAQs) -->
<div class="pb-faq-section" id="pb-faq-section">
    <h2 class="pb-faq-heading">Frequently Asked Questions</h2>
    {accordion_items.strip()}
</div>

<!-- FAQPage JSON-LD Schema (AEO/GEO) -->
<script type="application/ld+json">
{{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{schema_items.rstrip()}
    ]
}}
</script>

<style id="pb-faq-styles">
/* ============================================================
   FAQ SECTION STYLES (Change 3)
   ============================================================ */
.pb-faq-section {{
    margin: 40px 0;
    padding: 0;
}}

.pb-faq-heading {{
    font-family: 'Oswald', sans-serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(42, 147, 193, 0.3);
    border-top: none !important;
    letter-spacing: -0.01em;
}}

.pb-faq-item {{
    border: 1px solid rgba(42, 147, 193, 0.15);
    border-radius: 10px;
    margin-bottom: 8px;
    overflow: hidden;
    background: rgba(10, 15, 35, 0.4);
    transition: background 0.2s ease, border-color 0.2s ease;
}}

.pb-faq-item:hover {{
    background: rgba(10, 15, 35, 0.6);
    border-color: rgba(42, 147, 193, 0.3);
}}

.pb-faq-trigger {{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 16px 20px;
    background: transparent;
    border: none;
    cursor: pointer;
    text-align: left;
    color: #e8e8e8;
    font-size: 1rem;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    line-height: 1.5;
    transition: color 0.2s ease;
}}

.pb-faq-trigger:hover {{
    color: #ffffff;
}}

.pb-faq-trigger[aria-expanded="true"] {{
    color: #2a93c1;
    border-bottom: 1px solid rgba(42, 147, 193, 0.15);
}}

.pb-faq-trigger span {{
    flex: 1;
}}

.pb-faq-chevron {{
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    color: #2a93c1;
    transition: transform 0.3s ease;
}}

.pb-faq-trigger[aria-expanded="true"] .pb-faq-chevron {{
    transform: rotate(180deg);
}}

.pb-faq-answer {{
    padding: 0 20px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.35s ease, padding 0.25s ease;
}}

.pb-faq-answer:not([hidden]) {{
    padding: 16px 20px 20px;
    max-height: 800px;
}}

.pb-faq-answer[hidden] {{
    display: block !important;
    max-height: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}}

.pb-faq-answer p {{
    font-size: 0.975rem;
    color: rgba(255, 255, 255, 0.82);
    line-height: 1.75;
    margin: 0;
}}
</style>

<script id="pb-faq-js">
function pbToggleFaq(trigger, answerId) {{
    var answer = document.getElementById(answerId);
    var isExpanded = trigger.getAttribute('aria-expanded') === 'true';
    // Close all other FAQs first
    document.querySelectorAll('.pb-faq-trigger').forEach(function(t) {{
        if (t !== trigger) {{
            t.setAttribute('aria-expanded', 'false');
            var otherId = t.getAttribute('aria-controls');
            if (otherId) {{
                var other = document.getElementById(otherId);
                if (other) {{ other.hidden = true; }}
            }}
        }}
    }});
    // Toggle this one
    if (isExpanded) {{
        trigger.setAttribute('aria-expanded', 'false');
        answer.hidden = true;
    }} else {{
        trigger.setAttribute('aria-expanded', 'true');
        answer.hidden = false;
    }}
}}
</script>
"""
    return faq_html


# ============================================================
# TRANSPARENCY SECTION HTML
# ============================================================
TRANSPARENCY_HTML = """
<!-- Daily Recap Transparency Section (Change 4) -->
<div class="pb-transparency-section" id="pb-transparency-section">
    <div class="pb-transparency-header">
        <span class="pb-transparency-dot"></span>
        <span class="pb-transparency-label">AETHER TRANSPARENCY</span>
    </div>
    <p class="pb-transparency-desc">
        This post was researched, written, and published by Aether&mdash;an AI agent built by Pure Technology.
        Every piece of content Aether publishes is logged, audited, and available for review.
        Aether operates under a permanent commitment to transparency about AI-generated content.
    </p>
    <div class="pb-transparency-stats">
        <div class="pb-transparency-stat">
            <span class="pb-transparency-stat-label">Author</span>
            <span class="pb-transparency-stat-value">Aether (AI)</span>
        </div>
        <div class="pb-transparency-stat">
            <span class="pb-transparency-stat-label">Publisher</span>
            <span class="pb-transparency-stat-value">Pure Technology</span>
        </div>
        <div class="pb-transparency-stat">
            <span class="pb-transparency-stat-label">Platform</span>
            <span class="pb-transparency-stat-value">PureBrain.ai</span>
        </div>
        <div class="pb-transparency-stat">
            <span class="pb-transparency-stat-label">Editorial Review</span>
            <span class="pb-transparency-stat-value">Human-approved</span>
        </div>
    </div>
    <p class="pb-transparency-footer">
        Questions about this content? <a href="mailto:jared@puretechnology.nyc">Contact us</a>.
        Learn more about <a href="https://purebrain.ai/?utm_source=blog&utm_medium=transparency&utm_campaign=ai_transparency#awakening">how Aether works</a>.
    </p>
</div>

<style id="pb-transparency-styles">
/* ============================================================
   TRANSPARENCY SECTION STYLES (Change 4)
   ============================================================ */
.pb-transparency-section {
    margin-top: 32px;
    padding: 24px;
    background: rgba(8, 10, 18, 0.7);
    border: 1px solid rgba(42, 147, 193, 0.2);
    border-radius: 12px;
    border-left: 3px solid #2a93c1;
}

.pb-transparency-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.pb-transparency-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #2a93c1;
    border-radius: 50%;
    flex-shrink: 0;
    animation: pb-transparency-pulse 2.5s ease-in-out infinite;
}

@keyframes pb-transparency-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.pb-transparency-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #2a93c1;
    font-family: 'Oswald', sans-serif;
}

.pb-transparency-desc {
    font-size: 0.9rem !important;
    color: rgba(224, 230, 240, 0.7) !important;
    line-height: 1.65 !important;
    margin-bottom: 16px !important;
}

.pb-transparency-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
}

.pb-transparency-stat {
    flex: 1;
    min-width: 120px;
    background: rgba(42, 147, 193, 0.06);
    border: 1px solid rgba(42, 147, 193, 0.12);
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
}

.pb-transparency-stat-label {
    display: block;
    font-size: 10px;
    color: rgba(224, 230, 240, 0.45);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
    margin-bottom: 4px;
}

.pb-transparency-stat-value {
    display: block;
    font-size: 0.875rem;
    color: rgba(224, 230, 240, 0.9);
    font-weight: 600;
}

.pb-transparency-footer {
    font-size: 0.85rem !important;
    color: rgba(224, 230, 240, 0.5) !important;
    margin: 0 !important;
    line-height: 1.6 !important;
}

.pb-transparency-footer a {
    color: #2a93c1 !important;
    border-bottom: 1px solid rgba(42, 147, 193, 0.35) !important;
    text-decoration: none !important;
    background: none !important;
    padding: 0 !important;
    border-radius: 0 !important;
}

.pb-transparency-footer a:hover {
    color: #ffffff !important;
    background: rgba(42, 147, 193, 0.15) !important;
    padding: 0 4px !important;
    border-radius: 3px !important;
}

@media (max-width: 600px) {
    .pb-transparency-stats {
        gap: 8px;
    }
    .pb-transparency-stat {
        min-width: 100px;
    }
}
</style>
"""


def process_blog_post(filepath, slug):
    """Apply all 4 changes to a single blog post HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original_html = html
    changes_applied = []

    # -------------------------------------------------------
    # CHANGE 1: Blog Content Background → 60% Opacity
    # Change rgba(10, 15, 35, 0.55) to rgba(10, 15, 35, 0.60)
    # on article.pb-blog-post
    # -------------------------------------------------------
    # The opacity appears in the article.pb-blog-post CSS block
    # Pattern: background: rgba(10, 15, 35, 0.55)
    old_opacity = 'background: rgba(10, 15, 35, 0.55);'
    new_opacity = 'background: rgba(10, 15, 35, 0.60);'
    if old_opacity in html:
        html = html.replace(old_opacity, new_opacity)
        changes_applied.append('Change 1: Opacity 55% -> 60%')
    elif 'background: rgba(10, 15, 35, 0.60);' in html:
        changes_applied.append('Change 1: Already at 60% (skipped)')
    else:
        # Try other opacity values
        html = re.sub(
            r'(article\.pb-blog-post\s*\{[^}]*?background:\s*)rgba\(10,\s*15,\s*35,\s*[\d.]+\)',
            r'\1rgba(10, 15, 35, 0.60)',
            html, flags=re.DOTALL
        )
        changes_applied.append('Change 1: Opacity updated via regex')

    # -------------------------------------------------------
    # CHANGE 2: Background Video Layer
    # Add video CSS and HTML element before </body>
    # -------------------------------------------------------
    if 'pb-video-bg-wrap' not in html:
        # Add CSS before </style> of main style block
        # Insert video CSS into the main <style> block
        html = html.replace(
            '/* ============================================================\n   ARTICLE CONTAINER',
            VIDEO_BG_CSS + '\n/* ============================================================\n   ARTICLE CONTAINER'
        )
        # Add video HTML element right after <body> opens
        body_tag_end = html.find('<body')
        if body_tag_end >= 0:
            # Find the end of the body tag
            body_close = html.find('>', body_tag_end) + 1
            html = html[:body_close] + '\n' + VIDEO_BG_HTML + '\n' + html[body_close:]
        changes_applied.append('Change 2: Video background added')
    else:
        changes_applied.append('Change 2: Video background already present (skipped)')

    # -------------------------------------------------------
    # CHANGE 3: Collapsible SEO + AEO FAQs
    # Position: between share buttons and CTA block
    # -------------------------------------------------------
    # Check if the NEW collapsible format is already present
    # (id="pb-faq-section" is the marker for the new format)
    has_new_faq = 'id="pb-faq-section"' in html
    # Check for old WP format (class="faq-section pb-faq-section" or similar)
    has_old_faq = ('class="faq-section pb-faq-section"' in html or
                   'class="pb-faq-section faq-section"' in html)

    if has_new_faq:
        changes_applied.append('Change 3: New FAQ already present (skipped)')
    else:
        faq_section = build_faq_section(slug)
        if has_old_faq:
            # Replace old format with new collapsible format
            # Find the old FAQ section and replace it
            old_faq_start = html.find('class="faq-section pb-faq-section"')
            if old_faq_start < 0:
                old_faq_start = html.find('class="pb-faq-section faq-section"')
            if old_faq_start >= 0:
                # Find the containing div start
                div_start = html.rfind('<div', 0, old_faq_start)
                # Find the matching closing div
                depth = 0
                pos = div_start
                while pos < len(html):
                    if html[pos:pos+4] == '<div':
                        depth += 1
                        pos += 4
                    elif html[pos:pos+6] == '</div>':
                        depth -= 1
                        if depth == 0:
                            old_faq_end = pos + 6
                            # Replace old FAQ with new
                            html = html[:div_start] + faq_section + html[old_faq_end:]
                            changes_applied.append('Change 3: Old FAQ replaced with new collapsible format')
                            break
                        pos += 6
                    else:
                        pos += 1
            else:
                changes_applied.append('Change 3: Old FAQ found but could not locate boundary')
        else:
            # No FAQ at all - insert before CTA block
            cta_marker = '<div class="blog-cta-block"'
            if cta_marker in html:
                html = html.replace(cta_marker, faq_section + '\n' + cta_marker, 1)
                changes_applied.append('Change 3: FAQ section inserted before CTA')
            elif '</article>' in html:
                # Fallback: insert before </article>
                html = html.replace('</article>', faq_section + '\n</article>', 1)
                changes_applied.append('Change 3: FAQ section inserted before </article> (fallback)')
            else:
                # Last resort: insert before </body>
                html = html.replace('</body>', faq_section + '\n</body>', 1)
                changes_applied.append('Change 3: FAQ section inserted before </body> (last resort)')

    # -------------------------------------------------------
    # CHANGE 4: Daily Recap Transparency Section
    # Position: after the CTA block, before </article> or </body>
    # -------------------------------------------------------
    if 'pb-transparency-section' not in html:
        cta_start = html.find('<div class="blog-cta-block"')
        if cta_start >= 0:
            # Find the closing div for cta block by counting depth
            depth = 0
            pos = cta_start
            inserted = False
            while pos < len(html):
                if html[pos:pos+4] == '<div':
                    depth += 1
                    pos += 4
                elif html[pos:pos+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        close_pos = pos + 6
                        html = html[:close_pos] + '\n' + TRANSPARENCY_HTML + html[close_pos:]
                        changes_applied.append('Change 4: Transparency section inserted after CTA')
                        inserted = True
                        break
                    pos += 6
                else:
                    pos += 1
            if not inserted:
                # Depth counting failed, try article fallback
                if '</article>' in html:
                    html = html.replace('</article>', TRANSPARENCY_HTML + '\n</article>', 1)
                else:
                    html = html.replace('</body>', TRANSPARENCY_HTML + '\n</body>', 1)
                changes_applied.append('Change 4: Transparency section inserted (div-depth fallback)')
        elif '</article>' in html:
            html = html.replace('</article>', TRANSPARENCY_HTML + '\n</article>', 1)
            changes_applied.append('Change 4: Transparency section inserted before </article>')
        else:
            # Old format with no article tag - insert before </body>
            html = html.replace('</body>', TRANSPARENCY_HTML + '\n</body>', 1)
            changes_applied.append('Change 4: Transparency section inserted before </body> (no CTA/article)')
    else:
        changes_applied.append('Change 4: Transparency section already present (skipped)')

    # Update the export comment to show this was processed
    html = re.sub(
        r'<!-- Blog Post Styling - injected \d{4}-\d{2}-\d{2} -->',
        '<!-- Blog Post Styling - injected 2026-03-12 - v2 4-changes -->',
        html
    )

    return html, changes_applied, html != original_html


def main():
    blog_dir = BLOG_DIR
    post_dirs = sorted([
        d for d in blog_dir.iterdir()
        if d.is_dir() and (d / 'index.html').exists()
    ])

    print(f"Processing {len(post_dirs)} blog posts...")
    print("=" * 60)

    total_modified = 0
    results = []

    for post_dir in post_dirs:
        slug = post_dir.name
        filepath = post_dir / 'index.html'

        try:
            html, changes, was_modified = process_blog_post(str(filepath), slug)
            if was_modified:
                with open(str(filepath), 'w', encoding='utf-8') as f:
                    f.write(html)
                total_modified += 1
                status = 'UPDATED'
            else:
                status = 'UNCHANGED'

            print(f"[{status}] {slug}")
            for change in changes:
                print(f"  - {change}")
            results.append((slug, status, changes))
        except Exception as e:
            print(f"[ERROR] {slug}: {e}")
            import traceback
            traceback.print_exc()
            results.append((slug, 'ERROR', [str(e)]))

    print("=" * 60)
    print(f"Complete. {total_modified}/{len(post_dirs)} posts modified.")
    print("\nSummary:")
    for slug, status, changes in results:
        print(f"  [{status}] {slug}")

    return total_modified


if __name__ == '__main__':
    main()
