#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
fixture_parent="$repo_root/redcap_library/.test_tmp"
mkdir -p "$fixture_parent"
fixture_root=$(mktemp -d "$fixture_parent/to_spec_add.XXXXXX")
trap 'rm -rf -- "$fixture_root"' EXIT

change_id=approved-root-change
worktree="$fixture_root/worktree"
bare_remote="$fixture_root/origin.git"
command_under_test="$repo_root/redcap_library/bash_tool/scripts/to_spec_add.sh"

git init --quiet --bare "$bare_remote"
git init --quiet --initial-branch=main "$worktree"
git -C "$worktree" config user.name "to-spec fixture"
git -C "$worktree" config user.email "to-spec-fixture@example.invalid"
git -C "$worktree" remote add origin "$bare_remote"
mkdir -p "$worktree/openspec/changes/$change_id"
printf '# Approved root change\n' >"$worktree/openspec/changes/$change_id/proposal.md"
git -C "$worktree" add "openspec/changes/$change_id/proposal.md"
git -C "$worktree" commit --quiet -m "Add exact approved change"
full_sha=$(git -C "$worktree" rev-parse HEAD)

set +e
output=$(cd "$worktree" && "$command_under_test" "$change_id" --confirm-scope 2>&1)
status=$?
set -e

if ((status != 0)); then
  printf 'not ok - confirmed exact revision exits zero (got %d)\n%s\n' "$status" "$output" >&2
  exit 1
fi

mapfile -t remote_tags < <(
  git --git-dir="$bare_remote" for-each-ref \
    --format='%(refname:strip=2)' "refs/tags/openspec/$change_id/approved/"
)
[[ ${#remote_tags[@]} -eq 1 ]] || {
  printf 'not ok - expected one remote approved tag, got %d\n' "${#remote_tags[@]}" >&2
  exit 1
}

approved_tag=${remote_tags[0]}
short_sha=${approved_tag##*/}
[[ -n $short_sha && $full_sha == "$short_sha"* ]] || {
  printf 'not ok - tag suffix is not a prefix of the committed SHA: %s\n' "$approved_tag" >&2
  exit 1
}
[[ $(git --git-dir="$bare_remote" cat-file -t "$approved_tag") == tag ]] || {
  printf 'not ok - remote approval ref is not an annotated tag\n' >&2
  exit 1
}
[[ $(git --git-dir="$bare_remote" rev-parse "$approved_tag^{}") == "$full_sha" ]] || {
  printf 'not ok - remote tag does not target the exact committed revision\n' >&2
  exit 1
}
remote_heads=$(git --git-dir="$bare_remote" for-each-ref --format='%(refname)' refs/heads/)
[[ -z $remote_heads ]] || {
  printf 'not ok - approval operation pushed a branch: %s\n' "$remote_heads" >&2
  exit 1
}

expected_annotation=$(printf '%s\n' \
  'OpenSpec approved revision' \
  'Human scope confirmation: confirmed' \
  "Change: $change_id" \
  'Parent: none' \
  'Parent tag: none' \
  "Commit: $full_sha" \
  "Proposal: openspec/changes/$change_id/proposal.md")
actual_annotation=$(git --git-dir="$bare_remote" for-each-ref \
  --format='%(contents)' "refs/tags/$approved_tag")
[[ $actual_annotation == "$expected_annotation" ]] || {
  printf 'not ok - remote tag annotation does not match the fixed record\n' >&2
  exit 1
}

expected_output=$(printf '%s\n' \
  "change: $change_id" \
  "annotated tag: $approved_tag" \
  "commit: $full_sha" \
  'tag pushed: pushed' \
  '摘要：已推送批准標籤；GitHub Issue mirror 由 GitHub Actions 後續處理。')
[[ $output == "$expected_output" ]] || {
  printf 'not ok - success output differs from the public contract\nexpected:\n%s\nactual:\n%s\n' \
    "$expected_output" "$output" >&2
  exit 1
}

printf 'ok - confirmed exact revision pushes one valid annotated tag\n'
