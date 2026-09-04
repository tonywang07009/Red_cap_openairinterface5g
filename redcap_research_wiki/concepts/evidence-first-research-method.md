---
status: review-required
source_refs:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - agent_doc/830225959-研究生完全求生手冊-彭明輝PDF电子书.pdf
  - agent_doc/Project_management/redcap_ai_native_review_validation_workflow.md
evidence_tier: mixed
last_reviewed: 2026-07-30
related_pages:
  - redcap_research_wiki/sources/karpathy-llm-wiki-pattern.md
  - redcap_research_wiki/sources/research-survival-guide.md
  - redcap_research_wiki/decisions/simulator-decision-contract.md
---

# Evidence-First Research Method

## Compiled Method

[Paper Evidence] Begin research by locating related work, assessing source
quality, comparing evidence and reasoning, and identifying unresolved
questions before starting a new investigation.

[Paper Evidence] A literature review is not background collection. It is a
mechanism for finding relative strengths, weaknesses, conflicts, and reusable
prior knowledge.

[Inference] In this repository, the method maps to:

```text
question
  -> governing specification and paper search
  -> current source/runtime trace
  -> comparison and falsification
  -> explicit knowledge gap
  -> decision/experiment contract
  -> implementation and evidence
  -> reviewed documentation update
```

## Quality Questions

Answer these questions before accepting a conclusion:

1. What exact question is being answered?
2. Which source type can answer it?
3. Which evidence could refute the current explanation?
4. Is the source current, local, and directly applicable?
5. Which parts remain inference?
6. Which observation can falsify the conclusion?
7. Does the requested claim exceed the simulator or instrumentation boundary?

## Innovation Boundary

[Paper Evidence] Prefer integrating and improving demonstrated prior approaches
instead of beginning with unsupported novel implementation.

[Inference] Before proposing custom code, RedCap/OAI work checks existing
owning modules, installed tooling, current experiment contracts, and
standard-defined mechanisms.

[Needs Verification] A promising paper method does not imply that the current
OAI checkout can implement it or that RFsim can compare it directly.
