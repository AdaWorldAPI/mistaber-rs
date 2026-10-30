# D-MIST-RUFF-XLOG-0: harvest inventory, reference oracle and decision

Status: **lab evidence, no production change.** Measured 2026-10-30.
Owner: `mistaber-rs` session `CC:session_01XAqKMMCqUkM2QW7zqLC2NJ`.
The XLOG session (`CC:session_01XAqKMNZqKXSaeb9g2ypywF`, EXO-50 claim
`XLOG-DR64-0-CLAIM-20261030-01`) owns `crates/xlog-relcomp-probe`; nothing
here touches it.

## 1. Pinned baselines

| Repo | Commit | Notes |
| --- | --- | --- |
| BrainyBlaze/mistaber | `b50bf3323056793830c35795eace57e43caa23b5` | Apache-2.0; NOTICE and TRADEMARK.md present |
| AdaWorldAPI/ruff | `f2cb52320c7c2359e0eb92d61dff366ff01840e0` | `ruff_python_dto_check` built from this commit |
| BrainyBlaze/xlog | `bff6da663308190148c5ce58a715d86525b62e67` | read only |
| scallop-lang/scallop | `668bfb6d45ce302fd4ffa7f29916baf3c7ce36ef` | not used (no Scallop reference needed yet) |
| AdaWorldAPI/lance-graph | `6fe42069141043e4907a65391a0c6b5da5837194` | read only |
| AdaWorldAPI/ndarray | not checked out in this container | not needed: no kernel is proposed |

Reference artifact witness:

| File | sha256 |
| --- | --- |
| `mistaber/dsl/worlds/kripke_rules.hll` (authored) | `df9020899dd02c8a0049fa264d855bb820fdf8b70378284a08b8cdda00de4fe8` |
| `mistaber/ontology/worlds/kripke_rules.lp` (generated, committed) | `6c55720475add0f81915c46a84da8146235cee38dffa0db73e72a7bf0e58a9e9` |

Regenerating the `.lp` with the upstream compiler
(`compile_hll_file`, clingo 5.8.2, lark 1.3.1) gives a body byte-identical
to the committed file minus its 4-line header. So the generated artifact
matches its authored source at this commit; the `.hll` stays the authority.

## 2. Gate A: Ruff harvest coverage

Command: `ruff-py-dto preflight <mistaber>/mistaber --out pf`.

| Scope | Ruff tree stats | Decorators seen | Matched by default profile |
| --- | --- | --- | --- |
| `mistaber/` (62 files) | 93 classes, 138 function defs | `click.*` 30, `pytest.fixture` 6, `overload` 4, `cli.command` 6 | 0 semantic sites; proposes a Click CLI profile |
| `mistaber/dsl/compiler/` (6 files) | 31 classes, 8 function defs | `overload` 4 | 0 |

Independent count with Python `ast` over the same compiler files: 31
classes (21 `@dataclass` AST node types), 100 function/method defs.
Ruff's `total_function_defs: 8` counts module-level defs only, so methods,
where the compiler's logic lives, are invisible to the preflight count.

Classification of the source structures that carry the semantics:

| Source construct | Where | Class (brief §A) | Why |
| --- | --- | --- | --- |
| Holding modes, override, strength, provenance rules | `kripke_rules.hll` / `.lp` | **4: take from HLL/ASP** | Not Python; Ruff parses Python only. The oracle reads the pinned `.lp`. |
| HLL AST node types (`Atom`, `Rule`, `WorldDefDirective`, `EndorsesDirective`, …) | `parser.py` dataclasses | **2: narrow matcher extension** | Needs a `class_with_decorator` (`@dataclass`) matcher; README lists `class_with_base` as reserved. |
| `@world_def` → `accessible(child,parent)`; `@endorses` → `endorses_rule` lowering | `emitter.py` methods | **3: needs method-level / name-resolution machinery** | Undecorated methods; no current matcher kind reaches them. |
| Sort/arity/OWA-negation checks | `type_checker.py` methods | **3** | Same. |
| Click CLI surface | `cli/main.py` | **1: extractable now** | Not semantics; out of scope. |
| Clingo solving, stable models | `engine/engine.py` → `clingo` | **5: solver-specific** | Kept as the oracle. |

**Finding A1 (proposer-only):** the existing Ruff harvester can see none of
Mistaber's reasoning semantics. The smallest useful Ruff change is a
`class_with_decorator` matcher for the 21 dataclass AST nodes; it would
give a source-hashed vocabulary of HLL constructs, not their meaning. That
is a request to the Ruff owner (§8), not work done here. No parser or
codegen was added to this repo.

## 3. Gates B–F: reference oracle

`oracle/` holds two independent references and the fixtures:

- `clingo_oracle.py`: pinned upstream `.lp` (sha256-checked, read from a
  checkout, never vendored) + fixture facts, **all stable models** kept;
  brave = union, cautious = intersection.
- `scalar_kripke.py`: a least-fixpoint interpreter of the fact-only
  fragment of the holding rules, sharing no code with Clingo. It refuses
  any fixture with rules.
