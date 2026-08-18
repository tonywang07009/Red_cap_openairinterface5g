# Profile contract

Gate `none`:

- Allow image, library, Gymnasium, bridge health, and offline model work.
- Refuse every E2SM-RC action.

Gate `ul-prb-cap-v1`:

- Read `redcap_ul_prb_cap` from the existing control contract.
- Require exactly one eligible E2 node.
- Require distinct fresh cell and UE E2SM-KPM observations.
- Require a verified binding containing KPM UE key, RC UE ID, RNTI, and source
  sequence; never use `ue_id=rnti` as a fallback.
- Permit one candidate value inside the contract range and restore baseline.

Gate new research semantics:

- Define state, action, reward, reset, episode, timing, freshness, alignment,
  baseline, and post-action windows in a new OpenSpec profile.
- Keep the shared runtime algorithm-agnostic.
- Create a new immutable profile/version; do not rewrite an existing profile.
