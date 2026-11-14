# School Intelligence

A full-stack academic intelligence application that analyzes examination performance and subject-wise attendance, identifies students who may need academic support, and provides evidence-based explanations through machine learning and a Generative AI assistant.

The application is built with **FastAPI, PostgreSQL, SQLAlchemy, React, TypeScript, scikit-learn, and Groq**.

> **Dataset notice:** The included demonstration dataset is synthetic. It is intended for development and evaluation, not as a representation of real student records or real-world model performance.

## Table of contents

- [Project overview](#project-overview)
- [Features](#features)
- [Technology stack](#technology-stack)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Database setup](#database-setup)
- [Backend setup](#backend-setup)
- [Frontend setup](#frontend-setup)
- [Using the application](#using-the-application)
- [Machine learning methodology](#machine-learning-methodology)
- [Generative AI Academic Assistant](#generative-ai-academic-assistant)
- [Reports and exports](#reports-and-exports)
- [Testing](#testing)
- [API documentation](#api-documentation)
- [Security notes](#security-notes)
- [Limitations](#limitations)
- [Documentation](#documentation)

## Project overview

School Intelligence brings academic marks and subject-wise attendance together so that school staff can explore performance, compare trends, identify students who may need support, and review the evidence behind those findings.

The system provides:

1. Academic data import and validation.
2. Student-, class-, subject-, examination-, and period-level analytics.
3. Subject-wise attendance analytics and attendance/performance comparisons.
4. A machine-learning workflow for identifying possible examination underperformance.
5. A Groq-powered Academic Assistant that retrieves application data before generating explanations.
6. Dashboards, detailed reports, and PDF/Excel exports.

## Features

### 1. Academic Data Management

- Import student, examination-mark, and attendance data from CSV or Excel files.
- Validate uploaded data and referenced academic entities.
- Record accepted and rejected rows with rejection reasons.
- Store validated academic records in PostgreSQL.
- Review import history and row-level rejection details.

### 2. Academic Performance Analytics

- Review student-level examination performance.
- Compare performance by class, subject, examination, and academic period.
- View subject averages and performance trends.
- Identify declining performance across consecutive examinations.

### 3. Subject-wise Attendance Analytics

- Analyze attendance at student and subject level.
- Compare attendance across classes and academic periods.
- Identify students below the configured attendance threshold.
- Examine the relationship between attendance and marks.
- Treat correlation as association, not proof of causation.

### 4. Machine Learning Predictions

- Predict whether a student may fall below the configured academic performance threshold in a target examination.
- Display a risk category and supporting indicators.
- Show the historical marks and attendance features used by the model.
- Report data sufficiency limitations when the required historical information is unavailable.

### 5. Generative AI Academic Assistant

- Ask questions about academic performance, attendance, declining trends, and subject results.
- Ask why a student was flagged by the ML workflow.
- Request teacher-intervention suggestions grounded in retrieved academic indicators.
- Handle general data-quality questions and insufficient records without inventing student metrics.
- Use structured academic retrieval from the application's database.

### 6. Dashboard and Reports

- View student and academic performance summaries.
- Review attendance and at-risk indicators.
- Generate student, subject, class, and attendance reports.
- Export supported reports to Excel and PDF.

## Technology stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, Uvicorn |
| Database | PostgreSQL |
| ORM and migrations | SQLAlchemy 2.x, Alembic |
| Backend validation/settings | Pydantic, pydantic-settings |
| Data processing | Pandas, NumPy, OpenPyXL |
| Machine learning | scikit-learn, Joblib |
| Generative AI | Groq API |
| Authentication | JWT (`python-jose`), Argon2 password hashing |
| Frontend | React, TypeScript, Vite |
| HTTP client | Axios |
| Charts | Recharts |
| Testing | Pytest, HTTPX |
| PDF reports | ReportLab |
| Version control | Git |

## Architecture

The application uses a separated frontend/backend architecture:

```text
React + TypeScript frontend
          |
          | HTTP requests / JWT
          v
       FastAPI
          |
          +---- Authentication and authorization
          |
          +---- Academic analytics services
          |
          +---- Import and validation services
          |
          +---- ML feature and prediction services
          |
          +---- AI retrieval and Groq integration
          |
          +---- Report and export services
          |
          v
      PostgreSQL
```

The Academic Assistant uses structured queries and application services to retrieve academic records. It is not a general-purpose document RAG system. A vector database is not required for the current structured academic-data retrieval design.

## Repository structure

The main project layout is:

```text
School_Intelligence/
|
+-- backend/
|   +-- app/
|   |   +-- api/
|   |   |   +-- v1/
|   |   +-- ai/
|   |   +-- core/
|   |   +-- database/
|   |   +-- ml/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- services/
|   |   +-- utils/
|   +-- alembic/
|   +-- tests/
|   +-- requirements.txt
|
+-- frontend/
|   +-- src/
|   +-- package.json
|   +-- vite.config.ts
|
+-- dataset/
|   +-- generated/
|   +-- templates/
|
+-- docs/
|   +-- architecture.md
|   +-- database_design.md
|   +-- ml_methodology.md
|   +-- ai_methodology.md
|
+-- ml_artifacts/
|   +-- models/
|   +-- evaluation/
|
+-- README.md
```

Individual files may evolve as the application is maintained. The folders above describe the principal project areas.

## Prerequisites

Install the following before starting:

- Python (a Python 3.10 environment was used during development).
- Node.js and npm compatible with the installed Vite version.
- PostgreSQL.
- Git.

Check the installations:

```bash
python --version
node --version
npm --version
psql --version
git --version
```

## Configuration

### Backend environment variables

Create `backend/.env` using the following template. Replace the placeholder values locally. **Do not commit this file or share its secrets.**

```dotenv
# Application
APP_NAME=School Intelligence
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=True

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=school_intelligence
DB_USER=postgres
DB_PASSWORD=replace_with_your_database_password

# JWT Authentication
JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq Generative AI
GROQ_API_KEY=replace_with_your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_MAX_TOKENS=2048
```

`DB_PASSWORD` and `JWT_SECRET_KEY` are required by the backend settings. `GROQ_API_KEY` is optional for starting the backend, but it is required for Groq-powered assistant requests.

Generate a strong JWT secret locally. Do not use the example placeholder as a real secret.

The settings class loads `.env` from the process working directory. Run backend commands from the `backend` directory so `backend/.env` is found.

## Database setup

1. Start PostgreSQL.
2. Create the database:

```sql
CREATE DATABASE school_intelligence;
```

You can run this statement from `psql` or a PostgreSQL administration tool.

3. Confirm that the database name, user, password, host, and port in `backend/.env` match your local PostgreSQL configuration.
4. Apply the Alembic migrations after completing the backend setup:

```bash
cd backend
alembic upgrade head
```

The migration history in `backend/alembic/` defines the database schema.

## Backend setup

From the project root:

```bash
cd backend
```

Create and activate a virtual environment.

**Windows Command Prompt:**

```bat
python -m venv venv
venv\Scripts\activate
```

**PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Make sure `backend/.env` exists and contains the local configuration.

Apply database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

Keep the backend terminal open while using the frontend.

## Frontend setup

Open a second terminal from the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open the local URL printed by Vite in the terminal (commonly `http://localhost:5173`).

The frontend API client is configured in the frontend source. If the backend is running on a different host or port, update the API base URL in the relevant frontend API configuration before running the application.

For a production build:

```bash
npm run build
```

For linting:

```bash
npm run lint
```

## Using the application

A typical workflow is:

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Sign in with a provisioned application account.
5. Import student, examination, and subject-wise attendance data as needed.
6. Review the import summary and resolve rejected rows where appropriate.
7. Explore dashboard, performance, attendance, and declining-performance analytics.
8. Review ML predictions for a student, subject, and target examination where sufficient historical data is available.
9. Ask the Academic Assistant questions about the retrieved academic data.
10. Generate reports and export supported reports to PDF or Excel.

The application requires a valid provisioned user account. Do not assume that a default username or password exists.

## Machine learning methodology

### Prediction objective

The ML workflow identifies students who may underperform in a target examination. The target is whether the next examination percentage is below **40%**.

### Input features

The training and prediction workflow uses historical information available before the target examination, including:

- Previous examination percentage.
- Historical average percentage.
- Marks trend.
- Number of previous examinations.
- Historical attendance percentage.
- Recent and previous attendance windows.
- Attendance trend.
- Attendance sessions available up to the prediction point.
- Class grade.

Student identifiers and future target-examination outcomes are not model input features.

### Training and evaluation

The development experiment used a chronological examination-based split:

| Split | Target examinations | Rows |
|---|---:|---:|
| Training | Examinations 2–4 | 3,600 |
| Validation | Examination 5 | 1,200 |
| Test | Examination 6 | 1,200 |

A Logistic Regression baseline was compared with a Random Forest model. Random Forest was selected based on validation F1-score.

Recorded Random Forest test metrics on the synthetic dataset:

| Metric | Result |
|---|---:|
| Accuracy | 0.9042 |
| Precision | 0.7093 |
| Recall | 0.7667 |
| F1-score | 0.7368 |
| ROC-AUC | 0.9518 |
| PR-AUC | 0.7983 |

Test confusion matrix:

```text
                 Predicted
                 Not at risk   At risk
Actual Not at risk     924        66
Actual At risk          49       161
```

The model's displayed underperformance score is an **uncalibrated model score**, not a calibrated probability of failure. The application also uses configured classification and risk-category thresholds; consult the ML methodology and model metadata for their definitions.

### Important ML limitations

- The evaluation dataset is synthetic. These metrics do not establish real-world school performance.
- The temporal split uses records from the same student cohort across different examination periods. It is not an independent-student generalization test.
- Historical marks were more influential than attendance in the recorded permutation-importance analysis. Attendance should not be described as a strong predictor based on this experiment.
- A prediction should not be treated as a final academic decision.
- Predictions should be withheld or qualified when required historical features are insufficient.

See [`docs/ml_methodology.md`](docs/ml_methodology.md) for the detailed methodology and evaluation notes.

## Generative AI Academic Assistant

The Academic Assistant uses the Groq API with the configured model:

```text
openai/gpt-oss-120b
```

The assistant retrieves relevant academic information through application services and structured database queries, then supplies that context to the language model to produce a natural-language answer.

Supported question areas include:

- Students with low marks and low attendance.
- Lowest-performing subjects.
- Declining examination performance.
- Explanations of a student's ML risk indicators.
- Teacher-intervention suggestions based on retrieved evidence.
- Missing-data and data-sufficiency questions.

### Grounding and safeguards

- Academic figures should come from retrieved application data.
- The assistant should not invent student names, marks, attendance percentages, or prediction outputs.
- General data-quality questions should not trigger an individual prediction.
- An individual prediction requires the relevant student, subject, and target examination.
- Model scores must be described as uncalibrated when applicable.
- Recommendations are decision support, not guaranteed outcomes.

The current design uses structured academic retrieval rather than a vector database. This is suitable for the application's relational student, examination, marks, and attendance data.

See [`docs/ai_methodology.md`](docs/ai_methodology.md) for retrieval, prompt, provider, and evaluation details.

## Reports and exports

The Reports module provides academic report views and supported export options. Available report categories include student, subject, class, and attendance reports.

Exports include:

- Excel (`.xlsx`)
- PDF (`.pdf`)

The contents of each report depend on the selected filters and the academic records available in the database.

## Testing

### Backend tests

From the backend directory, with the virtual environment activated and test configuration available:

```bash
pytest
```

To run with more detailed output:

```bash
pytest -v
```

### Frontend checks

From the frontend directory:

```bash
npm run lint
npm run build
```

The build command runs the TypeScript project build before the Vite production build.

### Manual verification

The application should also be checked through the UI and Swagger for:

- Login and protected API access.
- Invalid or unauthenticated requests.
- Valid and invalid CSV/Excel imports.
- Rejected rows and import history.
- Analytics filters and report generation.
- ML predictions with sufficient and insufficient historical data.
- AI answers grounded in retrieved academic records.
- General missing-data questions.
- PDF and Excel downloads.

Run the relevant tests in the current environment before reporting that all checks pass.

## API documentation

When the backend is running, use:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The API is organized under the versioned `/api/v1` route prefix. Swagger displays the registered endpoints, request schemas, authentication requirements, and response models.

Protected endpoints require a valid JWT access token obtained through the application's authentication flow.

## Security notes

- Keep `.env` files and API keys out of Git.
- Use a strong, unique JWT secret outside local development.
- Do not commit database passwords, access tokens, or real student personal information.
- Keep academic API routes protected by authentication and role-appropriate authorization.
- Scope academic queries to the authenticated institution where institution-level scoping is implemented.
- Use synthetic or explicitly authorized data for demonstrations.

## Limitations

1. **Synthetic data:** Demonstration records are generated data and must not be presented as real student observations.
2. **Model generalization:** The current temporal evaluation includes the same student cohort across examination periods. Further evaluation on independent students and real, authorized data is required before operational use.
3. **Uncalibrated score:** The model score is not a calibrated probability.
4. **Attendance relationship:** Observed attendance/marks associations do not prove that attendance causes a particular academic result.
5. **Historical data dependency:** Prediction quality depends on the availability and consistency of historical marks and subject-wise attendance.
6. **AI grounding:** AI responses depend on the accuracy, scope, and completeness of retrieved database records. Important decisions should be checked against the underlying records.
7. **Development configuration:** Local development settings and the Vite development server are not a production deployment configuration.

## Documentation

Additional technical documentation is maintained in the `docs/` directory:

- [`docs/architecture.md`](docs/architecture.md) — application architecture.
- [`docs/database_design.md`](docs/database_design.md) — database design and relationships.
- [`docs/ml_methodology.md`](docs/ml_methodology.md) — ML objective, features, training, evaluation, and limitations.
- [`docs/ai_methodology.md`](docs/ai_methodology.md) — AI provider, retrieval approach, and prompt strategy.

---

## License and academic use

This repository was developed as an individual technical assignment. Review the assignment's requirements for disclosure of AI-assisted development tools and third-party libraries. Add a license file only if a license has been selected for this repository.
