# mistaber-rs agent/session contract

This is a **harvest planning repo**. Never interpret its name as an instruction to rewrite Mistaber in Rust.

## First read

1. [README](README.md)
2. [.claude/plans/MIST-HARVEST-0.md](.claude/plans/MIST-HARVEST-0.md)
3. [.claude/plans/MIST-PIPELINE-0.md](.claude/plans/MIST-PIPELINE-0.md)
4. [.claude/plans/MIST-EPI5-0.md](.claude/plans/MIST-EPI5-0.md)

Read upstream [Mistaber](https://github.com/BrainyBlaze/mistaber) source and current target repo before asserting behavior. Source comments, generated artifacts and formal claims are **distinct** evidence levels. Pin actual upstream revision IDs (do not substitute blob SHAs).

## Working order

- **M0 docs/reference baseline:** source, behavior, license, exact revision, scopes, exclusions.
- **M1 Ruff proposer:** route through existing [ruff_python_dto_check](https://github.com/AdaWorldAPI/ruff/blob/main/crates/ruff_python_dto_check/README.md), existing ModelGraph/OGAR/route contracts where verified. Propose source-qualified mappings and codegen recipes. No truth from a proposer.
- **M2 differential oracle:** upstream HLL -> generated ASP -> Clingo, fixture comparison including all stable models where relevant.
- **M3 decision:** prefer bounded algebra/RelAlg/mask-risc polyfill if oracle parity, identity witnesses and economics justify. Otherwise retain solver boundary. Small Rust port is only a separate, explicitly approved residual decision.

## Hard boundaries

- This repo owns plans, evidence inventories, normalized fixture expectations and admission decisions. Python AST/codegen stays with Ruff; OGAR owns existing facts/IR; lance-graph owns algebra/CE64/Epi5; ndarray owns SIMD.
- Never allocate new CE64 bit ranges, invent Epi5 state codes, or equate taxonomy/inheritance with causal Pearl3 evidence.
- Source agreement, copied derivations and endorsements do not automatically constitute independent evidence. Separate proposer, derivation, oracle and proof witness identities.
- Preserve Open World / Closed World / explicit negation / negation-as-failure distinctions. A general ASP program is not assumed compilable to monotonic bitmask algebra.
- WORLD remains sealed, THOUGHT sparse. No mutable ANGLE and no duplicated 64-world materialization.
- No duplicate relation/value store, no new planner or engine without an explicit admitted gap. Prefer **position-and-order folds over existing substrate**, including stale version refusal.
- No unsourced correctness/performance claims. Cite exact source path/line, revision, test and comparison result.
- No wholesale upstream code or corpus copies. Observe upstream Apache-2.0, NOTICES, trademark and translation-specific rights; respect the halachic context and keep reference outputs domain-neutral where possible.
- No production implementation, branch merge, automatic cross-repo changes, or source port in M0.

## Communication between sessions

For each new finding write `Claim | Source ref+revision | Proposed target owner | Exact evidence | Falsifier | Status | Next action`.
Allowed status words: `source-verified`, `hypothesis`, `proposer-only`, `oracle-confirmed`, `admitted`, `excluded`, `deferred`.
Consult available Linear ownership/board messages before claiming another session's work; use established claimed-vs-claiming convention and avoid duplicating open work. EXO-50 is an example coordination reference, not authority to edit it.

Do not say `proved` unless the checked theorem and snapshot bridge support precisely the stated proposition. A passing Ruff lint or Clingo run is not Lean proof. Reference the upstream claim ledger's `repair_note` when propositions narrow.

## Suggested session start prompt

> Rebase/read `mistaber-rs` main and the latest docs PR, then pin current BrainyBlaze/mistaber and AdaWorldAPI/ruff source revisions. Run a read-only Ruff AST harvester coverage reconnaissance over Mistaber's parser, checker, emitter and world rules. Produce a source-qualified proposal inventory and identify only the minimal gaps in the existing harvester. Keep all claims separate from Clingo/Lean evidence; do not write production code. Report closed ends, loose ends, one falsifier and the smallest next admission gate.
