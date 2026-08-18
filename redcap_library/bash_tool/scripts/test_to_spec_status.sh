#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
status_script="$script_dir/to_spec_status.sh"
fixture_root="$(mktemp -d)"

cleanup()
{
  rm -rf "$fixture_root"
}
trap cleanup EXIT

failures=0

expect()
{
  local expected="$1"
  local actual="$2"
  local label="$3"
  if [[ "$actual" != *"$expected"* ]]; then
    printf 'FAIL %s: expected %q in %q\n' "$label" "$expected" "$actual" >&2
    failures=$((failures + 1))
  fi
}

run_status()
{
  local change_id="$1"
  set +e
  status_output="$(TO_SPEC_REPO_ROOT="$fixture_root" bash "$status_script" "$change_id" 2>&1)"
  status_rc=$?
  set -e
}

write_state()
{
  local state="$1"
  local diagnosis="${2:-}"
  mkdir -p "$fixture_root/openspec/.to-spec/known-change"
  printf '{"state":"%s","attempt":2,"issue_url":"https://example.invalid/issues/42","diagnosis":"%s"}\n' \
    "$state" "$diagnosis" > "$fixture_root/openspec/.to-spec/known-change/state.json"
}

mkdir -p "$fixture_root/openspec/changes/known-change"
printf '# fixture\n' > "$fixture_root/openspec/changes/known-change/proposal.md"
rtk git -C "$fixture_root" init -q
rtk git -C "$fixture_root" config user.email fixture@example.invalid
rtk git -C "$fixture_root" config user.name fixture
rtk git -C "$fixture_root" add openspec
rtk git -C "$fixture_root" commit -qm fixture
rtk git -C "$fixture_root" tag -a openspec/known-change/approved/1234567 -m approved

run_status known-change
expect 'state: approved' "$status_output" approved_state
expect 'next action: push approved tag' "$status_output" approved_next_action
expect 0 "$status_rc" approved_exit

rtk git -C "$fixture_root" tag -d openspec/known-change/approved/1234567 >/dev/null
run_status known-change
expect 'state: draft' "$status_output" draft_state
expect 'next action: request human approval' "$status_output" draft_next_action
expect 0 "$status_rc" draft_exit

for state in publishing published diagnosing failed; do
  write_state "$state" 'GitHub API 503'
  before="$(find "$fixture_root/openspec" -type f -print | sort | xargs sha256sum)"
  run_status known-change
  after="$(find "$fixture_root/openspec" -type f -print | sort | xargs sha256sum)"
  expect "state: $state" "$status_output" "${state}_state"
  expect 0 "$status_rc" "${state}_exit"
  expect "$before" "$after" "${state}_read_only"
done

expect 'next action: record remedy, then run to-spec retry known-change' "$status_output" failed_next_action

write_state failed 'Authorization: Bearer supersecret'
run_status known-change
expect '[REDACTED]' "$status_output" token_redacted
if [[ "$status_output" == *supersecret* ]]; then
  printf 'FAIL token_redacted: secret leaked\n' >&2
  failures=$((failures + 1))
fi

printf '{invalid}\n' > "$fixture_root/openspec/.to-spec/known-change/state.json"
run_status known-change
expect 'error: invalid mirror state' "$status_output" invalid_state_message
expect 3 "$status_rc" invalid_state_exit

run_status missing-change
expect 'error: change not found: missing-change' "$status_output" missing_change_message
expect 2 "$status_rc" missing_change_exit

if (( failures > 0 )); then
  exit 1
fi

printf 'PASS to_spec_status\n'
