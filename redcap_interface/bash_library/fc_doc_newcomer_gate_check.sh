#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
INTERFACE_DIR=$(realpath "${SCRIPT_DIR}/..")
REPO_ROOT=$(realpath "${INTERFACE_DIR}/..")

cd "${REPO_ROOT}"

required_files=(
  "README.md"
  "README.en.md"
  "README.zh-TW.md"
  "redcap_doc/manuals/install/README.en.md"
  "redcap_doc/manuals/install/README.zh-TW.md"
  "redcap_doc/manuals/install/redcap_begin_from_zero.en.md"
  "redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md"
  "redcap_doc/manuals/install/redcap_rebuild_after_changes.en.md"
  "redcap_doc/manuals/install/redcap_rebuild_after_changes.zh-TW.md"
  "redcap_doc/manuals/install/redcap_newcomer_runtime_gate.en.md"
  "redcap_doc/manuals/install/redcap_newcomer_runtime_gate.zh-TW.md"
)

markers=(
  "sample=29"
  "running=29"
  "attach=29"
  "pdu=29"
  "tun=29"
  "forward_ping_ok=29"
  "gnb_restart=0"
  "failures=0"
)

public_md_files()
{
  find README.md README.en.md README.zh-TW.md redcap_doc redcap_interface redcap_library \
    -path 'redcap_doc/mineru_markdown' -prune -o \
    -path 'redcap_library/redcap_doc_writer_skill' -prune -o \
    -path 'redcap_library/redcap_log_curator_skill' -prune -o \
    -path 'redcap_library/AGENTS.md' -prune -o \
    -name '*.md' -print
}

echo "[Doc Gate] Checking required files"
for path in "${required_files[@]}"; do
  if [[ ! -f "${path}" ]]; then
    echo "Missing required file: ${path}" >&2
    exit 1
  fi
done

echo "[Doc Gate] Checking unsupported language links"
if public_md_files | xargs rg -n "日本語|韓国語|한국어" >/tmp/redcap_doc_gate_unsupported_lang.txt; then
  cat /tmp/redcap_doc_gate_unsupported_lang.txt >&2
  exit 1
fi

echo "[Doc Gate] Checking public docs for Codex-only wrappers"
if public_md_files | xargs rg -n "\\brtk\\b|RTK" >/tmp/redcap_doc_gate_rtk.txt; then
  cat /tmp/redcap_doc_gate_rtk.txt >&2
  exit 1
fi

echo "[Doc Gate] Checking encoding replacement characters"
if public_md_files | xargs rg -n "���" >/tmp/redcap_doc_gate_encoding.txt; then
  cat /tmp/redcap_doc_gate_encoding.txt >&2
  exit 1
fi

echo "[Doc Gate] Checking language-crossing links"
while IFS= read -r path; do
  case "${path}" in
    *.en.md)
      if awk '/\.zh-TW\.md/ && !/English.*繁體中文/ { print FILENAME ":" FNR ":" $0; bad=1 } END { exit bad ? 1 : 0 }' "${path}" >/tmp/redcap_doc_gate_crosslink.txt; then
        :
      else
        cat /tmp/redcap_doc_gate_crosslink.txt >&2
        exit 1
      fi
      ;;
    *.zh-TW.md)
      if awk '/\.en\.md/ && !/English.*繁體中文/ { print FILENAME ":" FNR ":" $0; bad=1 } END { exit bad ? 1 : 0 }' "${path}" >/tmp/redcap_doc_gate_crosslink.txt; then
        :
      else
        cat /tmp/redcap_doc_gate_crosslink.txt >&2
        exit 1
      fi
      ;;
  esac
done < <(public_md_files)

echo "[Doc Gate] Checking required 29 UE markers"
for marker in "${markers[@]}"; do
  if ! rg -q "${marker}" redcap_doc/manuals/install/redcap_begin_from_zero.en.md redcap_doc/manuals/install/redcap_begin_from_zero.zh-TW.md redcap_doc/manuals/install/redcap_newcomer_runtime_gate.en.md redcap_doc/manuals/install/redcap_newcomer_runtime_gate.zh-TW.md; then
    echo "Missing marker in install/gate docs: ${marker}" >&2
    exit 1
  fi
done

echo "[Doc Gate] PASS"
