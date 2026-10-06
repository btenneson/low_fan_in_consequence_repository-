#!/usr/bin/env python3
"""Regenerate the machine-readable Low-Fan-In repository from the original PDF.

The original publication remains the source of truth. This script intentionally
does not infer missing verifier metadata or alternative supports.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SOURCE_URL = (
    "https://raw.githubusercontent.com/btenneson/pub/main/"
    "cs.LO_Logic_in_Computer_Science/"
    "low_fan_in_consequence_repository_strength_ordered_0_2/"
    "Low_Fan_In_Consequence_Repository_Strength_Ordered_0_2.pdf"
)
SOURCE_PUBLICATION_URL = (
    "https://btenneson.github.io/pub/cs.LO_Logic_in_Computer_Science/"
    "low_fan_in_consequence_repository_strength_ordered_0_2/"
)
SOURCE_TITLE = (
    "A Low-Fan-In Consequence Repository — Derived from Depths of Induction "
    "and Formalized Self-Awareness"
)
SOURCE_EDITION = "Strength-Ordered Consolidated Edition 0.2"


def clean_text(value: str) -> str:
    value = re.sub(
        r"\n\s*Band [A-D]\s*[-–].*?(?=\n\s*Entries \d+-\d+ of 182|\Z)",
        "\n",
        value,
        flags=re.S,
    )
    value = re.sub(
        r"\n\s*Entries \d+-\d+ of 182.*?(?=\n\d{1,3}\.\s+LF-|\Z)",
        "\n",
        value,
        flags=re.S,
    )
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_source(text: str) -> list[dict]:
    text = (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\x0c", "\n")
        .replace("\x02", "")
    )
    text = re.sub(
        r"^\s*Low-Fan-In Consequence Repository\s*[–-]\s*"
        r"Strength-Ordered Edition 0\.2\s*\|\s*\d+\s*$",
        "",
        text,
        flags=re.M,
    )

    start_pattern = re.compile(
        r"(?m)^\s*(\d{1,3})\.\s+(LF-[A-Za-z0-9.]+)\.\s+(.+?)\s*$"
    )
    starts = list(start_pattern.finditer(text))
    if len(starts) != 182:
        raise RuntimeError(f"Expected 182 theorem headers; found {len(starts)}")

    appendix = text.find("Appendix: source-volume provenance")
    if appendix < 0:
        appendix = len(text)

    records: list[dict] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else appendix
        chunk = text[match.end() : end]
        theorem_id = match.group(2)

        signature_pattern = re.compile(
            re.escape(theorem_id)
            + r"\s*\|\s*Src:\s*(.*?)"
            + r"\s*\|\s*Par:\s*\{(.*?)\}"
            + r"\s*\|\s*f:\s*(\d+)"
            + r"\s*\|\s*Hyp:\s*(.*?)"
            + r"\s*\|\s*Stat:\s*([A-Z])"
            + r"\s*\|\s*Use:\s*(.*?)(?=\bStatement\.)",
            re.S,
        )
        signature = signature_pattern.search(chunk)
        statement = re.search(r"\bStatement\.\s*(.*?)(?=\bProof\.)", chunk, re.S)
        proof = re.search(r"\bProof\.\s*(.*)$", chunk, re.S)

        if not signature or not statement or not proof:
            raise RuntimeError(f"Could not parse complete entry {theorem_id}")

        parents_raw = clean_text(signature.group(2))
        parent_theorem_ids = list(
            dict.fromkeys(re.findall(r"LF-[A-Za-z0-9.]+", parents_raw))
        )

        records.append(
            {
                "id": theorem_id,
                "catalogue_number": int(match.group(1)),
                "title": clean_text(match.group(3)),
                "statement": clean_text(statement.group(1)),
                "hypotheses": clean_text(signature.group(4)),
                "proof": clean_text(proof.group(1)),
                "status": signature.group(5).strip(),
                "displayed_fan_in": int(signature.group(3)),
                "intended_use": clean_text(signature.group(6)),
                "source": clean_text(signature.group(1)),
                "parents_displayed_raw": parents_raw,
                "parent_theorem_ids": parent_theorem_ids,
                "support_semantics": "conjunctive_displayed_parent_set",
                "source_edition": SOURCE_EDITION,
                "machine_verified_in_this_repository": False,
                "extraction_source": "original published PDF text",
            }
        )

    if [r["catalogue_number"] for r in records] != list(range(1, 183)):
        raise RuntimeError("Catalogue numbering is not exactly 1..182")
    if len({r["id"] for r in records}) != 182:
        raise RuntimeError("Theorem IDs are not unique")

    distribution = Counter(r["displayed_fan_in"] for r in records)
    required = Counter({0: 34, 1: 131, 2: 17})
    if distribution != required:
        raise RuntimeError(
            f"Fan-in distribution mismatch: {dict(distribution)} != {dict(required)}"
        )
    return records


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"))
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )


def make_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Low-Fan-In Consequence Repository machine-readable schema",
        "description": (
            "Definitions for theorem, conjunctive support-hyperedge, and "
            "provenance records extracted from Strength-Ordered Consolidated Edition 0.2."
        ),
        "$defs": {
            "theorem": {
                "type": "object",
                "required": [
                    "id",
                    "catalogue_number",
                    "title",
                    "statement",
                    "hypotheses",
                    "proof",
                    "status",
                    "displayed_fan_in",
                    "source",
                    "parents_displayed_raw",
                    "support_semantics",
                ],
                "properties": {
                    "id": {"type": "string", "pattern": "^LF-"},
                    "catalogue_number": {"type": "integer", "minimum": 1},
                    "title": {"type": "string"},
                    "statement": {"type": "string"},
                    "hypotheses": {"type": "string"},
                    "proof": {"type": "string"},
                    "status": {"type": "string"},
                    "displayed_fan_in": {"type": "integer", "minimum": 0},
                    "intended_use": {"type": "string"},
                    "source": {"type": "string"},
                    "parents_displayed_raw": {"type": "string"},
                    "parent_theorem_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "support_semantics": {
                        "const": "conjunctive_displayed_parent_set"
                    },
                    "source_edition": {"type": "string"},
                    "machine_verified_in_this_repository": {"type": "boolean"},
                    "extraction_source": {"type": "string"},
                },
            },
            "support": {
                "type": "object",
                "required": [
                    "support_id",
                    "target_theorem_id",
                    "conjunctive",
                    "displayed_fan_in",
                    "parents_displayed_raw",
                    "certificate",
                ],
                "properties": {
                    "support_id": {"type": "string"},
                    "target_theorem_id": {"type": "string"},
                    "conjunctive": {"const": True},
                    "displayed_fan_in": {"type": "integer", "minimum": 0},
                    "parents_displayed_raw": {"type": "string"},
                    "parent_theorem_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "external_or_source_support_present": {"type": "boolean"},
                    "certificate": {"type": "object"},
                    "support_closed_machine_check": {"type": "string"},
                },
            },
            "provenance": {
                "type": "object",
                "required": [
                    "theorem_id",
                    "catalogue_number",
                    "source",
                    "hypotheses",
                    "status",
                    "source_edition",
                ],
                "properties": {
                    "theorem_id": {"type": "string"},
                    "catalogue_number": {"type": "integer"},
                    "source": {"type": "string"},
                    "hypotheses": {"type": "string"},
                    "status": {"type": "string"},
                    "intended_use": {"type": "string"},
                    "source_edition": {"type": "string"},
                    "source_object_title": {"type": "string"},
                    "source_object_url": {"type": "string", "format": "uri"},
                },
            },
        },
    }


def build(records: list[dict]) -> None:
    theorems = records
    supports = []
    provenance = []

    for record in records:
        supports.append(
            {
                "support_id": f"SUPPORT:{record['id']}:displayed-1",
                "target_theorem_id": record["id"],
                "conjunctive": True,
                "displayed_fan_in": record["displayed_fan_in"],
                "parents_displayed_raw": record["parents_displayed_raw"],
                "parent_theorem_ids": record["parent_theorem_ids"],
                "external_or_source_support_present": (
                    bool(record["parents_displayed_raw"])
                    and len(record["parent_theorem_ids"])
                    < record["displayed_fan_in"]
                ),
                "certificate": {
                    "kind": "written_proof_text",
                    "proof_text": record["proof"],
                    "catalogue_status": record["status"],
                    "machine_verifier": None,
                },
                "support_closed_machine_check": "not_yet_encoded",
            }
        )

        provenance.append(
            {
                "theorem_id": record["id"],
                "catalogue_number": record["catalogue_number"],
                "source": record["source"],
                "hypotheses": record["hypotheses"],
                "status": record["status"],
                "intended_use": record["intended_use"],
                "source_edition": SOURCE_EDITION,
                "source_object_title": SOURCE_TITLE,
                "source_object_url": SOURCE_PUBLICATION_URL,
            }
        )

    write_jsonl(ROOT / "theorems.jsonl", theorems)
    write_jsonl(ROOT / "supports.jsonl", supports)
    write_jsonl(ROOT / "provenance.jsonl", provenance)
    (ROOT / "repository.schema.json").write_text(
        json.dumps(make_schema(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pdf = tmp / "source.pdf"
        text = tmp / "source.txt"

        print(f"Downloading source: {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, pdf)
        subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(text)],
            check=True,
        )
        records = parse_source(text.read_text(encoding="utf-8", errors="replace"))
        build(records)

    distribution = Counter(r["displayed_fan_in"] for r in records)
    print(f"theorems: {len(records)}")
    print(f"fan-in: {dict(sorted(distribution.items()))}")
    print("build: PASS")


if __name__ == "__main__":
    main()
