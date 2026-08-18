#!/usr/bin/env bash
set -euo pipefail

usage()
{
  printf 'usage: %s <change-id>\n' "${0##*/}" >&2
  exit 2
}

error_invalid_state()
{
  printf 'error: invalid mirror state\n' >&2
  exit 3
}

redact()
{
  sed -E \
    -e 's/(Authorization:[[:space:]]*Bearer[[:space:]]+)[^[:space:]]+/\1[REDACTED]/Ig' \
    -e 's/(GITHUB_TOKEN=)[^[:space:]]+/\1[REDACTED]/g'
}

[[ $# -eq 1 ]] || usage
change_id="$1"
[[ "$change_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || usage

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="${TO_SPEC_REPO_ROOT:-$(cd "$script_dir/../../.." && pwd)}"
proposal="$repo_root/openspec/changes/$change_id/proposal.md"
state_file="$repo_root/openspec/.to-spec/$change_id/state.json"

if [[ ! -f "$proposal" ]]; then
  printf 'error: change not found: %s\n' "$change_id" >&2
  exit 2
fi

state=""
attempt=""
issue_url=""
diagnosis=""

if [[ -f "$state_file" ]]; then
  mapfile -t fields < <(python3 - "$state_file" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("state must be an object")
    state = data.get("state")
    if not isinstance(state, str):
        raise ValueError("state is required")
    attempt = data.get("attempt", "")
    if attempt != "" and not isinstance(attempt, int):
        raise ValueError("attempt must be an integer")
    issue_url = data.get("issue_url", "")
    diagnosis = data.get("diagnosis", "")
    if not isinstance(issue_url, str) or not isinstance(diagnosis, str):
        raise ValueError("text fields must be strings")
    print(state.replace("\n", " ").replace("\r", " "))
    print(attempt)
    print(issue_url.replace("\n", " ").replace("\r", " "))
    print(diagnosis.replace("\n", " ").replace("\r", " "))
except (OSError, ValueError, json.JSONDecodeError):
    sys.exit(1)
PY
  ) || error_invalid_state
  [[ ${#fields[@]} -eq 4 ]] || error_invalid_state
  state="${fields[0]}"
  attempt="${fields[1]}"
  issue_url="${fields[2]}"
  diagnosis="${fields[3]}"
else
  while IFS= read -r tag; do
    [[ -n "$tag" ]] || continue
    if [[ "$(rtk git -C "$repo_root" cat-file -t "$tag" 2>/dev/null)" == "tag" ]]; then
      state="approved"
      break
    fi
  done < <(rtk git -C "$repo_root" tag --list "openspec/$change_id/approved/*" 2>/dev/null)
  state="${state:-draft}"
fi

case "$state" in
  draft)
    next_action="request human approval"
    ;;
  approved)
    next_action="push approved tag"
    ;;
  publishing)
    next_action="wait for publication"
    ;;
  published)
    next_action="inspect issue mirror"
    ;;
  diagnosing)
    next_action="wait for diagnosis"
    ;;
  failed)
    next_action="record remedy, then run to-spec retry $change_id"
    ;;
  *)
    error_invalid_state
    ;;
esac

diagnosis="$(printf '%s' "$diagnosis" | redact)"
printf 'change: %s\n' "$change_id"
printf 'state: %s\n' "$state"
printf 'issue: %s\n' "${issue_url:-none}"
printf 'attempt: %s\n' "${attempt:-none}"
printf 'diagnosis: %s\n' "${diagnosis:-none}"
printf 'next action: %s\n' "$next_action"
