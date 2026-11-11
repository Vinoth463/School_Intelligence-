
from pathlib import Path
import json
import joblib


# Project root: E:\School Intelligence
PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml_artifacts"
    / "models"
    / "underperformance_model.joblib"
)

METADATA_PATH = (
    PROJECT_ROOT
    / "ml_artifacts"
    / "models"
    / "model_metadata.json"
)


def load_model():
    """Load the trained ML pipeline."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def load_metadata():
    """Load model evaluation and configuration metadata."""

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
        )

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# Load once when the module is imported.
model = load_model()
metadata = load_metadata()
