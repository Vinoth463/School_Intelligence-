# System Architecture – School Intelligence

## 1. Overview

School Intelligence is a full-stack academic intelligence application designed to help school administrators and teachers manage academic data, analyze student performance, monitor attendance, identify students who may underperform, and obtain AI-assisted academic insights.

The application follows a frontend-backend architecture.

The frontend provides the user interface, while the FastAPI backend handles authentication, business logic, academic analytics, machine learning inference, AI retrieval and database operations.

PostgreSQL is used as the primary relational database.

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 |
| Frontend language | TypeScript |
| Frontend build tool | Vite |
| UI navigation | React Router |
| HTTP communication | Axios |
| Charts | Recharts |
| Backend | FastAPI |
| Backend language | Python |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Database migrations | Alembic |
| Data processing | Pandas, NumPy |
| Machine learning | Scikit-learn |
| Model persistence | Joblib |
| Generative AI | Groq API |
| Authentication | JWT |
| Password hashing | Argon2 |
| Report generation | Pandas, OpenPyXL, ReportLab |
| Backend testing | Pytest |
| API testing | HTTPX / FastAPI TestClient |

## 3. High-Level Architecture

```text
                 USER
                   |
                   v
       React + TypeScript Frontend
                   |
             Axios HTTP Client
                   |
                   v
             FastAPI Backend
                   |
      +------------+-------------+
      |            |             |
      v            v             v
 Authentication  Analytics   Import / Reports
      |            |             |
      +------------+-------------+
                   |
        +----------+----------+
        |                     |
        v                     v
  ML Prediction         AI Assistant
        |                     |
        v                     v
  Scikit-learn          Academic Retrieval
  Model Service         and Entity Resolution
                              |
                              v
                         Groq API
                   |
                   v
             SQLAlchemy ORM
                   |
                   v
              PostgreSQL
```

The AI Assistant also retrieves academic information through database queries and backend services. The machine learning workflow uses historical database records to construct prediction features.

## 4. Frontend Architecture

The frontend is implemented using React, TypeScript and Vite.

Its responsibilities include:

- User login and authentication.
- Displaying dashboard KPIs.
- Academic performance analytics.
- Subject-wise attendance analytics.
- Machine learning prediction results.
- AI Academic Assistant interaction.
- Student, marks and attendance imports.
- Report preview and export.

### Frontend structure

```text
frontend/
├── public/
├── src/
│   ├── components/
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── Analytics/
│   │   ├── Attendance/
│   │   ├── MLPredictions/
│   │   ├── AIAssistant/
│   │   ├── Imports/
│   │   └── Reports/
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

The Axios API service communicates with the FastAPI backend.

The frontend stores the access token using the application token key:

`school_intelligence_access_token`

Protected API requests use the authentication token.

## 5. Backend Architecture

The backend uses FastAPI and is organized into API routes, services, models, schemas, database configuration, machine learning and AI components.

### Backend structure

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ml/
│   ├── ai/
│   ├── utils/
│   └── main.py
├── alembic/
├── tests/
├── requirements.txt
└── .env
```

### Main responsibilities

| Component | Responsibility |
|---|---|
| `api/v1/` | HTTP endpoints and request handling |
| `core/` | Application configuration and security |
| `database/` | Database engine and session management |
| `models/` | SQLAlchemy database models |
| `schemas/` | Request and response validation |
| `services/` | Academic business logic and analytics |
| `ml/` | Feature generation, model loading and prediction |
| `ai/` | Academic retrieval, entity resolution and AI response generation |
| `utils/` | Shared utility functionality |
| `alembic/` | Database migration management |
| `tests/` | Automated backend tests |

## 6. Database Architecture

PostgreSQL is the primary data store.

SQLAlchemy 2.0 provides ORM-based database interaction, and Alembic manages database schema migrations.

The database includes academic entities such as:

- Institutions.
- Academic periods.
- Classrooms.
- Students.
- Subjects.
- Examinations.
- Marks.
- Attendance.
- Users.
- Import logs.
- Import rejections.

The academic data is related through database identifiers and foreign-key relationships.

The application uses database-backed academic records for dashboard calculations, analytics, reporting, ML feature generation and AI retrieval.

## 7. Authentication and Security Architecture

The application uses JWT-based authentication.

The authentication workflow is:

1. A user submits login credentials.
2. The backend verifies the stored password hash.
3. The backend generates an access token.
4. The frontend stores the returned access token.
5. The frontend includes the token in protected API requests.
6. The backend validates the token and identifies the current user.
7. Role-based authorization is applied where required.

Passwords are hashed using Argon2id.

Database credentials, JWT secrets and the Groq API key are maintained in environment configuration.

Institution context is obtained from the authenticated user for institution-scoped operations.

