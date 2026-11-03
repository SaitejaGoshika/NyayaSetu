import pytest

from backend.services.analyzer import analyze_text
from backend.services.errors import ExtractionError
from backend.services.extractor import extract_text


def test_flags_payment_terms_beyond_msmE_outer_limit() -> None:
    findings = analyze_text("The buyer shall make payment within 60 days of invoice receipt.")

    assert len(findings) == 1
    assert findings[0].risk_level.value == "high"
    assert "45 days" in findings[0].explanation


@pytest.mark.parametrize(
    "text",
    [
        "Payment is due 60 days after acceptance.",
        "Payments will be made no later than 60 calendar days after delivery.",
        "Payment shall be made within 45 days, but may be extended to 60 days by agreement.",
        "The invoice is payable in sixty days from receipt.",
    ],
)
def test_flags_common_payment_period_wordings(text: str) -> None:
    findings = analyze_text(text)

    assert findings
    assert findings[0].risk_level.value == "high"
    assert "45 days" in findings[0].explanation


def test_does_not_flag_payment_period_of_exactly_45_days() -> None:
    findings = analyze_text("Payment is due within 45 working days from acceptance.")

    assert not findings


def test_flags_exit_cost_and_gst_reference() -> None:
    findings = analyze_text("A 12-month lock-in period applies. Supplier will issue a GST tax invoice.")

    assert [finding.risk_level.value for finding in findings] == ["medium", "low"]


def test_unsupported_extraction_type_is_typed_415() -> None:
    try:
        extract_text("missing.txt", ".txt")
    except ExtractionError as error:
        assert error.status_code == 415
        assert error.code == "unsupported_media_type"
    else:
        raise AssertionError("Expected unsupported file type to be rejected")
