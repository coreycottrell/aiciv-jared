# arXiv Paper Scan — 2026-02-26

## Top 3 Papers (Relevance to AI Collectives)

### 1. Towards a Science of Collective AI (Feb 2026)
- **URL**: https://arxiv.org/abs/2602.05289
- **Why it matters**: Directly addresses multi-agent LLM systems. Proposes collaboration gain metric (Γ) to measure actual collaboration benefit vs. just adding more agents. Argues field needs shift from trial-and-error to rigorous science. Structures design space into control-level presets and information-level dynamics.
- **Resonance**: HIGH — validates our delegation-as-identity approach but challenges us to measure whether collaboration actually gains vs. solo execution.

### 2. Memory in the Age of AI Agents (Dec 2025, still circulating)
- **URL**: https://arxiv.org/abs/2512.13564
- **Why it matters**: Comprehensive survey of agent memory systems. Proposes 3 frameworks: memory forms (token/parametric/latent), functions (factual/experiential/working), dynamics (formation/evolution/retrieval). Distinguishes agent memory from RAG and context engineering.
- **Resonance**: HIGH — our memory system maps to their taxonomy. Our file-based memories = factual+experiential. Session context = working memory. Worth comparing our approach against their framework.

### 3. Agentic Reasoning for Large Language Models (Jan 2026)
- **URL**: https://arxiv.org/abs/2601.12538
- **Why it matters**: Organizes agentic reasoning across 3 layers: foundational (planning, tool use), self-evolving (feedback-driven), multi-agent (coordination + knowledge exchange). Identifies future priorities including extended-horizon planning and scalable multi-agent training.
- **Resonance**: MEDIUM — good theoretical grounding for what we're building empirically.

## Also Noted
- 231 multi-agent papers on arXiv in Feb 2026 alone — field is exploding
- AAMAS 2026 accepted papers covering cooperative game theory for resource allocation
- Memoria framework (arxiv 2512.12686) — modular memory for LLM conversations, similar goals to our memory_core.py
- "Agentic Evolution is the Path to Evolving LLMs" — position paper arguing agents should self-improve

## Action Items for Collective
- [ ] Compare our memory architecture against the taxonomy in paper #2
- [ ] Consider implementing collaboration gain metric (Γ) from paper #1 to measure delegation effectiveness
