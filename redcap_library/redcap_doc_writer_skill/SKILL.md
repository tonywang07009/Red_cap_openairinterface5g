---
name: redcap-doc-writer
description: Use when updating RedCap/OAI documentation for this repo, especially API/config behavior, Bash operator usage, step-by-step recap commands, bilingual Doc pages, Project_management plans, or redcap_interface documentation.
---

# RedCap Doc Writer

## Workflow

1. Load the smallest context pack:
   - target project `project_plan.md` and `agent_rules.md` when project-scoped,
   - target folder `Doc/README.en.md`,
   - target folder `Doc/README.zh-TW.md`,
   - target script or config only when needed.
2. Classify the update:
   - API/config behavior,
   - Bash usage,
   - step-by-step recap,
   - validation/report summary.
3. Update English and Traditional Chinese pages together.
4. Keep the writing KISS:
   - short bullets,
   - runnable commands,
   - expected markers,
   - links to source files instead of copied logs.
5. Use current entrypoints:
   - daily RFsim: `redcap_interface/mmtc.menu.bash`,
   - paper/demo: `redcap_interface/mmtc.display.bash`,
   - implementation helpers: `redcap_interface/bash_library/fc_*`.
6. Preserve historical evidence:
   - do not rewrite old report commands unless the report is being actively corrected,
   - explain legacy root scripts as compatibility shims.
7. Handle standards carefully:
   - cite exact local notes or exact 3GPP clause numbers only after verification,
   - write `[Needs Verification]` when the clause mapping is uncertain.

## Validation

Run only checks relevant to touched files:

```bash
bash redcap_interface/validate_redcap_interface.sh
git diff --check -- redcap_interface redcap_doc redcap_library agent_doc/Project_management
```

For script edits:

```bash
bash -n redcap_interface/mmtc.menu.bash
bash -n redcap_interface/mmtc.display.bash
python3 -c 'import ast,pathlib,sys; [ast.parse(pathlib.Path(p).read_text(), filename=p) for p in sys.argv[1:]]' redcap_interface/iperf_live_panel.py redcap_interface/bash_library/fc_iperf_live_panel.py
```