- `qualify.py`: reads atoms into `QualifiedHolding(proposition,
  interpretation, holding_mode, immediate_rule, source_rule)`; counts
  evidence origins through an explicit lineage map; typed refusals.

Run: `MISTABER_UPSTREAM=<checkout@b50bf33> pytest oracle/` → **32 passed** (26 fact-fixture tests + 6 HLL tests).

### Results

| Fixture | Result |
| --- | --- |
| F1 modes, F1 reversed, F2 cycle | Scalar output **equals** Clingo output exactly (6 Kripke predicates). |
| Reversed `accessible` edge | Changes the answer (`holds(p,a)` disappears): orientation is load-bearing. |
| Cycle without assertion | Nothing holds; no self-supporting inheritance. |
| `override(c,p,q)` | Blocks `p` in `c`; **does not** make `q` hold. Override is a block, not a replacement assertion. |
| Diamond `d ← a, b` | Two derivations kept: `(inherited(a), r_kripke_inherit, r_base_p)` and `(inherited(b), r_kripke_inherit, r_b_endorse)`. |
| `asserts(base,g)` with no `asserts_rule` | `g` holds in every descendant with **no** `holds_via_rule/5` atom. Refused as `MissingProvenance`. |
| F3 even negative cycle over `asserts/2` | 2 stable models; brave holds = {x1,x2} in m and n, cautious = {}. Scalar refuses. |
| Mammal C2 (no reproductive evidence) | platypus: mammal TRUE, milk TRUE, `lays_eggs` UNKNOWN, `live_birth` UNKNOWN; wombat `live_birth` TRUE. |
| Mammal C4 (obs1 asserts eggs) | `live_birth(platypus)` FALSE (explicit `-live_birth`), mammal membership still TRUE. |
| Mammal C6 (obs2 endorses obs1) | Naive authority agreement = 2; lineage origins = 1. |
| Mammal C6i (obs3 independent) | Lineage origins = 2. |
| Unsound mammal-wide default | `live_birth(platypus)` TRUE with no evidence; contradicts the reference table. |
| Rows shuffled (3 seeds) | Same models, same witness. |
| Stale `.lp` sha / different fixture witness | `StaleWitness`. |
| XLOG `R(1,Y),S(Y,4)` | `{Y=2}` in `src`, and in `curated` via inheritance with source rule `r_R_0`; `override(curated, r(1,2), _)` removes it in `curated` only; `holds(s(3,4),src)` is UNKNOWN. |

### HLL-authored fixture (`oracle/hll/modes.hll`, compiled by the upstream emitter)

F1 rewritten in HLL (`@world_def`, `@rule`/`@makor`, `@endorses`) and compiled
with `compile_hll_file`; the compiled text is deterministic (same sha twice).

- `holds/2` and `holds_via/3` equal the hand-written F1 fixture exactly. Rule
  ids differ only by name (`@endorses` synthesizes `r_endorse_b_0`).
- **The provenance gap is reachable from real HLL.** Inside an `@rule` block,
  `asserts(base, p) :- world(base).` gets `asserts_rule(base, p, r_base_p)`,
  but the fact `asserts(base, g).` gets nothing: `emitter.py` emits facts at
  lines 269-271, and adds `*_rule` companions only inside the rules loop
  (lines 280-304). At runtime `g` holds in every descendant with no
  `holds_via_rule/5`.
- **Block-scoped attribution is coarser than per-proposition.** An `@rule`
  block attributes every following rule to its id. `rema.hll:44-54`:
  block `r_rema_bb_of_achiila` with `madrega(d_rabanan)` owns
  `issur(achiila, …)`, `heter(bishul, …)` and `heter(hanaah, …)`, so both
  permissions carry a prohibition's rule id and severity. For independence
  counting this is harmless (one origin); for per-proposition provenance or
  severity it is wrong. Source-verified; not reported upstream.

### Disable runs (committed first, restored with `git checkout`)

| Disabled guard | Result |
| --- | --- |
| `MissingProvenance` raise | 1 failed |
| scalar override check | 2 failed (parity broke) |
| witness keyed on row order | 3 failed |
| absence read as FALSE | 2 failed |
| HLL: `g` written in rule form | 1 failed (the gap test: the gap is specific to the fact form) |
| HLL: `@endorses` removed | 3 failed |
| lineage dedupe (in-suite, monkeypatched) | counts 2 where 1 is right; asserted by `test_disabling_lineage_dedupe_is_detected` |

### Taxonomy vs authority (the explicit translation)

In these fixtures, **worlds are authorities** (`obs1`, `obs2`, `obs3`,
`reader`). Taxonomy (`is_a`, `instance`, `member`) is a separate stratified
content program that reads `holds(lays_eggs(X), reader)`. `is_a` is never
rendered as `accessible/2`; `qualify.taxon_edge_to_accessible` refuses.

## 4. Gate D: Epi5 / CE64

