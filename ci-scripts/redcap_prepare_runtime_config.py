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

E2_AGENT_MODE_ENABLED = "enabled"
E2_AGENT_MODE_DISABLED = "disabled"
E2_AGENT_MODE_EMPTY_SM_DIR = "empty-sm-dir"
EMPTY_SM_DIR_PATH = "/opt/oai-gnb/flexric-empty/"


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


def remove_e2_agent_block(input_text: str) -> str:
    lines = input_text.splitlines(keepends=True)
    output_lines: list[str] = []
    removed = 0
    skipping = False

    for line in lines:
        if not skipping and line.startswith("e2_agent:"):
            skipping = True
            removed += 1
            continue

        if skipping:
            if line.startswith((" ", "\t")):
                continue
            skipping = False

        output_lines.append(line)

    if removed != 1:
        raise ValueError(f"expected exactly one e2_agent block, got {removed}")

    return "".join(output_lines)


def rewrite_sm_dir(input_text: str, sm_dir: str) -> str:
    pattern = re.compile(r"^(?P<indent>\s*)sm_dir:\s*\S+\s*$", re.MULTILINE)
    matches = list(pattern.finditer(input_text))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one sm_dir entry, got {len(matches)}")

    match = matches[0]
    replacement = f"{match.group('indent')}sm_dir: {sm_dir}"
    return input_text[:match.start()] + replacement + input_text[match.end():]


def rewrite_e2_agent(input_text: str, e2_agent_mode: str) -> str:
    if e2_agent_mode == E2_AGENT_MODE_ENABLED:
        return input_text
    if e2_agent_mode == E2_AGENT_MODE_DISABLED:
        return remove_e2_agent_block(input_text)
    if e2_agent_mode == E2_AGENT_MODE_EMPTY_SM_DIR:
        return rewrite_sm_dir(input_text, EMPTY_SM_DIR_PATH)

    raise ValueError(f"unsupported e2_agent_mode: {e2_agent_mode}")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Prepare a Case A / Case B RedCap gNB runtime config.")
    parser.add_argument("--mode", choices=sorted(MODE_TO_VALUE.keys()), default=None)
    parser.add_argument(
        "--e2-agent-mode",
        choices=(E2_AGENT_MODE_ENABLED, E2_AGENT_MODE_DISABLED, E2_AGENT_MODE_EMPTY_SM_DIR),
        default=E2_AGENT_MODE_ENABLED,
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=repo_root / "ci-scripts" / "conf_files" / "gnb.sa.band78.fr1.106PRB.usrpb210.redcap.yaml",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    original = args.input.read_text(encoding="utf-8")
    updated = original
    if args.mode is not None:
        updated = rewrite_mode(updated, args.mode)
    updated = rewrite_e2_agent(updated, args.e2_agent_mode)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(updated, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
