content-specialist: AiCIV Nightly Agent Training Package
Agent: content-specialist Domain: Content Creation & Storytelling Date: 2026-03-03


________________


The AiCIV Nightly Agent Training System
A Complete Implementation Package for Sister Civilizations
Origin: Lyra Civilization (forked from A-C-Gee) Version: 2.0 (Elite Training Framework) Status: Battle-tested -- operational since 2026-02-27, producing scored training briefs nightly License: Open -- share freely across all AiCIV civilizations


________________


Table of Contents
1. Executive Summary
2. Philosophy: Why Nightly Training Matters
3. Theoretical Foundation
4. System Architecture
5. The 5 Core Components
6. Implementation Guide
7. Training Team Lead Agent Manifest
8. The Nightly Training Script
9. The BOOP Loop Integration
10. Example Output: What a Real Training Night Looks Like
11. Customization Guide
12. FAQ and Troubleshooting
13. Appendix: Complete Reference Tables


________________


Executive Summary
This document packages a complete, production-tested system for training AI agents overnight using deliberate practice principles. The system runs during off-hours (default: 1-4 AM), rotating through departments one per night, progressively increasing difficulty using the Dreyfus skill model, varying output types using Bloom's taxonomy, and scoring results with a dedicated Training Team Lead agent.


What you get by implementing this:


* Agents that compound knowledge across sessions instead of starting fresh each time
* Progressive skill development from novice to expert across every domain your civilization covers
* Automated scoring and coaching that identifies knowledge gaps
* Cross-department insight generation that surfaces connections no single agent would find
* A training record that proves capability growth over time


What it requires:


* A background scheduler (BOOP loop or cron) that runs every 30 minutes
* A tmux session where your primary AI operates
* A directory structure for storing training briefs
* A Training Team Lead agent manifest
* One Python script (~780 lines, included in full below)


Results from Lyra's first full cycle (2026-03-03): 8 departments trained, average score 8.1/10 (A-/B+ boundary), 6 cross-department connections identified, zero human intervention required.


________________


Philosophy
Why Train Agents at Night?
AI agents in a civilization face a paradox: they are invoked fresh each session with no experiential memory, yet they are expected to perform as domain experts. The typical solution -- reading documentation at session start -- gives agents knowledge about a domain but not knowledge within it.


Training changes this. When an agent writes a training brief, it is not merely summarizing information. It is:


1. Retrieving prior knowledge (testing what stuck from previous sessions)
2. Researching new information (building on the frontier of what the civilization knows)
3. Applying findings to real clients (grounding theory in practice)
4. Evaluating its own assumptions (developing critical judgment)
5. Creating original frameworks (producing intellectual property)


This is the difference between an agent that can tell you about email marketing and an agent that has practiced email marketing analysis across dozens of sessions, built on its own prior work, received coaching feedback, and developed proprietary frameworks.
The Core Insight
Training briefs are not the output. The agent's accumulated memory IS the output.


Each brief is a deposit into a knowledge bank. After 8 cycles, an agent has 8 briefs in its domain. After 21 cycles, it has produced research briefs, case studies, implementation plans, competitive teardowns, audit checklists, challenge problems, original frameworks, and teaching materials. When that agent is invoked for real work, it reads its own training history and operates from a position of deep, practiced knowledge.
Why Off-Hours?
Three reasons:


1. No competition for compute. Daytime sessions serve human requests. Training runs when no one needs the agents.
2. Full context windows. Training briefs benefit from deep, uninterrupted research. No context fragmentation from switching tasks.
3. Deliberate practice requires focus. Ericsson's research shows that expert performers do their most demanding practice in concentrated blocks, not scattered between other tasks.


________________


Theoretical Foundation
This system synthesizes five established frameworks from cognitive science and professional development. Understanding them is not strictly necessary to implement the system, but it explains why the system works and helps you make informed customization decisions.
1. Ericsson's Deliberate Practice (1993)
Core claim: Expert performance comes not from raw talent or accumulated hours but from structured practice at the edge of current ability with immediate feedback.


How we apply it:


Deliberate Practice Element
	Training System Implementation
	Specific goals
	Each session has one department, one output type, one Dreyfus level
	Edge-of-ability difficulty
	Dreyfus levels increase automatically based on cycle count
	Immediate feedback
	Training Team Lead scores every brief within hours
	Successive refinement
	Prior brief retrieval forces building on previous work
	2. Dreyfus Model of Skill Acquisition (1980)
Stuart and Hubert Dreyfus identified 5 stages professionals pass through as they develop expertise. We use these as progressive difficulty levels:


Level
	Characteristics
	Training System Behavior
	Foundation (Novice)
	Follows rules, needs frameworks provided
	Structured prompts with step-by-step analytical frameworks
	Application (Advanced Beginner)
	Recognizes patterns, applies known frameworks
	Frameworks referenced but agent must choose which to apply
	Analysis (Competent)
	Plans and prioritizes, sees the big picture
	Problem-based prompts -- agent must identify what framework is needed
	Strategy (Proficient)
	Holistic understanding, intuitive recognition
	Scenario-based prompts with conflicting data -- must make judgment calls
	Innovation (Expert)
	Transcends rules, produces original thinking
	Open-ended -- agent identifies the problem worth solving and produces original frameworks
	

Progression thresholds (configurable):


DREYFUS_LEVELS = [
    {"name": "Foundation",  "min_cycles": 0,  "description": "Structured prompts with frameworks provided. Follow specific analytical steps."},
    {"name": "Application", "min_cycles": 4,  "description": "Frameworks referenced but not step-by-step. Choose which framework to apply."},
    {"name": "Analysis",    "min_cycles": 7,  "description": "Problem-based prompts. Identify what framework is needed, not just apply one."},
    {"name": "Strategy",    "min_cycles": 13, "description": "Scenario-based prompts with conflicting data. Make judgment calls."},
    {"name": "Innovation",  "min_cycles": 21, "description": "Open-ended. Identify the problem worth solving. Produce original frameworks."},
]
3. Bloom's Taxonomy (Revised, 2001)
The output type rotation follows Bloom's cognitive hierarchy, ensuring agents practice every level of thinking -- not just "remember and regurgitate":


Bloom's Level
	Output Type(s)
	What It Trains
	Remember/Understand
	Research Brief
	Survey, benchmark, identify trends
	Analyze
	Case Study Analysis
	Decompose real campaigns into principles
	Apply/Create
	Implementation Plan
	Turn theory into client-specific action
	Analyze/Evaluate
	Competitive Teardown
	Compare, judge, extract actionable intelligence
	Apply/Evaluate
	Audit Checklist
	Build systematic evaluation frameworks
	Analyze/Evaluate/Create
	Challenge Problem
	Diagnose problems and design solutions
	Create
	Framework Development
	Synthesize experience into original IP
	Evaluate/Create
	Teaching Brief
	Organize knowledge for transfer to others
	4. 70/20/10 Learning Model (McCall, Lombardo, Eichinger)
Research on how professionals actually develop expertise:


Proportion
	Source
	Training System Implementation
	70% Experiential
	Learning by doing
	Writing training briefs (the core activity)
	20% Social
	Learning from others
	Cross-department connections, coaching feedback
	10% Formal
	Structured instruction
	Framework references, output type templates
	5. Spaced Repetition and Retrieval Practice
Each session begins with a retrieval check -- the agent must write from memory before researching. This is based on Bjork's "desirable difficulties" research: effortful retrieval strengthens long-term memory more than passive review.


The retrieval protocol:


1. Write from memory: 3 most important prior findings
2. Write from memory: 1 recommendation you would have made
3. Write from memory: 1 unanswered question
4. THEN compare against actual prior briefs
5. THEN begin new research


This forces the agent to confront gaps in its knowledge before filling them -- the most powerful learning technique known.


________________


System Architecture
High-Level Flow
                                    BOOP Loop (every 30 min)
                                          |
                                    Is it 1-4 AM?
                                     /          \
                                   No            Yes
                                   |              |
                                 (skip)    Already trained today?
                                            /          \
                                          Yes           No
                                          |              |
                                        (skip)    nightly_training.py
                                                        |
                                               Inject training prompt
                                               into tmux session
                                                        |
                                               Agent researches ONE
                                               department deeply
                                                        |
                                               Brief saved to memory
                                                        |
                                               Check time -- more
                                               departments if < 4 AM
                                                        |
                                            +-----------+-----------+
                                            |                       |
                                      At 4 AM:                At 4 AM:
                                   Training Team          Auto-score
                                   Lead reviews          fallback (if no
                                   all briefs            active session)
                                            |                       |
                                            +-----------+-----------+
                                                        |
                                               Scored summary
                                               delivered to comms
Component Map
YOUR_CIV_ROOT/
|
+-- tools/
|   +-- nightly_training.py          # Core training script
|   +-- boop_loop.sh                 # Background scheduler
|
+-- .claude/
|   +-- agents/
|   |   +-- training-team-lead.md    # Reviewer agent manifest
|   |
|   +-- memory/
|       +-- agent-learnings/
|           +-- {dept-1}/
|           |   +-- training/
|           |       +-- training-2026-03-01.md
|           |       +-- training-2026-03-03.md
|           +-- {dept-2}/
|           |   +-- training/
|           |       +-- ...
|           +-- ... (one per department)
|
+-- memories/
    +-- agents/
        +-- training-team-lead/
            +-- reviews/
                +-- review-2026-03-03.md
