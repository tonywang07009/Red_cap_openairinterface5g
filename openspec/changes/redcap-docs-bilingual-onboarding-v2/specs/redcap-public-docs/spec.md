## ADDED Requirements

### Requirement: Public README language routing
The repository SHALL provide a short root README language selector and separate English and Traditional Chinese public entry pages.

#### Scenario: Root README exposes supported languages only
- **WHEN** a user opens `README.md`
- **THEN** the page links to `README.en.md` and `README.zh-TW.md`
- **AND** the page does not advertise unsupported language pages.

#### Scenario: English and Traditional Chinese routes stay separated
- **WHEN** a user follows the English public entry page
- **THEN** install, rebuild, gate, interface, library, and paper tutorial links route to English pages where such pages exist.
- **WHEN** a user follows the Traditional Chinese public entry page
- **THEN** install, rebuild, gate, interface, library, and paper tutorial links route to Traditional Chinese pages where such pages exist.

### Requirement: Public install and rebuild manuals
The documentation SHALL provide English and Traditional Chinese install manuals for first-time setup, rebuild-after-change, and newcomer validation.

#### Scenario: Beginner setup reaches the 29 UE target
- **WHEN** a new user follows the begin-from-zero manual
- **THEN** the manual includes host checks, interface validation, CMake build, RFsim image rebuild, and a 29 UE stage scan command.
- **AND** the pass criteria include `sample=29`, `running=29`, `attach=29`, `pdu=29`, `tun=29`, `forward_ping_ok=29`, `gnb_restart=0`, and `failures=0`.

#### Scenario: Rebuild workflow covers source and control changes
- **WHEN** a user changes C code, xApp/rApp/dApp integration, scripts, configs, or local libraries
- **THEN** the rebuild manual classifies the change type and lists the minimum rebuild or validation command.

### Requirement: Paper recovery tutorials
The documentation SHALL provide bilingual public tutorials for the supported evaluation-paper recovery workflows while preserving historical reports as evidence.

#### Scenario: Paper recovery index routes to tutorials
- **WHEN** a user opens the evaluation recovery index
- **THEN** the index links to Paper-07, Paper-10, Paper-11 service-gate, and Paper-11 Table 3 tutorials in the selected language.

#### Scenario: Tutorials preserve comparability limits
- **WHEN** a paper tutorial describes a local RFsim reproduction
- **THEN** it marks target-rate proxy, service-gate proxy, RF equivalence limits, or `[Needs Verification]` where exact paper equivalence or standard mapping is not proven.

### Requirement: Public documentation static gate
The repository SHALL provide a non-runtime static documentation gate for the public RedCap documentation routes.

#### Scenario: Static gate validates public documentation hygiene
- **WHEN** `bash redcap_interface/bash_library/fc_doc_newcomer_gate_check.sh` is run from the repository root
- **THEN** it verifies required bilingual files, unsupported language links, forbidden public command wrappers, encoding replacement characters, language-crossing links, and required 29 UE markers.

#### Scenario: Runtime gate feedback is actionable
- **WHEN** a newcomer runtime gate fails
- **THEN** the gate document provides a feedback format with step, command, expected result, actual result, log path, unclear wording, and suggested document fix.
