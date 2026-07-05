# RedCap Newcomer Runtime Gate

[English](./redcap_newcomer_runtime_gate.en.md) | [繁體中文](./redcap_newcomer_runtime_gate.zh-TW.md)

## Goal

Use this gate to test whether a new user, or a fresh Codex window acting as a new user, can reproduce the RedCap/OAI workspace from zero setup to a 29 UE RFsim validation.

## Gate Rule

- Follow the public documents only.
- Do not use internal Codex-only wrappers or private notes.
- Stop at the first unclear or failing step and record the evidence.
- If a host dependency is missing, report it as a documentation or environment blocker.

## 1. Static Documentation Gate

Run from the repository root:

```bash
bash redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh
```

Expected result:

- English and Traditional Chinese install files exist.
- Public Markdown files do not contain Codex-only command wrappers.
- Public Markdown files do not contain obvious encoding replacement characters.
- Install and gate documents contain the required 29 UE markers.

## 2. Begin From Zero

Open and follow:

```bash
sed -n '1,240p' redcap_doc/manuals/install/redcap_begin_from_zero.en.md
```

Required checkpoints:

- Repository root is correct.
- Docker and Docker Compose work.
- Local CN5G compose file exists.
- RedCap interface validator passes.
- `nr-softmodem` builds.
- `nr-uesoftmodem` builds.
- Local RFsim images rebuild.
- gNB image inspection passes.

## 3. Run The 29 UE Stage Scan

Run the command from the beginner guide:

```bash
env MMTC_TOTAL_UES_TARGET=29 \
    MMTC_STAGE_LIST=29 \
    MMTC_REBUILD_IMAGES_BEFORE_SCAN=0 \
    MMTC_FORWARD_PING_MODE=parallel \
    MMTC_RUN_REVERSE_PING=0 \
    MMTC_IPERF_ENABLE=0 \
    MMTC_UE_START_GAP=3 \
    MMTC_GNB_WARMUP=10 \
    MMTC_SLEEP_AFTER_UP=25 \
    bash redcap_interface/redcap_mmtc_stage_scan.sh
```

## 4. Pass Criteria

The latest summary log must contain:

```text
sample=29
running=29
attach=29
pdu=29
tun=29
forward_ping_ok=29
gnb_restart=0
failures=0
```

## 5. Feedback Format

When the gate fails or the document is unclear, report:

```markdown
## Newcomer Gate Feedback

- Step:
- Command:
- Expected:
- Actual:
- Log path:
- Unclear wording:
- Suggested document fix:
```

## 6. Completion Statement

The gate is complete only when both are true:

- Static documentation gate passes.
- Runtime summary contains all pass markers.
