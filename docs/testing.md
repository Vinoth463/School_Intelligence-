# School Intelligence – Testing Documentation

## 1. Introduction

This document describes the testing strategy used for the School Intelligence application.

The purpose of testing is to verify that the application correctly processes academic data, calculates performance and attendance analytics, generates machine learning predictions, provides grounded AI responses, protects academic information, and generates reports.

Testing covers the backend, frontend, database operations, machine learning pipeline, Generative AI integration, authentication, and complete application workflows.

## 2. Testing Objectives

The main testing objectives are:

- Verify the correctness of academic calculations.
- Validate student, examination, marks, and attendance imports.
- Ensure invalid records are rejected with meaningful reasons.
- Verify database operations and academic relationships.
- Test authentication and protected API endpoints.
- Evaluate machine learning predictions and feature processing.
- Verify that AI responses use retrieved academic information.
- Test missing-data handling and prevent unsupported answers.
- Verify report generation and file exports.
- Check frontend functionality and production builds.

## 3. Testing Environment

The application uses the following testing environment.

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database migrations | Alembic |
| Backend testing | Pytest |
| HTTP/API testing | HTTPX |
| Frontend | React, TypeScript, Vite |
| Frontend checks | ESLint, TypeScript build |
| Machine Learning | scikit-learn |
| Generative AI | Groq API |
| Report generation | ReportLab, OpenPyXL |

## 4. Backend Testing

Backend testing verifies the correctness of API endpoints, services, database operations, validation rules, and business logic.

### 4.1 Running Backend Tests

Navigate to the backend directory:

```bash
cd backend
```

Activate the Python virtual environment.

Install dependencies if required:

```bash
pip install -r requirements.txt
```

Run the complete test suite:

```bash
pytest
```

Run tests with detailed output:

```bash
pytest -v
```

Run tests with additional failure details:

```bash
pytest -v -s
```

### 4.2 Backend Testing Areas

The following areas are covered by the backend testing strategy:

| Module | Testing Focus |
|---|---|
| Authentication | Login, JWT generation, token validation |
| Dashboard | Academic summary calculations |
| Analytics | Student, class, subject and examination calculations |
| Attendance | Attendance percentages and low-attendance identification |
| Imports | File validation, accepted rows and rejected rows |
| Machine Learning | Feature generation and prediction processing |
| AI Assistant | Academic retrieval and response grounding |
| Reports | Report data retrieval and PDF/Excel generation |

## 5. Authentication and Authorization Testing

Authentication testing verifies that protected academic information cannot be accessed without valid authentication.

### Test Cases

| Test Case | Expected Result |
|---|---|
| Login with valid credentials | Access token returned |
| Login with invalid credentials | Authentication rejected |
| Access protected API without token | HTTP 401 Unauthorized |
| Access protected API with valid token | Request proceeds subject to authorization |
| Access current-user endpoint with valid token | Authenticated user information returned |
| Access with invalid or expired token | Authentication rejected |

### Verified Authentication Test

The dashboard endpoint was tested without an authentication token.

**Endpoint:**

```http
GET /api/v1/dashboard/overview?academic_period_id=1
```

**Observed response:**

```json
{
  "detail": "Not authenticated"
}
```

**HTTP Status:**

```text
401 Unauthorized
```

This confirms that the dashboard endpoint rejects unauthenticated requests.

Authenticated dashboard access should also be verified using a valid token.

## 6. Academic Data Import Testing

Import testing verifies that CSV and Excel files are validated before academic records are stored in PostgreSQL.

### Test Cases

| Test Case | Description | Expected Result |
|---|---|---|
| Valid student file | Upload valid student records | Records accepted |
| Valid marks file | Upload valid examination marks | Records accepted |
| Valid attendance file | Upload valid attendance records | Records accepted |
| Missing required fields | Upload records with missing values | Invalid rows rejected |
| Duplicate records | Upload duplicate academic records | Duplicate rows rejected |
| Invalid data types | Upload incorrect field types | Invalid rows rejected |
| Missing references | Use nonexistent student, class or subject references | Rows rejected |
| Invalid attendance dates | Upload attendance outside valid student dates | Rows rejected |
| Import history | Retrieve previous imports | Import summaries returned |
| Rejection details | Retrieve rejected records | Rejection reasons returned |

