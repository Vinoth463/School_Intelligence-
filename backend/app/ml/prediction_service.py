
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

CATEGORICAL_FEATURES = [
    "class_grade",
]

REQUIRED_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def get_risk_category(score: float) -> str:
    """
    Categorize model scores using validation-derived thresholds.

    These categories are operational decision-support labels,
    not calibrated probability ranges.
    """

    thresholds = metadata["risk_category_thresholds"]

    low_upper_bound = float(
        thresholds["low_upper_bound"]
    )

    high_lower_bound = float(
        thresholds["high_lower_bound"]
    )

    if low_upper_bound >= high_lower_bound:
        raise ValueError(
            "Invalid risk category thresholds in model metadata."
        )

    if score < low_upper_bound:
        return "low"

    if score < high_lower_bound:
        return "medium"

    return "high"


def get_risk_indicators(features: dict) -> list[str]:
    """Return concerning historical academic observations."""

    indicators = []

    previous_score = features["previous_exam_percentage"]
    historical_average = features[
        "historical_average_percentage"
    ]

    if previous_score < 40:
        indicators.append(
            f"Previous examination percentage is below "
            f"40% ({previous_score:.2f}%)."
        )

    if historical_average < 40:
        indicators.append(
            f"Historical average is below 40% "
            f"({historical_average:.2f}%)."
        )

    marks_trend = features["marks_trend"]

    if marks_trend is not None and marks_trend < 0:
        indicators.append(
            f"Marks declined by {abs(marks_trend):.2f} "
            "percentage points compared with the previous exam."
        )

    attendance_percentage = features["attendance_percentage"]

    if (
        attendance_percentage is not None
        and attendance_percentage < 75
    ):
        indicators.append(
            f"Historical subject attendance is below 75% "
            f"({attendance_percentage:.2f}%)."
        )

    attendance_trend = features["attendance_trend"]

    if attendance_trend is not None and attendance_trend < 0:
        indicators.append(
            "Attendance declined during the recent "
            "60-day period compared with the previous 60 days."
        )

    return indicators


def get_positive_indicators(features: dict) -> list[str]:
    """Return positive historical academic observations."""

    indicators = []

    previous_score = features["previous_exam_percentage"]
    historical_average = features[
        "historical_average_percentage"
    ]

    if previous_score >= 40:
        indicators.append(
            f"Previous examination percentage is at least 40% "
            f"({previous_score:.2f}%)."
        )

    if previous_score > historical_average:
        indicators.append(
            "Previous examination performance is above "
            "the student's historical average."
        )

    marks_trend = features["marks_trend"]

    if marks_trend is not None and marks_trend > 0:
        indicators.append(
            f"Marks improved by {marks_trend:.2f} "
            "percentage points compared with the previous exam."
        )

    attendance_percentage = features["attendance_percentage"]

    if (
        attendance_percentage is not None
        and attendance_percentage >= 75
    ):
        indicators.append(
            f"Historical subject attendance is at least 75% "
            f"({attendance_percentage:.2f}%)."
        )

    attendance_trend = features["attendance_trend"]

    if attendance_trend is not None and attendance_trend > 0:
        indicators.append(
            "Attendance improved during the recent "
            "60-day period compared with the previous 60 days."
        )

    return indicators


def get_data_sufficiency(features: dict) -> dict:
    """
    Describe the availability of historical prediction data.

    Operational rule:
    - At least two historical exam records.
    - At least one historical attendance session.

    This is a data-availability check, not a statistical
    guarantee that the prediction is reliable.
    """

    warnings = []

    exam_count = features["previous_exam_count"]

    attendance_sessions = features[
        "attendance_sessions_to_date"
    ]

    if exam_count < 2:
        warnings.append(
            "Fewer than two historical examination records "
            "are available."
        )

    if attendance_sessions == 0:
        warnings.append(
            "No historical subject attendance records "
            "are available."
        )

    if features["attendance_percentage"] is None:
        warnings.append(
            "Historical attendance percentage is unavailable."
        )

    if warnings:
        status = "limited"
    else:
        status = "more_complete"

    return {
        "data_sufficiency_status": status,
        "data_sufficiency_warnings": warnings,
        "historical_examination_count": exam_count,
        "historical_attendance_sessions": attendance_sessions,
    }


def predict_underperformance(features: dict) -> dict:
    """
    Predict whether a student may underperform in the next exam.

    Missing numerical values are handled by the trained
    preprocessing pipeline's numerical imputer.
    """

    if not isinstance(features, dict):
        raise ValueError(
            "Features must be provided as a dictionary."
        )

    missing_features = [
        feature
        for feature in REQUIRED_FEATURES
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    input_data = pd.DataFrame(
        [
            {
                feature: features[feature]
                for feature in REQUIRED_FEATURES
            }
        ]
    )

    # Validate numerical features.
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
        raise ValueError(
            "class_grade cannot be missing."
        )

    if not isinstance(class_grade, str) or not class_grade.strip():
        raise ValueError(
            "class_grade must be a non-empty string."
        )

    input_data.at[0, "class_grade"] = class_grade.strip()

    probabilities = model.predict_proba(input_data)[0]

    positive_class_index = list(
        model.named_steps["classifier"].classes_
    ).index(1)

    underperformance_score = float(
        probabilities[positive_class_index]
    )

    classification_threshold = float(
        metadata["classification_probability_threshold"]
    )

    if not 0.0 <= classification_threshold <= 1.0:
        raise ValueError(
            "Invalid classification threshold in model metadata."
        )

    prediction = int(
        underperformance_score >= classification_threshold
    )

    academic_threshold = float(
        metadata["underperformance_threshold"]
    )

    risk_category = get_risk_category(
        underperformance_score
    )

    risk_indicators = get_risk_indicators(features)

    positive_indicators = get_positive_indicators(features)

    data_sufficiency = get_data_sufficiency(features)

    return {
        "predicted_underperformance": bool(prediction),

        "underperformance_score": round(
            underperformance_score, 4
        ),

        "score_interpretation": (
            "Uncalibrated Random Forest model score. "
            "It is not a guaranteed probability of "
            "academic underperformance."
        ),

        "classification_threshold": classification_threshold,

        "academic_marks_threshold": academic_threshold,

        "risk_category": risk_category,

        "risk_indicators": risk_indicators,

        "positive_indicators": positive_indicators,

        **data_sufficiency,

        "model_name": metadata["model_name"],

        "prediction_type": "next_exam_underperformance",

        "data_type": metadata["data_type"],
    }
