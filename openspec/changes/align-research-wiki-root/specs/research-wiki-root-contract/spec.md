## ADDED Requirements

### Requirement: Canonical wiki root
The registered research-wiki validator SHALL use the repository-relative
`redcap_research_wiki/` directory as its default root. Its self-test fixtures
SHALL model that same root. The validator SHALL not silently fall back to the
retired `agent_doc/Project_management/redcap_research_wiki/` location.

#### Scenario: Validate the maintained wiki
- **WHEN** the validator is invoked with no arguments in this repository
- **THEN** it validates `redcap_research_wiki/` and reports its mechanical
  result without requiring a retired-root directory

#### Scenario: Exercise validator fixtures
- **WHEN** the validator is invoked with `--self-test`
- **THEN** it creates and validates fixtures rooted at
  `redcap_research_wiki/` and still rejects the invalid fixtures

### Requirement: Current navigation uses the canonical root
Current skill Load Contracts, maintained internal wiki references, and current project/course navigation SHALL resolve below `redcap_research_wiki/`.

#### Scenario: Load a bounded wiki operation
- **WHEN** an agent follows the current `redcap-research-wiki` skill Load
  Contracts
- **THEN** every required governance and index path resolves below the
  canonical wiki root

#### Scenario: Validate maintained metadata links
- **WHEN** the validator scans a maintained content page or reusable template
- **THEN** its internal wiki `source_refs` and `related_pages` resolve below
  `redcap_research_wiki/`

#### Scenario: Follow current project navigation
- **WHEN** an agent follows a current wiki route from `AGENTS.md` or the Luna
  CLI trace course
- **THEN** that route resolves below the canonical wiki root

### Requirement: Historical records preserve their original paths
The root-alignment migration SHALL preserve append-only `log.md` entries and
their historical path text. It SHALL not rewrite raw evidence paths solely to
conform them to the canonical current navigation root.

#### Scenario: Review the root-alignment diff
- **WHEN** the root-alignment change is reviewed
- **THEN** `redcap_research_wiki/log.md` has no migration edit and raw evidence
  locations are unchanged
