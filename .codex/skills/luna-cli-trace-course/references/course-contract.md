# Course Authoring Contract

Use this only when creating or revising the learner-facing material reserved
for `redcap_library/luna_cli_trace_course/`. Do not create that dashboard until
the user approves the reviewed history ledger and chapter sequence.

## Scope and Order

Teach the fixed foundation route first: RedCap, Topology 2, AIOTF, then
xApp/dApp. Each historical lesson must have a corroborated project/OpenSpec
record, source path, and evidence owner. Keep current-source applicability
separate from the retained historical claim.

## Chapter Contract

Each Markdown chapter contains:

1. Learning objective and bounded change context.
2. One operator input, program state, or control guard explained from first
   principles: purpose, producer, consumer, source owner, and effect.
3. A path/symbol table and an explanatory Mermaid flow when the relationship is
   non-linear.
4. One read-only learner lookup at a time with expected observation and stop
   condition. Use Symdex for source ownership and call relationships, rtk for
   Git, and filesystem MCP for Markdown, PDF, config, logs, and file content;
   state the fallback reason when the primary tool cannot perform the lookup.
5. Evidence ladder, failure boundary, three understanding checks, and handoff
   card.

Diagrams must explain causal flow or ownership, never decorate. Preserve raw
evidence and make links portable Markdown for Obsidian. The research wiki and
canonical manuals remain the source routers; chapters link to them rather than
duplicating operational truth.

## Dashboard and Privacy

The future dashboard is an index for chapter sequence, current handoff, system
maps, and canonical owners. Keep personal completion state and raw learner
handoffs in an untracked local-progress file; never commit them or present them
as shared project evidence.
