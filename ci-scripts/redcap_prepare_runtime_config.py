#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


MODE_TO_VALUE = {
    "case-a": 0,
    "case-b": 1,
}

MODE_TO_COMMENT = {
    "case-a": "0: Case A (type0 CSS), 1: Case B (edge-only commonControlResourceSet)",
    "case-b": "0: Case A (type0 CSS), 1: Case B (edge-only commonControlResourceSet)",
}


def render_mode_line(mode: str, indent: str) -> str:
    return f"{indent}coreset0_redcap_mode_r17: {MODE_TO_VALUE[mode]} # {MODE_TO_COMMENT[mode]}"


def rewrite_mode(input_text: str, mode: str) -> str:
    pattern = re.compile(r"^(?P<indent>\s*)coreset0_redcap_mode_r17:\s*\d+\s*(?:#.*)?$", re.MULTILINE)
    matches = list(pattern.finditer(input_text))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one coreset0_redcap_mode_r17 entry, got {len(matches)}")

    match = matches[0]
    replacement = render_mode_line(mode, match.group("indent"))
    return input_text[:match.start()] + replacement + input_text[match.end():]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Prepare a Case A / Case B RedCap gNB runtime config.")
    parser.add_argument("--mode", required=True, choices=sorted(MODE_TO_VALUE.keys()))
    parser.add_argument(
        "--input",
        type=Path,
        default=repo_root / "ci-scripts" / "conf_files" / "gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    original = args.input.read_text(encoding="utf-8")
    updated = rewrite_mode(original, args.mode)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(updated, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
