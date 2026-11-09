from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _last_day_of_month(day: date) -> date:
    if day.month == 12:
        return date(day.year + 1, 1, 1) - timedelta(days=1)
    return date(day.year, day.month + 1, 1) - timedelta(days=1)


def calculate_msme_interest(
    amount: Decimal,
    acceptance_date: date,
    has_written_payment_period: bool,
    written_payment_period_days: int | None,
    payment_date: date,
    bank_rate_percent: Decimal,
) -> tuple[str, int, int, Decimal, list[dict[str, object]]]:
    if has_written_payment_period and written_payment_period_days is not None:
        days_allowed = min(int(written_payment_period_days), 45)
    else:
        days_allowed = 15

    due_date = acceptance_date + timedelta(days=days_allowed)
    if payment_date <= due_date:
        return due_date.isoformat(), days_allowed, 0, Decimal("0"), []

    days_delayed = (payment_date - due_date).days
    monthly_rate = (Decimal(3) * bank_rate_percent / Decimal("100")) / Decimal(12)
    balance = amount
    breakdown: list[dict[str, object]] = []
    month_start = due_date
    month_index = 1

    while month_start < payment_date:
        month_end = min(_last_day_of_month(month_start), payment_date)
        days_in_period = (month_end - month_start).days + 1
        fraction = Decimal(days_in_period) / Decimal(30)
        interest = balance * monthly_rate * fraction
        balance += interest
        breakdown.append({
            "month_label": f"Month {month_index}",
            "days_in_month": days_in_period,
            "interest": float(_quantize(interest)),
            "ending_balance": float(_quantize(balance)),
        })
        month_start = month_end + timedelta(days=1)
        month_index += 1

    total_interest = _quantize(balance - amount)
    return due_date.isoformat(), days_allowed, days_delayed, total_interest, breakdown
