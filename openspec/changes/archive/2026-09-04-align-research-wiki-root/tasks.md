## 1. Root-drift baseline

- [x] 1.1 Run the registered validator with its current default root, retain a
  timestamped RED log, and confirm the reported retired-root failure.

## 2. Canonical-root repair

- [x] 2.1 Update the validator default root and its self-test fixtures to
  `redcap_research_wiki/`; keep validation read-only outside its temporary
  fixture directory.
- [x] 2.2 Update maintained wiki metadata, reusable-template internal paths,
  and current project/course navigation to the canonical root; exclude
  append-only `redcap_research_wiki/log.md` and raw evidence locations.
- [x] 2.3 Update the reusable research-wiki skill Load Contracts to the
  canonical governance and index paths.

## 3. Regression evidence and review

- [x] 3.1 Run the validator `--self-test`, Python syntax check, and default
  full validation; retain timestamped evidence, confirm no retired-root or
  canonical-navigation failure, and classify remaining non-root debt separately.
- [x] 3.2 Complete independent spec and standards re-review of the scoped diff
  for retired-root references in maintained navigation, unchanged historical
  log text, and no unrelated edits.
