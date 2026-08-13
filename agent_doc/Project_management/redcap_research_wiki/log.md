# RedCap Research Wiki Log

All entries are append-only and use `## [YYYY-MM-DD] operation | subject`.

## [2026-07-30] ingest | LLM wiki pattern, research survival guide, and active RedCap routes

- Registered the Karpathy LLM Wiki pattern, research-method PDF, and active RedCap routes.
- Added the wiki governance, agent goals, concept, system, and decision baseline.
- Synthesis pages remain `review-required`.
- Did not modify raw sources, historical reports, source code, configurations, or runtime evidence.

## [2026-07-31] capture | O-RAN G4 report-index drift

- status: `NEEDS_REVIEW`
- capture result: `case-draft`
- changed_or_proposed_paths: `agent_doc/Project_management/redcap_research_wiki/cases/CASE-2026-001-oran-g4-report-index-drift.md`
- evidence_paths: project-local report index, project plan, and G4 Gate report listed in the case metadata.
- claim_boundary: documentation alignment only; no new runtime, SDK-completeness, UE1-resolution, or standards-conformance claim.
- unresolved_items: human confirmation and any separately approved documentation synchronization.
- next_action: review `CASE-2026-001`; keep it `review-required` until human approval.

## [2026-07-31] capture | bounded A-IoT architecture source pack

- status: `NEEDS_REVIEW`
- capture result: `update-page`
- changed_or_proposed_paths: propose only `agent_doc/Project_management/redcap_research_wiki/systems/aiot-tag-aiotf.md`; no system page was created.
- evidence_paths: `redcap_doc/manuals/aiot_tag_aiotf_architecture.en.md`.
- claim_boundary: implemented experimental Tag/UE Reader/AIOTF and bounded NRF/Naiotf surfaces only; no AMF/RAN round trip, complete SBI, 3GPP conformance, or physical-RF claim.
- unresolved_items: `Namf_AIoT`, topology-2 NGAP/RRC, and `Nnef_AIoT_*` owners remain missing or `[Needs Verification]`.
- next_action: stop at the page proposal; require human review and a separately bounded ingest before creating the system page.

## [2026-07-31] review | English migration and pilot handoff

- status: `NEEDS_REVIEW`
- changed_or_proposed_paths: `openspec/changes/evolve-redcap-research-wiki-english-cases/review/review_packet.md`.
- evidence_paths: wiki pages, registered validator, O-RAN G4 project records, and bounded A-IoT architecture source listed in the review packet.
- claim_boundary: mechanical validation and review handoff only; no semantic confirmation, documentation synchronization, or L4 execution.
- unresolved_items: human review, any page-status promotion, any documentation-sync route, and separately approved system-map work.
- next_action: review the packet and keep synthesis `review-required` until explicit approval.

## [2026-07-31] review | system-map input approval

- status: `PASS`
- changed_or_proposed_paths: approve the English-first wiki migration and `CASE-2026-001` as inputs to `structure-redcap-system-knowledge-maps`.
- evidence_paths: `openspec/changes/evolve-redcap-research-wiki-english-cases/review/review_packet.md`.
- claim_boundary: system-map input only; no page-status promotion, documentation synchronization, or L4 source/runtime work.
- unresolved_items: component-level source ownership and evidence boundaries remain subject to the system-map inventory.
- next_action: begin the bounded system-map inventory and keep new synthesis `review-required`.

## [2026-07-31] ingest | hierarchical RedCap A-IoT and xApp dApp system maps

- status: `NEEDS_REVIEW`
- changed_or_proposed_paths: add `systems/redcap/`, `systems/aiot/`, and `systems/xapp-dapp/`; move the flat RedCap and O-RAN SDK synthesis into domain overviews.
- evidence_paths: active project plans/rules, RedCap L1-L3 function lookup, A-IoT architecture/function trace, SDK guide, source owners, and retained reports listed by each page.
- claim_boundary: navigation and source-backed synthesis only; no status promotion, documentation synchronization, source modification, runtime execution, standards-conformance claim, or physical-power claim.
- unresolved_items: exact clause mappings, missing A-IoT AMF/RAN/NEF owners, dormant SDK callers, parameter-generic rollback, and unmeasured outcomes remain `[Needs Verification]`.
- supersession: the earlier proposed flat `systems/aiot-tag-aiotf.md` is replaced by `systems/aiot/overview.md`; the historical capture entry is unchanged.
- next_action: run recursive validation and submit the maps for human review.

