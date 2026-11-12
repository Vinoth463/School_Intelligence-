# Machine Learning Methodology – School Intelligence

## 1. Overview

The School Intelligence platform uses a supervised machine learning model to identify students who may underperform in their next examination.

The objective is to provide an early-warning decision-support system that helps teachers identify students who may need additional academic attention.

The model uses historical academic performance and attendance information to predict whether a student's percentage in the next examination will be below 40%.

**Prediction target:**

- Target variable: `underperformed_next_exam`
- Positive class: 1 – Next examination percentage is below 40%.
- Negative class: 0 – Next examination percentage is 40% or above.

The 40% threshold is an illustrative academic threshold used for this assignment.

## 2. Dataset Description

The model was trained using a synthetic academic dataset generated for the School Intelligence project.

The dataset contains:

- 200 students.
- 6 subjects.
- 6 examinations.
- 7,200 examination mark records.
- 52,800 attendance sessions.

The ML feature dataset contains 6,000 student-subject examination-transition records.

Each record represents a student's historical information before a target examination.

### Dataset construction

For every student-subject combination, historical examination information was used to generate features for the next examination.

The target variable was generated from the next examination percentage:

`underperformed_next_exam = 1 if target_percentage < 40 else 0`

The target examination marks were used only to create the training label, not as model input features.

## 3. Feature Engineering

Features were calculated using information available before the target examination.

### Numerical features

| Feature | Description |
|---|---|
| `previous_exam_percentage` | Percentage obtained in the latest completed examination |
| `historical_average_percentage` | Average percentage across available examinations up to the latest completed examination |
| `marks_trend` | Difference between the latest and previous examination percentages |
| `previous_exam_count` | Number of completed historical examinations |
| `attendance_percentage` | Overall attendance percentage up to the historical cutoff date |
| `attendance_recent_60d` | Attendance percentage during the recent 60-day window |
| `attendance_previous_60d` | Attendance percentage during the preceding 60-day window |
| `attendance_trend` | Difference between recent and previous 60-day attendance percentages |
| `attendance_sessions_to_date` | Number of attendance sessions available up to the cutoff date |

### Categorical feature

| Feature | Description |
|---|---|
| `class_grade` | Student's grade at the latest completed examination |

### Missing-value handling

Some historical features may be unavailable.

Examples include:

- Marks trend when only one historical examination is available.
- Attendance percentage when no historical attendance sessions exist.
- Recent or previous attendance windows when no sessions exist in those windows.
- Attendance trend when either attendance window is unavailable.

Missing numerical values are handled using `SimpleImputer` with median imputation and missing-value indicators.

Categorical values are processed using `OneHotEncoder` with `handle_unknown="ignore"`.

## 4. Data Leakage Prevention

The model must use only information available before the target examination.

The following fields are not used as model predictors:

- Student ID.
- Subject ID.
- Current examination ID.
- Current examination date.
- Target examination ID.
- Target examination date.
- Target examination percentage.
- Target variable.

Historical marks and attendance are restricted to the appropriate cutoff date.

The dataset was sorted chronologically before generating examination transitions.

## 5. Training, Validation and Testing Strategy

A chronological split was used based on the target examination.

This approach ensures that earlier examination transitions are used for training and later examinations are used for validation and testing.

| Dataset | Target examination IDs | Records |
|---|---|---:|
| Training | 2, 3, 4 | 3,600 |
| Validation | 5 | 1,200 |
| Testing | 6 | 1,200 |
| Total | 2–6 | 6,000 |

### Target distribution

| Dataset | Underperformance records | Other records |
|---|---:|---:|
| Training | 448 | 3,152 |
| Validation | 201 | 999 |
| Testing | 210 | 990 |

The same students appear across chronological splits. Therefore, this evaluation measures performance on later examinations for a known student cohort, not generalization to completely unseen students or schools.

## 6. Models Evaluated

Two classification models were trained.

### 6.1 Logistic Regression

Logistic Regression was used as the baseline classification model.

Configuration:

- Maximum iterations: 2,000.
- Class weighting: Balanced.
- Random state: 42.
- Numerical features: Median imputation and standard scaling.
- Categorical features: One-hot encoding.

### 6.2 Random Forest Classifier

Random Forest was evaluated as a nonlinear classification model.

Configuration:

- Number of estimators: 300.
- Maximum depth: 10.
- Minimum samples per leaf: 3.
- Class weighting: Balanced.
- Random state: 42.
- Parallel processing: Enabled.

Both models used the same preprocessing and feature definitions.

## 7. Model Selection

The model was selected using the highest validation F1-score.

### Validation results

| Metric | Logistic Regression | Random Forest |
|---|---:|---:|
| Accuracy | 0.8900 | 0.9133 |
| Precision | 0.6177 | 0.7343 |
| Recall | 0.9005 | 0.7562 |
| F1-score | 0.7328 | 0.7451 |
| ROC-AUC | 0.9619 | 0.9562 |
| PR-AUC | 0.8535 | 0.8414 |

Random Forest achieved the highest validation F1-score and was selected as the final model.

The majority-class baseline achieved an F1-score of 0.

## 8. Final Test Evaluation

The selected Random Forest model was evaluated on the held-out chronological test examination.

### Test metrics