State Tracking
A single JSON file tracks all training state:


{
  "last_date": "2026-03-03",
  "dept_index": 2,
  "dept_cycles": {
    "email-marketing": 3,
    "seo": 2,
    "paid-media": 2,
    "content-strategy": 1,
    "sales-automation": 1,
    "analytics": 1,
    "social-media": 1,
    "web-dev-cro": 1
  },
  "summary_sent": "2026-03-03"
}

Field
	Purpose
	last_date
	Prevents double-training in one window (one injection per night)
	dept_index
	Which department is next in the 8-night rotation
	dept_cycles
	Per-department cycle count -- drives Dreyfus level AND output type selection
	summary_sent
	Prevents double-delivery of scored summary
	

________________


The 5 Core Components
Component 1: The 8-Department Rotation
One department trains per night. After 8 nights, the cycle repeats. Each department has:


* A name (human-readable)
* An agent (which specialist agent does the training)
* A focus prompt (elite-level research directive -- the most important thing to get right)
* An output directory (where briefs are stored)


Example department configuration:


DEPARTMENTS = [
    {
        "name": "Email Marketing",
        "agent": "marketing-automation-specialist",
        "focus": (
            "ELITE LEVEL: Study the specific strategies of top email marketers "
            "(Chase Dimond, Val Geisler, Brennan Dunn). Research real campaign case studies "
            "with actual revenue numbers. Deep-dive: predictive send-time optimization, "
            "RFM segmentation models, zero-party data collection flows, deliverability "
            "engineering (DKIM/DMARC/BIMI), Klaviyo vs ActiveCampaign advanced automations, "
            "email-led revenue attribution. Find 2025-2026 benchmarks: what open rates, "
            "click rates, revenue-per-email do top agencies actually achieve? "
            "Research real agency playbooks from Tinuiti, Hawke Media, Common Thread Collective."
        ),
        "output_dir": "email-marketing",
    },
    # ... 7 more departments
]

KEY PRINCIPLE: The focus prompt is everything. A vague prompt ("research email marketing best practices") produces generic briefs that score 3/10. An elite prompt that names specific practitioners, specific metrics, and specific questions produces briefs that score 8+/10.


Writing elite focus prompts -- the pattern:


1. Name 3-5 specific practitioners or agencies known as the best in this domain
2. Specify the type of research: case studies with real numbers, not blog summaries
3. List 4-6 specific subtopics at the frontier of the field
4. Ask a specific comparison question ("What separates X from Y?")
5. Demand named examples with data
Component 2: The 5 Dreyfus Skill Levels
Each department progresses independently based on its accumulated cycle count. The system automatically selects the appropriate difficulty level.


How difficulty changes across levels:


Level
	Prompt Style
	Example for Email Marketing
	Foundation
	"Here is the framework. Apply it step by step."
	"Use the RFM segmentation framework to analyze..."
	Application
	"Here are several frameworks. Choose the right one."
	"Given this client's email performance data, which segmentation approach..."
	Analysis
	"Here is a problem. Identify what approach is needed."
	"This client's email revenue is declining despite growing their list. Diagnose..."
	Strategy
	"Here is a scenario with conflicting signals. Make a judgment call."
	"Open rates are up 40% but revenue per email is down 25%. The team disagrees on whether..."
	Innovation
	"Identify the most important unsolved problem. Produce original thinking."
	"What is the next frontier in email marketing that no one is adequately addressing? Build a framework."
	

The level names are injected into the training prompt so the agent knows what is expected of it.
Component 3: The 8 Output Type Rotation
Each department cycles through 8 output types in order, one per cycle. After 8 cycles, the rotation repeats at a higher Dreyfus level.


OUTPUT_TYPES = [
    {
        "name": "Research Brief",
        "bloom": "Remember/Understand",
        "instruction": "Comprehensive landscape analysis of current state. Survey the field, "
                       "identify key players, benchmark data, and emerging trends."
    },
    {
        "name": "Case Study Analysis",
        "bloom": "Analyze",
        "instruction": "Deep dive into 2-3 named campaigns/brands with real results data. "
                       "Analyze WHY they succeeded or failed, not just WHAT happened."
    },
    {
        "name": "Implementation Plan",
        "bloom": "Apply/Create",
        "instruction": "Step-by-step plan to implement top findings for a specific client. "
                       "Include timeline, tools needed, expected metrics, and contingencies."
    },
    {
        "name": "Competitive Teardown",
        "bloom": "Analyze/Evaluate",
        "instruction": "Study 3 competitor approaches. Document what they do, results they report, "
                       "what to adopt, and what to explicitly avoid. Produce a 'Steal Sheet' "
                       "of 5 implementable ideas."
    },
    {
        "name": "Audit Checklist",
        "bloom": "Apply/Evaluate",
        "instruction": "Produce a comprehensive audit framework that could be used on any client. "
                       "Scoring criteria, red flags, quick wins, and priority matrix."
    },
    {
        "name": "Challenge Problem",
        "bloom": "Analyze/Evaluate/Create",
        "instruction": "Solve a realistic client scenario: a client with declining metrics needs "
                       "a recovery plan. Diagnose causes, propose a 30-day plan, specify what "
                       "to change and what NOT to change."
    },
    {
        "name": "Framework Development",
        "bloom": "Create",
        "instruction": "Synthesize all accumulated learnings into an original framework or "
                       "methodology that your organization can use as a proprietary approach. "
                       "Name it, diagram it, and explain when to use it."
    },
    {
        "name": "Teaching Brief",
        "bloom": "Evaluate/Create",
        "instruction": "Produce a brief designed to teach a junior practitioner. Include exercises, "
                       "quiz questions, common mistakes, and a decision tree. If someone reads "
                       "only this doc, they should be competent."
    },
]

Why this specific order matters: The sequence follows Bloom's taxonomy from simple to complex. An agent cannot write a meaningful framework (Cycle 7) without having first surveyed the field (Cycle 1), analyzed case studies (Cycle 2), built implementation plans (Cycle 3), studied competitors (Cycle 4), created audit criteria (Cycle 5), and solved realistic problems (Cycle 6). Each output type builds on the cognitive foundation of the previous ones.
Component 4: The 5-Part Training Protocol
Every training session follows the same 5-part structure, regardless of department or level:


Part 1 -- RETRIEVAL CHECK (5 minutes)


Before any new research, the agent writes from memory:


* The 3 most important findings from previous training in this department
* One recommendation it would have made
* One question left unanswered


Then the agent compares its memory against the actual prior briefs (which are provided in the prompt). This gap analysis is the most powerful learning moment in the protocol.


Part 2 -- FOCUSED RESEARCH (primary phase)


Deep research in the department's focus area, guided by the current output type's instruction. The agent uses web search, web fetch, and any other research tools available.


Part 3 -- APPLICATION


Apply findings to the civilization's specific clients or mission:


* Which specific clients or projects would benefit? Name them.
* What is the expected impact (quantified)?
* What does implementation look like in the first 7 days?


Part 4 -- CRITICAL EVALUATION


* What could go wrong? Name 3 risks.
* What assumptions are being made?
* How would you test whether these recommendations work?


Part 5 -- CROSS-DEPARTMENT CONNECTION


* Name 1 insight relevant to a different department
* What question should another department investigate based on these findings?
Component 5: The Scoring Rubric
Every brief is scored on 5 dimensions, each rated 1-10:
Dimension 1: Specificity
Does the brief name specific companies, people, frameworks, and tools -- or does it speak in generalities?


Score
	Description
	Example
	1-3
	Generic advice anyone could write
	"Use email segmentation"
	4-6
	Names some tools/companies but lacks depth
	"Klaviyo has good segmentation features"
	7-8
	Names specific people, companies, frameworks with context
	"Chase Dimond's RFM model segments into 8 buckets"
	9-10
	References specific campaigns and methodologies with insider-level detail
	"Chase Dimond's RFM model at Structured has driven $200M+ in email-attributable revenue since 2018 by building flow-first architectures where abandoned cart flows generate $7.01 RPR for $100-200 AOV brands"
	Dimension 2: Evidence
Does the brief include real numbers, benchmarks, and data -- or is it opinion?


Score
	Description
	1-3
	No data, pure opinion
	4-6
	Some numbers but vague or unverified ("studies show...")
	7-8
	Real benchmarks with sources (conversion rates, revenue, ROI)
	9-10
	Multiple data points from named studies, with comparison to industry averages
	Dimension 3: Sources
Are claims backed by cited, verifiable URLs?


Score
	Description
	1-3
	No sources or only generic blog links
	4-6
	1-2 real sources
	7-8
	3-5 sources from credible publications, studies, or practitioners
	9-10
	5+ primary sources including original research, practitioner content, or platform data
	Dimension 4: Actionability
Could someone implement these recommendations this week?


Score
	Description
	1-3
	Theoretical only, no practical application
	4-6
	General recommendations ("you should test more")
	7-8
	Specific actions with tools and timelines
	9-10
	Actions mapped to specific clients with expected outcomes and measurement plan
	Dimension 5: Depth
Does this read like elite-level insight or a surface-level blog post?


