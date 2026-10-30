# mistaber-rs

**Harvest and planning workspace**, not a Rust rewrite of [BrainyBlaze/mistaber](https://github.com/BrainyBlaze/mistaber).

## North star

Harvest source-qualified multi-world reasoning, inheritance/override semantics, and proof-attribution contracts from Mistaber for the existing AdaWorldAPI relational and cognitive substrate.

**Order of operations:**
1. **Ruff codegen proposer first.** Use the existing [AdaWorldAPI/ruff](https://github.com/AdaWorldAPI/ruff) Python AST / DTO harvester and existing OGAR facts/IR route to emit reviewable semantic proposals and source-linked codegen recipes. A proposal is **not** a proof, generated code, or an admission to production.
2. **Prefer an internal algebra polyfill** over existing lance-graph RelAlg / Datalog / Quack / mask-risc surfaces when source semantics and differential tests justify it.
3. **Full Rust port only by explicit decision gate**, and only for a demonstrated unrepresentable residual; no automatic port mandate.

The target is not a new ontology runtime or a second reasoning engine. It is the smallest semantic contract that can make Mistaber's *asserted / endorsed / inherited / overridden* distinctions and their provenance visible to Epi5, position-and-order folds, and source-independent evidence accounting.

## References

- Mistaber upstream: https://github.com/BrainyBlaze/mistaber
- HLL parser: https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/parser.py
- HLL type checker: https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/type_checker.py
- HLL to ASP emitter: https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/compiler/emitter.py
- Holding / Kripke rules: https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/dsl/worlds/kripke_rules.hll
- Generated reference ASP: https://github.com/BrainyBlaze/mistaber/blob/main/mistaber/ontology/worlds/kripke_rules.lp
- Formal claim ledger: https://github.com/BrainyBlaze/mistaber/blob/main/lean/claims/ledger.yaml
- Ruff harvest README: https://github.com/AdaWorldAPI/ruff/blob/main/crates/ruff_python_dto_check/README.md
- lance-graph execution/CE64 overview: https://github.com/AdaWorldAPI/lance-graph

Mistaber upstream reports Apache-2.0 for code, with separate trademark restrictions for its name/logo. Do not copy upstream code or datasets blindly; honor licenses, notices, provenance, and source-specific corpus restrictions. Upstream's domain is computational Jewish law; our fixture is *domain-neutral semantics*, not a replacement for normative expertise.

## Plans

- [Harvest map](.claude/plans/MIST-HARVEST-0.md)
- [Staged Ruff proposer to algebra admission plan](.claude/plans/MIST-PIPELINE-0.md)
- [Semantic differential oracle and falsifiers](.claude/plans/MIST-EPI5-0.md)
- [Agent/session ownership and exclusions](AGENTS.md)

**Status:** documents only. No Rust crate, no Clingo replacement, no modified upstream sources, no runtime implementation, no production admission.