### Import Summary Verification

Each import operation should provide:

- Total rows processed.
- Accepted row count.
- Rejected row count.
- Import status.
- Rejection details and reasons.

### Previously Verified Import Results

The initial synthetic attendance dataset contained:

| Metric | Count |
|---|---:|
| Total attendance records | 52,800 |
| Initially accepted | 51,756 |
| Initially rejected | 1,044 |

The initial rejections were related to attendance sessions dated before student admission dates.

The missing attendance records were subsequently corrected and imported.

The rejection endpoint was also tested and returned the corresponding validation reason.

A separate student CSV upload was tested successfully:

| Metric | Result |
|---|---:|
| Total rows | 1 |
| Accepted rows | 1 |
| Rejected rows | 0 |

## 7. Academic Performance Analytics Testing

Analytics testing verifies that examination marks are processed and aggregated correctly.

### Test Cases

| Test Case | Expected Result |
|---|---|
| Student performance | Student examination results returned |
| Subject performance | Subject averages calculated |
| Class performance | Class-level performance summaries returned |
| Examination comparison | Examination results compared correctly |
| Academic-period comparison | Period-level performance summaries returned |
| Declining performance | Declining examination transitions identified |
| Subject decline | Subject-level declining performance identified |
| Filter by class | Only matching class records returned |
| Filter by subject | Only matching subject records returned |
| Filter by examination | Only matching examination records returned |

### Calculation Verification

Academic percentages should be calculated using:

```text
Percentage = (Obtained Marks / Maximum Marks) * 100
```

Aggregated performance calculations should use the same definitions as the corresponding backend analytics services.

Declining-performance counts must be interpreted according to their calculation method. A count of declining transitions is not necessarily the count of unique students.

## 8. Attendance Analytics Testing

Attendance testing verifies that attendance is calculated separately for students and subjects.

### Attendance Calculation

```text
Attendance Percentage =
(Present Sessions / Total Sessions) * 100
```

### Test Cases

| Test Case | Expected Result |
|---|---|
| Student attendance | Student attendance summary returned |
| Subject attendance | Subject-wise attendance calculated |
| Class attendance | Class attendance summary returned |
| Low attendance | Students below configured threshold identified |
| Academic-period filtering | Correct period records returned |
| Attendance-performance analysis | Attendance and marks relationship calculated |
| High attendance with low marks | Such cases can be identified |
| Low attendance with high marks | Such cases can be identified |

### Correlation Interpretation

The attendance-performance analysis must not automatically interpret statistical correlation as causation.

Attendance may be associated with academic performance, but other academic and personal factors can also influence examination results.

## 9. Machine Learning Testing

Machine learning testing verifies feature processing, prediction generation, model evaluation, and data sufficiency handling.

### 9.1 Prediction Objective

The model identifies students who may score below the configured academic performance threshold in a target examination.

The target variable is:

```text
Underperformance = 1 if next examination percentage < 40%
Underperformance = 0 otherwise
```

### 9.2 Feature Validation

The model uses historical information available before the target examination.

Features include:

- Previous examination percentage.
- Historical average percentage.
- Marks trend.
- Number of previous examinations.
- Historical attendance percentage.
- Recent attendance percentage.
- Previous attendance percentage.
- Attendance trend.
- Attendance sessions.
- Class grade.

Student identifiers and future examination outcomes must not be included as prediction features.

### 9.3 Train, Validation and Test Strategy

The model was evaluated using a chronological examination-based split.

| Dataset | Target Examinations | Records |
|---|---|---:|
| Training | Examinations 2–4 | 3,600 |
| Validation | Examination 5 | 1,200 |
| Testing | Examination 6 | 1,200 |

This strategy uses earlier examinations for training and later examinations for validation and testing.

### 9.4 Model Evaluation

Two models were compared:

- Logistic Regression baseline.
- Random Forest classifier.

Random Forest was selected based on its higher validation F1-score.

Recorded Random Forest test metrics:

| Metric | Result |
|---|---:|
| Accuracy | 0.9042 |
| Precision | 0.7093 |
| Recall | 0.7667 |
| F1-score | 0.7368 |
| ROC-AUC | 0.9518 |
| PR-AUC | 0.7983 |

Confusion matrix:

