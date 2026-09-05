# Continuation Review Evidence

## Scope

This record covers the continuation check for task 2.11.2. It is kept outside
`design.md`; it records implementation and validation evidence without
changing the experiment contract.

## Current verification

| Check | Command or source | Result | Boundary |
|---|---|---|---|
| AIOTF source check | `cc -std=c11 -Wall -Wextra -Werror -Iopenair3/AIOTF openair3/AIOTF/aiotf_inventory.c openair3/AIOTF/tests/test_aiotf_inventory.c -o /tmp/aiotf_inventory_current_20260906 && /tmp/aiotf_inventory_current_20260906`; `test_log/compiler_logs/aiot_topology2_aiotf_source_check_2026-09-06_review_final.log` | `AIOTF_INVENTORY_TEST PASS`; 60 unique slots; 30/30 primary split | AIOTF source-level state only |
| PF/PO parameter owner | `openair2/RRC/NR/MESSAGES/asn1_msg.c:1551-1627`; public declarations in `openair2/RRC/NR/MESSAGES/asn1_msg.h:185-226` | PCCH cycle, configured PF divisor/offset, Ns, and paging-search-space validation are exposed through the existing NR RRC message owner | PF/PO identity only; exact PDCCH monitoring occasion is not calculated |
| PF/PO identity owner | `openair2/RRC/NR/MESSAGES/asn1_msg.c:1629-1657`; TS 38.304 clause 7.1 | `nr_rrc_get_paging_occasion()` evaluates the configured PF equation, derives `i_s`, and returns occasion/not-occasion/error | SFN input is a focused timing seam; no NR MAC event is emitted |
| Existing RRC caller | `openair2/RRC/NR/rrc_gNB.c:3445-3476` | `rrc_gNB_generate_pcch_msg()` reuses the shared PCCH parameter owner before encoding the existing PCCH message | NGAP trigger remains commented and PCCH delivery remains incomplete |
| Paging/timer focused check | `test_log/compiler_logs/aiot_topology2_paging_test_run_2026-09-06_enum_fix.log`; `test_asn1_msg` | 9/9 tests passed; PF previous/current/next boundaries and SFN 1024 error passed; configured `quarterT=2` passed; `paging_frame * 10 ms - 100 ms` starts AIOTF session and expiry passes at deadline equality only | source-level PF/PO plus AIOTF deadline coincidence; not over-the-air paging |
| AIOTF expiry owner | `openair3/AIOTF/aiotf_inventory.c:439-445` | `aiotf_inventory_expire()` remains pending before deadline, expires at equality, and remains terminal afterwards | no paging input or shared runtime clock |
| Affected gNB/UE build | `CCACHE_DISABLE=1 ASAN_OPTIONS=detect_leaks=0 cmake --build cmake_targets/ran_build/build_aiot_tdd --target nr-softmodem nr-uesoftmodem`; `test_log/build_logs/aiot_topology2_paging_owner_enum_fix_build_2026-09-06.log` | `49/49`; both `nr-uesoftmodem` and `nr-softmodem` linked successfully after the paging-status enum fix | checkout-local build; sanitizer leak detection disabled because `check_vcd` cannot run under this environment's ptrace restriction |
| Change artifacts | `openspec validate add-aiot-topology2-reader-experiment --strict` | PASS after the continuation edits | artifact validation only |

## Decision

Task 2.11.2 is complete because the existing NR RRC message owner now exposes
the configured PF/PO identity calculation and the focused test ties a derived
paging-frame boundary to the existing AIOTF timeout owner. The test does not
claim an NR MAC PCCH/PDCCH scheduling event or an over-the-air paging
transmission.

## Remaining limitation

The NGAP paging call remains commented and no NR MAC paging producer/consumer
was found in the current `openair2/LAYER2/NR_MAC_gNB` scheduler path. Exact
PDCCH monitoring occasions and runtime PCCH delivery therefore remain
`[Needs Verification]` and require a separately scoped NR MAC paging change.

## Review gate

The final review used `HEAD=096b758a1d62e5c304867b4ad15d4200731f8f53` as the
repository baseline and reviewed only the five scoped source/test files with
`git diff HEAD`. The Standards axis returned `PASS` with no findings. The Spec
axis returned `PASS` with no findings. Other dirty worktree changes were not
included.
