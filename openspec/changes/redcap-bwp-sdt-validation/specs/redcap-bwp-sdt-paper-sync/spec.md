## ADDED Requirements

### Requirement: Paper PDFs are converted to Markdown
The system SHALL convert each PDF in `redcap_doc/evaluation_papers/redcap_vaildation_BWP_SDT/` to a Markdown file in the same directory.

#### Scenario: Known BWP and SDT papers are converted
- **WHEN** the sync workflow runs in the paper directory
- **THEN** `paper1_BWP_switching.md` and `paper2_SDT_small_data.md` exist and are non-empty

### Requirement: Paper metadata index is refreshed
The system SHALL maintain `redcap_vaildation_BWP_SDT_index.json` with title, authors, year, keywords, scenario tags, source PDF path, Markdown path, and extraction status.

#### Scenario: Index JSON is parseable
- **WHEN** the metadata index is refreshed
- **THEN** the JSON parses successfully and contains one record per source PDF

### Requirement: Paper folder is indexed with SymDex
The system SHALL refresh a SymDex text index for the converted paper folder using the repo-local `.symdex` state directory.

#### Scenario: Text search works after indexing
- **WHEN** SymDex indexing completes
- **THEN** a SymDex text search can find paper terms such as `BWP Inactivity Timer` or `2-step SDT`
