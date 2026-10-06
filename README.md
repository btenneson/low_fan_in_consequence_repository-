# Low-Fan-In Consequence Repository

Machine-readable proof-infrastructure representation of the original publication:

**A Low-Fan-In Consequence Repository — Derived from Depths of Induction and Formalized Self-Awareness, Strength-Ordered Consolidated Edition 0.2**

Source publication:

https://btenneson.github.io/pub/cs.LO_Logic_in_Computer_Science/low_fan_in_consequence_repository_strength_ordered_0_2/

## Source-first contract

The repository is generated from the original 182-entry Strength-Ordered Edition 0.2 text, not reconstructed from a later summary.

The source provides stable theorem IDs, theorem statements, displayed parent sets, displayed theorem-level fan-in, hypotheses, catalogue status, provenance, intended use, and written proofs.

This repository does **not** claim that the imported written proofs have been independently machine-verified here. `machine_verified_in_this_repository` therefore remains `false` until a concrete verifier/certificate layer is added.

## Why support is represented as a hyperedge

If a theorem has displayed support

```text
{A, B} => T
```

the parent set is conjunctive: the parents jointly support one certificate for `T`.

Accordingly, `supports.jsonl` stores each displayed parent set as one support object instead of pretending that `A -> T` and `B -> T` are independent proofs. This distinction is required for verifier-safe pruning.

## Published inventory

The build is required to reproduce exactly:

- theorem records: **182**
- displayed fan-in 0: **34**
- displayed fan-in 1: **131**
- displayed fan-in 2: **17**
- maximum displayed fan-in: **2**

The source edition treats `f` as displayed immediate theorem-parent count; it does not claim minimum possible fan-in.

## Generated files

- `theorems.jsonl` — one source-faithful theorem record per catalogue entry.
- `supports.jsonl` — one conjunctive displayed-support object per theorem.
- `provenance.jsonl` — source, hypotheses, status, and intended-use metadata.
- `repository.schema.json` — JSON Schema definitions.
- `repository_hypergraph.dot` — bipartite support-hypergraph export.

## Build and verification

- `scripts/build_from_source.py` downloads the original published PDF and regenerates the repository.
- `scripts/validate_repository.py` checks record counts, identities, support targets, and the published fan-in distribution.
- `scripts/export_graph.py` exports a bipartite Graphviz representation without collapsing conjunctive supports into ordinary theorem edges.

Run locally:

```bash
python scripts/build_from_source.py
python scripts/validate_repository.py
python scripts/export_graph.py
```

GitHub Actions runs the same build and validation from the original publication.

## Proof-infrastructure role

This is the source-faithful data layer for verifier-safe repository transformations such as:

- `MERGE`
- `PRUNE`
- `FACTOR`
- `SHORTCUT`

Machine-verifier fields not supplied by the original publication are deliberately left unresolved rather than invented.
