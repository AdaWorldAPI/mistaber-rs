# MIST-PIPELINE-0: Ruff proposer -> semantic oracle -> algebra/polyfill decision

Status: **planning only**. Owner: `mistaber-rs` harvest session; production changes remain in their owning repositories. Reference [MIST-HARVEST-0](MIST-HARVEST-0.md).

## Decision order (binding)

```text
BrainyBlaze/mistaber Python/HLL/ASP source
  -> AdaWorldAPI/ruff AST harvest + preflight, source/body hashes
  -> existing OGAR facts/IR route (where admitted)
  -> Ruff codegen PROPOSER: typed mapping + generated recipe/patch proposal
  -> independent reference checks (Mistaber Python / Clingo; tests; Lean claim ledger)
  -> source-qualified semantic decision and residual classification
       | (A) representable bounded fragment  => prefer existing RelAlg/Datalog/Quack/mask-risc polyfill
       | (B) solver-specific behavior          => keep ASP/Clingo oracle/foreign boundary
       | (C) irreducible, high-value residual  => separately evaluate minimal Rust port
```

No proposed mapping is executable merely because Ruff emitted it. The codegen proposer emits **candidates** and reviewable recipes, never automatic truth/admission.

## Ownership

| Repo/session | Owns | Does not own |
| --- | --- | --- |
| `mistaber-rs` | harvest registry, source links, fixtures, proposal contracts, comparison reports, decision record | forked full Mistaber implementation, new engine |
| `AdaWorldAPI/ruff` | Python AST extraction, existing `ruff_python_dto_check` and proposer machinery, minimal additive matcher/profile if proved necessary | ASP truth oracle, lance-graph execution |
| `OGAR` | existing facts/IR and reviewed wiring where applicable | second RDF/SPO ontology created by Mistaber |
| `lance-graph` | existing RelAlg/Datalog/planning/Quack/mask-risc integration contracts, CE64/Epi5 semantics, source evidence admission | Ruff AST/codegen implementation |
| `ndarray` | proven CPU SIMD mask/palette kernels, perf and parity | authority semantics, ASP engine |
| upstream Mistaber/Clingo/Lean | reference behavior and formally scoped claims | proof of our compiled/polyfill parity without differential tests |

Consult the appropriate existing Linear board threads for multi-session ownership and claimed vs verified status; EXO-50 is a reference for the coordination convention, not presumed to own this new work. Do not silently claim or modify another repo's scope.

## H0: Baseline freeze + inventory (no code)

- Capture actual upstream commit IDs, Python/Clingo versions, license/NOTICE, source and generated-file paths.
- Read upstream `parser.py`, `type_checker.py`, `emitter.py`, `kripke_rules.hll`, generated `.lp`, claim ledger, test harness.
- Read the current Ruff extractor CLI, config schema, `ModelGraph`/route contract/target-spec interfaces **before** proposing new schema fields.
- Produce a coverage table: parser, declarations, `@world_def`, `@endorses`, rules, negation, aggregates, source annotations, proof ledger, solver-only constructs.
- Gate H0: every claimed feature has a source path+span, every unverified feature is explicitly unknown.

## H1: Ruff codegen proposer (FIRST implementation candidate, in Ruff owner)

- Run existing `ruff-py-dto preflight` and `harvest` against the pinned upstream Python tree. Record what the existing matcher can and cannot see.
- Extend existing Ruff harvester minimally **only if** current APIs cannot represent needed shapes (e.g., class/method bodies or registry metadata). No duplicative parser and no new proposer framework.
- Keep raw AST structure, rule dispatch, source spans, source hashes, import edges and generated-vs-authored provenance as **ore**; candidate mappings are **proposals**.
- Emit a reviewable `proposal` (or adapt the existing OGAR contract), with semantic mode, input/output sorts, provenance, source span, target operator/recipe, refusal reason, evidence requests and residual classification.
- Generate candidate schema/recipe/patch proposals for review; **do not write target runtime code automatically**. Preserve matching target contracts; ask for explicit admission before implementation.
- Gate H1: deterministic regeneration and zero missing origin paths for all accepted proposals; at least one deliberately unsupported construct must be refused, not guessed.

