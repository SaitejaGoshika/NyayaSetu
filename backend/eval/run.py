from __future__ import annotations

import json
from pathlib import Path

from backend.services.analyzer import analyze_text
from backend.services.rules import RULES

DATASET_PATH = Path(__file__).resolve().parent / "dataset.jsonl"
REPORT_PATH = Path(__file__).resolve().parent / "REPORT.md"


def _matches_rule(text: str, rule_id: str) -> bool:
    findings = analyze_text(text)
    return any(finding.id.startswith(f"{rule_id}-") or finding.title == next((r.title for r in RULES if r.id == rule_id), "") for finding in findings)


def _metrics_for_rule(rule_id: str, rows: list[dict[str, str]]) -> dict[str, float | int]:
    tp = fp = fn = 0
    for row in rows:
        expected = row["label"] == rule_id
        predicted = _matches_rule(row["text"], rule_id)
        if expected and predicted:
            tp += 1
        elif (not expected) and predicted:
            fp += 1
        elif expected and (not predicted):
            fn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def main() -> None:
    rows = []
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    provenance_counts = {}
    for row in rows:
        provenance_counts[row.get("provenance", "unknown")] = provenance_counts.get(row.get("provenance", "unknown"), 0) + 1

    lines = [
        "# NyayaSetu evaluation report",
        "",
        "Synthetic evaluation is only a regression check and is not a real-world accuracy claim.",
        "",
        f"Dataset size: {len(rows)}",
        "",
        "## Provenance counts",
    ]
    for name, count in sorted(provenance_counts.items()):
        lines.append(f"- {name}: {count}")

    lines.extend(["", "## Rule metrics", "", "| Rule | Precision | Recall | F1 | TP | FP | FN |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for rule in RULES:
        metrics = _metrics_for_rule(rule.id, rows)
        lines.append(f"| {rule.id} | {metrics['precision']:.3f} | {metrics['recall']:.3f} | {metrics['f1']:.3f} | {metrics['tp']} | {metrics['fp']} | {metrics['fn']} |")

    lines.extend([
        "",
        "The evaluation data is intentionally synthetic and was written to test regression coverage and example behavior only. Real public contract data will be added later for a more meaningful accuracy estimate.",
    ])

    report = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
