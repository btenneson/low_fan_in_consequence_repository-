#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "repository_hypergraph.dot"

def read_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

theorems = {t["id"]: t for t in read_jsonl(ROOT / "theorems.jsonl")}
supports = read_jsonl(ROOT / "supports.jsonl")

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

lines = [
    "digraph LowFanInSupportHypergraph {",
    "  rankdir=LR;",
    '  node [fontname="Helvetica"];'
]

for tid in theorems:
    lines.append(f"  {q('T:'+tid)} [shape=box,label={q(tid)}];")

for support in supports:
    sid = support["support_id"]
    target = support["target_theorem_id"]
    lines.append(f'  {q(sid)} [shape=circle,label="AND",width=0.35,height=0.35,fixedsize=true];')
    lines.append(f"  {q(sid)} -> {q('T:'+target)};")

    parent_ids = support.get("parent_theorem_ids", [])
    for pid in parent_ids:
        if pid in theorems:
            lines.append(f"  {q('T:'+pid)} -> {q(sid)};")
        else:
            ext = "EXT:" + pid
            lines.append(f"  {q(ext)} [shape=note,label={q(pid)}];")
            lines.append(f"  {q(ext)} -> {q(sid)};")

    raw = support.get("parents_displayed_raw", "").strip()
    if raw and not parent_ids:
        ext = "EXTSUP:" + target
        label = raw if len(raw) <= 120 else raw[:117] + "..."
        lines.append(f"  {q(ext)} [shape=note,label={q(label)}];")
        lines.append(f"  {q(ext)} -> {q(sid)};")

lines.append("}")
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUT)
