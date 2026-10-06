#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

theorems = read_jsonl(ROOT / "theorems.jsonl")
supports = read_jsonl(ROOT / "supports.jsonl")
provenance = read_jsonl(ROOT / "provenance.jsonl")

assert len(theorems) == 182, f"expected 182 theorems, got {len(theorems)}"
assert len(supports) == 182, f"expected 182 supports, got {len(supports)}"
assert len(provenance) == 182, f"expected 182 provenance records, got {len(provenance)}"

ids = [t["id"] for t in theorems]
assert len(set(ids)) == 182, "duplicate theorem IDs"
assert [t["catalogue_number"] for t in theorems] == list(range(1, 183)), "catalogue numbering is not 1..182"
idset = set(ids)

support_targets = [s["target_theorem_id"] for s in supports]
assert len(set(support_targets)) == 182, "duplicate support target"
assert set(support_targets) == idset, "support targets do not exactly match theorem IDs"

prov_ids = [p["theorem_id"] for p in provenance]
assert set(prov_ids) == idset, "provenance records do not exactly match theorem IDs"

dist = Counter(t["displayed_fan_in"] for t in theorems)
expected = Counter({0: 34, 1: 131, 2: 17})
assert dist == expected, f"fan-in distribution mismatch: {dict(dist)}"

for t in theorems:
    assert t["support_semantics"] == "conjunctive_displayed_parent_set"
    assert t["machine_verified_in_this_repository"] is False
    if t["displayed_fan_in"] == 0:
        assert t["parents_displayed_raw"].strip() == "", f"{t['id']}: f=0 but parent display is nonempty"
    else:
        assert t["parents_displayed_raw"].strip() != "", f"{t['id']}: f>0 but parent display is empty"

for s in supports:
    assert s["conjunctive"] is True
    assert s["certificate"]["kind"] == "written_proof_text"
    assert s["support_closed_machine_check"] == "not_yet_encoded"

print(f"theorems: {len(theorems)}")
print(f"supports: {len(supports)}")
print(f"fan-in: {dict(sorted(dist.items()))}")
print("validation: PASS")
