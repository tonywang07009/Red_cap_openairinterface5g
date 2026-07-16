# RedCap Install Manuals

[English](./README.en.md) | [繁體中文](./README.zh-TW.md)

## Purpose

This folder contains the public install and rebuild path for the RedCap/OAI workspace.

## Manuals

| File | Use |
|---|---|
| [redcap_begin_from_zero.en.md](./redcap_begin_from_zero.en.md) | Start from a fresh local checkout and reach a 29 UE RFsim validation. |
| [redcap_rebuild_after_changes.en.md](./redcap_rebuild_after_changes.en.md) | Rebuild after C, xApp, rApp, dApp, script, config, or library changes. |
| [redcap_newcomer_runtime_gate.en.md](./redcap_newcomer_runtime_gate.en.md) | Run the newcomer gate and report where the documentation is unclear. |

## Reading Order

1. Run `./mmtc.menu.bash install`; use [Begin from zero](./redcap_begin_from_zero.en.md) for installer details or the manual fallback.
2. Use [Rebuild after changes](./redcap_rebuild_after_changes.en.md) after code or configuration edits.
3. Use [Newcomer runtime gate](./redcap_newcomer_runtime_gate.en.md) to verify that the documentation is reproducible.

The installer acceptance is a 1 UE smoke. The 29 UE newcomer gate remains a separate validation.