```text
                 Predicted
                 Not at risk   At risk
Actual Not at risk     924        66
Actual At risk          49       161
```

### 9.5 Prediction Testing

| Test Case | Expected Result |
|---|---|
| Valid student, subject and target examination | Prediction generated |
| Student with sufficient historical data | Prediction and indicators returned |
| Missing historical features | Data sufficiency handled |
| Invalid student ID | Appropriate error or no-record response |
| Invalid subject ID | Appropriate error or no-record response |
| Invalid examination ID | Appropriate error or no-record response |
| Examination from a different selected period | Period validation applied |
| Risk category generation | Configured thresholds applied |
| Prediction explanation | Supporting risk and positive indicators returned |

### 9.6 Model Limitations

The model was trained and evaluated using synthetic data.

The same student cohort appears across different chronological examination splits. Therefore, the evaluation does not establish generalization to entirely unseen students.

The model score is uncalibrated and must not be presented as a verified probability of failure.

Historical marks were substantially more influential than attendance in the recorded permutation-importance analysis. Attendance should not be described as a strong predictor based on this experiment.

Predictions must be treated as decision-support information rather than final academic decisions.

## 10. Generative AI Testing

The AI Academic Assistant is tested to verify that its responses are based on retrieved academic records and that unsupported information is not fabricated.

### 10.1 AI Testing Areas

- Academic intent identification.
- Student, subject and examination resolution.
- Academic database retrieval.
- ML prediction integration.
- Grounded numerical explanations.
- Teacher-intervention recommendations.
- Missing-data handling.
- Unsupported question handling.
- Institution-scoped data access.

### 10.2 AI Test Cases

| Test Case | User Question / Scenario | Expected Behaviour |
|---|---|---|
| Low marks and attendance | Identify students with low marks and attendance in a subject | Retrieve matching academic records |
| Lowest subject average | Identify the lowest-performing subject | Return subject averages and identify the lowest |
| Declining performance | Identify students with declining examination performance | Retrieve declining-performance records |
| ML prediction explanation | Explain why a particular student was flagged | Use actual model prediction and indicators |
| Teacher intervention | Recommend interventions for an identified student | Give evidence-based recommendations |
| Missing-data question | Explain incomplete marks and attendance records | Identify missing information and avoid unsupported predictions |
| General data-quality question | Ask whether a prediction is reliable with incomplete data | Explain data requirements without requesting individual prediction entities |
| Unavailable academic records | Ask about records that cannot be retrieved | Clearly report unavailable information |
| Unsupported question | Ask an unrelated question | Return an appropriate unsupported response |

### 10.3 Verified AI Prediction Test

The assistant was tested using Deepak Singh (STU0041), English, and the Practice Assessment.

The response successfully retrieved and explained:

- Previous examination percentage: 31.96%.
- Historical average percentage: 33.37%.
- Historical subject attendance: 51.61%.
- Recent attendance: 50%.
- Previous attendance window: 66.67%.
- Marks improvement: 3.36 percentage points.
- Predicted underperformance: Yes.
- Risk category: High.

The AI also returned teacher-intervention suggestions addressing low marks, attendance decline, progress monitoring, and positive academic improvement.

### 10.4 Verified Missing-Data Test

The assistant was asked to explain the academic performance and risk of a student with incomplete examination and attendance records, without supplying a student identity.

The initial intent-routing behaviour was corrected so that general data-quality questions do not enter the individual prediction branch.

The final response correctly:

- Identified that no specific student was provided.
- Confirmed that no individual academic records were retrieved.
- Explained the examination information required.
- Explained the attendance information required.
- Confirmed that no individual prediction was generated.
- Avoided inventing student details or academic metrics.

### 10.5 AI Grounding Requirements

The assistant must:

- Use retrieved academic information for numerical answers.
- Avoid inventing student details.
- Distinguish missing information from verified records.
- Explain when historical data is insufficient.
- Avoid presenting correlation as causation.
- Distinguish model indicators from proven causes.
- Avoid interpreting uncalibrated model scores as probabilities.

## 11. Report and Export Testing

Report testing verifies report retrieval, filtering, formatting, and file downloads.

### Test Cases

