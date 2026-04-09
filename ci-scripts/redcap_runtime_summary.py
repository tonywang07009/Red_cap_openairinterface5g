#!/usr/bin/env python3

import argparse
import html
import re
from pathlib import Path


TARGET_TESTS = {
    "333331": "[Attach UE1]",
    "302001": "[Verify UE1 non-RedCap]",
    "333332": "[Attach UE2 RedCap]",
    "302002": "[Verify UE2 RedCap]",
    "302003": "[Verify SIB1 RedCap initial DL BWP]",
    "020005": "[Ping both UEs]",
    "030001": "[Iperf DL 60 Mbps UDP on UE2]",
    "030002": "[Iperf UL 20 Mbps UDP on UE2]",
}

GNB_MARKERS = {
    "[SIB1 RedCap initial DL BWP]": re.compile(r"SIB1 RedCap initial DL BWP"),
    "[UE marked as RedCap]": re.compile(r"UE with RNTI [0-9a-fA-F]{4} is RedCap"),
}


def strip_tags(value: str) -> str:
    text = value.replace("</pre>", "\n").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\r", "")
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line.strip()).strip()


def parse_html_rows(html_path: Path) -> dict[str, dict[str, str]]:
    if not html_path.exists():
        return {}

    content = html_path.read_text(encoding="utf-8", errors="ignore")
    row_pattern = re.compile(
        r"<tr>\s*"
        r"<td bgcolor = \"lightcyan\" >(?P<time>.*?)</td>\s*"
        r"<td bgcolor = \"lightcyan\" >(?P<test_id>\d+)</td>\s*"
        r"<td>(?P<desc>.*?)</td>\s*"
        r"<td>(?P<options>.*?)</td>\s*"
        r"<td[^>]*>(?P<status>.*?)</td>\s*"
        r"<td[^>]*>(?P<info>.*?)</td>\s*"
        r"</tr>",
        re.S,
    )

    rows = {}
    for match in row_pattern.finditer(content):
        test_id = match.group("test_id").strip()
        rows[test_id] = {
            "time": strip_tags(match.group("time")),
            "desc": strip_tags(match.group("desc")),
            "options": strip_tags(match.group("options")),
            "status": strip_tags(match.group("status")),
            "info": strip_tags(match.group("info")),
        }
    return rows


def find_artifacts(artifacts_dir: Path, test_id: str) -> list[Path]:
    if not artifacts_dir.exists():
        return []
    return sorted(artifacts_dir.glob(f"*-{test_id}-*"))


def find_service_log(artifacts_dir: Path, service_name: str) -> Path | None:
    matches = sorted(artifacts_dir.glob(f"*-{service_name}.logs"))
    return matches[-1] if matches else None


def grep_excerpt(path: Path, pattern: re.Pattern[str], limit: int = 3) -> list[str]:
    if not path or not path.exists():
        return []

    matches = []
    with path.open(encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if pattern.search(line):
                matches.append(line.strip())
                if len(matches) >= limit:
                    break
    return matches


def summarize_gnb_log(artifacts_dir: Path) -> list[str]:
    gnb_log = find_service_log(artifacts_dir, "oai-gnb.logs")
    if gnb_log is None:
        return [
            "- [gNB log]：未找到 `*-oai-gnb.logs`，無法交叉驗證 [302002] / [302003]。",
        ]

    lines = [f"- [gNB log]：`{gnb_log}`"]
    for title, pattern in GNB_MARKERS.items():
        excerpts = grep_excerpt(gnb_log, pattern)
        if excerpts:
            lines.append(f"- {title}：找到 {len(excerpts)} 筆範例")
            for excerpt in excerpts:
                lines.append(f"  {excerpt}")
        else:
            lines.append(f"- {title}：未在 gNB log 中找到")
    return lines


def summarize_test_rows(rows: dict[str, dict[str, str]], artifacts_dir: Path) -> list[str]:
    lines = []
    for test_id, label in TARGET_TESTS.items():
        row = rows.get(test_id)
        artifacts = find_artifacts(artifacts_dir, test_id)
        artifact_text = ", ".join(str(path.name) for path in artifacts) if artifacts else "[none]"
        if row is None:
            lines.append(f"- {label} `{test_id}`：⚠ [missing in test_results.html]；artifacts={artifact_text}")
            continue

        status = row["status"] or "[unknown]"
        desc = row["desc"] or "[no desc]"
        lines.append(f"- {label} `{test_id}`：[{status}] {desc}")
        if row["info"]:
            info_lines = row["info"].splitlines()
            for info_line in info_lines[:6]:
                lines.append(f"  {info_line}")
        lines.append(f"  [Artifacts]：{artifact_text}")
    return lines


def build_report(args: argparse.Namespace) -> str:
    rows = parse_html_rows(args.html)

    report = []
    report.append("# RedCap Runtime Validation Summary")
    report.append("")
    report.append("## Scope")
    report.append(f"- [Scenario]：`{args.scenario}`")
    report.append(f"- [HTML Report]：`{args.html}`")
    report.append(f"- [Artifacts Dir]：`{args.artifacts}`")
    if args.run_log:
        report.append(f"- [Run Log]：`{args.run_log}`")
    report.append("")
    report.append("## Task Mapping")
    report.append("- [Task Name]：[RedCap RFsim end-to-end validation]")
    report.append("- [3GPP Spec Clause]：[TS 38.306 Clause 4.2.21.1] / [TS 38.331 Clause 5.2.2.4.2] / [TS 38.331 Clause 5.6.1.3]")
    report.append("- [Prerequisite Tasks]：[Milestone 2 SIB1 support] / [Milestone 3 BWP & CORESET#0] / [build recovery]")
    report.append("")
    report.append("## Test Case Summary")
    report.extend(summarize_test_rows(rows, args.artifacts))
    report.append("")
    report.append("## gNB Log Cross-Check")
    report.extend(summarize_gnb_log(args.artifacts))
    report.append("")
    report.append("## Exit Criteria")
    report.append("- [302003] 應為 [OK]，且 [gNB log] 內應出現 `SIB1 RedCap initial DL BWP`。")
    report.append("- [302002] 應為 [OK]，且 [gNB log] 內應出現 `UE with RNTI .... is RedCap`。")
    report.append("- [030001] / [030002] 應為 [OK]，並可在對應 `iperf_client_rfsim5g_ue2.log` 中看到 [Receiver Bitrate] 與 [Packet Loss]。")
    report.append("- [020005] 應為 [OK]，並可在 `ping_rfsim5g_ue*.log` 中看到 [0% 或可接受門檻內] 的 [packet loss]。")
    report.append("")
    report.append("## Notes")
    report.append("- [⚠ Needs Verification]：若 `test_results.html` 或 artifacts 缺失，通常代表 scenario 尚未完整跑完，或在 deploy 前即失敗。")
    report.append("- 若要補完整學習報告，可直接引用這份摘要，再加上 [Technical Background] 與 [Practice Exercises]。")
    report.append("")
    return "\n".join(report)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Summarize RedCap RFsim runtime results from CI artifacts.")
    parser.add_argument("--scenario", default="container_5g_flexric_rfsim_redcap.xml")
    parser.add_argument("--html", type=Path, default=repo_root / "ci-scripts" / "test_results.html")
    parser.add_argument("--artifacts", type=Path, default=None)
    parser.add_argument("--run-log", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.artifacts is None:
        args.artifacts = repo_root / "cmake_targets" / "log" / f"{args.scenario}.d"

    report = build_report(args)
    print(report)

    if args.output is not None:
        args.output.write_text(report + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
