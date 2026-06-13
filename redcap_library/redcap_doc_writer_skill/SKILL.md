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
   - beginner build/run guide,
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

## Beginner Build/Run Guide Rules

Use this workflow when writing a guide for a first-time user:

1. Define the audience and the final validation target first.
2. Start from the repository root.
3. Separate the guide into:
   - prerequisites,
   - dependency install,
   - local CMake build,
   - Docker image rebuild,
   - runtime execution,
   - expected markers,
   - short troubleshooting.
4. Keep user-facing commands as normal shell commands.
   - Do not write Codex-only wrappers such as `rtk` into stable user manuals.
   - Use `rtk` only in Codex conversation-side validation commands when local rules require it.
5. Prefer one concrete acceptance target over many branches.
   - Example: 29 UE RFsim validation with `sample=29`, `running=29`, `attach=29`, `pdu=29`, `tun=29`, `forward_ping_ok=29`, `gnb_restart=0`, `failures=0`.
6. Put logs behind paths and marker names.
   - Do not paste raw runtime logs into the stable guide.
7. When a guide has an English page and a Traditional Chinese page, update both in the same change.

## Validation

Run only checks relevant to touched files:

```bash
bash redcap_interface/validate_redcap_interface.sh
git diff --check -- redcap_interface redcap_doc redcap_library agent_doc/Project_management
```

For beginner build/run guide routing, also check:

```bash
rg -n "redcap_zero_to_build_and_run_guide|Beginner build|新手" README.md redcap_doc redcap_library agent_doc/Project_management
rg -n "shaojintian|MIT License|LinkedIn|your_github_name|your_repository" README.md redcap_doc/manuals
```

For script edits:

```bash
bash -n redcap_interface/mmtc.menu.bash
bash -n redcap_interface/mmtc.display.bash
python3 -c 'import ast,pathlib,sys; [ast.parse(pathlib.Path(p).read_text(), filename=p) for p in sys.argv[1:]]' redcap_interface/iperf_live_panel.py redcap_interface/bash_library/fc_iperf_live_panel.py
```
