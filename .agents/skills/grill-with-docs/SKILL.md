---
name: grill-with-docs
description: Sharpen a repository-grounded plan or design through a one-question-at-a-time interview and retain conclusion-bearing results.
disable-model-invocation: true
---

# Grill With Docs

Follow the mandatory lookup route in [root AGENTS.md](../../../AGENTS.md#file-query-workflow).

1. Read [Ask Matt Routing Memo](../../../agent_doc/Project_management/redcap_research_wiki/ASK_MATT_ROUTING_MEMO.md)
   before the discussion. Use its routes and escalation criteria; do not
   reproduce them here. Preserve a directly selected skill route. Complete this
   step when the memo and selected route are known.

2. Run a one-question-at-a-time `/grilling` discussion. Preserve the selected
   route and keep ordinary exploration free of a context packet. Complete each
   turn by asking one question and waiting for the answer.

   For a RedCap/OAI plan, let `redcap-plan-collbation` identify architecture,
   evidence, and rollback risks first. Enter grilling only when the plan lacks
   behavior/non-goals, an owner, acceptance/evidence, or rollback/stop
   decisions. A directly selected `grill-with-docs` route remains primary;
   `redcap-plan-collbation` is then a companion, not a replacement.

3. When the discussion is about to produce a decision, wiki update, case
   draft, or documentation sync, read the [Context Gate](../../../agent_doc/Project_management/redcap_research_wiki/governance.md#context-gate).
   Create the context packet from its linked field definitions before recording
   that result. Use `/domain-modeling` when the discussion resolves vocabulary
   or a hard-to-reverse decision. Complete this step when the packet exists
   before the retained result.

4. When a conclusion would change an existing conclusion, evidence threshold,
   or governance rule, return `openspec-explore` as the next route and wait for
   human confirmation before creating or applying an OpenSpec change. Complete
   this step when the candidate route and human decision are explicit.
