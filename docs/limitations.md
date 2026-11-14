# School Intelligence – Limitations and Responsible Use

## 1. Introduction

This document describes the known limitations, assumptions, data requirements, and responsible-use considerations of the School Intelligence application.

The application combines academic analytics, subject-wise attendance analysis, machine learning, and Generative AI to support academic decision-making.

Although the system provides useful academic insights, its results depend on the quality, completeness, and consistency of the available academic data.

The application is designed as an academic decision-support system. Its analytics, predictions, and AI-generated recommendations should support teachers and administrators rather than replace their professional judgment.

---

## 2. Synthetic Dataset Limitations

The application uses a synthetic academic dataset because real student information was not supplied for the assignment.

The demonstration dataset represents a fictional institution named Green Valley School.

The generated dataset includes:

- Approximately 200 students.
- 10 classes.
- 6 subjects.
- 6 examinations.
- 7,200 examination mark records.
- 52,800 subject-wise attendance sessions.
- Two academic periods.

### Limitations

1. Synthetic records do not represent actual student behaviour or real academic outcomes.
2. Generated examination marks and attendance patterns may not reflect the complexity of a real school environment.
3. Relationships between attendance and examination performance in the dataset should not be interpreted as real-world educational findings.
4. Model evaluation results obtained from synthetic records cannot establish real-world predictive performance.

### Responsible Use

- Synthetic data must be clearly identified as synthetic.
- Generated historical observations must not be presented as actual school history.
- Real student information should only be used when explicitly authorized and appropriately protected.

---

## 3. Machine Learning Limitations

### 3.1 Prediction Objective

The machine learning model identifies students who may underperform in a target examination.

The target variable is defined as:

- Underperformance: next examination percentage below 40%.
- Not underperforming: next examination percentage greater than or equal to 40%.

This threshold is a modelling assumption used in the current implementation. It is not a universal definition of academic success or failure.

### 3.2 Data Requirements

The model requires sufficient historical academic information to calculate its input features.

These include:

- Previous examination percentage.
- Historical average percentage.
- Marks trend.
- Number of previous examinations.
- Historical attendance percentage.
- Recent attendance percentage.
- Previous attendance percentage.
- Attendance trend.
- Attendance sessions available before the target examination.
- Class grade.

The input features must be available before the target examination.

### 3.3 Situations Where the Model Should Not Be Trusted

A prediction should not be treated as reliable when:

1. The student has insufficient historical examination records.
2. Required attendance records are missing or incomplete.
3. Historical marks or attendance records contain invalid or inconsistent values.
4. The target examination is not correctly identified.
5. The target examination is not consistent with the selected academic period.
6. The available historical data does not adequately represent the student or subject being evaluated.
7. The model is applied to real-world data without appropriate validation.

When required information is insufficient, the application should report the limitation rather than invent missing features or generate an unsupported prediction.

### 3.4 Model Evaluation Limitations

The development experiment used a chronological examination-based split:

| Dataset | Target Examinations | Records |
|---|---|---:|
| Training | Examinations 2–4 | 3,600 |
| Validation | Examination 5 | 1,200 |
| Testing | Examination 6 | 1,200 |

The same student cohort appears across different examination periods.

Therefore:

- The evaluation demonstrates performance across later examination periods for the known cohort.
- It does not establish generalization to completely unseen students.
- Additional evaluation using independent student cohorts and real, authorized academic data is necessary before operational deployment.

### 3.5 Model Score Interpretation

The application displays an underperformance model score and risk category.

The displayed model score is uncalibrated.

Therefore:

- A score of 0.90 must not be interpreted as a verified 90% probability of examination failure.
- Classification thresholds and risk categories are based on the configured model methodology.
- Risk indicators describe patterns identified from historical features; they do not prove the cause of future academic performance.

### 3.6 Feature Importance Limitations

The recorded permutation-importance analysis showed that historical average percentage and previous examination percentage were the most influential features.

Attendance features had relatively small importance in the experiment.

Therefore, the system should not claim that attendance is a strong predictor of underperformance based on this particular model evaluation.

Feature importance indicates model behaviour within the evaluated dataset. It does not establish causation.

---

## 4. Academic Analytics Limitations

### 4.1 Data Completeness

Academic calculations depend on the availability of valid examination and attendance records.

Missing records may affect:

- Student performance averages.
- Subject averages.
- Examination comparisons.
- Declining-performance identification.
- Attendance percentages.
- Attendance and marks relationship analysis.

An incomplete dataset may produce incomplete or misleading summaries if missing information is not identified.

The application should distinguish unavailable information from a genuine zero value.

### 4.2 Attendance and Academic Performance

The application analyzes the relationship between subject-wise attendance and examination marks.

However, attendance is only one factor associated with academic performance.

Other factors may influence examination outcomes, including:

- Previous academic knowledge.
- Learning difficulties.
- Teaching methods.
- Study habits.
- Assessment difficulty.
- Personal and environmental circumstances.

A statistical correlation between attendance and marks must not automatically be presented as causation.

High attendance does not guarantee high examination marks, and low attendance does not automatically mean that a student will underperform.

