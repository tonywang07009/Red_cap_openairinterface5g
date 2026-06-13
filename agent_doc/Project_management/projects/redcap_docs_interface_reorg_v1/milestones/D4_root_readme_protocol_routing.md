# D4 Root README and Protocol Routing

## Goal
- Rework the root `README.md` into a template-style RedCap/OAI route page.
- Add a dedicated RedCap L1/L2 protocol guide without overloading the function lookup table.

## Scope
- Update root `README.md`.
- Add `redcap_doc/specs/redcap_l1_l2_protocol_guide.md`.
- Fix RedCap documentation routes that point to stale function-reference paths.
- Keep OAI license, NOTICE, upstream docs, and community support references.

## Acceptance Criteria
- [x] Root `README.md` has quick start, documentation routes, operator routes, protocol learning path, repository map, build/test, and license/support sections.
- [x] RedCap users can reach `redcap_interface/`, `redcap_doc/`, `redcap_library/`, and project-management docs from the root README.
- [x] L1/L2 protocol explanation is separate from `redcap_l1_l3_function_lookup.md`.
- [x] No copied `doc_example` sample branding, MIT license text, LinkedIn, or placeholder GitHub repository links remain in root README.
- [x] Unverified 3GPP clause mappings remain marked `[Needs Verification]`.

## Discussion Point
- `doc_example` is useful for structure, not content ownership. The root README remains an OAI Public License V1.1 project entrypoint.
