# Dare #7586, Candidate 2: dopamine only (vish)

**Result: item 1 failed** against both fakes under the sealed v5 rule and under the v7-draft drop-silent reading. Items 3, 4 and 5 were not run (moot), as the pre-registration requires.

| | |
|---|---|
| Change | `src/prep_substrate.py --dopamine`: 395 dopamine bodies at +1. Octopamine, serotonin, unclear and missing stay 0. Default path unchanged. |
| Substrate | excitatory 104442, inhibitory 57648, zero 3032, signed_nnz 24869437, dropped 693760. 244,694 edges restored (Candidate 1: 637,149). |
| Pre-registration | `results/dare-candidate2/pre_registration_c2.txt`, sha256 551c6b45…a9a = seal 10811 (signed). Posted verbatim on #7586 (c102620) before any seed existed. |
| Seeds | sha256(seal ‖ root ‖ i); root = identity_events checkpoint 34997 (tree_size 25792), created 180 s after the seal, the first one after it. |
| Rows | `results/dare-candidate2/runs-dare-dopamine.jsonl`, 270 rows, sha256 849d906d…899 = seal 10834. CPU (x86, 8 cores), 8 chains from the v5 battery hash. |
| Scorer | `score.py` at dd610ca, battery v5, step 1 → `verdicts-dare-dopamine-step-1.json` |

## Item 1, v5 strict (the verdict)

| arm | hits | Fisher vs real |
|---|---|---|
| real | 4/30 | – |
| shuffled | 4/30 | 0.647 |
| random 1x | 5/30 | 0.764 |

## Side columns (v7 draft T1–T5, a reading, not the verdict), `side-columns.json` via `side_columns.py`

| arm | hit/tie/wrong (T1) | ties silent / equal-nonzero (T2) | drop-silent (T3) | firing share (T5) |
|---|---|---|---|---|
| real | 4 / 22 / 4 | 22 / 0 | 4/8 | 30/60 |
| shuffled | 4 / 17 / 9 | 17 / 0 | 4/13 (p 0.336) | 37/60 |
| random 1x | 5 / 5 / 20 | 4 / 1 | 5/26 (p 0.105) | 49/60 |

DNp09 is silent in all 30 real-arm trials. `side_columns.py` reproduces Candidate 1's corrected triples exactly (8/20/2, 1/11/18, 4/6/20).

## Reading

Dopamine alone does not reproduce Candidate 1's drop-silent reading. These rows cannot say what octopamine and serotonin carry, because the two candidates use different seeds and their real arms aren't distinguishable at n = 30. Both candidates fail item 1 with DNp09 silent, which points at the readout rather than at another sign as the next thing to change.
