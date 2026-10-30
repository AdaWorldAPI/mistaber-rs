# MIST-HARVEST-0: Source-qualified upstream harvest map

Status: **planned / source reconnaissance** (2026-10-30). This is a map of verified source locations and **proposed** target seams, not a claim that adapters exist.

## Why this repository

[BrainyBlaze/mistaber](https://github.com/BrainyBlaze/mistaber) is a Python HLL -> ASP/Clingo system for computational halacha with authority-qualified worlds, disagreement, overrides, source attribution, and a Lean 4 audit. Harvest the *semantic distinctions* and a runnable reference oracle, not an entire domain-specific ontology. Keep upstream license/NOTICE/trademark/corpus limits separate from generic semantics.

## Verified upstream source surfaces

| Source | Observed behavior (as read 2026-10-30) | Harvest proposal |
| --- | --- | --- |
| [mistaber/dsl/compiler/parser.py](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/parser.py) | Lark frontend; AST nodes for atoms, rules, comparisons, arithmetic, constraints, aggregates | Ruff Python AST harvest of parser shapes and dispatch, not a second HLL parser |
| [mistaber/dsl/compiler/type_checker.py](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/type_checker.py) | Sort/arity/source validation; warns for unsafe open-world negation | Type/negation policy proposals, never silently normalize OWA to CWA |
| [mistaber/dsl/compiler/emitter.py](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/emitter.py) | Emits ASP; @world_def child-to-parent accessible edges; @endorses emits source-qualified rule IDs | Propose structural lowering recipes and metadata-preserving IR mappings |
| [mistaber/dsl/worlds/kripke_rules.hll](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/worlds/kripke_rules.hll) | asserted / endorsed / inherited holding modes, overrides, strength, origin world, rule provenance | Parent-child propagation and exception-fold oracle |
| [mistaber/ontology/worlds/kripke_rules.lp](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/ontology/worlds/kripke_rules.lp) | Generated ASP implementation of holding rules | Clingo golden oracle; generated output is not authoritative editable source |
| [mistaber/dsl/worlds/rema.hll](https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/worlds/rema.hll) | Domain case with explicit source metadata and narrower descendant interpretations | Inspect for semantic cases; do not import domain claims as taxonomic facts |
| [lean/claims/ledger.yaml](https://github.com/BrainyBlaze/mistaber/blob/main/lean/claims/ledger.yaml) | proved/refuted/underspecified/artifact-mismatch/blocked-by-bridge/deferred statuses | Claim-to-test/proof ledger with no silent weakening |
| [pyproject.toml](https://github.com/BrainyBlaze/mistaber/blob/main/pyproject.toml) | Python package uses clingo, lark, PyYAML, Ruff; extra tools include xclingo/asprin | Keep Python/Clingo as oracle, not default Rust dependency |

**Important:** The HLL world graph uses `accessible(child,parent)`. A source is inherited conditionally: `holds_via(inherited(parent), prop, child)` requires accessibility, parent holding, and no local override/direct assertion/endorsement. An inferred 'endorsement' is not evidence independence. Strength labels (strong/moderate/weak) are not probabilities or NARS frequency/confidence.

## Verified existing AdaWorldAPI surfaces

- [ruff_python_dto_check README](https://github.com/AdaWorldAPI/ruff/blob/main/crates/ruff_python_dto_check/README.md): existing `ruff-py-dto` preflight, `harvest`, `harvest-one`, JSON/NDJSON bundles + indices over Ruff's Python AST. Current README explicitly limits the matcher implementation; a new Mistaber profile may require a bounded extension rather than pretending class/attribute matchers already exist.
- [lance-graph README](https://github.com/AdaWorldAPI/lance-graph/blob/main/README.md): Quack Rust builders lower to mask-risc; no production text frontend currently reaches Quack. Planner is planning-only. Existing execution has separate routes, not a unified parser.
- [lance-graph CausalEdge64](https://github.com/AdaWorldAPI/lance-graph/blob/main/docs/architecture/ce64-semantic-upper-half.md): Pearl3 occupies bits 40..42, Epi5 bits 59..63; bits 53..58 are a witness handle in the current documented overview. Do not invent a new packed layout, repurpose bits, or equate an `is_a` edge with Pearl causality.
- Existing OGAR facts/IR and Ruff proposal path belong to their owning repositories. No second codegraph, SPO registry, or evidence store here.
- Scallop and XLOG are related exploration paths, **not** dependencies of this harvest.

## Mapping candidates (hypotheses, not implementation)

| Mistaber concept | Proposed relational reading | Must preserve |
| --- | --- | --- |
| `world(w)`, `accessible(child,parent)` | interpretation identity + ancestry/visibility edge | Direction, DAG/cycle assumptions, version |
| `asserts(w,p)` | asserted holding | Evidence source and producer rule |
| `endorses(w,p)` | explicit endorsement | Do not infer independent witness merely from endorsement |
| `holds_via(inherited(parent),p,child)` | qualified inheritance | Source lineage, local shadowing and precedence |
| `override(child,p,replacement)` | scoped exception/replacement relation | Difference between negation, replacement, conflict |
| `holds_via_rule(mode,p,w,immediate,origin)` | provenance chain relation | Both first-hop and original rule |
| `holding_strength(level,p,w)` | authority/derivation strength class | Distinct from calibrated certainty, Epi5, NARS F/C |
| `machloket` / `safek` | divergent viewpoint / doubt under policy | Unresolved alternatives; no premature collapse |
| Lean ledger row | formal claim ledger entry | Status/repair note, artifact bridge, proof boundary |

## Extraction evidence contract

For each proposed transformation, record:
- upstream repository, revision SHA *at harvest time*, source path, source-span, source kind and AST/body hash;
- original rule/predicate identifiers, source citation, HLL/ASP semantics, explicit dependency graph and negation policy;
- candidate target owner/IR, generated recipe, required predicate vocabulary, confidence in **extraction** only;
- witnesses (Python/Clingo output, tests, Lean claim ID if any), unresolved gaps, accepted/rejected decision and reviewer;
- generated-result hash so regeneration is detectable; a hash or repeated derivation does **not** imply independent evidence.

Do not fabricate the upstream revision SHA from a file/blob hash. Pin an actual commit before reproducible harvest. For generated artifacts, retain the .hll source as the authoritative origin.

## Risk register

1. **ASP != Datalog**: non-stratified negation, choices, stable-model multiplicity and optimization require oracle/fallback, not mask AND/OR pretend-parity.
2. **OWA != CWA**: unknown is not false. Explicit negation and negation-as-failure require different modes.
3. **World != WORLD**: Mistaber possible worlds are interpretation contexts; our WORLD stays sealed; THOUGHT is sparse deltas. ANGLE is metaphor, not mutable focus.
4. **Provenance != truth**: proposers and copied witnesses do not promote certainty; NARS F/C must account for evidence lineage/independence.
5. **Graph inheritance != causation**: `is_a` and inheritance do not automatically earn Pearl3 intervention/causal status.
6. **Mask position witness**: intersect/fold only when relation/domain/version/order identity matches; stale identity must refuse.
7. **Trademark/corpus**: Apache-2.0 code terms, nonlicensed trademarks, source-specific historical/translation rights, and normative domain review.
8. **No premature SoA**: relational identity is canonical; prepared hot focus may project into registers after admission, without duplicate value stores.

## H0 deliverable

A reviewable extract report with source inventory, candidate mapping, reachable Ruff AST coverage, unsupported grammar/solver constructs, exact oracle fixture inventory, and a **decision**, not a Rust port.
