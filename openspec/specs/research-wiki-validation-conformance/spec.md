## Purpose

Define the maintained-content contract required for the existing full
research-wiki validator to pass without relaxing its rules.

## Requirements

### Requirement: Archived source references remain resolvable
Maintained wiki pages SHALL reference the existing archived OpenSpec artifact
when their cited change is no longer active. They SHALL not require a retired
active change directory to satisfy the validator.

#### Scenario: Validate archived xApp and pipeline sources
- **WHEN** the full research-wiki validator scans the xApp observation/control
  page and pipeline approval decision
- **THEN** both archived OpenSpec `source_refs` resolve and produce no missing
  source-reference error

### Requirement: Decision evidence uses supported vocabulary
Maintained decision pages SHALL use a validator-supported `evidence_tier` and
include an approved evidence label whose claim is bounded by cited repository
sources.

#### Scenario: Validate decision evidence metadata
- **WHEN** the full research-wiki validator scans the three affected decision
  pages
- **THEN** it reports neither an invalid evidence tier nor a missing approved
  evidence-label error

### Requirement: Maintained decisions are indexed
Every maintained decision page SHALL be linked from the canonical research-wiki
index.

#### Scenario: Validate decision index coverage
- **WHEN** the full research-wiki validator scans the pipeline approval and
  TDD observable-behavior decisions
- **THEN** it reports no index-membership error for either page

### Requirement: Full validation closes the recorded debt
The existing no-argument research-wiki validator SHALL return PASS after the
content-only repair, without relaxing validation rules.

#### Scenario: Run the public validator
- **WHEN** the validator is invoked with no arguments after the repair
- **THEN** it prints `REDCAP_RESEARCH_WIKI_CHECK PASS` and exits zero