## H2: semantic oracle fixture (mistaber-rs docs/fixtures; Python tests only if authorized)

Fixture family:
1. assertion vs endorsement vs inherited holding in an acyclic graph;
2. diamond ancestry, same source replicated along two parents, distinct source lineage;
3. scoped override and competing propositions;
4. OWA unknown vs explicit false vs NAF;
5. stratified derivation vs non-stratified ASP counterexample;
6. animal taxonomy: mammal / monotreme / marsupial / placental, platypus eggs vs therian live birth default;
7. stale position/order witness and 64-slot boundary;
8. claim ledger: a narrowed theorem cannot be labeled proven without explaining the narrowing.

- Run Mistaber/Clingo reference and normalize **all** answer sets/derivations, not a single arbitrary model, where applicable.
- Check source provenance and scopes, not just Boolean answers.
- Gate H2: source-qualified exact parity for the supported fragment; deliberate counterexamples expose exclusions.

## H3: internal algebra polyfill candidate (PREFERRED, but evidence-gated)

Only if H2 shows a well-defined fragment:
- Design mappings onto existing relational operators, `is_a` adjacency, checked position/order witness, and prepared DR64/DR256 folds; rebind/refresh stale versions or refuse, never quietly gather at execution.
- Require stable relation/domain identity and per-side version at each fold. Prove position reuse correctness before benchmarking.
- Reuse current `Quack -> mask-risc` borrow path **where available**; do not assume a text/Datalog frontend already reaches it.
- Preserve origin rule, immediate rule, source lineage and evidence class in relational data rather than packing every value into CausalEdge64.
- Epi5 (bits 59..63) remains its existing epistemic classification; Pearl3 (40..42) remains causal; neither is overwritten by imported ASP labels.
- Separate precomputation cost, recurring mask-fold cost, model enumeration cost, and explanation-materialization cost.
- Gate H3: byte/tuple parity of accepted observables against Clingo for admissible fixtures, zero unsupported silent fallbacks, and measured benefit for repeated queries **including preparation**.

## H4: residual routing decision

| Outcome | Choice | Required evidence |
| --- | --- | --- |
| Existing algebra supports admitted semantics | **A: internal polyfill** | parity, witness safety, non-regression, benchmark |
| ASP behavior requires stable-model solver/optimization | **B: reference/foreign boundary** | explicit unsupported constructs, correct retained oracle |
| Narrow critical operation cannot be expressed internally but has strong repeat demand | **C: evaluate minimal Rust port** | smallest missing operator, maintained dependency cost, parity + better economics than B |
| Benefit or correctness unproved | **D: defer** | open falsifier documented, no runtime change |

Porting the whole HLL language, Clingo, the halachic corpus, the dashboard, the Lean audit, or the upstream plugin is **not** the default or a backdoor to H3.

## Session definition of done

- Docs and references committed first; optional draft PR, not auto-merged.
- Claim ledger distinguishing `verified-source`, `proposed`, `oracle-confirmed`, `admitted`, `excluded`, `deferred`.
- A single runnable repro command per reference fixture once H2 is authorized.
- Reviewable narrow PRs for any later Ruff/OGAR/lance-graph/ndarray changes, never cross-repo silent edits.
- Report closed ends, unresolved questions, concrete falsifier, fastest low-hanging experiment, and high-cost residual separately.

## Explicit exclusions

No AGI demo, no new Rust engine, no arbitrary ASP-to-bitmask equivalence claim, no whole-repo transpilation, no speculative source-independence amplification, no mutable ANGLE, no duplicate WORLD, no execution-time gather, no new SPO store, no invented CE64 bit allocation.
