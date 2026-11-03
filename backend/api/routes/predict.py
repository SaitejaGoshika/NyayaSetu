from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.ml.predictor import case_predictor
from backend.models.schemas import CasePredictRequest, CasePredictResponse, CasePredictStatus
from backend.services.errors import ModelUnavailableError

router = APIRouter(prefix="/api")


@router.get("/predict/status", response_model=CasePredictStatus)
def prediction_status() -> CasePredictStatus:
    if not case_predictor.is_available:
        return CasePredictStatus(
            available=False,
            message=(
                "No approved case prediction model is installed. Provision a validated "
                "model at the configured model path before requesting estimates."
            ),
        )
    return CasePredictStatus(available=True, message="The configured case prediction model is ready.")


@router.post(
    "/predict",
    response_model=CasePredictResponse,
    responses={
        401: {"description": "Invalid or missing local session"},
        422: {"description": "Invalid feature payload or model schema mismatch"},
        503: {"description": "Model is not provisioned"},
    },
)
def predict_case(
    request: CasePredictRequest,
) -> CasePredictResponse:
    try:
        classes, probabilities = case_predictor.predict(request.features)
    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "model_unavailable", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_features", "message": str(exc)},
        ) from exc
    return CasePredictResponse(classes=classes, probabilities=probabilities)
