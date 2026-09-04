## Purpose

Define bounded, fail-closed evolution of research-wiki skills from retained
evidence to a human-promoted candidate procedure.

## Requirements

### Requirement: Evolution uses a bounded evidence packet
An Evolution Worker SHALL receive no more than two representative task traces,
one reviewed wiki pattern or case, and one existing validation command for one
root-cause hypothesis.

#### Scenario: Propose from repeated evidence
- **WHEN** a qualified root cause is selected for evolution
- **THEN** the worker receives only the bounded packet and produces at most one
  candidate skill diff

#### Scenario: Reject unbounded context
- **WHEN** a request lacks a root cause or exceeds the bounded packet
- **THEN** the worker SHALL refuse to propose a candidate and retain the active
  skill

### Requirement: Water-spider qualification is pull-only
The Water Spider SHALL qualify a candidate only after the same root cause is
observed at least twice with positive and negative evidence. It SHALL enforce
candidate WIP equal to one and SHALL not edit wiki or skill state.

#### Scenario: Insufficient recurrence
- **WHEN** evidence contains only one occurrence or lacks either polarity
- **THEN** the Water Spider SHALL reject qualification without creating or
  activating a candidate

### Requirement: Candidate promotion is fail-closed
A candidate skill SHALL declare applicability, a counterexample, a stop
condition, and an independent validation command. Only a human MAY promote it
by editing the active skill after validation passes.

#### Scenario: Candidate validation fails
- **WHEN** the independent validation command fails or evidence is incomplete
- **THEN** the active skill remains unchanged and the candidate records its
  rejection reason

#### Scenario: Candidate validation passes
- **WHEN** independent validation passes and a human approves promotion
- **THEN** the active skill may receive the reviewed minimal diff
