# DeepWrite candidate — Prior-Art / Second-Discovery Gate (v0.1)

**State: EXPERIMENTAL · SHADOW ONLY · NOT ACTIVE BY DEFAULT.** This is a general writing-research helper, not a change to `deepwrite/CURRENT.json`. When used in an existing project, keep the stable manuscript unchanged, run as a parallel candidate, and record exact input/output identities. Unpublished writing and private source material must never enter this public repository.

## Problem
A fluent new article can repackage a point already present in an earlier draft, and a rhetorically satisfying “second discovery” can merely rename the first claim. The normal quality gate may notice this too late, after writing. This candidate pulls two questions before promotion: (1) does the supposed new idea have a prior-art trace? (2) does the later argument introduce an independently falsifiable decision variable and observable counterexample?

## How to use
1. Store original draft and current experimental draft **outside public GitHub**. Freeze their hashes.
2. Write a JSON claim sheet with atomic claims (`cause`, `effect`, `scope`, `failure_case`, `reader_decision`); record source class: primary, commentary, prior writing, independent synthesis, market/domain evidence.
3. Run `python originality_gate.py --claims claims.json --before original.md --after candidate.md --prior prior1.md --prior prior2.md --output result.json` **locally**, where private files remain local.
4. Review every surfaced prior-art passage manually. Exact string matches are *retrieval aids*, not semantic novelty proof; no hit is not evidence of originality.
5. If prior-art already contains the claim, label it `DEEPEN` or `REWRITE`, never `NEW_DISCOVERY_PASS`. A genuinely new mechanism is still only `NEW_HYPOTHESIS_PENDING_EXTERNAL` without independent counterexamples/evidence.
6. Require an actual full revised article/chapter, show a concrete user-decision delta, and get human judgment. Use the stable protocol if candidate fails or merely adds paperwork.

## Distinct gates
- `SOURCE`: can cite the origin for each important proposition, preserving source-type boundaries.
- `PRIOR_ART`: old passages retrieved for manual inspection before announcing originality.
- `RIVAL`: can articulate the strongest counterexample and specify observable falsification.
- `SECOND_DISCOVERY`: changes explanatory variable or predicted consequences, not just heading/terminology.
- `ARTIFACT`: two complete readable artifacts with hashes and review identities.
- `DECISION_DELTA`: identify what an actual reader would do differently in a comparable situation.

**Automatic result can be `PASS_STRUCTURAL_EVIDENCE_ONLY` or `INCOMPLETE`; never human novelty, research competence, or book quality PASS.**

## Evaluation contract
Use a stable untouched manuscript as baseline. Compare raw draft, previous stable output, and candidate output, at roughly similar writing effort; explicitly account for extra information, length and editing budget. If the result depends on previously exposed author examples, label it contaminated. Independent research ability needs unseen tasks with isolated inputs and external judges. No candidate can promote itself to active under this file.
