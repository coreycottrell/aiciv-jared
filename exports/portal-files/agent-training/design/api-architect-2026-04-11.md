# API Architect Training: Observation from Witness API Spec

**Date**: 2026-04-11
**Source**: /home/jared/projects/AI-CIV/aether/docs/witness-api-spec.md

## Key Design Observation: Explicit Decision Points as API Design Debt Prevention

The Witness API specification includes a clear callback pattern decision at Endpoint 6 with two documented options (polling vs callback), requiring explicit choice before implementation. This design pattern prevents silent failures where different implementations assume different handoff mechanisms—a common integration debt source.

The spec makes visible that "post-auth automation" involves a decision boundary: does Aether poll Witness for completion, or does Witness push completion back to Aether? By documenting both paths with implementation costs ("polling first for simplicity"), the spec prevents teams from diverging mid-implementation and creating incompatible assumptions.

This observation reveals that mature API design treats decision points themselves as first-class API elements worthy of documentation—not just the endpoints themselves.

## Memory Written
Path: `.claude/memory/agent-learnings/api-architect/2026-04-11--decision-points-as-api-debt-prevention.md`
Type: teaching
Topic: Explicit decision documentation prevents integration divergence