## 8. Academic Analytics Architecture

Academic analytics are implemented through FastAPI endpoints and backend service functions.

The analytics layer supports:

- Dashboard overview metrics.
- Student performance analysis.
- Subject-wise performance analysis.
- Examination comparisons.
- Academic-period comparisons.
- Declining-performance analysis.
- Attendance analysis.
- Attendance and academic-performance analysis.

The backend retrieves and aggregates academic records using SQLAlchemy and SQL queries.

The frontend presents the results using tables, KPI cards and charts.

## 9. Machine Learning Architecture

The ML component uses a trained Random Forest classification pipeline to identify potential academic underperformance.

The model is trained separately from the application runtime.

The saved model artifact is loaded by the backend for inference.

### ML components

| Component | Responsibility |
|---|---|
| `app/ml/model_loader.py` | Loads the saved model and metadata |
| `app/ml/feature_service.py` | Retrieves historical academic information and builds model features |
| `app/ml/prediction_service.py` | Validates prediction features and runs inference |
| `app/api/v1/ml_predictions.py` | Exposes the authenticated prediction API |
| `app/schemas/ml_predictions.py` | Defines prediction request and response schemas |

### Prediction workflow

1. The user selects a student, subject and target examination.
2. The backend validates the selected academic entities.
3. Historical marks and attendance are retrieved.
4. Prediction features are generated using information available before the target examination.
5. The trained model generates a classification and model score.
6. The backend returns prediction information and supporting indicators.
7. The frontend displays the prediction and relevant academic features.

The model score is uncalibrated and must not be interpreted as a verified probability.

## 10. Generative AI Architecture

The AI Academic Assistant combines structured academic retrieval with a Groq language model.

The workflow includes:

1. Receiving the user's question.
2. Identifying the academic intent.
3. Resolving relevant students, subjects, classes, examinations and periods.
4. Retrieving academic information from the database and backend services.
5. Preparing the retrieved academic context.
6. Sending the context to the Groq language model.
7. Returning a natural-language answer.

The current implementation uses SQL-based retrieval and application-level routing. It does not require a vector database.

The AI assistant is designed to explain retrieved academic information rather than invent academic records.

## 11. Import Management Architecture

The import module supports uploading academic data files.

The backend validates incoming records and processes supported student, examination-mark and attendance imports.

The import workflow includes:

1. Receiving an uploaded CSV or Excel file.
2. Reading and validating the file.
3. Checking required fields and academic references.
4. Processing accepted records.
5. Recording rejected records and rejection reasons.
6. Storing import history.
7. Returning an import summary to the frontend.

Import logs and rejection records support traceability and review of uploaded data.

## 12. Reporting Architecture

The reporting module retrieves academic information through institution-scoped backend endpoints.

It supports reports for:

- Students.
- Subjects.
- Classes.
- Attendance.
- Overall report summaries.

Reports can be previewed in the frontend and exported in Excel and PDF formats.

The backend uses OpenPyXL for Excel generation and ReportLab for PDF generation.

## 13. API Communication

The frontend communicates with the backend through REST API endpoints.

The backend API base path is:

`/api/v1`

During local development, the frontend API base URL is configured as:

`http://127.0.0.1:8000/api/v1`

FastAPI provides interactive API documentation through:

`http://127.0.0.1:8000/docs`

## 14. Database Migration Architecture

Alembic manages database schema changes.

Migrations are stored in the backend Alembic directory.

The migration workflow is:

1. Update SQLAlchemy model definitions.
2. Generate a migration revision.
3. Review the generated migration.
4. Apply migrations using Alembic.
5. Verify the database schema.

This allows database changes to be tracked and applied consistently.

## 15. Testing Architecture

Pytest is used for backend automated testing.

The current ML prediction tests cover:

- Feature generation.
- Prediction service execution.
- Prediction API.
- Invalid student, subject and examination handling.
- Existing target-mark rejection.
- Insufficient historical marks.
- Institution access validation.
- Past target examination rejection.
- Examination and academic-period validation.

Frontend build and lint checks are separate verification steps.

## 16. Deployment Considerations

The current project is configured for local development and technical demonstration.

A production deployment should additionally configure:

- Secure environment variables.
- HTTPS.
- Production database access and backups.
- Application monitoring.
- Error logging.
- Secure file uploads.
- Appropriate API access controls.
- External AI provider failure handling.

## 17. Conclusion

The School Intelligence architecture combines a React and TypeScript frontend, FastAPI backend, PostgreSQL database, machine learning inference pipeline and Generative AI Academic Assistant.

The modular architecture separates presentation, authentication, academic business logic, data access, ML inference and AI response generation.

This structure supports the academic data management, analytics, prediction, AI assistance and reporting requirements of the assignment.