| Test Case | Expected Result |
|---|---|
| Report overview | Summary information returned |
| Student report | Student-specific report generated |
| Subject report | Subject report generated |
| Class report | Class report generated |
| Attendance report | Attendance report generated |
| Report filters | Selected filters applied |
| Excel export | Valid Excel file downloaded |
| PDF export | Valid PDF file downloaded |
| Invalid student reference | Appropriate validation or not-found response |

### Previously Verified Results

The student report was tested through Swagger.

Both Excel and PDF exports were generated and downloaded successfully.

The frontend report preview was also updated to display structured report information rather than raw JSON.

## 12. Frontend Testing

Frontend testing verifies the application interface, navigation, API integration, and production build.

### Frontend Modules

| Module | Testing Focus |
|---|---|
| Authentication | Login and token handling |
| Dashboard | KPI and academic summary display |
| Analytics | Charts, filters and academic results |
| Attendance | Attendance summaries and comparisons |
| ML Predictions | Prediction inputs and result display |
| AI Assistant | Question submission and response display |
| Imports | File upload, import history and rejection details |
| Reports | Report preview, filters and downloads |

### Frontend Commands

Navigate to the frontend directory:

```bash
cd frontend
```

Run linting:

```bash
npm run lint
```

Run the TypeScript and Vite production build:

```bash
npm run build
```

Start the development server:

```bash
npm run dev
```

### Frontend Verification

Check the following:

- Login works with valid credentials.
- Invalid login attempts are handled.
- Protected pages require authentication.
- API errors are displayed appropriately.
- Analytics filters update displayed results.
- Import summaries are visible.
- ML prediction results are displayed correctly.
- AI responses are rendered correctly.
- Reports display structured information.
- Excel and PDF downloads work.

## 13. End-to-End Testing

End-to-end testing verifies the complete workflow across the frontend, backend, database, ML model, and AI assistant.

### Main Application Workflow

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Log in using a valid application account.
5. Upload student data.
6. Upload examination marks.
7. Upload subject-wise attendance.
8. Review accepted and rejected import records.
9. Open the academic dashboard.
10. Review performance analytics.
11. Review attendance analytics.
12. Generate an ML prediction for a suitable student, subject, and target examination.
13. Ask the AI assistant to explain the prediction.
14. Ask the AI assistant for teacher-intervention recommendations.
15. Test a general missing-data question.
16. Generate a student report.
17. Export the report to Excel or PDF.

### Expected Outcome

The complete workflow should operate using PostgreSQL-backed academic records, authenticated API requests, ML prediction services, and the Groq-powered Academic Assistant.

## 14. Testing Summary

The following table summarizes the testing work and verification status recorded during development.

| Area | Recorded Status |
|---|---|
| Authentication | Unauthenticated dashboard request verified as HTTP 401 |
| Academic imports | Import endpoints and rejection handling tested |
| Academic analytics | Core analytics services and endpoints implemented and tested |
| Attendance analytics | Attendance calculations and analysis implemented and tested |
| Machine learning | Model training, evaluation and prediction workflow implemented |
| AI prediction explanation | Tested successfully |
| AI teacher interventions | Tested successfully |
| AI missing-data handling | Tested successfully after intent-routing correction |
| Reports | PDF and Excel exports tested |
| Frontend report preview | Structured rendering tested |
| Full backend test suite | Run and verify before final submission |
| Frontend lint and build | Run and verify before final submission |
| Complete end-to-end workflow | Final demonstration verification required |

## 15. Known Testing Limitations

1. The academic dataset is synthetic and does not represent real student observations.
2. The ML evaluation uses the same student cohort across chronological examination splits.
3. The current model score is uncalibrated.
4. AI answer quality depends on retrieved database information and the configured Groq model.
5. Full end-to-end behaviour depends on the availability of PostgreSQL, the backend, frontend, model artifacts, and Groq API configuration.
6. Passing a manual test does not replace automated regression tests.
7. Institution-level isolation should be verified according to the application's implemented multi-institution scope.

## 16. Conclusion

Testing is an important part of ensuring that School Intelligence provides reliable academic analytics, responsible machine learning predictions, grounded AI explanations, and secure access to student information.

The testing strategy covers individual modules and complete application workflows.

The application should be considered ready for final demonstration only after the current backend test suite, frontend checks, and complete end-to-end workflow have been verified in the target environment.