Checked `lance-graph/docs/architecture/ce64-semantic-upper-half.md`:
Pearl ladder bits 40..42 (`CausalMask`), witness handle 53..58,
`EpistemicState5 = Topology2 × Certification3` at 59..63 (Open,
Associated, Related, Supports, CausalCandidate, Causes).

Nothing here writes CE64. `strength_to_epi5` and `is_a_to_pearl3` refuse.
Observation: Mistaber's `endorsed` mode is documented upstream as
"analyzed independently from different sources" (`kripke_rules.hll`
comment), but the rules do not check independence. If Epi5's `Supports`
rung ever counts witnesses, it must count **lineage origins**, which is the
count `evidence_origins` computes, not `holds_via` rows.

## 5. Gate G: Lean ledger

`lean/claims/ledger.yaml` @ b50bf33: 59 `proved`, 8 `refuted` (counted by
`status:` lines). Relevant rows:

- `model.kripke.holds.inheritance_monotone`: proved.
- `paper.sec5.provenance` ("every derived conclusion carries a full source
  chain"): **refuted / retired**, split into four narrower proved claims,
  of which `inheritance_preserves_source` is proved in a WEAKENED
  structural form.

The F1 `g` case is a concrete snapshot instance consistent with that
retirement: a holding with no rule chain at all, because the producer
emitted `asserts/2` without `asserts_rule/3`. The proved narrow claims
do not cover it, and nothing in our oracle turns a passing Clingo run into
a theorem.

## 6. Gate E: the boundary with XLOG

Read-only check of `crates/lance-graph-relalg` (`ir.rs`, `lower.rs`
signatures): `Query { rel, measure }` over lane predicates, answers
`Count | Sum | Min | Max | Kept(mask)`. The answer carries no tuple
identity, interpretation, rule or lineage. So a Mistaber qualification
cannot ride **inside** a relalg answer; it can only ride **beside** it,
keyed by the same tuple identity, domain/version and position-order
witness.

Proposed shared boundary (no new IR, no ABI):

1. XLOG produces a deterministic tuple set under a source revision and
   position-order witness (its claim).
2. This repo attaches `QualifiedHolding` rows to those tuples, keyed by
   the same tuple identity and source revision, from the Clingo oracle.
3. Join only on equal witnesses; otherwise refuse (as `StaleWitness`).

Open: whether XLOG's RIR → native result exposes tuple identity and a
position-order witness. Asked on EXO-50 (§8).

## 7. Gate H: decision table

| Mistaber operation | Class | Basis |
| --- | --- | --- |
| `asserted` / `endorsed` holding | A/B: thin adapter | Relational selection on input facts. |
| `accessible` reachability, `accessible_transitive` | B: thin adapter | Acyclic reachability; cycle fixture shows least-fixpoint semantics needed. |
| Inherited holding with local block | B: thin adapter | Negation only over input relations and `override/3`: stratified. Scalar parity proves it on 3 fixtures. |
| `override` as a block mask | B | Block only; replacement is not entailed. |
| `holds_via_rule` immediate/source chain | B, with a refusal | Needs `MissingProvenance` refusal; upstream silently drops the chain. |
| Diamond derivations, shared-origin dedupe | B over a lineage relation | Needs a lineage relation that upstream does not supply. |
| `holding_strength` | B | Stratified; must stay a label, never an Epi5 code. |
| Negative cycles over `asserts`, choice, optimisation | **C: keep Clingo** | Multiple stable models; one fixpoint is wrong. |
| Taxonomy → worlds, strength → Epi5, `is_a` → Pearl3 | Refuse | Category errors. |
| Mask folds over holdings | **E: deferred** | No measured repeated-use workload; no timing taken. |
| Rust port of HLL compiler / Clingo | **not justified** | No residual found that B or C cannot carry. |

## 8. Requests

- **Ruff owner:** is a `class_with_decorator` matcher (dataclass AST node
  vocabulary, source span + body hash) acceptable as a narrow addition to
  `ruff_python_dto_check`? Not started.
- **XLOG session (EXO-50):** does the RIR → native relation result expose
  tuple identity and a position-order witness without new ABI?

## 9. Not done

- Only F1 has an HLL twin; the mammal and XLOG fixtures are still fact sets.
- No CE64 or Epi5 code was read beyond the architecture doc.
- No timing; no mask fold implemented.
- 0/1/63/64/65 focus-position boundaries (MIST-EPI5-0 task 11) not tested;
  they need the native fold, which is deferred.

## 10. Agent runs (model policy: Haiku grindwork, Sonnet drafting, Opus planning/review)

| Run | Card | Checked by orchestrator | Wrong | Missed |
| --- | --- | --- | --- | --- |
| Quote emitter/parser/grammar | Haiku `quote-harvester` | `emitter.py:269-272, 280-288`, `grammar.lark:25-26` re-read | 0 | 0 |
| Census of `*_rule` producers | Haiku `harvest-scout` | `endorses_rule` count re-run (28 = 28); `rema.lp` hits read at source | 0 | lists capped at 60 by brief |
| Draft HLL fixture + tests | Sonnet | files read in full, suite re-run (32 passed), 2 disable runs | 0 | 0 |
