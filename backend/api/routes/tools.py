from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from backend.models.schemas import MsmeInterestRequest, MsmeInterestResponse
from backend.services.msme_interest import calculate_msme_interest

router = APIRouter(prefix="/api")


@router.post("/tools/msme-interest", response_model=MsmeInterestResponse)
def calculate_msme_tool(payload: MsmeInterestRequest) -> MsmeInterestResponse:
    try:
        acceptance = date.fromisoformat(payload.acceptance_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_date", "message": "acceptance_date must be an ISO date."}) from exc

    payment_day = payload.payment_date or payload.as_of_date
    if payment_day is None:
        raise HTTPException(status_code=400, detail={"code": "missing_payment_date", "message": "Provide payment_date or as_of_date."})

    try:
        payment_date = date.fromisoformat(payment_day)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "invalid_date", "message": "payment_date or as_of_date must be an ISO date."}) from exc

    due_date, days_allowed, days_delayed, total_interest, breakdown = calculate_msme_interest(
        amount=Decimal(str(payload.amount)),
        acceptance_date=acceptance,
        has_written_payment_period=payload.has_written_payment_period,
        written_payment_period_days=payload.written_payment_period_days,
        payment_date=payment_date,
        bank_rate_percent=Decimal(str(payload.bank_rate_percent)),
    )

    return MsmeInterestResponse(
        due_date=due_date,
        payment_due_days=days_allowed,
        days_delayed=days_delayed,
        total_interest=float(total_interest),
        monthly_breakdown=[
            {
                "month_label": item["month_label"],
                "days_in_month": item["days_in_month"],
                "interest": item["interest"],
                "ending_balance": item["ending_balance"],
            }
            for item in breakdown
        ],
    )