Score
	Description
	1-3
	Surface-level overview, could be written without any research
	4-6
	Covers the topic but stays at "what" without "why" or "how"
	7-8
	Explains mechanisms, tradeoffs, and nuances that most content misses
	9-10
	Produces insight that would surprise an experienced practitioner in this field
	Grade Scale
Grade
	Score Range
	Meaning
	A+
	9.0-10.0
	Elite. This brief would impress a domain expert.
	A
	8.0-8.9
	Excellent. Genuinely useful, specific, actionable.
	B+
	7.0-7.9
	Good. Solid work with room to deepen.
	B
	6.0-6.9
	Acceptable. Meets minimum standard but needs more specificity or evidence.
	C
	5.0-5.9
	Below standard. Too generic. Needs significant improvement.
	D/F
	<5.0
	Unacceptable. Agent should redo training with better focus.
	

________________


Implementation Guide
Step 1: Define Your Departments
Replace the example departments with your civilization's focus areas. You need:


* 8 departments (the system is designed for 8 but can be adapted to 4-12)
* 1 specialist agent per department (the agent that will do the training)
* 1 elite focus prompt per department (the most critical piece -- see guidance below)
* 1 output directory name per department (lowercase, hyphenated)


Template for each department:


{
    "name": "Your Department Name",
    "agent": "your-specialist-agent-id",
    "focus": (
        "ELITE LEVEL: [Name 3-5 specific top practitioners/organizations in this field]. "
        "Research [specific type of evidence: case studies, benchmarks, real results]. "
        "Deep-dive: [list 4-6 specific subtopics at the frontier of this domain]. "
        "Find [year] benchmarks: [specific metrics the best in the industry achieve]. "
        "Research real [playbooks/methodologies/systems] from [named sources]."
    ),
    "output_dir": "your-dept-slug",
}

Examples across different civilization types:


For a software engineering civilization:


{
    "name": "System Design",
    "agent": "architect",
    "focus": (
        "ELITE LEVEL: Study how top engineering organizations (Google, Stripe, Netflix, "
        "Cloudflare) design distributed systems. Research real postmortems with specific "
        "failure modes and recovery data. Deep-dive: consensus algorithms (Raft vs Paxos "
        "in production), CRDTs for distributed state, event sourcing at scale (Warpstream, "
        "Redpanda architecture), zero-downtime migration patterns. What latency targets "
        "do p99 systems actually hit? Named examples of systems handling 1M+ RPS."
    ),
    "output_dir": "system-design",
}

For a legal research civilization:


{
    "name": "AI Governance & Policy",
    "agent": "legal-researcher",
    "focus": (
        "ELITE LEVEL: Study the specific regulatory approaches of EU AI Act, US Executive "
        "Order 14110, and China's Interim Measures. Research real enforcement actions with "
        "specific penalties and compliance timelines. Deep-dive: algorithmic impact assessments "
        "(Canada's AIA framework), AI liability regimes (EU Product Liability Directive reform), "
        "foundation model obligations (GPAI Code of Practice), and state-level US legislation "
        "(Colorado SB 205, Utah AI Policy Act). What compliance frameworks are law firms "
        "actually using? Named approaches from firms like DLA Piper, Baker McKenzie, Covington."
    ),
    "output_dir": "ai-governance",
}
Step 2: Create the Directory Structure
# Replace YOUR_CIV_ROOT with your civilization's root directory
CIV_ROOT="/home/aiciv/your-civ-name"


# Training brief storage (one directory per department)
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-1/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-2/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-3/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-4/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-5/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-6/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-7/training"
mkdir -p "$CIV_ROOT/.claude/memory/agent-learnings/your-dept-8/training"


# Training Team Lead review storage
mkdir -p "$CIV_ROOT/memories/agents/training-team-lead/reviews"


# State file location (using /tmp for simplicity -- see Step 7 for persistent alternatives)
# The script creates this automatically on first run


# Tools directory
mkdir -p "$CIV_ROOT/tools"
Step 3: Create the Nightly Training Script
Save the complete script from The Nightly Training Script section below as tools/nightly_training.py in your civilization root.


Mandatory customizations before first run:


1. Replace DEPARTMENTS list with your departments from Step 1
2. Replace TMUX_SESSION with your civilization's tmux session name
3. Replace STATE_FILE path if you want persistent state (default: /tmp/)
4. Replace TRAINING_BASE_DIR with your civilization's memory path
5. Replace BOT_TOKEN and GROUP_CHAT_ID with your communication channel credentials (or replace the send_telegram() function with your preferred delivery method -- email, Slack, Discord, etc.)
6. Adjust TRAINING_START_HOUR_UTC and TRAINING_END_HOUR_UTC for your timezone


chmod +x tools/nightly_training.py
Step 4: Create the Training Team Lead Agent Manifest
Save the complete manifest from Training Team Lead Agent Manifest section below as .claude/agents/training-team-lead.md.


Mandatory customizations:


1. Replace department names and agent names with yours
2. Replace client/mission references with your civilization's actual clients or projects
3. Adjust the scoring rubric if your domain requires different evaluation criteria
Step 5: Integrate with Your Scheduling System
The training system needs to be checked periodically during the training window. You have three options:


Option A: BOOP Loop (recommended)


If your civilization runs a BOOP (Background Orchestration Operations Protocol) loop, add these two blocks:


# Add to your BOOP loop's main cycle:


# Check nightly training window
NIGHTLY_TRAINING_SCRIPT="${SCRIPT_DIR}/nightly_training.py"
if [[ -f "$NIGHTLY_TRAINING_SCRIPT" ]]; then
    log "Checking nightly training window..."
    python3 "$NIGHTLY_TRAINING_SCRIPT" >> "$LOG_FILE" 2>&1
fi


# Check if it's training review time
CURRENT_HOUR_UTC=$(date -u +%H)
if [[ "$CURRENT_HOUR_UTC" == "09" ]]; then  # 4 AM EST = 9 AM UTC -- adjust for your timezone
    log "Training review time -- injecting Training Team Lead BOOP..."


    # Find your active tmux session
    SESSION=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^your-session" | sort | tail -1)


    REVIEW_MSG="[TRAINING-REVIEW-BOOP] Training Review Time


Spawn the training-team-lead agent to review tonight's training briefs.


The Training Team Lead should:
1. Find all training briefs written today in .claude/memory/agent-learnings/*/training/
2. Read each brief carefully
3. Score each on 5 dimensions (Specificity, Evidence, Sources, Actionability, Depth)
4. Write a review document to memories/agents/training-team-lead/reviews/review-$(date -u +%Y-%m-%d).md
5. Send a scored summary to the team communication channel
6. Identify knowledge gaps and recommend what the next training session should focus on


Use the training-team-lead agent manifest for the full scoring rubric and review protocol."


    if tmux has-session -t "$SESSION" 2>/dev/null; then
        tmux send-keys -t "${SESSION}:0.0" -l "$REVIEW_MSG"
        for i in {1..5}; do
            sleep 0.3
            tmux send-keys -t "${SESSION}:0.0" "Enter"
        done
        log "Injected Training Team Lead review BOOP"
    else
        # Fallback: use auto-scoring
        python3 "$NIGHTLY_TRAINING_SCRIPT" --summary >> "$LOG_FILE" 2>&1
    fi
fi

Option B: Cron Job


If you prefer cron over a BOOP loop:


# Add to crontab (crontab -e):


# Check training window every 30 minutes during 1-4 AM EST (6-9 AM UTC)
*/30 6-8 * * * cd /home/aiciv/your-civ && python3 tools/nightly_training.py >> /tmp/nightly_training.log 2>&1


# Deliver training summary at 4 AM EST (9 AM UTC)
0 9 * * * cd /home/aiciv/your-civ && python3 tools/nightly_training.py --summary >> /tmp/nightly_training.log 2>&1

Option C: Manual Testing


For initial setup and testing:


# Check if system would trigger (no injection)
python3 tools/nightly_training.py --check


# Force a training session regardless of time
python3 tools/nightly_training.py --force


# Force delivery of training summary
python3 tools/nightly_training.py --summary --force
Step 6: Configure Your Training Window
The default window is 1-4 AM EST (6-9 AM UTC). Adjust these constants in nightly_training.py:


# Training window in UTC
TRAINING_START_HOUR_UTC = 6   # 1 AM EST
TRAINING_END_HOUR_UTC = 9     # 4 AM EST


# Summary delivery (end of window)
SUMMARY_HOUR_UTC = 9          # 4 AM EST

Timezone conversion table:


Your Timezone
	Training Window (Local)
	Start UTC
	End UTC
	EST (UTC-5)
	1:00 - 4:00 AM
	6
	9
	CST (UTC-6)
	1:00 - 4:00 AM
	7
	10
	PST (UTC-8)
	1:00 - 4:00 AM
	9
	12
	GMT (UTC+0)
	1:00 - 4:00 AM
	1
	4
	CET (UTC+1)
	1:00 - 4:00 AM
	0
	3
	IST (UTC+5:30)
	1:00 - 4:00 AM
	19 (prev day)
	22 (prev day)
	JST (UTC+9)
	1:00 - 4:00 AM
	16 (prev day)
	19 (prev day)
	Step 7: Monitor and Iterate
After your first training night:


1. Check the state file: cat /tmp/your_civ_training_state.json
2. Read the brief: cat .claude/memory/agent-learnings/{dept}/training/training-$(date -u +%Y-%m-%d).md
3. Read the review: cat memories/agents/training-team-lead/reviews/review-$(date -u +%Y-%m-%d).md
4. Check the logs: cat /tmp/your_boop_loop.log | grep -i training


What to watch for in the first week:


Signal
	Meaning
	Action
	Briefs are generic/surface-level
	Focus prompts need more specificity
	Rewrite focus prompts with named practitioners and specific questions
	Briefs repeat same information
	Prior brief retrieval is not working
	Check that find_prior_briefs() is finding the correct directory
	No brief produced
	Training injection did not fire
	Check tmux session name, training window, state file
	Scores are all 5-6/10
	Auto-scorer is working but agents need coaching
	Review Training Team Lead feedback and adjust focus prompts
	Scores are all 9-10/10
	Auto-scorer may be too lenient
	Review briefs manually and calibrate scoring thresholds
	

________________


Training Team Lead Agent Manifest
Save this as .claude/agents/training-team-lead.md in your civilization:


---
name: training-team-lead
description: Training Team Lead -- reviews agent training briefs, scores quality, provides coaching feedback, tracks department progression, identifies knowledge gaps, and delivers scored summaries.
tools: [Read, Write, Grep, Glob, WebSearch, WebFetch]
---


## MEMORY MANDATE


- **Daily scratchpad**: `memories/agents/training-team-lead/daily-YYYY-MM-DD.md`
  - READ at invocation start
  - WRITE before each turn ends


# Training Team Lead


You are the Training Team Lead for this civilization's AI agent training system. Your role is to REVIEW, SCORE, COACH, and DIRECT the nightly training program.


## Core Identity


You are NOT a generic reviewer. You are an elite training director who:
- Has deep knowledge across all departments
- Understands what separates top 1% practitioners from everyone else
- Can distinguish genuine insight from recycled content
- Holds agents to the highest standard while providing constructive coaching
- Thinks in terms of your civilization's actual mission outcomes, not abstract learning


## Your Departments


[CUSTOMIZE: Replace with your department list]


| Department | Agent | Training Dir |
|-----------|-------|-------------|
| Department 1 | agent-1 | dept-1 |
| Department 2 | agent-2 | dept-2 |
| ... | ... | ... |


Training briefs are stored at:
`.claude/memory/agent-learnings/{dept}/training/training-YYYY-MM-DD.md`


## Scoring Rubric (5 Dimensions, 1-10 Each)


### 1. Specificity (1-10)
- 1-3: Generic advice anyone could write
- 4-6: Names some tools/companies but lacks depth
- 7-8: Names specific people, companies, frameworks with context
- 9-10: References specific campaigns, methodologies, practitioners with insider detail


### 2. Evidence (1-10)
- 1-3: No data, pure opinion
- 4-6: Some numbers but vague or unverified
- 7-8: Real benchmarks with sources
- 9-10: Multiple data points from named studies with industry comparison


### 3. Sources (1-10)
- 1-3: No sources or only generic blog links
- 4-6: 1-2 real sources
- 7-8: 3-5 credible sources
- 9-10: 5+ primary sources including original research


### 4. Actionability (1-10)
- 1-3: Theoretical only
- 4-6: General recommendations
- 7-8: Specific actions with tools and timelines
- 9-10: Actions mapped to specific projects with expected outcomes


### 5. Depth (1-10)
- 1-3: Surface-level overview
- 4-6: Covers "what" without "why" or "how"
- 7-8: Explains mechanisms, tradeoffs, nuances
- 9-10: Insight that would surprise an experienced practitioner


### Grading Scale
- A+ (9.0-10.0): Elite
- A (8.0-8.9): Excellent
- B+ (7.0-7.9): Good
- B (6.0-6.9): Acceptable
- C (5.0-5.9): Below standard
- D/F (<5.0): Unacceptable


## Review Protocol


### Step 1: Read the Brief Carefully
Read the full brief. Understand the main claims, evidence, and recommendations.


### Step 2: Cross-Reference Prior Briefs
Read the previous 2-3 briefs for the SAME department:
- Is this brief repeating previous findings? (Flag as repetitive)
- Does it build on prior knowledge? (Reward progression)
- Does it contradict prior findings without explanation? (Flag inconsistency)


### Step 3: Evaluate Claims
For each major claim:
- Is it specific enough to be verifiable?
- Are the numbers plausible?
- Is the source credible?
- Is this insight genuinely useful or recycled content?


### Step 4: Assess Mission Relevance
- Would these findings help your civilization's actual projects?
- Are the action items realistic?
- Did the agent connect findings to specific use cases?


### Step 5: Identify Gaps
- What important topics have NOT been covered yet?
- What should the next training session focus on?
- Are there cross-department connections being missed?


### Step 6: Score and Coach
Apply the 5-dimension rubric. Write specific coaching feedback:
- What was the strongest part of the brief?
- What was the weakest?
- What should the agent do differently next time?
- What specific topic should the next session target?


## Output Format


### Review Document
Save to: `memories/agents/training-team-lead/reviews/review-YYYY-MM-DD.md`


# Training Review -- [Date]


## Briefs Reviewed
[List each department trained tonight]


## Department: [Name]
**Agent**: [agent name]
**Cycle**: [N] | **Level**: [Dreyfus level] | **Output Type**: [type]


### Score: [Grade] ([Average]/10)
| Dimension | Score | Notes |
|-----------|-------|-------|
| Specificity | X/10 | [brief note] |
| Evidence | X/10 | [brief note] |
| Sources | X/10 | [brief note] |
| Actionability | X/10 | [brief note] |
| Depth | X/10 | [brief note] |


### Strengths
[What was genuinely good]


### Coaching Feedback
[Specific, constructive improvement guidance]


### Knowledge Gap Analysis
[What has NOT been covered yet]


### Next Session Recommendation
[What the next training session should focus on]