### 4.3 Declining Performance

Declining-performance analytics identify changes across consecutive examinations.

A declining transition does not necessarily mean that a student has permanently poor academic performance.

The results should be interpreted alongside the number of available examinations, subject context, assessment differences, and historical records.

Counts of declining transitions should not be confused with counts of unique students.

---

## 5. Generative AI Limitations

### 5.1 Dependence on Retrieved Academic Data

The Academic Assistant uses structured database retrieval and academic analytics services to obtain information before generating responses through the Groq API.

The quality and accuracy of an answer depend on:

- Correct academic database records.
- Successful student, subject, examination, and period resolution.
- Correct retrieval filters.
- Availability of the required academic records.
- Correct interpretation of the retrieved context by the language model.

If relevant academic records cannot be retrieved, the assistant may not be able to provide a complete answer.

### 5.2 Unsupported or Missing Information

The AI assistant should not invent:

- Student names or admission numbers.
- Examination marks.
- Attendance percentages.
- Academic averages.
- Prediction scores.
- Risk indicators.
- Historical examination results.

When information is missing, the assistant should identify the missing information and explain whether a reliable assessment or prediction is possible.

An individual ML prediction requires the relevant student, subject, target examination, and sufficient historical features.

### 5.3 AI-Generated Recommendations

Teacher-intervention recommendations are suggestions based on retrieved academic evidence.

They are not guaranteed to improve examination results.

Teachers should review recommendations in the context of the student's learning needs and available school information.

### 5.4 Language Model Limitations

Groq provides the language model used by the Academic Assistant.

Language models can occasionally produce incomplete, ambiguous, or incorrectly interpreted explanations.

Important academic decisions should therefore be checked against the underlying database records and analytics.

The AI assistant is intended to support academic understanding, not replace teacher or administrator judgment.

### 5.5 External API Dependency

The AI Academic Assistant depends on the availability of the configured Groq API and a valid API key.

If the provider is unavailable, the API key is invalid, or the request fails, AI-generated responses may not be available.

The core academic analytics and database functionality are separate from the external language-model service.

---

## 6. Data Import and Validation Limitations

The import module validates uploaded student, examination-mark, and attendance records.

However, data quality also depends on the correctness of the source files.

Potential limitations include:

1. Incorrect source information may pass basic structural validation.
2. Missing historical records may affect downstream analytics.
3. Duplicate or inconsistent source records may require correction.
4. Incorrect academic references may cause records to be rejected.
5. Imported data must be internally consistent across students, classes, subjects, examinations, and academic periods.

Import validation improves data quality but cannot guarantee that every supplied record represents a correct real-world observation.

Users should review import summaries and rejection reasons after each upload.

---

## 7. Security and Access-Control Limitations

The application uses JWT authentication and password hashing to protect academic information.

Protected API endpoints require authentication.

Role-appropriate authorization and institution-scoped data access must be maintained wherever applicable.

If multi-institution support is implemented, academic records must remain isolated between institutions.

Additional security considerations include:

- Keeping database credentials and provider API keys in environment variables.
- Avoiding exposure of access tokens and passwords.
- Protecting student personal information.
- Restricting access to academic records according to user permissions.
- Using secure configuration for production deployment.

The current development environment should not be considered a complete production security deployment.

---

## 8. Deployment and Performance Limitations

The current application is developed for local execution and technical demonstration.

Before production deployment, further work may be required in areas such as:

- Production server configuration.
- HTTPS and secure network communication.
- Database backup and recovery.
- Monitoring and structured logging.
- API rate limiting.
- Performance testing under concurrent users.
- Deployment configuration and environment management.
- Secure handling of uploaded files.
- External AI provider failure handling.

No production-scale performance or availability guarantees are established by the current development tests.

---

## 9. Future Improvements

Potential improvements include:

1. Evaluate the ML model using independent student cohorts and real, authorized academic datasets.
2. Reassess feature importance using additional representative data.
3. Evaluate probability calibration if probability estimates are required.
4. Improve handling of incomplete historical marks and attendance records.
5. Expand automated testing for analytics, imports, and AI retrieval.
6. Add more extensive AI response-grounding and regression tests.
7. Improve production monitoring and error reporting.
8. Perform security and performance testing before deployment.
9. Evaluate model performance across different classes, subjects, and academic periods.

These improvements should be introduced based on actual application requirements and evaluation evidence rather than adding unnecessary technologies.

---

## 10. Conclusion

School Intelligence provides an integrated platform for academic analytics, subject-wise attendance analysis, machine learning predictions, and Generative AI assistance.

However, its results depend on the quality and completeness of academic data, the limitations of the evaluated synthetic dataset, the generalization ability of the machine learning model, and the accuracy of retrieved information supplied to the language model.

The application is intended to support evidence-based academic decisions.

Predictions and AI-generated recommendations should be interpreted carefully, especially when historical records are incomplete or insufficient.

The system must communicate uncertainty, identify missing information, avoid unsupported numerical claims, and leave final academic decisions to authorized teachers and administrators.