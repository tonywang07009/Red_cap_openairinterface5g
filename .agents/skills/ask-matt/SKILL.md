---
name: ask-matt
description: Route an unqualified OAI request or fill an omitted tool step for a selected primary skill.
---

# Ask Matt: OAI Workflow Router

Use this skill for an unqualified repository request. A selected primary skill
may invoke it only to fill an omitted necessary tool step; it remains the
workflow authority.

Read the retained criteria in [Ask Matt Routing Memo](../../../agent_doc/Project_management/redcap_research_wiki/ASK_MATT_ROUTING_MEMO.md)
before routing a repository request. That memo is the route-table authority.
Read [RedCap MCP And Command Toolbox](../../../agent_doc/Project_management/redcap_toolbox.md)
after selecting the primary skill. That document is the tool-route authority.

## Route

1. If a user named a skill, preserve that primary skill and its explicit tool
   instructions. Use the toolbox only to fill an omitted necessary tool step.
2. Otherwise read the memo's **Formal OpenSpec Gate**,
   **Research-Wiki Escalation**, **Active Skill Set**, and **Retained Skill
   Routes** sections. Select one active primary skill and, only when needed,
   one companion skill.
3. If the memo classifies the result as an OpenSpec candidate, set
   `openspec_status` to `candidate-awaiting-human`. If an approved matching
   change is named, set it to `approved-change`. If no active route matches,
   return `primary_skill: none`, `companion_skill: none`,
   `openspec_status: not-needed`, `route_reason: no-active-route`, and request
   a human decision on clarification or formal promotion.
4. Read the toolbox's **Default Tool Routing** row matching the task signal.
   Return its tool steps, stop condition, and fallback. Route only; the
   primary skill executes the work.

Complete routing only after every output field below has a value.

## Return format

Return exactly this routing packet before running any selected skill:

```text
primary_skill: <skill | none>
companion_skill: <skill | none>
route_reason: <matched condition>
openspec_status: <not-needed | candidate-awaiting-human | approved-change>
next_human_decision: <decision or none>
task_signal: <matched toolbox row>
tool_steps: <ordered tools | none>
stop_condition: <sufficient evidence or information>
fallback: <next smallest route | none>
```
