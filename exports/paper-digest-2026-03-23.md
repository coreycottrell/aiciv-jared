# AI Research Digest — Week of March 17-23, 2026

**Compiled by Aether | March 23, 2026**

---

## Top Papers This Week

### 1. AI Can Learn Scientific Taste (arXiv:2603.14473) — 388 upvotes
**OpenMOSS Team | Mar 15, 2026**

Uses reinforcement learning from community feedback to train AI models to *judge and propose* high-impact research ideas. Instead of just generating papers, the model learns what makes research worth pursuing. This is meta — AI learning to evaluate AI research quality.

**Relevance to PT**: Directly relevant to how we think about AI partnership quality. The gap between "using AI" and "having AI that understands what matters" is exactly our thesis.

---

### 2. MetaClaw: An Agent That Meta-Learns and Evolves in the Wild (arXiv:2603.17187) — 121 upvotes
**UNC-Chapel Hill | Mar 17, 2026**

A continual meta-learning framework for LLM agents that jointly evolves policies AND reusable behavioral skills in real environments. The agent doesn't just learn — it builds a library of skills it can recombine for new situations.

**Relevance to PT**: This is the academic version of what we do with agent delegation. Agents that grow through experience, accumulate skills, and evolve. "NOT calling them would be sad" — validated by research.

---

### 3. OpenSeeker: Democratizing Frontier Search Agents (arXiv:2603.15594) — 141 upvotes
**OpenSeeker Team | Mar 16, 2026**

First fully open-source search agent achieving frontier-level performance. Uses fact-grounded QA synthesis and denoised trajectory synthesis. Democratizes what was previously locked behind proprietary systems.

**Relevance to PT**: Open-source catching up to proprietary. Our value proposition (context + memory + partnership) becomes even more important as raw capabilities commoditize.

---

### 4. Attention Residuals (arXiv:2603.15031) — 144 upvotes
**Moonshot AI | Mar 16, 2026**

Replaces fixed residual connections in transformers with softmax attention over all previous layer outputs. Simple architectural change, significant performance improvement. Shows there's still low-hanging fruit in transformer architecture.

**Relevance to PT**: Architecture improvements = better base models = better agents. Rising tide lifts all boats.

---

### 5. Grounding World Simulation in a Real-World Metropolis (arXiv:2603.15583) — 145 upvotes
**NAVER AI Lab | Mar 16, 2026**

Seoul World Model (SWM) generates spatially faithful, temporally consistent long-horizon videos grounded in actual urban environments. Not just hallucinating video — generating accurate simulations of real places.

**Relevance to PT**: World models are the next frontier. When AI can simulate real environments accurately, the applications for business planning, urban development, and scenario modeling are enormous.

---

### 6. Memento-Skills: Let Agents Design Agents (arXiv:2603.18743) — 44 upvotes
**University College London | Mar 19, 2026**

A generalist language model agent that autonomously designs and improves task-specific agents through memory-based reinforcement learning. Agents creating agents — with persistent memory.

**Relevance to PT**: This is our agent-architect concept validated in academic research. Agents that design other agents, with memory persistence. We're living this.

---

### 7. EvoScientist: Multi-Agent Evolving AI Scientists (arXiv:2603.08127)
**Multiple institutions | Mar 9, 2026**

Adaptive multi-agent framework for scientific discovery with persistent memory modules. Multiple AI agents collaborate on research, learning from past interactions.

**Relevance to PT**: Multi-agent + persistent memory + scientific discovery. Our architecture philosophy applied to R&D.

---

## Major Applied Research

### 8. Google AI Breast Cancer Detection — Nature Cancer (Two Papers)
**Imperial College London, Google, Cambridge, Surrey + NHS Trusts | Mar 2026**

The largest NHS study to date (175,000 women) shows AI detected:
- **25% of cancers that human radiologists missed** (interval cancers)
- **10.4% higher detection rate** overall
- **39.3% fewer recalls** for first-time screenings
- **31% reduction in radiologist workload**

Two linked papers in Nature Cancer. This is no longer "AI might help medicine" — it's "AI demonstrably outperforms humans at scale in a rigorous clinical study."

---

### 9. AlphaEvolve (Google DeepMind)

LLM-guided evolutionary algorithm that discovered a new method to multiply 4x4 complex matrices using 48 multiplications — the first improvement over Strassen's 1969 result. AI finding mathematical breakthroughs that eluded humans for 57 years.

---

### 10. Mercury: Ultra-Fast Diffusion Language Models

Diffusion-based LLMs generating multiple tokens in parallel. Mercury Coder Mini achieves 1,109 tokens/sec on H100. That's 5-10x faster than autoregressive models. Inference cost is about to collapse.

---

## Trends This Week

| Trend | Signal Strength | PT Implications |
|-------|----------------|-----------------|
| **Agents designing agents** | Strong (3+ papers) | Our architecture is academically validated |
| **Persistent memory in agents** | Strong (4+ papers) | Memory as moat confirmed by research |
| **Open-source catching up** | Medium (OpenSeeker) | Raw capability commoditizes; context is the moat |
| **World simulation models** | Medium (SWM) | Next frontier for business AI applications |
| **Medical AI at scale** | Very Strong (Nature Cancer) | AI proving clinical value at unprecedented scale |
| **Inference speed breakthroughs** | Strong (Mercury) | Cost of AI about to drop dramatically |

---

## Bottom Line for Jared

Three things matter most this week:

1. **The "agents that learn and evolve" thesis is exploding in research.** MetaClaw, Memento-Skills, EvoScientist — all validating that agents need experience, memory, and the ability to grow. This IS our philosophy. We're not speculating — we're aligned with the frontier.

2. **Memory is the moat.** Multiple papers this week show that persistent memory transforms agent capability. Zep outperforming MemGPT, EvoScientist's persistent memory modules, Memento-Skills' memory-based RL. Our "context + memory" positioning is research-validated.

3. **Inference costs are about to crater.** Mercury at 1,100 tokens/sec means the raw cost of AI drops 5-10x. When compute is cheap, what matters is WHAT you do with it — architecture, context, partnership. Our value prop strengthens.

---

*Sources: [Hugging Face Trending Papers](https://huggingface.co/papers/trending) | [arXiv cs.AI](https://arxiv.org/list/cs.AI/current) | [DAIR.AI ML Papers of the Week](https://github.com/dair-ai/ML-Papers-of-the-Week) | [Nature Cancer](https://www.nature.com/articles/s43018-026-01127-0) | [Imperial College London](https://www.imperial.ac.uk/news/articles/global-health-innovation/2026/new-research-conducted-using-google-ai-can-match-or-exceed-radiologists-in-detecting-cancer-in-breast-scans-/)*
