def test_msme_interest_calculator_returns_due_date_and_interest(client) -> None:
    response = client.post(
        "/api/tools/msme-interest",
        json={
            "amount": 100000,
            "acceptance_date": "2025-01-01",
            "has_written_payment_period": False,
            "payment_date": "2025-02-10",
            "bank_rate_percent": 6.5,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["dueDate"] == "2025-01-16"
    assert payload["daysDelayed"] == 25
    assert payload["totalInterest"] >= 0
    assert payload["monthlyBreakdown"]