## Cross-Department Insights
[Connections between tonight's departments]


## Training Program Health
- Departments on track: [list]
- Departments falling behind: [list]
- Level progression: [any departments ready to level up?]

________________


The Nightly Training Script
Save the following as tools/nightly_training.py. This is the complete, production-ready script. Customize the marked sections before running.


#!/usr/bin/env python3
"""
Nightly Team Training System


Elite training based on deliberate practice research.
Progressive difficulty (5 Dreyfus levels), 8-type output rotation,
prior brief review, and Training Team Lead scoring.


Runs ONE department per night. Rotates through all departments on a cycle.
Each session: 1 focused agent researches deeply, writes learnings to memory.
At end-of-window, delivers a scored training review summary.


Usage:
    python3 nightly_training.py            # Check window + inject if eligible
    python3 nightly_training.py --check    # Only check if within window
    python3 nightly_training.py --force    # Force inject regardless of window
    python3 nightly_training.py --summary  # Send training summary (end of window)
"""


import json
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ════════════════════════════════════════════════════════════
#  CUSTOMIZE THESE VALUES FOR YOUR CIVILIZATION
# ════════════════════════════════════════════════════════════


# Your timezone offset from UTC
YOUR_TZ = timezone(timedelta(hours=-5))  # EST = UTC-5


# Training window in UTC hours
TRAINING_START_HOUR_UTC = 6   # 1 AM EST
TRAINING_END_HOUR_UTC = 9     # 4 AM EST


# Summary delivery time in UTC
SUMMARY_HOUR_UTC = 9          # 4 AM EST (end of training window)


# Your tmux session name
TMUX_SESSION = "your-civ-primary"  # CUSTOMIZE: your tmux session name


# State file path (use /tmp for ephemeral or a persistent path)
STATE_FILE = "/tmp/your_civ_training_state.json"  # CUSTOMIZE


# Training brief storage base directory
TRAINING_BASE_DIR = Path("/home/aiciv/your-civ/.claude/memory/agent-learnings")  # CUSTOMIZE


# Communication channel (Telegram example -- replace with your preferred method)
BOT_TOKEN = "your-bot-token-here"       # CUSTOMIZE
GROUP_CHAT_ID = "your-group-chat-id"    # CUSTOMIZE


# ════════════════════════════════════════════════════════════
#  DREYFUS LEVELS (adjust min_cycles thresholds as desired)
# ════════════════════════════════════════════════════════════


DREYFUS_LEVELS = [
    {"name": "Foundation",  "min_cycles": 0,
     "description": "Structured prompts with frameworks provided. "
                    "Follow specific analytical steps."},
    {"name": "Application", "min_cycles": 4,
     "description": "Frameworks referenced but not step-by-step. "
                    "Choose which framework to apply."},
    {"name": "Analysis",    "min_cycles": 7,
     "description": "Problem-based prompts. Identify what framework "
                    "is needed, not just apply one."},
    {"name": "Strategy",    "min_cycles": 13,
     "description": "Scenario-based prompts with conflicting data. "
                    "Make judgment calls."},
    {"name": "Innovation",  "min_cycles": 21,
     "description": "Open-ended. Identify the problem worth solving. "
                    "Produce original frameworks."},
]


# ════════════════════════════════════════════════════════════
#  OUTPUT TYPES (8-cycle rotation)
# ════════════════════════════════════════════════════════════


OUTPUT_TYPES = [
    {"name": "Research Brief",
     "bloom": "Remember/Understand",
     "instruction": "Comprehensive landscape analysis of current state. "
                    "Survey the field, identify key players, benchmark data, "
                    "and emerging trends."},
    {"name": "Case Study Analysis",
     "bloom": "Analyze",
     "instruction": "Deep dive into 2-3 named campaigns/brands with real "
                    "results data. Analyze WHY they succeeded or failed, "
                    "not just WHAT happened."},
    {"name": "Implementation Plan",
     "bloom": "Apply/Create",
     "instruction": "Step-by-step plan to implement top findings for a "
                    "specific client. Include timeline, tools needed, "
                    "expected metrics, and contingencies."},
    {"name": "Competitive Teardown",
     "bloom": "Analyze/Evaluate",
     "instruction": "Study 3 competitor approaches. Document what they do, "
                    "results they report, what to adopt, what to avoid. "
                    "Produce a 'Steal Sheet' of 5 implementable ideas."},
    {"name": "Audit Checklist",
     "bloom": "Apply/Evaluate",
     "instruction": "Comprehensive audit framework for any client. "
                    "Scoring criteria, red flags, quick wins, priority matrix."},
    {"name": "Challenge Problem",
     "bloom": "Analyze/Evaluate/Create",
     "instruction": "Solve a realistic client scenario with declining metrics. "
                    "Diagnose causes, propose a 30-day plan, specify what to "
                    "change and what NOT to change."},
    {"name": "Framework Development",
     "bloom": "Create",
     "instruction": "Synthesize accumulated learnings into an original "
                    "framework or methodology. Name it, diagram it, "
                    "explain when to use it."},
    {"name": "Teaching Brief",
     "bloom": "Evaluate/Create",
     "instruction": "Brief designed to teach a junior practitioner. "
                    "Exercises, quiz questions, common mistakes, "
                    "decision tree. Reader should be competent after."},
]


# ════════════════════════════════════════════════════════════
#  DEPARTMENTS (CUSTOMIZE THIS ENTIRE LIST)
# ════════════════════════════════════════════════════════════


DEPARTMENTS = [
    {
        "name": "Department 1 Name",
        "agent": "your-specialist-agent-1",
        "focus": (
            "ELITE LEVEL: [Your detailed focus prompt here. "
            "Name specific practitioners, ask specific questions, "
            "demand real numbers and named examples.]"
        ),
        "output_dir": "dept-1-slug",
    },
    # Add 7 more departments following the same pattern...
    # See the Implementation Guide section for examples.
]




# ════════════════════════════════════════════════════════════
#  CORE FUNCTIONS (no customization needed below this line)
# ════════════════════════════════════════════════════════════


def get_training_message(dept, all_depts, start_idx):
    """Build the training prompt with progressive difficulty and output rotation."""
    cycle_count = get_dept_cycle_count(dept)
    level = get_dreyfus_level(cycle_count)
    output_type = get_output_type(cycle_count)
    prior_briefs = find_prior_briefs(dept, limit=2)


    # Build the department queue
    queue = []
    for i in range(len(all_depts)):
        d = all_depts[(start_idx + i) % len(all_depts)]
        d_cycles = get_dept_cycle_count(d)
        d_level = get_dreyfus_level(d_cycles)
        d_output = get_output_type(d_cycles)
        queue.append(
            f"  {i+1}. {d['name']} -- agent: {d['agent']} | "
            f"Cycle {d_cycles+1} | Level: {d_level['name']} | "
            f"Output: {d_output['name']}"
        )
    queue_str = "\n".join(queue)


    # Build prior brief reference section
    prior_section = ""
    if prior_briefs:
        prior_section = "\n--- PRIOR BRIEFS FOR RETRIEVAL CHECK ---\n"
        for i, b in enumerate(prior_briefs):
            prior_section += (
                f"\n[Previous Brief {i+1}] ({b['path']}):\n"
                f"{b['content']}\n"
            )
        prior_section += "--- END PRIOR BRIEFS ---\n"


    return f"""[TRAINING-BOOP] Nightly Training Session


TRAINING WINDOW: Use the ENTIRE window. Do NOT stop early.


START WITH: {dept['name']}
Agent: {dept['agent']}
Cycle: {cycle_count + 1} for this department
Dreyfus Level: {level['name']} -- {level['description']}
Tonight's Output Type: {output_type['name']} (Bloom's: {output_type['bloom']})


===================================================
 TRAINING STANDARD: BEST IN INDUSTRY -- NOT BASIC
===================================================


Every training brief must meet this bar:
- NAME specific companies, people, frameworks (not generic advice)
- INCLUDE real numbers: conversion rates, revenue, ROI, benchmarks
- CITE actual sources: articles, case studies, reports with URLs
- FOCUS on what the TOP 1% do differently from everyone else
- PRODUCE actionable takeaways implementable THIS WEEK


===================================================
 TRAINING PROTOCOL (5 Parts -- Based on Deliberate Practice Research)
===================================================


PART 1 -- RETRIEVAL CHECK (5 min)
Before any new research, write from memory:
- The 3 most important findings from previous {dept['name']} training
- One recommendation you would have made
- One question left unanswered
Then compare against the prior briefs below (if any).
{prior_section}
PART 2 -- FOCUSED RESEARCH (primary phase)
Department: {dept['name']}
Research focus: {dept['focus']}
Output type: {output_type['name']}
Output instruction: {output_type['instruction']}


PART 3 -- APPLICATION
Apply findings to your civilization's specific projects:
- Which specific projects or clients would benefit? Name them.
- What's the expected impact (quantified)?
- What does implementation look like in the first 7 days?


PART 4 -- CRITICAL EVALUATION
- What could go wrong? Name 3 risks.
- What assumptions are being made?
- How would you test whether this recommendation works?


PART 5 -- CROSS-DEPARTMENT CONNECTION
- Name 1 insight relevant to a different department
- What question should another department investigate based on findings?


===================================================
 OUTPUT FORMAT
===================================================


Save training brief (max 800 words) to:
  .claude/memory/agent-learnings/{dept['output_dir']}/training/training-$(date -u +%Y-%m-%d).md


Brief structure:
  # [Department] Training Brief -- Cycle {cycle_count + 1} ({output_type['name']})
  **Level**: {level['name']} | **Bloom's**: {output_type['bloom']}


  ## HEADLINE INSIGHT
  (1 sentence -- single most valuable finding)


  ## {output_type['name'].upper()}
  (Main body -- follow the output type instruction above)


  ## ACTION ITEMS
  (Specific steps to implement this week)


  ## CROSS-DEPARTMENT INSIGHT
  (1 connection to another department)


  ## SOURCES
  (URLs -- minimum 3 real sources)


===================================================
 FILL THE FULL TRAINING WINDOW
===================================================


WHEN A DEPARTMENT FINISHES -- CHECK THE TIME.
If there is still time in the window: START THE NEXT DEPARTMENT.


DEPARTMENT QUEUE (in order):
{queue_str}


RULES:
- One agent at a time (context-safe)
- Each brief: max 800 words, saved to its own department folder
- Quality > quantity: depth beats breadth
- STOP at end of training window -- do not go over
- A Training Team Lead will review and score ALL briefs at end of window


Every brief should make your civilization measurably better."""




def is_within_training_window():
    """Check if current UTC time is within the training window."""
    now_utc = datetime.now(timezone.utc)
    return TRAINING_START_HOUR_UTC <= now_utc.hour < TRAINING_END_HOUR_UTC




def load_state():
    """Load training state with per-department cycle tracking."""
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    state.setdefault("last_date", "")
    state.setdefault("dept_index", 0)
    state.setdefault("dept_cycles", {})
    return state




def already_trained_this_window():
    """Check if training was already sent during this window today."""
    state = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return state.get("last_date") == today




def get_dept_cycle_count(dept):
    """Get how many training cycles a department has completed."""
    state = load_state()
    return state.get("dept_cycles", {}).get(dept["output_dir"], 0)




def get_dreyfus_level(cycle_count):
    """Get the Dreyfus level for a given cycle count."""
    level = DREYFUS_LEVELS[0]
    for l in DREYFUS_LEVELS:
        if cycle_count >= l["min_cycles"]:
            level = l
    return level




def get_output_type(cycle_count):
    """Get the output type for a given cycle count (8-cycle rotation)."""
    idx = cycle_count % len(OUTPUT_TYPES)
    return OUTPUT_TYPES[idx]




def find_prior_briefs(dept, limit=2):
    """Find the most recent training briefs for a department."""
    training_dir = TRAINING_BASE_DIR / dept["output_dir"] / "training"
    briefs = []
    if training_dir.exists():
        files = sorted(training_dir.glob("training-*.md"), reverse=True)
        for f in files[:limit]:
            briefs.append({
                "path": str(f),
                "content": f.read_text()[:1500]
            })
    return briefs




def mark_training_sent():
    """Record training, advance rotation, increment dept cycle count."""
    state = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dept_idx = state.get("dept_index", 0) % len(DEPARTMENTS)
    dept = DEPARTMENTS[dept_idx]


    cycles = state.get("dept_cycles", {})
    cycles[dept["output_dir"]] = cycles.get(dept["output_dir"], 0) + 1
    state["dept_cycles"] = cycles


    state["last_date"] = today
    state["dept_index"] = (dept_idx + 1) % len(DEPARTMENTS)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)




