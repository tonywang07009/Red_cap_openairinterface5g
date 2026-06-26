#!/usr/bin/env python3
"""Audit local OAI hooks required by the BWP/SDT reproduction plan."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP_RESULT = PROJECT_ROOT / "exp_result"


@dataclass(frozen=True)
class Hook:
    area: str
    hook: str
    path: str
    needle: str
    expected_status: str
    reproduction_impact: str


HOOKS = [
    Hook(
        "BWP",
        "gNB BWP configuration",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c",
        "void configure_UE_BWP",
        "present",
        "Configures current DL/UL BWP structures used by gNB scheduling.",
    ),
    Hook(
        "BWP",
        "gNB BWP reconfiguration trigger",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c",
        "void nr_mac_trigger_reconfiguration",
        "present",
        "Candidate hook for future BWP switch-delay instrumentation.",
    ),
    Hook(
        "BWP",
        "gNB transmission interruption timer",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_primitives.c",
        "nr_timer_setup(&UE->UE_sched_ctrl.transm_interrupt",
        "present",
        "Existing timing hook that can approximate switch interruption in local validation.",
    ),
    Hook(
        "BWP",
        "UE random-access BWP operation",
        "openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c",
        "perform the BWP operation as specified in clause 5.15",
        "present",
        "UE RA path switches current BWP according to TS 38.321 clause 5.15.",
    ),
    Hook(
        "BWP",
        "UE bwp-InactivityTimer implementation",
        "openair2/LAYER2/NR_MAC_UE/nr_ra_procedures.c",
        "TODO bwp-InactivityTimer not implemented",
        "gap_present",
        "Paper timer curves cannot be claimed reproduced until this gap is instrumented or implemented.",
    ),
    Hook(
        "SDT",
        "gNB SDT log file hook",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c",
        "NR_REDCAP_SDT_LOG_PATH_DEFAULT",
        "present",
        "Provides a stable log target for SDT FSM transitions.",
    ),
    Hook(
        "SDT",
        "gNB CG-SDT classifier",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c",
        "nr_redcap_sdt_classify_cg_rx",
        "present",
        "Detects configured-grant SDT RX candidates in gNB UL processing.",
    ),
    Hook(
        "SDT",
        "gNB SDT UL grant transition",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c",
        "nr_redcap_sdt_note_ul_grant",
        "present",
        "Starts SDT FSM transition logging when scheduler grants UL bytes.",
    ),
    Hook(
        "SDT",
        "gNB SDT UL burst completion",
        "openair2/LAYER2/NR_MAC_gNB/gNB_scheduler_ulsch.c",
        "nr_redcap_sdt_maybe_complete_ul_burst",
        "present",
        "Completes SDT FSM state when UL pending bytes drain.",
    ),
    Hook(
        "SDT",
        "SDT FSM step",
        "openair2/LAYER2/NR_MAC_gNB/nr_mac_sdt_fsm.c",
        "bool nr_redcap_sdt_fsm_step",
        "present",
        "Encodes the local SDT state/path transitions used by log extraction.",
    ),
    Hook(
        "SDT",
        "UE CG-SDT config detection",
        "openair2/LAYER2/NR_MAC_UE/nr_ue_scheduler.c",
        "nr_ue_has_cg_sdt_config",
        "present",
        "UE-side CG-SDT configuration gate for future runtime verification.",
    ),
]


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "openair2").is_dir() and (parent / "ci-scripts").is_dir():
            return parent
    raise SystemExit("repo root not found")


def find_line(root: Path, hook: Hook) -> tuple[str, int | None, str]:
    path = root / hook.path
    if not path.exists():
        return "missing_file", None, ""

    for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if hook.needle in line:
            if hook.expected_status == "gap_present":
                return "gap_present", line_no, line.strip()
            return "present", line_no, line.strip()

    return "missing", None, ""


def write_csv(rows: list[dict[str, str]]) -> Path:
    out = EXP_RESULT / "oai_hook_inventory.csv"
    fieldnames = ["area", "hook", "status", "file", "line", "evidence", "reproduction_impact"]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return out


def write_markdown(rows: list[dict[str, str]]) -> Path:
    out = EXP_RESULT / "oai_hook_inventory.md"
    lines = [
        "# OAI Hook Inventory For BWP / SDT Reproduction",
        "",
        f"- [Generated At]: {datetime.now(timezone.utc).isoformat()}",
        "- [Source]: local OAI source tree scan",
        "- [Interpretation]: [gap_present] is an explicit implementation gap, not a missing file.",
        "",
        "| area | hook | status | file:line | reproduction_impact |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        file_line = row["file"] if not row["line"] else f"{row['file']}:{row['line']}"
        lines.append(
            f"| [{row['area']}] | {row['hook']} | [{row['status']}] | `{file_line}` | {row['reproduction_impact']} |"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    root = repo_root()
    EXP_RESULT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []

    for hook in HOOKS:
        status, line_no, evidence = find_line(root, hook)
        rows.append(
            {
                "area": hook.area,
                "hook": hook.hook,
                "status": status,
                "file": hook.path,
                "line": "" if line_no is None else str(line_no),
                "evidence": evidence,
                "reproduction_impact": hook.reproduction_impact,
            }
        )

    csv_path = write_csv(rows)
    md_path = write_markdown(rows)
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
