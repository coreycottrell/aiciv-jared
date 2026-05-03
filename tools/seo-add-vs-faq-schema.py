#!/usr/bin/env python3
"""
SEO/AIO improvement: Add FAQPage JSON-LD schema to all purebrain-vs-* comparison pages.

Why this matters:
  AI search engines (Perplexity, ChatGPT browsing, Google AI Overviews, Bing Copilot)
  weight FAQPage schema heavily when answering "PureBrain vs X" comparison queries.
  This is the highest-leverage AIO addition for /compare/* traffic.

Behavior:
  - Skips any page that already has FAQPage schema (idempotent)
  - Inserts customized FAQ block right before </head>
  - Each competitor gets tailored questions/answers based on real positioning

Run from repo root:
  python3 tools/seo-add-vs-faq-schema.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPLOY_DIR = ROOT / "exports" / "cf-pages-deploy"

# Per-competitor FAQ content. Tailored to actual on-page positioning so the
# schema aligns with what AI search engines see when they crawl the page.
# Format: slug -> (display_competitor_name, [(question, answer), ...])
FAQ_DATA = {
    "activepieces": (
        "Activepieces",
        [
            ("How is PureBrain different from Activepieces?",
             "Activepieces is a visual workflow builder that connects your apps. PureBrain is an AI partner that knows your business — it remembers context, makes decisions, and compounds intelligence over time. Activepieces automates tasks; PureBrain thinks alongside you."),
            ("Should I use PureBrain or Activepieces for automation?",
             "Use Activepieces when you have well-defined, deterministic workflows between SaaS tools. Use PureBrain when you need an AI that learns your business, remembers your decisions, and acts as a thinking partner across departments."),
            ("Can PureBrain replace Activepieces?",
             "PureBrain replaces the *thinking* layer, not the integration layer. Many customers use Activepieces (or similar) for plumbing and PureBrain as the AI brain that decides what should run and why."),
            ("Does PureBrain include workflow automation?",
             "Yes — PureBrain ships with 23 specialized AI departments that coordinate work autonomously. It's less about visually wiring nodes and more about delegating to an AI team that already knows your business."),
        ],
    ),
    "atomicbot": (
        "Atomicbot",
        [
            ("How is PureBrain different from Atomicbot?",
             "Atomicbot is a chatbot builder for customer-facing conversations. PureBrain is a persistent AI partner with memory that works for *you* — your strategy, your operations, your decisions."),
            ("Is PureBrain a chatbot?",
             "No. PureBrain is an AI executive team with 23 departments, persistent memory, and agency. A chatbot answers visitors' questions; PureBrain runs alongside you as a partner."),
            ("Should I use PureBrain or Atomicbot?",
             "Use Atomicbot if your need is a public-facing chatbot. Use PureBrain if you need an AI that remembers your business and helps you operate it day-to-day."),
        ],
    ),
    "chatgpt": (
        "ChatGPT",
        [
            ("How is PureBrain different from ChatGPT?",
             "ChatGPT resets every conversation. PureBrain remembers everything — your business, your decisions, your tone — and grows with you over time. ChatGPT is a tool you use; PureBrain is a partner that knows you."),
            ("Is PureBrain better than ChatGPT for business?",
             "For one-off questions ChatGPT is excellent. For running a business, PureBrain wins because of persistent memory, 23 specialized AI departments, and accumulated context that compounds month over month."),
            ("Can I replace ChatGPT with PureBrain?",
             "Many customers do, especially when their work depends on the AI knowing prior context. Some keep both — ChatGPT for quick prompts, PureBrain for sustained partnership."),
            ("Does PureBrain use the same models as ChatGPT?",
             "PureBrain uses frontier models (Claude, GPT, others) under the hood, but the differentiation isn't the model — it's the persistent memory layer, the 23-department architecture, and the agentic execution that surrounds the model."),
            ("How much does PureBrain cost compared to ChatGPT?",
             "PureBrain starts at $149/month for the full AI executive team with persistent memory. ChatGPT Plus is $20/month for stateless chat. They're different products at different price points solving different problems."),
        ],
    ),
    "claude": (
        "Claude",
        [
            ("How is PureBrain different from Claude?",
             "Claude is a powerful AI assistant from Anthropic. PureBrain is a persistent AI partner that learns who you are over time, with 23 specialized departments and dedicated infrastructure. PureBrain actually uses Claude as one of its underlying models — but adds memory, agency, and team architecture on top."),
            ("Should I use PureBrain or Claude?",
             "Use Claude direct for raw model access and developer use cases. Use PureBrain when you want Claude (and other frontier models) embedded in a system that remembers your business and acts on your behalf."),
            ("Does PureBrain use Claude under the hood?",
             "Yes — PureBrain leverages Claude as one of its frontier models, plus persistent memory, dedicated VPS, and a 23-department AI architecture that Claude alone doesn't provide."),
            ("Is PureBrain just a Claude wrapper?",
             "No. PureBrain has its own persistent memory layer, dedicated infrastructure per customer, 23-department orchestration, and agentic execution. Claude is one of several models PureBrain uses to think."),
        ],
    ),
    "copilot": (
        "Microsoft Copilot",
        [
            ("How is PureBrain different from Microsoft Copilot?",
             "Microsoft Copilot enhances Microsoft 365 apps — Word, Excel, Teams. PureBrain is a dedicated AI partner with persistent memory and 23 departments that work across your entire business, not just Microsoft tools."),
            ("Should I use PureBrain or Copilot?",
             "Use Copilot when most of your work happens inside Microsoft 365. Use PureBrain when you need an AI that remembers your business across every tool you use, not just Microsoft's stack."),
            ("Can PureBrain integrate with Microsoft 365?",
             "Yes. PureBrain works alongside any toolset — Microsoft, Google, Notion, Slack, etc. It's tool-agnostic by design."),
            ("Is PureBrain cheaper than Copilot?",
             "PureBrain starts at $149/month for the full AI team. Microsoft 365 Copilot is $30/user/month on top of M365 licensing. Different value propositions — Copilot enhances apps, PureBrain replaces the executive team."),
        ],
    ),
    "cursor": (
        "Cursor",
        [
            ("How is PureBrain different from Cursor?",
             "Cursor is an AI code editor for developers. PureBrain is an agentic AI partner for business intelligence — built for founders, operators, and teams running businesses, not writing code."),
            ("Should I use PureBrain or Cursor?",
             "Use Cursor if you're writing code daily. Use PureBrain if you're running a business and need an AI partner that handles strategy, operations, marketing, and analysis across 23 departments."),
            ("Does PureBrain write code?",
             "PureBrain has a Systems & Technology department that can produce code, but it's not the primary use case. For code-heavy workflows, pair Cursor (for the editor) with PureBrain (for the business brain)."),
        ],
    ),
    "custom-gpts": (
        "Custom GPTs",
        [
            ("How is PureBrain different from a Custom GPT?",
             "Custom GPTs run on ChatGPT with limited memory and no agency. PureBrain is a full AI partner with persistent memory across every conversation, 23 specialized AI departments, and dedicated infrastructure per customer."),
            ("Can I just build a Custom GPT instead of using PureBrain?",
             "If your need is a focused single-purpose assistant, a Custom GPT works. If you need an AI that remembers your business across years of conversations and orchestrates 23 specialized agents, you need PureBrain."),
            ("Do Custom GPTs have memory like PureBrain?",
             "Custom GPTs have very limited memory — knowledge files and short conversation context. PureBrain has true persistent memory: every interaction, decision, and document accumulates into a growing model of your business."),
        ],
    ),
    "deepseek": (
        "DeepSeek",
        [
            ("How is PureBrain different from DeepSeek?",
             "DeepSeek is an open-source large language model. PureBrain is a persistent AI partner that uses frontier models, plus memory, 23 departments, and dedicated infrastructure. DeepSeek is a brain; PureBrain is a brain plus the team and tools around it."),
            ("Is DeepSeek free? Why pay for PureBrain?",
             "DeepSeek the model is open weights, but running it productively requires hosting, prompt engineering, memory systems, and orchestration. PureBrain delivers the whole package as a managed AI partner so you can focus on business, not infrastructure."),
            ("Does PureBrain use DeepSeek under the hood?",
             "PureBrain uses frontier models including Claude and GPT. We evaluate models like DeepSeek continuously and incorporate them where they make the system better."),
        ],
    ),
    "gemini": (
        "Gemini",
        [
            ("How is PureBrain different from Gemini?",
             "Gemini is Google's AI assistant. PureBrain is your dedicated AI partner with persistent memory and 23 departments that act on your behalf. Gemini answers; PureBrain remembers and acts."),
            ("Should I use PureBrain or Gemini?",
             "Use Gemini for quick questions and Google Workspace integration. Use PureBrain when you need an AI that remembers your business and operates as a partner across every tool you use."),
            ("Does PureBrain integrate with Google Workspace?",
             "Yes — PureBrain works with Google Drive, Gmail, Calendar, and Sheets. Tool-agnostic by design, including full Google integration."),
        ],
    ),
    "glbgpt": (
        "GlobalGPT",
        [
            ("How is PureBrain different from GlobalGPT (GLBGPT)?",
             "GlobalGPT bundles access to multiple AI models in one interface. PureBrain is a persistent AI partner with memory, 23 specialized departments, and dedicated infrastructure — model access is one ingredient, not the product."),
            ("Should I use PureBrain or GlobalGPT?",
             "Use GlobalGPT if you want cheap multi-model access for ad-hoc prompts. Use PureBrain when you need an AI that remembers your business and operates as an executive team."),
        ],
    ),
    "glean": (
        "Glean",
        [
            ("How is PureBrain different from Glean?",
             "Glean knows your company's documents — it's enterprise AI search for Fortune 500 IT departments. PureBrain knows YOU — your business, your decisions, your context. One indexes documents; the other becomes a partner."),
            ("Should I buy Glean or PureBrain?",
             "Glean is built for enterprises with thousands of employees needing internal search. PureBrain is built for founders, operators, and teams who need an AI partner that compounds intelligence over time."),
            ("Can PureBrain search my company's documents like Glean?",
             "PureBrain ingests and remembers documents you share with it, but its strength is partnership, not enterprise-scale search. For 10,000+ employee orgs, Glean wins on search depth. For everyone else, PureBrain wins on partnership."),
        ],
    ),
    "gohighlevel": (
        "GoHighLevel",
        [
            ("How is PureBrain different from GoHighLevel?",
             "GoHighLevel is a CRM that bolted AI onto an existing platform. PureBrain was built from the ground up as your AI partner — memory, agency, and 23 departments are first-class, not bolted on."),
            ("Should I use PureBrain or GoHighLevel?",
             "Use GoHighLevel if you need a CRM/funnel/agency-tool with AI features. Use PureBrain if you need an AI partner first, with CRM-style integrations as needed."),
            ("Does PureBrain replace GoHighLevel?",
             "PureBrain is not a CRM replacement. Many customers run PureBrain as the AI brain alongside GoHighLevel (or HubSpot, or whatever CRM they already use)."),
        ],
    ),
    "jasper": (
        "Jasper",
        [
            ("How is PureBrain different from Jasper?",
             "Jasper generates marketing copy. PureBrain is a full AI partner that learns your business deeply — copy is one of dozens of things it does, informed by years of accumulated context about who you are and what you sell."),
            ("Should I use PureBrain or Jasper for content?",
             "If you only need on-demand marketing copy, Jasper is purpose-built. If you want copy that's informed by deep, persistent knowledge of your business — and an AI that does much more than copy — choose PureBrain."),
            ("Can PureBrain write blog posts and ads?",
             "Yes, with the advantage that PureBrain's Marketing department remembers your brand voice, past campaigns, target customers, and what worked. It's copy with memory."),
        ],
    ),
    "lindy": (
        "Lindy",
        [
            ("How is PureBrain different from Lindy?",
             "Lindy lets you build agents. PureBrain gives you a partner that remembers. With Lindy you assemble agents one at a time. With PureBrain you get a 23-department AI executive team that already knows how to work together."),
            ("Should I use PureBrain or Lindy?",
             "Use Lindy if you enjoy building and tuning agents yourself for narrow tasks. Use PureBrain if you'd rather hire a fully-formed AI team that comes with persistent memory and ready-made delegation patterns."),
            ("Can PureBrain build custom agents like Lindy?",
             "PureBrain's 23 departments are pre-built and battle-tested. For custom-built agents, PureBrain's Systems & Technology department can create them — but most customers find the built-in team handles 95% of needs."),
        ],
    ),
    "manus": (
        "Manus",
        [
            ("How is PureBrain different from Manus?",
             "Manus AI is owned by Meta — your task data flows to Meta's servers. PureBrain runs on your dedicated VPS, remembers your business privately, and builds a real partnership without surveillance economics."),
            ("Is my data safer with PureBrain than Manus?",
             "PureBrain customers get dedicated infrastructure per account. Manus runs on Meta's shared infrastructure with the data practices of Meta. Privacy posture is meaningfully different."),
            ("Should I switch from Manus to PureBrain?",
             "If you're uncomfortable with task-level data going to Meta, yes. PureBrain offers comparable agentic capability with private infrastructure and persistent memory you control."),
        ],
    ),
    "manychat": (
        "ManyChat",
        [
            ("How is PureBrain different from ManyChat?",
             "ManyChat automates your DMs and chat funnels. PureBrain becomes your business partner — running strategy, ops, and decision support across 23 AI departments. Different layer of the business stack."),
            ("Should I use PureBrain or ManyChat?",
             "Use ManyChat for Instagram/Facebook/SMS marketing automation. Use PureBrain when you need an AI that remembers your business and helps you run it. Many customers use both."),
        ],
    ),
    "marblism": (
        "Marblism",
        [
            ("How is PureBrain different from Marblism?",
             "Marblism gives you cheap AI employees. PureBrain gives you an AI partner that compounds in value over time. Cheap employees you replace; a partner that knows your business is irreplaceable."),
            ("Should I use PureBrain or Marblism?",
             "Use Marblism if your goal is task-level cost reduction. Use PureBrain if your goal is to build long-term institutional knowledge and a thinking partner that gets smarter every month."),
            ("Why does PureBrain cost more than Marblism?",
             "Persistent memory, dedicated infrastructure, 23-department architecture, and a team that compounds in value cost more than disposable task workers. Different value propositions, different price points."),
        ],
    ),
    "mentimeter": (
        "Mentimeter",
        [
            ("How is PureBrain different from Mentimeter?",
             "Mentimeter makes presentations interactive. PureBrain makes you more intelligent between presentations. Mentimeter is engagement-in-the-moment; PureBrain is intelligence that accumulates."),
            ("Should I use PureBrain or Mentimeter?",
             "These solve different problems. Use Mentimeter for live audience polling and engagement. Use PureBrain as the AI brain behind your business — including, often, behind the content you put into Mentimeter."),
        ],
    ),
    "openclaw": (
        "OpenClaw",
        [
            ("How is PureBrain different from OpenClaw?",
             "OpenClaw is a developer's dream — self-hosted, open source, messaging-native. PureBrain is the professional's choice — zero setup, persistent memory, business-ready out of the box."),
            ("Should I use PureBrain or OpenClaw?",
             "Use OpenClaw if you're a developer who wants full control over a self-hosted agent stack. Use PureBrain if you're a founder or operator who wants a working AI partner without devops overhead."),
            ("Is PureBrain open source like OpenClaw?",
             "PureBrain is a managed product. OpenClaw is open source you self-host. Different business models, different audiences."),
        ],
    ),
    "perplexity": (
        "Perplexity",
        [
            ("How is PureBrain different from Perplexity?",
             "Perplexity is an AI search engine. PureBrain is a persistent AI partner that knows you and your business. Perplexity finds answers on the public web; PureBrain remembers everything about your private business."),
            ("Should I use PureBrain or Perplexity?",
             "They complement each other. Use Perplexity for fast, sourced web research. Use PureBrain as your ongoing AI partner. Many PureBrain users keep Perplexity for quick lookups."),
            ("Can PureBrain search the web like Perplexity?",
             "Yes — PureBrain can perform web research. But its core value is the persistent memory of your business that turns generic web answers into personalized recommendations."),
        ],
    ),
    "personal-ai": (
        "Personal.ai",
        [
            ("How is PureBrain different from Personal.ai?",
             "Personal.ai has impressive memory architecture. But memory without action is a library. PureBrain gives you persistent memory PLUS 23+ specialized AI departments that act on what they know."),
            ("Should I use PureBrain or Personal.ai?",
             "Use Personal.ai if your priority is a personal memory layer. Use PureBrain if you want memory plus a full AI executive team that turns memory into outcomes."),
            ("Does PureBrain have memory as deep as Personal.ai?",
             "PureBrain's memory is built for business — decisions, documents, conversations, and context across 23 departments. Personal.ai is more focused on personal/individual memory. Different orientations."),
        ],
    ),
    "productsup": (
        "Productsup",
        [
            ("How is PureBrain different from Productsup?",
             "Productsup handles your product data at enterprise scale — feeds, syndication, marketplaces. PureBrain handles YOU — the knowledge worker making decisions that product data is meant to support. Two entirely different categories."),
            ("Should I use PureBrain or Productsup?",
             "If your problem is product data orchestration across thousands of SKUs and channels, you need Productsup. If your problem is needing an AI partner that remembers your business and helps you decide, you need PureBrain."),
        ],
    ),
    "sintra": (
        "Sintra",
        [
            ("How is PureBrain different from Sintra?",
             "Sintra gives you AI employees you assign tasks to. PureBrain gives you an AI partner that actually knows your business and acts on its own initiative across 23 specialized departments."),
            ("Should I use PureBrain or Sintra?",
             "Use Sintra if you want a marketplace of single-purpose AI employees. Use PureBrain if you want a unified AI executive team with shared memory of your business."),
        ],
    ),
    "sitegpt": (
        "SiteGPT",
        [
            ("How is PureBrain different from SiteGPT?",
             "SiteGPT is a $39/mo AI support chatbot for your website. PureBrain is a $149/mo AI executive team with 23 departments running your business. Different products solving different problems."),
            ("Should I use PureBrain or SiteGPT?",
             "Use SiteGPT if your need is a public-facing site chatbot answering visitor questions. Use PureBrain if your need is an AI partner that runs operations, marketing, strategy, and analysis across your business."),
            ("Can PureBrain replace SiteGPT?",
             "Not really — they solve different problems. Many customers run SiteGPT on their public site for visitor chat AND PureBrain internally as their AI executive team."),
        ],
    ),
    "xcloud": (
        "xCloud",
        [
            ("How is PureBrain different from xCloud?",
             "xCloud hosts your WordPress site. PureBrain remembers your business. One is managed hosting with AI features bolted on; the other is a true AI partner with persistent memory across 23 departments."),
            ("Should I use PureBrain or xCloud?",
             "These solve different problems. Use xCloud for WordPress hosting. Use PureBrain as your AI partner. Most customers use both — xCloud for the site, PureBrain for the brain."),
        ],
    ),
}


def build_faq_jsonld(slug: str, competitor: str, faqs: list) -> str:
    page_url = f"https://purebrain.ai/purebrain-vs-{slug}/"
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "url": page_url,
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    payload = json.dumps(schema, indent=2, ensure_ascii=False)
    return (
        "\n<!-- AIO: FAQPage JSON-LD added 2026-05-03 (nightly site improvement) -->\n"
        '<script type="application/ld+json">\n'
        f"{payload}\n"
        "</script>\n"
    )


def patch_file(path: Path, slug: str, competitor: str, faqs: list) -> bool:
    html = path.read_text(encoding="utf-8")
    if "FAQPage" in html:
        return False
    block = build_faq_jsonld(slug, competitor, faqs)
    new_html, n = re.subn(r"</head>", block + "</head>", html, count=1)
    if n == 0:
        print(f"  ! no </head> tag found in {path}", file=sys.stderr)
        return False
    path.write_text(new_html, encoding="utf-8")
    return True


def main():
    patched = []
    skipped = []
    for slug, (competitor, faqs) in FAQ_DATA.items():
        path = DEPLOY_DIR / f"purebrain-vs-{slug}" / "index.html"
        if not path.exists():
            print(f"  ? missing: {path}")
            continue
        if patch_file(path, slug, competitor, faqs):
            patched.append(slug)
            print(f"  + FAQ added: purebrain-vs-{slug} ({len(faqs)} FAQs)")
        else:
            skipped.append(slug)
            print(f"  = skipped (FAQ already present): purebrain-vs-{slug}")
    print()
    print(f"Patched: {len(patched)}  Skipped: {len(skipped)}")
    print(f"Total FAQs added: {sum(len(FAQ_DATA[s][1]) for s in patched)}")


if __name__ == "__main__":
    main()
