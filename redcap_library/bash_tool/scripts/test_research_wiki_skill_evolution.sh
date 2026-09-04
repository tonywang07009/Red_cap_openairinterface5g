#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
skill_path="$repo_root/redcap_library/skills/redcap_research_wiki/SKILL.md"
missing=0

require_text()
{
  local expected=$1
  if ! grep -Fq "$expected" "$skill_path"; then
    printf 'RESEARCH_WIKI_SKILL_EVOLUTION_CONTRACT FAIL missing=%s\n' "$expected" >&2
    missing=1
  fi
}

require_text '## Evolution Roles'
require_text 'Runner'
require_text 'Evolution Worker'
require_text 'two representative traces'
require_text 'one reviewed wiki pattern or case'
require_text 'one existing validation command'
require_text 'same root cause observed at least twice'
require_text 'positive and negative evidence'
require_text 'WIP = 1'
require_text 'Do not create or activate a candidate'
require_text 'Keep the active skill unchanged'
require_text '## Candidate Contract'
require_text 'Return exactly one candidate envelope'
require_text 'applicability:'
require_text 'counterexample:'
require_text 'stop_condition:'
require_text 'validation_command: registered_read_only_tool'
require_text 'rejection_reason: non-empty reason required'
require_text 'Invoke only the registered read-only validation tool'
require_text 'Only a human may promote'

if (( missing != 0 )); then
  exit 1
fi

printf 'RESEARCH_WIKI_SKILL_EVOLUTION_CONTRACT PASS bounded_packet=1 refusal=1 wip=1 human_promotion=1\n'
