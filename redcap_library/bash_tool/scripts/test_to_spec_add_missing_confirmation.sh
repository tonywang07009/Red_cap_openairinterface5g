#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
fixture_parent="$repo_root/redcap_library/.test_tmp"
mkdir -p "$fixture_parent"
fixture_root=$(mktemp -d "$fixture_parent/to_spec_add_missing_confirmation.XXXXXX")
trap 'rm -rf -- "$fixture_root"' EXIT

change_id=unconfirmed-root-change
worktree="$fixture_root/worktree"
bare_remote="$fixture_root/origin.git"
command_under_test="$repo_root/redcap_library/bash_tool/scripts/to_spec_add.sh"
stdout_file="$fixture_root/stdout"
stderr_file="$fixture_root/stderr"

git init --quiet --bare "$bare_remote"
git init --quiet --initial-branch=main "$worktree"
git -C "$worktree" config user.name "to-spec fixture"
git -C "$worktree" config user.email "to-spec-fixture@example.invalid"
git -C "$worktree" remote add origin "$bare_remote"
mkdir -p "$worktree/openspec/changes/$change_id"
printf '# Unconfirmed root change\n' >"$worktree/openspec/changes/$change_id/proposal.md"
git -C "$worktree" add "openspec/changes/$change_id/proposal.md"
git -C "$worktree" commit --quiet -m "Add exact unconfirmed change"

set +e
(cd "$worktree" && "$command_under_test" "$change_id" >"$stdout_file" 2>"$stderr_file")
status=$?
set -e
stderr=$(<"$stderr_file")

[[ $status -eq 1 ]] || {
  printf 'not ok - missing confirmation exits one (got %d)\n' "$status" >&2
  exit 1
}
[[ $stderr == *'human scope confirmation'* ]] || {
  printf 'not ok - stderr does not identify missing human scope confirmation\n%s\n' "$stderr" >&2
  exit 1
}
[[ $stderr == *'未建立或推送批准標籤'* ]] || {
  printf 'not ok - stderr omits the pre-tag refusal summary\n%s\n' "$stderr" >&2
  exit 1
}

local_tags=$(git -C "$worktree" for-each-ref --format='%(refname)' refs/tags/)
remote_tags=$(git --git-dir="$bare_remote" for-each-ref --format='%(refname)' refs/tags/)
remote_heads=$(git --git-dir="$bare_remote" for-each-ref --format='%(refname)' refs/heads/)
[[ -z $local_tags ]] || {
  printf 'not ok - refusal created a local tag: %s\n' "$local_tags" >&2
  exit 1
}
[[ -z $remote_tags ]] || {
  printf 'not ok - refusal pushed a remote tag: %s\n' "$remote_tags" >&2
  exit 1
}
[[ -z $remote_heads ]] || {
  printf 'not ok - refusal pushed a branch: %s\n' "$remote_heads" >&2
  exit 1
}

printf 'ok - missing confirmation refuses before creating or pushing a tag\n'
