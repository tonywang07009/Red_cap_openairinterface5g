#!/usr/bin/env bash

set -euo pipefail

usage()
{
  printf '拒絕：缺少 human scope confirmation（需使用 --confirm-scope）；未建立或推送批准標籤。\n' >&2
  printf 'usage: %s <change-id> --confirm-scope\n' "${0##*/}" >&2
  exit 1
}

refusal()
{
  printf '拒絕：%s；未建立或推送批准標籤。\n' "$1" >&2
  exit 1
}

[[ $# -eq 2 && "$2" == "--confirm-scope" ]] || usage
change_id="$1"
[[ "$change_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || refusal "change-id 格式無效"

repo_root=$(rtk git rev-parse --show-toplevel 2>/dev/null) || refusal "目前目錄不在 Git repository"
proposal_rel="openspec/changes/$change_id/proposal.md"
change_rel="openspec/changes/$change_id"
proposal_path="$repo_root/$proposal_rel"
tag_prefix="openspec/$change_id/approved"

[[ -d "$repo_root/$change_rel" && -f "$proposal_path" ]] || refusal "找不到已提交的 OpenSpec proposal"

scoped_status=$(rtk git -C "$repo_root" status --porcelain=v1 --untracked-files=all -- "$change_rel" 2>/dev/null) || refusal "無法檢查 OpenSpec revision"
[[ "$scoped_status" == "ok" ]] && scoped_status=""
[[ -z "$scoped_status" ]] || refusal "指定 OpenSpec 目錄仍有未提交變更"

full_sha=$(rtk git -C "$repo_root" rev-parse HEAD 2>/dev/null) || refusal "無法解析目前 revision"
rtk git -C "$repo_root" cat-file -e "$full_sha:$proposal_rel" 2>/dev/null || refusal "proposal 不在目前已提交 revision"

rtk git -C "$repo_root" remote get-url origin >/dev/null 2>&1 || refusal "origin remote 不存在"
rtk git -C "$repo_root" ls-remote origin >/dev/null 2>&1 || refusal "origin remote 無法連線"

parent_change_id=none
parent_tag=none
parent_line=$(sed -n '/^\*\*Parent task:\*\*/p' "$proposal_path" | head -n 1)
if [[ -n "$parent_line" ]]; then
  parent_change_id=$(printf '%s\n' "$parent_line" | sed -nE 's#.*\(\.\./([^/]+)/proposal\.md[^)]*\).*#\1#p')
  [[ "$parent_change_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || refusal "Parent task 格式無效"

  while IFS= read -r candidate; do
    [[ -n "$candidate" ]] || continue
    [[ "$(rtk git -C "$repo_root" cat-file -t "refs/tags/$candidate" 2>/dev/null)" == "tag" ]] || continue
    candidate_annotation=$(rtk git -C "$repo_root" for-each-ref --format='%(contents)' "refs/tags/$candidate")
    candidate_target=$(rtk git -C "$repo_root" rev-parse "refs/tags/$candidate^{}")
    candidate_change=$(printf '%s\n' "$candidate_annotation" | sed -n 's/^Change: //p' | head -n 1)
    candidate_commit=$(printf '%s\n' "$candidate_annotation" | sed -n 's/^Commit: //p' | head -n 1)
    if [[ "$candidate_change" == "$parent_change_id" && "$candidate_commit" == "$candidate_target" ]]; then
      parent_tag="$candidate"
      break
    fi
  done < <(rtk git -C "$repo_root" tag --list "openspec/$parent_change_id/approved/*")

  [[ "$parent_tag" != "none" ]] || refusal "找不到與 Parent task 對齊的 approved annotated tag"
fi

short_sha=${full_sha:0:7}
tag_ref="$tag_prefix/$short_sha"
annotation=$(printf '%s\n' \
  'OpenSpec approved revision' \
  'Human scope confirmation: confirmed' \
  "Change: $change_id" \
  "Parent: $parent_change_id" \
  "Parent tag: $parent_tag" \
  "Commit: $full_sha" \
  "Proposal: $proposal_rel")

local_present=0
if rtk git -C "$repo_root" show-ref --verify --quiet "refs/tags/$tag_ref"; then
  local_present=1
  [[ "$(rtk git -C "$repo_root" cat-file -t "refs/tags/$tag_ref")" == "tag" ]] || refusal "既有批准 ref 不是 annotated tag"
  [[ "$(rtk git -C "$repo_root" rev-parse "refs/tags/$tag_ref^{}")" == "$full_sha" ]] || refusal "既有批准標籤指向不同 revision"
  [[ "$(rtk git -C "$repo_root" for-each-ref --format='%(contents)' "refs/tags/$tag_ref")" == "$annotation" ]] || refusal "既有批准標籤 annotation 不一致"
fi

remote_lines=$(rtk git -C "$repo_root" ls-remote origin \
  "refs/tags/$tag_ref" "refs/tags/$tag_ref^{}") || refusal "無法查詢 origin 的批准標籤"
remote_tag_oid=$(printf '%s\n' "$remote_lines" | awk -v ref="refs/tags/$tag_ref" '$2 == ref { print $1; exit }')
remote_target_oid=$(printf '%s\n' "$remote_lines" | awk -v ref="refs/tags/$tag_ref^{}" '$2 == ref { print $1; exit }')

if [[ -n "$remote_tag_oid" || -n "$remote_target_oid" ]]; then
  [[ -n "$remote_tag_oid" && -n "$remote_target_oid" ]] || refusal "origin 的批准 ref 不是完整 annotated tag"
  [[ "$remote_target_oid" == "$full_sha" ]] || refusal "origin 的批准標籤指向不同 revision"
  rtk git -C "$repo_root" fetch --no-tags origin "refs/tags/$tag_ref" >/dev/null 2>&1 || refusal "無法讀取 origin 的批准 annotation"
  [[ "$(rtk git -C "$repo_root" cat-file -t "$remote_tag_oid" 2>/dev/null)" == "tag" ]] || refusal "origin 的批准 ref 不是 annotated tag"
  remote_annotation=$(rtk git -C "$repo_root" cat-file -p "$remote_tag_oid" | sed '1,/^$/d')
  [[ "$remote_annotation" == "$annotation" ]] || refusal "origin 的批准 annotation 不一致"
  printf 'change: %s\n' "$change_id"
  printf 'annotated tag: %s\n' "$tag_ref"
  printf 'commit: %s\n' "$full_sha"
  printf 'tag pushed: already-present\n'
  printf '摘要：已確認批准標籤存在；GitHub Issue mirror 由 GitHub Actions 後續處理。\n'
  exit 0
fi

if (( local_present == 0 )); then
  rtk git -C "$repo_root" tag -a "$tag_ref" "$full_sha" -m "$annotation" >/dev/null 2>&1 || refusal "建立 annotated tag 失敗"
fi

if ! rtk git -C "$repo_root" push origin "refs/tags/$tag_ref:refs/tags/$tag_ref" >/dev/null 2>&1; then
  printf '拒絕：origin push 結果不確定；保留本地批准標籤 %s。\n' "$tag_ref" >&2
  exit 1
fi

printf 'change: %s\n' "$change_id"
printf 'annotated tag: %s\n' "$tag_ref"
printf 'commit: %s\n' "$full_sha"
printf 'tag pushed: pushed\n'
printf '摘要：已推送批准標籤；GitHub Issue mirror 由 GitHub Actions 後續處理。\n'
