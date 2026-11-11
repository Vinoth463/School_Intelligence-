
import pandas as pd

from app.ml.model_loader import model, metadata


# Exact feature names used during model training.
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

CATEGORICAL_FEATURES = [
    "class_grade",
]

REQUIRED_FEATURES = (
    NUMERIC_FEATURES + CATEGORICAL_FEATURES
)


def predict_underperformance(features: dict) -> dict:
    """
    Predict whether a student may score below the
    academic threshold in the next examination.

    Input features must be calculated from historical
    information available before the target examination.
    """

    missing_features = [
        feature
        for feature in REQUIRED_FEATURES
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    # Build a DataFrame with the exact trained feature schema.
    input_data = pd.DataFrame(
        [
            {
                feature: features[feature]
                for feature in REQUIRED_FEATURES
            }
        ]
    )

    # Validate numeric values.
    for feature in NUMERIC_FEATURES:
        value = input_data.at[0, feature]

        if pd.isna(value):
            raise ValueError(
                f"Feature '{feature}' cannot be missing."
            )

        try:
            input_data[feature] = pd.to_numeric(
                input_data[feature],
                errors="raise"
            )
        except (ValueError, TypeError):
            raise ValueError(
                f"Feature '{feature}' must be numeric."
            )

    # Validate categorical value.
    if pd.isna(input_data.at[0, "class_grade"]):
        raise ValueError("class_grade cannot be missing.")

    # Generate prediction.
    prediction = int(model.predict(input_data)[0])

    # Obtain model probability for the underperformance class.
    probabilities = model.predict_proba(input_data)[0]

    positive_class_index = list(
        model.named_steps["classifier"].classes_
    ).index(1)

    underperformance_score = float(
        probabilities[positive_class_index]
    )

    probability_threshold = metadata[
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
        "classification_threshold": probability_threshold,
        "academic_marks_threshold": academic_threshold,
        "model_name": metadata["model_name"],
        "prediction_type": "next_exam_underperformance",
        "data_type": metadata["data_type"],
    }
