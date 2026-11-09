from backend.services.analyzer import analyze_text
from backend.services.rules import RULES


def test_every_rule_example_matches_expected_behavior() -> None:
    for rule in RULES:
        for example in rule.examples_positive:
            matches = [
                finding
                for finding in analyze_text(example)
                if finding.id.startswith(f"{rule.id}-") or finding.title == rule.title
            ]
            assert matches, f"Positive example did not trigger rule {rule.id}: {example}"

        for example in rule.examples_negative:
            matches = [
                finding
                for finding in analyze_text(example)
                if finding.id.startswith(f"{rule.id}-") or finding.title == rule.title
            ]
            assert not matches, f"Negative example unexpectedly triggered rule {rule.id}: {example}"