| Metric | Result |
|---|---:|
| Accuracy | 0.9042 |
| Precision | 0.7093 |
| Recall | 0.7667 |
| F1-score | 0.7368 |
| ROC-AUC | 0.9518 |
| PR-AUC | 0.7983 |

### Confusion matrix

| | Predicted: No underperformance | Predicted: Underperformance |
|---|---:|---:|
| Actual: No underperformance | 924 | 66 |
| Actual: Underperformance | 49 | 161 |

The model correctly identified 161 underperforming records in the test dataset.

Recall is important because missing a student who may underperform can reduce the usefulness of an early-warning system.

Precision is also important because false alerts can result in unnecessary interventions.

## 9. Feature Importance Analysis

Permutation importance was calculated using the validation dataset.

| Feature | Mean importance |
|---|---:|
| Historical average percentage | 0.4635 |
| Previous examination percentage | 0.3869 |
| Attendance percentage | 0.0107 |
| Recent 60-day attendance | 0.0065 |
| Marks trend | 0.0029 |
| Class grade | 0.0023 |
| Previous 60-day attendance | 0.0013 |
| Previous examination count | 0.0000 |
| Attendance sessions to date | 0.0000 |
| Attendance trend | -0.0002 |

Historical academic performance contributed most strongly to the model's predictions.

Attendance features showed relatively small incremental importance in this synthetic dataset.

Therefore, the system does not claim that attendance alone strongly predicts academic underperformance.

Permutation importance indicates how much model performance changes when a feature is shuffled. It does not establish causation.

## 10. Model Integration

The trained model is integrated into the FastAPI backend.

### Model artifacts

- `ml_artifacts/models/underperformance_model.joblib`
- `ml_artifacts/models/model_metadata.json`
- `ml_artifacts/evaluation/feature_importance.csv`
- `ml_artifacts/evaluation/test_model_comparison.csv`

### Backend components

| Component | Responsibility |
|---|---|
| `app/ml/model_loader.py` | Loads the trained model and metadata |
| `app/ml/feature_service.py` | Retrieves historical database records and builds prediction features |
| `app/ml/prediction_service.py` | Validates features and runs model inference |
| `app/api/v1/ml_predictions.py` | Provides the authenticated prediction endpoint |
| `app/schemas/ml_predictions.py` | Defines request and response validation |

### Prediction endpoint

`POST /api/v1/ml/predictions/underperformance`

Request example:

```json
{
  "student_id": 1,
  "subject_id": 1,
  "target_examination_id": 8
}
```

The institution ID is obtained from the authenticated user rather than accepted from the request.

The endpoint:

1. Validates the student, subject and target examination.
2. Checks that the target examination is in the future.
3. Prevents predictions when target examination marks already exist.
4. Retrieves historical marks and attendance.
5. Builds the required model features.
6. Runs the Random Forest classifier.
7. Returns the prediction, model score, thresholds and feature values.

### Prediction interpretation

The model returns:

- Predicted underperformance classification.
- Model score.
- Classification threshold.
- Academic marks threshold.
- Model name.
- Input features.

The model score is an **uncalibrated model score**, not a guaranteed probability of academic underperformance.

The classification threshold is 0.5.

## 11. Testing and Verification

The ML pipeline was tested using both direct service execution and the FastAPI HTTP endpoint.

Verified operations:

- Model artifact loading.
- Feature service import.
- Prediction service import.
- Database feature generation.
- Historical marks retrieval.
- Historical attendance retrieval.
- Random Forest inference.
- Authenticated API routing.
- Request and response schema validation.
- Rejection when target examination marks already exist.
- Temporary examination creation and transaction rollback.

A successful HTTP test returned status code 200 with a prediction response.

The test also verified that temporary examination records were rolled back rather than permanently stored.

## 12. Limitations

The following limitations must be considered before using the model in a real school environment.

1. **Synthetic data:** The model was trained and tested using synthetic academic records. Its performance on real student data is unknown.

2. **Known student cohort:** Students overlap across chronological training, validation and testing periods. Results do not establish performance on unseen students or schools.

3. **Attendance importance:** Attendance features had relatively small permutation importance in the current synthetic dataset.

4. **Uncalibrated score:** The model score is not a calibrated probability.

5. **Academic threshold:** The 40% threshold is an assignment assumption and should be configurable according to institutional academic policies.

6. **Limited generalization:** Real-world data may contain different academic patterns, grading systems, examination structures and attendance practices.

7. **Decision support:** Predictions must not be used as the sole basis for academic decisions, disciplinary action or student labeling.

## 13. Future Improvements

Potential improvements include:

- Evaluate using real, authorized academic records.
- Test generalization using student-grouped and school-level holdout datasets.
- Reassess the academic underperformance threshold with school policies.
- Calibrate model scores if probability estimates are required.
- Monitor model performance over subsequent examination periods.
- Compare additional classification algorithms.
- Improve explainability using student-level feature contributions.
- Collect more representative attendance and academic history.

## 14. Conclusion

The School Intelligence ML pipeline demonstrates an end-to-end supervised learning workflow for identifying potential academic underperformance.

It includes feature engineering, chronological data splitting, baseline and Random Forest model comparison, evaluation, artifact storage, database-based feature generation and authenticated FastAPI inference.

The system is designed as an academic early-warning and decision-support tool. Its predictions require human review, and its synthetic evaluation results must not be interpreted as proven real-world performance.
