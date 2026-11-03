from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import joblib

from backend.services.errors import ModelUnavailableError

logger = logging.getLogger(__name__)


class CasePredictor:
    def __init__(self, model_path: str | Path | None = None) -> None:
        configured_path = (
            model_path
            or os.getenv("CASE_MODEL_PATH")
            or os.getenv("ML_MODEL_PATH")
            or "backend/ml/models/case_outcome_model.joblib"
        )
        self.model_path = Path(
            configured_path
        )
        self._model: Any | None = None

    @property
    def is_available(self) -> bool:
        return self._model is not None

    def load(self) -> None:
        if not self.model_path.is_file():
            self._model = None
            logger.warning("Case prediction model is not provisioned at %s", self.model_path)
            return
        model = joblib.load(self.model_path)
        if not callable(getattr(model, "predict_proba", None)):
            raise ValueError("The configured case model must implement predict_proba().")
        self._model = model
        logger.info("Loaded case prediction model from %s", self.model_path)

    def predict(self, features: dict[str, float]) -> tuple[list[str], list[float]]:
        if self._model is None:
            raise ModelUnavailableError(
                "Case prediction is unavailable until a trusted model artifact is installed."
            )

        model_features = getattr(self._model, "feature_names_in_", None)
        if model_features is not None:
            feature_names = [str(name) for name in model_features]
            if set(features) != set(feature_names):
                raise ValueError("Feature names must exactly match the trained model schema.")
        else:
            feature_names = sorted(features)

        ordered_values = [features[name] for name in feature_names]
        raw_probabilities = self._model.predict_proba([ordered_values])[0]
        classes = getattr(self._model, "classes_", range(len(raw_probabilities)))
        return (
            [str(value) for value in classes],
            [float(value) for value in raw_probabilities],
        )


case_predictor = CasePredictor()
