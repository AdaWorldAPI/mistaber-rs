# MIST-EPI5-0: Parent-child inference, Epi5 Sudoku and CausalEdge64 differential oracle

Status: **proposed lab fixture, no implementation**. This fixture tests semantics; it does not claim a production Epi5 encoding or a causal proof.

## Research question

Can a source-qualified relational implementation reproduce the admissible fragment of Mistaber's assertion/endorsement/inheritance/override semantics while performing position/order-safe bitwise folds over a shared sealed WORLD, and **not** treating copied evidence as independent?

### Boundaries

- Mistaber `world` is an interpretation/authority scope; AdaWorldAPI `WORLD` is immutable givens. One `THOUGHT` is a sparse interpretation delta. ANGLE remains metaphor.
- `is_a(child,parent)` is a taxonomic relation, **not** a Pearl intervention/causal edge. CausalEdge64 must retain its existing layout; Pearl3 bits 40..42 and EpistemicState5 bits 59..63 are not storage available for ad hoc imports.
- Epi5 status belongs to the epistemic evaluator; candidate masks, lineage, and a position/order witness are separate relations/fields.
- A 64-bit mask indexes **positions in a proven compatible domain/order**, not 64 physical replicas of WORLD. No eager 1024-mask matrix, no 64-thought value duplication.

## Ground truth: six mammalian exemplars

| Animal | Taxonomic group | Produces milk | Live birth | Lays eggs |
| --- | --- | --- | --- | --- |
| wombat | marsupial (therian) | yes | yes | no |
| possum | marsupial (therian) | yes | yes | no |
| whale | placental (therian) | yes | yes | no |
| fox | placental (therian) | yes | yes | no |
| elephant | placental (therian) | yes | yes | no |
| platypus | monotreme | yes | no | yes |

Biological truth is the **fixture's explicit reference**, not a license to infer all of it under Open World Assumption. Distinguish **observed**, **taxonomically inferred**, **default inferred**, **overridden**, **unknown** and **refuted**.

Do **not** encode `default(mammal,live_birth)` as an unqualified invariant. Use a *scoped* therian default (or a deliberately unsound broader default **only as a falsifier**) and explicit monotreme egg-laying evidence. Membership in Mammalia must survive the reproductive exception.

## Logical tasks

1. Parent-child taxonomy: mammal -> monotreme; mammal -> therian -> marsupial/placental; named animals in their respective branch. Ensure `accessible(child,parent)` orientation at the Mistaber world boundary; avoid conflating authority inheritance with `is_a`.
2. Derive `produces_milk(x)` through taxonomic inheritance with a source chain and accepted rule scope.
3. Withhold `egg_laying(platypus)`; query should remain unknown under OWA, not `false`.
4. Add independent observation `lays_eggs(platypus)` and the constrained monotreme branch; reject incompatible live-birth default while retaining mammal membership.
5. Add a second authority endorsing the first; trace immediate/source rule but **do not** double NARS evidence for copied lineage.
6. Diamond DAG: child inherits from two branches sharing the same ancestral source; preserve alternative derivations, de-duplicate *witness identities* for independence assessment.
7. Add explicit override: replacement and negation are different operations. Do not assume every override entails the replacement automatically; follow the specific HLL/ASP rules.
8. Force a genuine conflicting claim; keep source-qualified alternatives or reject according to explicit solver policy, not row order.
9. Use a negation-as-failure counterexample; `p :- not q.` and `q :- not p.` can have multiple stable models. A single bitset closure is not a complete oracle.
10. Reorder admissible rows while preserving identity; results must remain identical. Reuse masks with *stale or mismatched* position/order/domain witness and require typed refusal.
11. Exercise 0, 1, 63, 64 and 65 focused positions and the existing 256-focus boundary contract; refuse or split only where explicitly admitted. Do not invent gather-at-execution behavior.
12. Feed an inherited holding into an epistemic evaluation: Epi5's existing state mapping may be applied if contract-backed, never infer a numeric 5-bit value from Mistaber's authority strength alone.

## Abstract reference relations (NOT a new Rust schema)

```text
taxon(child, parent)
instance(animal, taxon)
inheritable(taxon, proposition, scope, source_rule)
asserted(world, proposition, rule, source)
endorsed(world, proposition, rule, source)
accessible(world_child, world_parent)
override(world, proposition, replacement)
holds_via(mode, proposition, world)
holds_via_rule(mode, proposition, world, immediate_rule, source_rule)
source_lineage(rule, origin_evidence_id)
focus_identity(domain_id, version, ordering_witness, position)
epistemic_reading(proposition, thought_id, classification)
```

The reference implementation's actual predicates and types must be imported by an *explicit, tested adapter*. This list is a desired relational reading, not a promise that upstream provides each predicate or that all can be packed into CE64.

## Reference execution and comparison

- Compile Mistaber-authored HLL with the original upstream generator. Record the exact upstream commit, tool versions, generated `.lp` hash and source paths.
- Use Clingo to evaluate the finite fixtures; preserve **all stable models**, modeled truth status, `holds_via` modes, scope, immediate/source rule, and explanation lineage.
- Normalize output into relation tuples with explicit world and source identities, then compare against (future) candidate algebra projection.
- Oracle quality: every expected tuple and relevant non-entailment must be checked. Absence from a chosen model is not universally false.
- Compare time for oracle solve, position preparation, repeated fold, lineage/explanation materialization **separately**. Only a repeated-use benefit with amortized preparation supports admission.

## Acceptance gate

| Dimension | Criterion |
| --- | --- |
| Logic | Exact equality of the normalized intended outputs for **every admitted fixture and stable model** |
| Provenance | No lost or invented immediate/source rule; origin lineage preserved |
| Independence | Copy, inheritance and endorsement never automatically turn into independent evidence |
| Epistemology | Unknown and NAF not silently converted to explicit false; Epi5 updates only via its existing contract |
| Witnesses | Cross-domain, cross-version, reordered or stale mask is rejected unless a verified rebinding exists |
| Defaults | Platypus exception does not eliminate Mammalia; inappropriate default must be falsifiable |
| Causality | Taxonomy never silently earns Pearl3 causality |
| Unsupported | Non-stratified or solver-specific features explicitly routed to reference/fallback |
| Performance | Measured on same fixtures, report both setup and repeated costs; no assumed threshold or claimed win |

**Single decisive falsifier:** a diamond or platypus fixture returns the right Boolean label but either loses the origin rule, counts repeated evidence twice, or treats unknown as false. That is *failure*, not partial success.

## Admission guidance

- **Low hanging fruit:** direct/endorsed/inherited/overridden relations + source-qualified diamond oracle.
- **Medium:** position/order-safe folds with measured repeated-use amortization.
- **High:** admissible ASP fragment detection, exact handling of nonmonotonic residuals, formal proof bridge to concrete snapshot.
- **Heavy:** general stable-model enumeration/optimization and full HLL/Clingo replacement. Outside present authorization.

## Next experiment request to owning sessions

Produce (1) an HLL+Clingo oracle fixture, (2) Ruff source-provenance proposal for each rule, (3) a normalized expected-relations table, (4) a comparison transcript and falsifier outcome. Do not merge anything outside this repository or make production changes as part of this docs PR.