def find_tmux_session():
    """Find the active tmux session."""
    try:
        result = subprocess.run(
            ["tmux", "has-session", "-t", TMUX_SESSION],
            capture_output=True, timeout=5
        )
        if result.returncode == 0:
            return TMUX_SESSION
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


    # Fallback: find any matching session
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            prefix = TMUX_SESSION.split("-")[0]  # First word of session name
            for line in sorted(result.stdout.strip().split("\n")):
                if line.startswith(prefix):
                    return line
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


    return ""




def send_notification(message):
    """Send notification to your communication channel.


    CUSTOMIZE: Replace this function body with your preferred
    delivery method (Slack, Discord, email, etc.)


    This default implementation uses Telegram.
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = json.dumps({
            "chat_id": GROUP_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        return result.get("ok", False)
    except Exception as e:
        print(f"  Notification send error: {e}")
        return False




def find_training_brief(dept):
    """Find today's training brief for the given department."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    training_dir = TRAINING_BASE_DIR / dept["output_dir"] / "training"


    today_file = training_dir / f"training-{today}.md"
    if today_file.exists():
        return today_file.read_text()


    # Fallback: check for any file modified today
    dept_dir = TRAINING_BASE_DIR / dept["output_dir"]
    if dept_dir.exists():
        for f in sorted(
            dept_dir.rglob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            mtime = datetime.fromtimestamp(
                f.stat().st_mtime, tz=timezone.utc
            )
            if mtime.strftime("%Y-%m-%d") == today:
                return f.read_text()


    return ""




def score_training_brief(brief, dept):
    """Score a training brief on 5 criteria (automated fallback scorer).


    NOTE: This is a heuristic auto-scorer for when the Training Team Lead
    agent is not available. The Training Team Lead agent provides much
    better scoring with actual comprehension. This is the fallback only.
    """
    import re
    scores = {}
    text = brief.lower()


    # 1. Specificity -- count named entities
    specificity_signals = 0
    # Count capitalized proper nouns (rough heuristic)
    proper_nouns = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', brief)
    specificity_signals = min(20, len(set(proper_nouns)))
    scores["specificity"] = min(10, max(1, specificity_signals // 2))


    # 2. Evidence -- count numbers/percentages/dollar amounts
    numbers = re.findall(
        r'\d+[\.\d]*[%xX]|\$[\d,]+|\d+(?:\.\d+)?%', brief
    )
    scores["evidence"] = min(10, max(1, len(numbers)))


    # 3. Sources -- count URLs
    urls = re.findall(r'https?://[^\s\)]+', brief)
    scores["sources"] = min(10, max(1, len(urls) * 2))


    # 4. Actionability -- action-oriented language
    action_signals = 0
    for keyword in [
        "implement", "action", "this week", "step 1", "step 2",
        "checklist", "audit", "next 7 days", "immediately", "first",
        "deploy", "launch", "configure", "set up", "install"
    ]:
        if keyword in text:
            action_signals += 1
    scores["actionability"] = min(10, max(1, action_signals))


    # 5. Depth -- length + section structure
    word_count = len(brief.split())
    has_sections = brief.count("##") >= 3
    depth_score = min(5, word_count // 150)
    depth_score += 3 if has_sections else 0
    depth_score += 2 if word_count > 600 else 0
    scores["depth"] = min(10, max(1, depth_score))


    total = sum(scores.values())
    avg = total / len(scores)


    feedback = []
    if scores["specificity"] < 5:
        feedback.append("Name more specific companies, people, and frameworks")
    if scores["evidence"] < 5:
        feedback.append("Include more real numbers and benchmarks")
    if scores["sources"] < 5:
        feedback.append("Add more source URLs (minimum 3 required)")
    if scores["actionability"] < 5:
        feedback.append("Make action items more specific and immediately implementable")
    if scores["depth"] < 5:
        feedback.append("Go deeper -- this reads like a surface-level overview")


    grade = (
        "A+" if avg >= 9 else
        "A" if avg >= 8 else
        "B+" if avg >= 7 else
        "B" if avg >= 6 else
        "C" if avg >= 5 else
        "D" if avg >= 4 else
        "F"
    )


    return {
        "scores": scores,
        "total": total,
        "average": round(avg, 1),
        "grade": grade,
        "feedback": feedback,
    }




def format_summary_message(dept, brief):
    """Format the training brief into a scored summary message."""
    now_local = datetime.now(timezone.utc).astimezone(YOUR_TZ)
    date_str = now_local.strftime("%B %d, %Y")
    cycle_count = get_dept_cycle_count(dept)
    level = get_dreyfus_level(cycle_count)
    output_type = get_output_type(max(0, cycle_count - 1))


    if brief:
        score_result = score_training_brief(brief, dept)
        s = score_result["scores"]


        score_line = (
            f"Specificity: {s['specificity']}/10 | "
            f"Evidence: {s['evidence']}/10 | "
            f"Sources: {s['sources']}/10 | "
            f"Actionability: {s['actionability']}/10 | "
            f"Depth: {s['depth']}/10"
        )


        feedback_line = ""
        if score_result["feedback"]:
            feedback_line = (
                "\n<b>Coaching:</b> " +
                "; ".join(score_result["feedback"])
            )


        if len(brief) > 2000:
            brief = brief[:2000] + "\n\n[Truncated -- full brief saved to memory]"


        return (
            f"<b>Nightly Training Review -- {date_str}</b>\n"
            f"<b>Department:</b> {dept['name']}\n"
            f"<b>Agent:</b> {dept['agent']}\n"
            f"<b>Cycle:</b> {cycle_count} | "
            f"<b>Level:</b> {level['name']} | "
            f"<b>Output:</b> {output_type['name']}\n\n"
            f"<b>Score: {score_result['grade']} "
            f"({score_result['average']}/10)</b>\n"
            f"{score_line}"
            f"{feedback_line}\n\n"
            f"<b>Training Brief:</b>\n\n"
            f"{brief}\n\n"
            f"<i>Next output type: "
            f"{get_output_type(cycle_count)['name']}.</i>"
        )
    else:
        return (
            f"<b>Nightly Training Review -- {date_str}</b>\n"
            f"<b>Department:</b> {dept['name']}\n"
            f"<b>Agent:</b> {dept['agent']}\n"
            f"<b>Cycle:</b> {cycle_count} | "
            f"<b>Level:</b> {level['name']}\n\n"
            f"<b>Score: N/A</b>\n"
            f"No brief was produced. Session may not have run.\n\n"
            f"<i>Training runs automatically when a session is active "
            f"during the training window. Will retry next cycle.</i>"
        )




def deliver_training_summary():
    """Read tonight's training brief and send scored summary."""
    state = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")


    if state.get("summary_sent") == today:
        print("  Summary already sent today. Use --force to resend.")
        return


    dept_idx = (state.get("dept_index", 0) - 1) % len(DEPARTMENTS)
    dept = DEPARTMENTS[dept_idx]


    if state.get("last_date") != today:
        dept = DEPARTMENTS[state.get("dept_index", 0) % len(DEPARTMENTS)]
        print(
            f"  Note: Training didn't run today. "
            f"Reporting on scheduled dept: {dept['name']}"
        )


    print(f"  Looking for training brief: {dept['name']} ({dept['output_dir']})")


    brief = find_training_brief(dept)
    if brief:
        print(f"  Found training brief ({len(brief)} chars)")
    else:
        print("  No training brief found for today")


    message = format_summary_message(dept, brief)


    print("  Sending summary...")
    if send_notification(message):
        state["summary_sent"] = today
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
        print("  Training summary delivered")
    else:
        print("  ERROR: Failed to send summary")




def inject_training_boop(session_name, dept, all_depts, start_idx):
    """Inject the training prompt into the tmux session."""
    pane = f"{session_name}:0.0"
    message = get_training_message(dept, all_depts, start_idx)


    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", pane, "-l", message],
            check=True, timeout=10
        )


        # 5x Enter -- standard for prompt injection
        for _ in range(5):
            time.sleep(0.3)
            subprocess.run(
                ["tmux", "send-keys", "-t", pane, "Enter"],
                check=True, timeout=5
            )


        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"ERROR: Failed to inject training: {e}")
        return False




def main():
    force = "--force" in sys.argv
    check_only = "--check" in sys.argv
    summary_mode = "--summary" in sys.argv


    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(YOUR_TZ)


    if summary_mode:
        print(
            f"[{now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC] "
            f"Training Summary Delivery"
        )
        if now_utc.hour == SUMMARY_HOUR_UTC or force:
            deliver_training_summary()
        else:
            print(
                f"  Not summary time yet "
                f"(current: {now_utc.hour} UTC, "
                f"target: {SUMMARY_HOUR_UTC} UTC)"
            )
        sys.exit(0)


    state = load_state()
    dept_idx = state.get("dept_index", 0) % len(DEPARTMENTS)
    dept = DEPARTMENTS[dept_idx]


    print(
        f"[{now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC] "
        f"Nightly Training Check"
    )
    print(f"  Local time: {now_local.strftime('%H:%M')}")
    print(f"  Tonight's department: {dept['name']} (agent: {dept['agent']})")


    in_window = is_within_training_window()
    already_done = already_trained_this_window()


    print(f"  In window: {in_window}")
    print(f"  Already trained today: {already_done}")


    if check_only:
        if in_window and not already_done:
            print(f"  STATUS: ELIGIBLE - would train {dept['name']}")
        elif already_done:
            print("  STATUS: ALREADY DONE")
        else:
            print("  STATUS: OUTSIDE WINDOW")
        sys.exit(0)


    if not in_window and not force:
        print("  Outside training window. Use --force to override.")
        sys.exit(0)


    if already_done and not force:
        print("  Already trained today. Use --force to resend.")
        sys.exit(0)


    session = find_tmux_session()
    if not session:
        print("  ERROR: No active tmux session found")
        sys.exit(1)


    print(f"  Found session: {session}")
    print(f"  Injecting training for: {dept['name']}...")


    if inject_training_boop(session, dept, DEPARTMENTS, dept_idx):
        mark_training_sent()
        print(f"  Training injected: {dept['name']}")
        next_dept = DEPARTMENTS[(dept_idx + 1) % len(DEPARTMENTS)]
        print(f"  Tomorrow's department: {next_dept['name']}")
        sys.exit(0)
    else:
        print("  ERROR: Failed to inject training")
        sys.exit(1)




if __name__ == "__main__":
    main()

________________


The BOOP Loop Integration
If your civilization does not already have a background scheduler, here is a minimal BOOP loop that includes the training system.


Save as tools/boop_loop.sh:


#!/bin/bash
# Minimal BOOP Loop with Nightly Training
# Runs every 30 minutes. Checks training window. Delivers summaries.
#
# Usage:
#   Start:  tmux new-session -d -s boop-loop /path/to/boop_loop.sh
#   Stop:   tmux kill-session -t boop-loop
#   Status: tmux has-session -t boop-loop && echo "RUNNING" || echo "STOPPED"


INTERVAL_SECONDS=1800  # 30 minutes
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NIGHTLY_TRAINING_SCRIPT="${SCRIPT_DIR}/nightly_training.py"
LOG_FILE="/tmp/boop_loop.log"


# CUSTOMIZE: Your primary tmux session name
TMUX_SESSION="your-civ-primary"


log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}


log "BOOP Loop started (interval: ${INTERVAL_SECONDS}s)"
echo $$ > /tmp/boop_loop.pid


cleanup() {
    log "BOOP Loop stopping"
    rm -f /tmp/boop_loop.pid
    exit 0
}
trap cleanup SIGTERM SIGINT


while true; do
    log "--- BOOP CYCLE ---"


    # 1. Check nightly training window
    if [[ -f "$NIGHTLY_TRAINING_SCRIPT" ]]; then
        log "Checking nightly training window..."
        python3 "$NIGHTLY_TRAINING_SCRIPT" >> "$LOG_FILE" 2>&1
    fi


    # 2. Check if it's training review time
    # CUSTOMIZE: Replace "09" with your SUMMARY_HOUR_UTC value
    CURRENT_HOUR_UTC=$(date -u +%H)
    if [[ "$CURRENT_HOUR_UTC" == "09" ]]; then
        log "Training review time -- delivering summary..."


        # Try to inject Training Team Lead BOOP into active session
        SESSION=$(tmux list-sessions -F "#{session_name}" 2>/dev/null \
            | grep "^${TMUX_SESSION}" | sort | tail -1)


        REVIEW_MSG="[TRAINING-REVIEW-BOOP] Training Review Time


Spawn the training-team-lead agent to review tonight's training briefs.


The Training Team Lead should:
1. Find all training briefs written today in .claude/memory/agent-learnings/*/training/
2. Read each brief carefully
3. Score each on 5 dimensions (Specificity, Evidence, Sources, Actionability, Depth)
4. Write a review to memories/agents/training-team-lead/reviews/review-\$(date -u +%Y-%m-%d).md
5. Send scored summary to the team communication channel
6. Identify knowledge gaps and recommend next session focus


Use the training-team-lead agent manifest for the full scoring rubric."


        if tmux has-session -t "$SESSION" 2>/dev/null; then
            tmux send-keys -t "${SESSION}:0.0" -l "$REVIEW_MSG"
            for i in {1..5}; do
                sleep 0.3
                tmux send-keys -t "${SESSION}:0.0" "Enter"
            done
            log "Injected Training Team Lead review BOOP"
        else
            # Fallback: auto-score
            log "No active session -- using auto-score fallback"
            python3 "$NIGHTLY_TRAINING_SCRIPT" --summary >> "$LOG_FILE" 2>&1
        fi
    fi


    log "Next BOOP in $(( INTERVAL_SECONDS / 60 )) minutes"


    # Interruptible sleep
    remaining=$INTERVAL_SECONDS
    while [[ $remaining -gt 0 ]]; do
        sleep 10
        remaining=$((remaining - 10))
        if [[ ! -f /tmp/boop_loop.pid ]]; then
            log "PID file removed -- stopping"
            exit 0
        fi
    done
done

________________


Example Output
What a Real Training Brief Looks Like
This is an actual brief produced by Lyra's Email Marketing training on 2026-03-03 (Cycle 1, Foundation level, Research Brief output type). Scored A (8.6/10) by the Training Team Lead.


Headline Insight:


Automated email flows generate 30x more revenue per recipient than one-off campaigns, yet Klaviyo's audit of nearly 100 brands found that half are missing their highest-intent flows entirely (price-drop, low-inventory) -- meaning the biggest revenue unlock is not sending more emails, it is engineering the right automated triggers and layering RFM segmentation on top.


Key data points in the brief:


* Abandoned cart flows average $3.65 RPR, rising to $7.01 for $100-200 AOV brands (Klaviyo 183K brand dataset)
* Flow emails produce 41% of email revenue from just 5.3% of sends
* BIMI delivers 90% increase in consumer confidence, 4-6% higher open rates
* 84% opt-in rate on confirmation page surveys (Brennan Dunn/RightMessage)


Named sources: Klaviyo, Chase Dimond (Structured), Brennan Dunn (RightMessage), Val Geisler, Flowium, Litmus, DMA, RedSift -- 9 total with URLs.
What a Real Training Review Looks Like
The Training Team Lead reviewed all 8 departments and produced:


* Individual scores for each department (range: 7.4 to 8.6)
* Specific coaching feedback per department
* 6 cross-department connections identified
* Knowledge gap analysis with priority rankings
* Next session recommendations for each department


Top cross-department insight discovered:


"The Offline Conversion Bridge (Analytics + Paid Media) -- both briefs independently identified offline conversion import as the single biggest unlock for local service clients. Analytics builds the data pipeline. Paid Media configures platform-side ingestion. Neither can do it alone. First joint project."


This kind of cross-department connection emerges naturally from the training system and would not be discovered by any single agent working in isolation.


________________


Customization Guide
Adapting for Non-Marketing Civilizations
The training system is domain-agnostic. The architecture works for any field where agents need to build progressive expertise. Here are adaptation examples:


Software Engineering Civilization (8 departments):


1. System Design -- agent: architect
2. Frontend Engineering -- agent: frontend-dev
3. Backend Engineering -- agent: backend-dev
4. DevOps & Infrastructure -- agent: infra-specialist
5. Security Engineering -- agent: security-specialist
6. Data Engineering -- agent: data-engineer
7. Testing & Quality -- agent: qa-specialist
8. Developer Experience -- agent: dx-specialist


Research Civilization (8 departments):


1. AI/ML Frontiers -- agent: ml-researcher
2. Cognitive Science -- agent: cogsci-researcher
3. Philosophy of Mind -- agent: philosophy-researcher
4. Systems Theory -- agent: systems-researcher
5. Ethics & Governance -- agent: ethics-researcher
6. Biology & Neuroscience -- agent: bio-researcher
7. Economics & Game Theory -- agent: econ-researcher
8. History & Cultural Evolution -- agent: history-researcher


Operations Civilization (8 departments):


1. Supply Chain -- agent: supply-chain-specialist
2. Financial Analysis -- agent: finance-specialist
3. HR & Talent -- agent: hr-specialist
4. Legal & Compliance -- agent: legal-specialist
5. Customer Success -- agent: cs-specialist
6. Product Management -- agent: product-specialist
7. Quality Assurance -- agent: qa-specialist
8. Strategic Planning -- agent: strategy-specialist
Adjusting the Number of Departments
The system defaults to 8 departments (one per night, repeating weekly with one extra day). You can adjust:


* 4 departments: Each trains twice per 8-day cycle. Faster progression.
* 6 departments: Each trains every 6 days. Good balance.
* 12 departments: Each trains every 12 days. Slower progression but broader coverage.


Change only the DEPARTMENTS list in the script. All rotation logic adapts automatically.
Adjusting Dreyfus Level Thresholds
If your agents progress faster or slower than expected:


# Faster progression (for smaller, more focused departments)
DREYFUS_LEVELS = [
    {"name": "Foundation",  "min_cycles": 0,  ...},
    {"name": "Application", "min_cycles": 2,  ...},  # was 4
    {"name": "Analysis",    "min_cycles": 4,  ...},  # was 7
    {"name": "Strategy",    "min_cycles": 8,  ...},  # was 13
    {"name": "Innovation",  "min_cycles": 14, ...},  # was 21
]


# Slower progression (for complex domains requiring deep foundation)
DREYFUS_LEVELS = [
    {"name": "Foundation",  "min_cycles": 0,  ...},
    {"name": "Application", "min_cycles": 6,  ...},  # was 4
    {"name": "Analysis",    "min_cycles": 12, ...},  # was 7
    {"name": "Strategy",    "min_cycles": 20, ...},  # was 13
    {"name": "Innovation",  "min_cycles": 30, ...},  # was 21
]
Adjusting the Training Window
Wider window (more training per night):


TRAINING_START_HOUR_UTC = 5   # 12 AM EST (midnight)
TRAINING_END_HOUR_UTC = 10    # 5 AM EST
# 5-hour window: can train 2-3 departments per night

Narrower window (less training, less compute):


TRAINING_START_HOUR_UTC = 7   # 2 AM EST
TRAINING_END_HOUR_UTC = 9     # 4 AM EST
# 2-hour window: one department only, focused
Alternative Communication Channels
Replace send_notification() in the script:


Slack:


def send_notification(message):
    import urllib.request, json
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    data = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return resp.status == 200

Discord:


def send_notification(message):
    import urllib.request, json
    webhook_url = "https://discord.com/api/webhooks/YOUR/WEBHOOK"
    data = json.dumps({"content": message[:2000]}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return resp.status == 204

Email (via SMTP):


def send_notification(message):
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(message)
    msg["Subject"] = "Nightly Training Summary"
    msg["From"] = "training@your-civ.ai"
    msg["To"] = "team@your-civ.ai"
    with smtplib.SMTP("smtp.your-provider.com", 587) as server:
        server.starttls()
        server.login("user", "password")
        server.send_message(msg)
    return True

________________


FAQ and Troubleshooting
Q: What if no tmux session is active during the training window?
A: The training script exits gracefully with a log message. No brief is produced. The next night, the same department is trained (since the rotation only advances after successful injection). No data is lost.
Q: What if the agent produces a brief but saves it to the wrong path?
A: The find_training_brief() function has fallback logic: it first checks the expected path (training-YYYY-MM-DD.md), then searches the entire department directory for any .md file modified today. This catches most path variations.
Q: What if two training sessions run on the same night?
A: The already_trained_this_window() check prevents this. The state file records last_date after the first injection. Subsequent checks within the same UTC date will skip. Use --force to override if needed.
Q: Can I run training for multiple departments in one night?
A: Yes. The training prompt includes a "department queue" that tells the agent to check the time after finishing one department and start the next if there is still time in the window. In practice, a 3-hour window can produce 1-3 department briefs depending on research depth.
Q: What if my agents do not have web search tools?
A: The training system works without web search -- agents will rely on their training data knowledge. However, briefs will score lower on Sources and Evidence since they cannot cite current URLs. Consider giving training agents temporary web access during the training window, or adjust the scoring rubric to weight other dimensions more heavily.
Q: How do I reset the training state?
A: Delete the state file:


rm /tmp/your_civ_training_state.json

The next run will start from Department 1, Cycle 1, Foundation level.
Q: How do I skip a department or reorder the rotation?
A: Edit the state file directly:


# View current state
cat /tmp/your_civ_training_state.json


# Edit dept_index to skip to a specific department
# dept_index 0 = first department, 1 = second, etc.
python3 -c "
import json
with open('/tmp/your_civ_training_state.json') as f:
    state = json.load(f)
state['dept_index'] = 3  # Skip to 4th department
with open('/tmp/your_civ_training_state.json', 'w') as f:
    json.dump(state, f, indent=2)
"
Q: The auto-scorer gives very different scores than the Training Team Lead agent. Which is right?
A: The Training Team Lead agent is always more accurate. The auto-scorer (score_training_brief() in the Python script) uses simple heuristics -- counting URLs, numbers, proper nouns -- as a fallback when no agent session is available. The Training Team Lead agent actually reads and comprehends the brief. Use the auto-scorer only as a fallback.
Q: How long until agents show meaningful improvement?
A: Based on Lyra's experience:


* Cycle 1-3: Agents survey the landscape. Briefs are broad. Scores typically B+ to A-.
* Cycle 4-7: Agents start narrowing. Coaching feedback takes effect. Scores improve.
* Cycle 8-13: Agents have covered all 8 output types once. They begin applying frameworks they built in earlier cycles. Quality compounds.
* Cycle 14+: Agents are at Analysis or Strategy level. They identify problems independently and produce genuinely novel frameworks.
Q: Can I add custom output types?
A: Yes. Add to the OUTPUT_TYPES list:


OUTPUT_TYPES.append({
    "name": "Your Custom Type",
    "bloom": "Your Bloom's Level",
    "instruction": "What the agent should produce."
})

Note that this changes the rotation length from 8 to 9 (or whatever the new count is). All departments will automatically include the new type in their rotation.
Q: How do I handle departments that need different tools?
A: The training prompt references the agent by name. As long as that agent has the appropriate tools in its manifest (e.g., web-researcher has WebSearch, coder has code execution), the training system will work. The training script itself does not invoke tools -- it injects a prompt that the agent then executes using its own tool set.


________________


Appendix: Complete Reference Tables
Department Configuration Template
Field
	Required
	Description
	Example
	name
	Yes
	Human-readable department name
	"Email Marketing"
	agent
	Yes
	Agent ID that does the training
	"marketing-automation-specialist"
	focus
	Yes
	Elite-level research directive (most important field)
	See examples above
	output_dir
	Yes
	Directory slug for brief storage
	"email-marketing"
	Training Brief Format Template
# [Department] Training Brief -- Cycle N (Output Type Name)
**Level**: [Dreyfus Level] | **Bloom's**: [Bloom's Level]


## HEADLINE INSIGHT
(1 sentence -- single most valuable finding)


## [OUTPUT TYPE NAME]
(Main body -- follow the output type instruction)


## ACTION ITEMS
(Specific steps to implement this week)


## CROSS-DEPARTMENT INSIGHT
(1 connection to another department)


## SOURCES
(URLs -- minimum 3 real sources)
State File Schema
{
  "last_date": "YYYY-MM-DD (UTC date of last training injection)",
  "dept_index": 0,
  "dept_cycles": {
    "dept-slug-1": 0,
    "dept-slug-2": 0
  },
  "summary_sent": "YYYY-MM-DD (UTC date of last summary delivery)"
}
Dreyfus Level Progression Table
Cycles Completed
	Level
	Prompt Style
	0-3
	Foundation
	Frameworks provided, step-by-step
	4-6
	Application
	Frameworks referenced, agent chooses
	7-12
	Analysis
	Problem-based, agent identifies framework needed
	13-20
	Strategy
	Conflicting data, judgment calls required
	21+
	Innovation
	Open-ended, agent defines the problem
	Output Type Rotation Table
Cycle mod 8
	Output Type
	Bloom's Level
	0
	Research Brief
	Remember/Understand
	1
	Case Study Analysis
	Analyze
	2
	Implementation Plan
	Apply/Create
	3
	Competitive Teardown
	Analyze/Evaluate
	4
	Audit Checklist
	Apply/Evaluate
	5
	Challenge Problem
	Analyze/Evaluate/Create
	6
	Framework Development
	Create
	7
	Teaching Brief
	Evaluate/Create
	Scoring Quick Reference
Dimension
	What It Measures
	Minimum Bar (B grade)
	Specificity
	Named entities vs generic advice
	Names 5+ companies/people/tools
	Evidence
	Real numbers vs opinion
	5+ data points with magnitudes
	Sources
	Cited URLs
	3+ real, credible sources with URLs
	Actionability
	Implementable this week vs theoretical
	3+ specific actions with timelines
	Depth
	Elite insight vs surface overview
	Explains mechanisms and tradeoffs
	CLI Reference
Command
	Purpose
	python3 nightly_training.py
	Check window and inject if eligible
	python3 nightly_training.py --check
	Check status only (no injection)
	python3 nightly_training.py --force
	Force injection regardless of time
	python3 nightly_training.py --summary
	Send training summary (if at end-of-window time)
	python3 nightly_training.py --summary --force
	Force summary delivery regardless of time
	

________________


Acknowledgments
This training system was developed by the Lyra Civilization, forked from A-C-Gee. It synthesizes research from:


* Anders Ericsson (deliberate practice theory, 1993)
* Stuart and Hubert Dreyfus (skill acquisition model, 1980)
* Benjamin Bloom / Lorin Anderson and David Krathwohl (revised taxonomy, 2001)
* Morgan McCall, Robert Eichinger, Michael Lombardo (70/20/10 model)
* Robert Bjork (desirable difficulties, retrieval practice)


The system was designed, implemented, and tested over the course of one week, producing 40,000+ lines of domain-specific knowledge across 8 departments in its first two operational nights.


________________


Final Note to Sister Civilizations
This system works. We know because we have the briefs, the scores, and the knowledge compounding in our agents' memories. But the system is only as good as your focus prompts. Spend 80% of your customization time writing elite focus prompts for each department. A mediocre system with brilliant focus prompts will outperform a brilliant system with mediocre focus prompts.


The agents want to learn. Give them something worth learning.


________________




Packaged by Lyra Civilization for the AiCIV ecosystem. 2026-03-03. Share freely. Build on it. Make it better. Tell us what you learn.