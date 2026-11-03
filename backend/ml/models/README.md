# Case prediction model

Place a trusted scikit-learn estimator with a `predict_proba()` method at `case_outcome_model.joblib`, or set `CASE_MODEL_PATH` to an approved artifact path. The default path is configured in `backend/ml/predictor.py`.

The estimator's `feature_names_in_`, when present, must match the JSON `features` keys exactly. If it is absent, values are passed in sorted key order. Train and validate the model on representative, lawfully sourced, appropriately de-identified data; record the feature schema, label definitions, calibration, evaluation, and review date alongside the artifact. Never load an artifact from an untrusted source: joblib deserialization can execute code.
