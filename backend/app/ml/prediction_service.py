
import math

import pandas as pd

from app.ml.model_loader import model, metadata


# Exact numerical features used during model training.
NUMERIC_FEATURES = [
    "previous_exam_percentage",
    "historical_average_percentage",
    "marks_trend",
    "previous_exam_count",
    "attendance_percentage",
    "attendance_recent_60d",
    "attendance_previous_60d",
    "attendance_trend",
    "attendance_sessions_to_date",
]

# Exact categorical features used during model training.
CATEGORICAL_FEATURES = [
    "class_grade",
]

REQUIRED_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def predict_underperformance(features: dict) -> dict:
    """
    Predict whether a student may underperform in the next exam.

    All input features must come from information available
    before the target examination.

    Missing numerical values are passed to the trained
    preprocessing pipeline, which handles imputation.
    """

    if not isinstance(features, dict):
        raise ValueError("Features must be provided as a dictionary.")

    # Check that all trained features are supplied.
    missing_features = [
        feature
        for feature in REQUIRED_FEATURES
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Build input using the exact training feature schema.
    input_data = pd.DataFrame(
        [
            {
                feature: features[feature]
                for feature in REQUIRED_FEATURES
            }
        ]
    )

    # Validate numerical features.
    # NaN values are allowed because the trained pipeline
    # contains a numerical imputer.
    for feature in NUMERIC_FEATURES:
        try:
            value = pd.to_numeric(
                pd.Series([features[feature]]),
                errors="raise"
            ).iloc[0]

        except (ValueError, TypeError):
            raise ValueError(
                f"Feature '{feature}' must be numeric or missing."
            )

        if pd.isna(value):
            input_data.at[0, feature] = float("nan")
            continue

        if not math.isfinite(float(value)):
            raise ValueError(
                f"Feature '{feature}' must be a finite number."
            )

        input_data.at[0, feature] = float(value)

    # Validate categorical feature.
    class_grade = features["class_grade"]

    if pd.isna(class_grade):
        raise ValueError("class_grade cannot be missing.")

    if not isinstance(class_grade, str) or not class_grade.strip():
        raise ValueError("class_grade must be a non-empty string.")

    input_data.at[0, "class_grade"] = class_grade.strip()

    # Generate prediction using the complete trained pipeline.
    prediction = int(model.predict(input_data)[0])

    # Get the model score for the underperformance class.
    probabilities = model.predict_proba(input_data)[0]

    positive_class_index = list(
        model.named_steps["classifier"].classes_
    ).index(1)

    underperformance_score = float(
        probabilities[positive_class_index]
    )

    classification_threshold = metadata[
        "classification_probability_threshold"
    ]

    academic_threshold = metadata[
        "underperformance_threshold"
    ]

    return {
        "predicted_underperformance": bool(prediction),
        "underperformance_score": round(
            underperformance_score, 4
        ),
        "score_interpretation": (
            "Uncalibrated model score; not a guaranteed "
            "probability of academic underperformance."
        ),
        "classification_threshold": classification_threshold,
        "academic_marks_threshold": academic_threshold,
        "model_name": metadata["model_name"],
        "prediction_type": "next_exam_underperformance",
        "data_type": metadata["data_type"],
    }