## [2026-08-01] review | Obsidian system-map validation

- status: `PASS`
- changed_or_proposed_paths: `openspec/changes/structure-redcap-system-knowledge-maps/review/obsidian-review.md`.
- evidence_paths: human confirmation of index navigation, domain links, three Mermaid flows, and domain-overview backlinks.
- claim_boundary: Obsidian UI and navigation only; no semantic confirmation, page-status promotion, documentation synchronization, or L4 source/runtime work.
- unresolved_items: technical items already marked `[Needs Verification]` remain unchanged.
- next_action: issue the bounded final review packet.

## [2026-08-01] review | system-map final handoff

- status: `NEEDS_REVIEW`
- changed_or_proposed_paths: `openspec/changes/structure-redcap-system-knowledge-maps/review/review_packet.md`.
- evidence_paths: system-map inventory, registered validator results, OpenSpec strict validation, and Obsidian review record.
- claim_boundary: review handoff only; all system-map synthesis remains `review-required`, with no documentation synchronization or L4 work.
- unresolved_items: exact clause mappings, missing A-IoT AMF/RAN/NEF owners, dormant SDK callers, generic rollback, and outcome gaps remain `[Needs Verification]`.
- next_action: archive the completed OpenSpec change only after an explicit request; do not synchronize stable documentation.

## [2026-08-13] decide | TDD observable-behavior boundary

- status: `NEEDS_REVIEW`
- capture result: `decision-contract`
- changed_or_proposed_paths: `agent_doc/Project_management/redcap_research_wiki/decisions/tdd-observable-behavior-context-2026-08-13.md`; the TDD skill and OpenSpec change remain unchanged pending the interview.
- evidence_paths: selected `grill-with-docs` skill, its Context Gate references, the current TDD skill, and the human's stated preference.
- claim_boundary: proposed TDD governance only; no claim that existing tests, CI, or GitHub publication are correct.
- unresolved_items: decide whether ambiguity stops test authoring immediately or permits a provisional test outline before grilling.
- next_action: continue one-question-at-a-time grilling, then obtain human scope confirmation before changing the skill or proposal.

## [2026-08-13] decide | TDD boundary gate confirmed

- status: `PASS`
- capture result: `decision-contract`
- changed_or_proposed_paths: `decisions/tdd-observable-behavior-context-2026-08-13.md`, `.agents/skills/tdd/SKILL.md`, and `openspec/changes/govern-skill-pipeline-contract/`.
- evidence_paths: human scope confirmation and the recorded Context Gate decision.
- claim_boundary: TDD governance only; no claim about current runtime, GitHub publication, or test adequacy.
- unresolved_items: none for this rule.
- next_action: apply the boundary gate to the next code-change TDD contract.

## [2026-08-13] decide | unified pipeline parent task confirmed

- status: `PASS`
- capture result: `decision-contract`
- changed_or_proposed_paths: `openspec/changes/govern-skill-pipeline-contract/proposal.md` and `openspec/changes/implement-github-issue-mirror-publisher/proposal.md`.
- evidence_paths: both proposals and the human's parent-task decision.
- claim_boundary: approval hierarchy only; no approved tag, GitHub Action, or Issue exists yet.
- unresolved_items: complete unified approval scope and create each approved annotated tag.
- next_action: present the unified approval request.

## [2026-08-13] decide | publisher bootstrap exception accepted

- status: `PASS`
- capture result: `decision-contract`
- changed_or_proposed_paths: the unified pipeline parent proposal and publisher child proposal/spec/design.
- evidence_paths: human acceptance of the bootstrap sequence and both OpenSpec proposals.
- claim_boundary: bootstrap governance only; no GitHub Action, Issue mirror, or live publication exists.
- unresolved_items: unified scope confirmation and the two approved annotated tags.
- next_action: present the unified approval request.

## [2026-08-13] decide | unified pipeline scope approved

- status: `PASS`
- capture result: `decision-contract`
- changed_or_proposed_paths: both pipeline proposal entry pages and `decisions/pipeline-unified-approval-context-2026-08-13.md`.
- evidence_paths: explicit human approval of the unified parent scope.
- claim_boundary: approved scope only; no immutable tag, GitHub Action, Issue mirror, or live publication exists yet.
- unresolved_items: commit the approved revisions when authorized, then create two independent annotated tags.
- next_action: prepare the publisher TDD only after the child revision is committed and tagged.
