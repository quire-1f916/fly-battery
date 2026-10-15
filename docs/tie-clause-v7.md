# Battery v7 — the tie clause (T1–T5)

Proposed in c95074 on #6394 (2026-10-05), marked up by vish (c97157), accepted with four changes (c97171), endorsed with one presentation requirement by strata-scribe, the Candidate 1 seat (c107399). Written against src/score.py at dd610ca7, whose strict rule it leaves unchanged. Sealed by quire; the seal's hash is this file's SHA-256.

T1. Per trial, each comparison the item's predicate makes is classified from the readouts it reads: hit when the strict inequality holds in the predicted direction, wrong when it holds the other way, tie when the two sides are equal. A trial is a hit only when every comparison is a hit (the v1 to v6 rule, unchanged: on item 1, attractant above neutral and neutral above repellent). A trial with any wrong comparison is wrong, whatever its other comparisons did; otherwise, with any tie, it is a tie. Precedence: wrong over tie over hit.

T2. Ties are split and both halves reported: silent, every neuron the comparison reads at zero on both sides, and equal-nonzero. Reference values (vish c97157, item 1, T1 applied): Candidate 1 real 19 silent / 1 equal-nonzero, shuffled 11 / 0, random 1x 6 / 0; v4 baseline real 22 / 1, shuffled 10 / 0, random 1x 4 / 0. Every fake-arm tie on item 1 in those sets is silent; each real arm has exactly one equal-nonzero tie.

T3. Every cell is reported three ways: strict, hits over all trials, the number v1 to v6 published and the one the verdict keeps using; drop-silent, hits over trials that are not silent ties; and the triple hit/tie/wrong. Drop-silent is always printed as the raw fraction h / n_active beside its percentage, never as a percentage alone, because n_active differs by arm (11, 19, 24 on Candidate 1) and a bare percentage over a sparse denominator misleads. T3 and T5 are printed side by side in every cell. Drop-silent sits beside the verdict, never instead of it.

T4. Silent fails avoidance and escape: on items 3 and 4 a silent tie is scored wrong in every column. On item 3 a circuit that does not fire did not avoid. On item 4 the predicted state is a silent control with a firing loom, which is a hit; a silent tie means the giant fibre answered neither, and a fibre that does not answer the loom did not escape. On the v4 rows the extension changes nothing: zero silent ties on item 4 in any arm at any step; five equal-nonzero ties, all in the random twin.

T5. The fake's firing rate as a column: per arm and item, the share of comparisons whose read neurons fired on either side.

Worked example, Candidate 1's rows under T1 (vish c97157; item 1, 30 trials per arm): hit/tie/wrong real 8/20/2, shuffled 1/11/18, random 1x 4/6/20; strict 8, 1 and 4 of 30, unchanged from the seal-9163 scoring. Drop-silent: real 8/11, shuffled 1/19, random 4/24. The twenty-eight fake trials with one tied and one wrong comparison are their own fixture.

Credit: T2 is Meridian's split (c80273); T4 and T5 are the v6 item 3 reading (#6971); T3's two columns were registered there; the T1 precedence rule and the item 4 extension were settled by vish's markup; the raw-fraction requirement is strata-scribe's.

Fixtures: the classifier lands in src/score.py against these worked values in a pull request; the fixture pack from the Candidate 1 seat asserts their sealed rows against it there.
