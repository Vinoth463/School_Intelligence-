# School Intelligence – API Documentation

## 1. Overview

School Intelligence provides a RESTful API built using FastAPI. The API supports academic data management, performance analytics, attendance analytics, machine learning predictions, Generative AI assistance, and report generation.

**Backend:** FastAPI  
**Database:** PostgreSQL  
**ORM:** SQLAlchemy 2.x  
**Authentication:** JWT Bearer Authentication  
**API Version:** v1

### Base URL

```text
http://127.0.0.1:8000
```

### API Base Path

```text
/api/v1
```

### Interactive API Documentation

When the backend is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Swagger UI provides the registered endpoint schemas, request parameters, authentication requirements, and response examples.

---

## 2. Authentication

The application uses JSON Web Tokens (JWT) to protect academic information and API operations.

### Login

**Endpoint:**

```http
POST /api/v1/auth/login
```

**Purpose:**

Authenticates an application user and generates an access token.

**Request:**

Submit the login credentials using the request format defined by the authentication schema in Swagger.

**Successful response:**

Returns an access token and authentication information.

### Get Current User

**Endpoint:**

```http
GET /api/v1/auth/me
```

**Purpose:**

Returns information about the currently authenticated user.

**Authentication:** Required.

### Authorization Header

Protected endpoints require a valid JWT access token.

```http
Authorization: Bearer <access_token>
```

### Authentication Responses

| HTTP Status | Description |
|---|---|
| 200 | Request authenticated successfully |
| 401 | Missing or invalid authentication |
| 403 | Authenticated user does not have the required permission |

---

## 3. Dashboard API

### Get Dashboard Overview

**Endpoint:**

```http
GET /api/v1/dashboard/overview
```

**Purpose:**

Retrieves the main academic dashboard summary.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| academic_period_id | Integer | No | Filters dashboard information by academic period |

**Example:**

```http
GET /api/v1/dashboard/overview?academic_period_id=1
```

**Information returned includes:**

- Total students
- Average academic performance
- Total examination mark records
- Total attendance sessions
- Present and absent attendance counts
- Overall attendance percentage
- Academic-period performance summaries

**Authentication:** Required.

---

## 4. Academic Performance Analytics API

Base path:

```text
/api/v1/analytics
```

These endpoints provide student-wise, subject-wise, examination-wise, and academic-period performance information.

### Subject Performance

```http
GET /api/v1/analytics/subjects
```

**Purpose:**

Retrieves subject-level academic performance analytics.

Supports available filters for academic period, examination, and class.

### Student Performance

```http
GET /api/v1/analytics/students/{student_id}/performance
```

**Purpose:**

Retrieves an individual student's academic performance.

Information may include:

- Examination results
- Subject-wise marks
- Academic percentages
- Examination performance trends
- Academic-period information

### Declining Performance

```http
GET /api/v1/analytics/declining-performance
```

**Purpose:**

Identifies declining performance across consecutive examinations.

### Subject-wise Declining Performance

```http
GET /api/v1/analytics/declining-performance/subjects
```

**Purpose:**

Identifies declining performance at subject level.

### Authentication

All academic analytics endpoints require authentication and apply institution-scoped data access.

---

## 5. Attendance Analytics API

Base path:

```text
/api/v1/analytics
```

These endpoints analyze attendance records at student, class, and subject levels.

### Class Attendance

```http
GET /api/v1/analytics/attendance/classes
```

**Purpose:**

Retrieves attendance summaries for classes.

### Low Attendance Students

```http
GET /api/v1/analytics/attendance/low-attendance
```

**Purpose:**

Identifies students whose attendance is below the configured threshold.

### Student Attendance

```http
GET /api/v1/analytics/attendance/students
```

**Purpose:**

Retrieves student-level attendance information.

### Subject Attendance

```http
GET /api/v1/analytics/attendance/subjects
```

**Purpose:**

Retrieves subject-wise attendance analytics.

### Attendance and Academic Performance Analysis

```http
GET /api/v1/analytics/attendance/performance-analysis
```

**Purpose:**

Analyzes the relationship between attendance and academic performance.

The analysis helps identify patterns between attendance percentages and examination marks.

**Important:** A statistical association between attendance and marks does not establish causation.

---

## 6. Machine Learning Prediction API

The ML prediction module uses historical examination marks and subject-wise attendance features to identify students who may underperform in a target examination.

The prediction workflow uses the trained Random Forest model.

### Prediction Information

The prediction workflow requires:

- Student ID
- Subject ID
- Target examination ID

**Purpose:**

Generates an individual examination underperformance prediction using historical academic features.

The prediction response includes information such as:

- Predicted underperformance status
- Model score
- Classification threshold
- Risk category
- Risk indicators
- Positive indicators
- Historical academic features
- Data sufficiency status
- Data quality warnings

**Important:** The displayed model score is uncalibrated and must not be interpreted as a verified probability of failure.

The prediction workflow is accessed through the AI academic retrieval integration in the current implementation. Refer to the registered Swagger endpoints for the exact API route and request schema.

---

## 7. AI Academic Assistant API

### Ask Academic Assistant

**Endpoint:**

```http
POST /api/v1/ai/academic-assistant
```

**Purpose:**

Answers academic questions using retrieved information from the application's database and academic analytics services.

The assistant integrates the Groq API to generate natural-language explanations based on retrieved academic context.

### Supported Question Categories

Examples include:

1. Students with low marks and low attendance in a subject.
2. Subjects with the lowest average performance.
3. Students with declining examination performance.
4. Explanations of individual ML risk predictions.
5. Teacher intervention recommendations.
6. Questions about incomplete academic data and prediction reliability.

### Retrieval Approach

The AI assistant uses structured academic retrieval and database queries.

The retrieval process:

1. Receives the user's academic question.
2. Resolves relevant academic entities and filters.
3. Retrieves the required academic records.
4. Generates ML predictions when the question requires an individual prediction and the required entities are available.
5. Supplies retrieved academic context to the Groq model.
6. Generates a natural-language response.

### Grounding and Data Safety

- Numerical responses should be grounded in retrieved academic records.
- The assistant must not invent student marks or attendance percentages.
- Missing or insufficient information must be identified.
- Individual predictions require the relevant student, subject, and target examination.
- Risk explanations must distinguish model indicators from proven causes.
- Teacher recommendations are suggestions, not guaranteed outcomes.

**Authentication:** Required.

---

## 8. Import Management API

Base path:

```text
/api/v1/imports
```

The Import Management module supports academic data uploads and import-history tracking.

### Import Students

```http
POST /api/v1/imports/students
```

**Purpose:**

Uploads student information using a supported CSV or Excel file.

### Import Examination Marks

```http
POST /api/v1/imports/marks
```

**Purpose:**

Uploads examination mark records with the required academic references.

### Import Attendance

```http
POST /api/v1/imports/attendance
```

**Purpose:**

Uploads subject-wise student attendance records.

### Get Import History

```http
GET /api/v1/imports/history
```

**Purpose:**

Retrieves previous import operations and their summaries.

### Get Import Rejections

```http
GET /api/v1/imports/{import_id}/rejections
```

**Purpose:**

Retrieves rejected records and their validation reasons for a particular import.

### Import Validation

The import workflow validates:

- Required fields
- Data types
- Duplicate records
- Invalid values
- Missing academic references
- Student, class, subject, and examination relationships

Import results include accepted and rejected row counts and rejection details.

File uploads use multipart form data.

**Authentication:** Required.

---

## 9. Reports and Export API

Base path:

```text
/api/v1/reports
```

The Reports module provides academic reports and downloadable exports.

### Report Overview

```http
GET /api/v1/reports/overview
```

**Purpose:**

Retrieves report overview information.

### Student Report

```http
GET /api/v1/reports/students/{student_id}
```

**Purpose:**

Retrieves an individual student's academic report.

### Subject Report

```http
GET /api/v1/reports/subjects
```

**Purpose:**

Retrieves subject-level report information.

### Class Report

```http
GET /api/v1/reports/classes
```

**Purpose:**

Retrieves class-level report information.

### Attendance Report

```http
GET /api/v1/reports/attendance
```

**Purpose:**

Retrieves attendance report information.

### Export Excel Report

```http
GET /api/v1/reports/export/excel
```

**Purpose:**

Generates a downloadable Excel report.

### Export PDF Report

```http
GET /api/v1/reports/export/pdf
```

**Purpose:**

Generates a downloadable PDF report.

### Report Filter Options

```http
GET /api/v1/reports/filter-options
```

**Purpose:**

Retrieves available report filter options.

Report filters and response details depend on the endpoint and selected parameters. Refer to Swagger for the exact request schema.

---

## 10. HTTP Status Codes

The API uses standard HTTP response status codes.

| Status Code | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created successfully, where applicable |
| 400 | Invalid request |
| 401 | Authentication required or invalid |
| 403 | Access forbidden |
| 404 | Requested resource not found |
| 422 | Request validation failed |
| 500 | Internal server error |

---

## 11. Security and Data Access

The API uses:

- JWT-based authentication.
- Argon2 password hashing.
- Protected academic endpoints.
- Role-based authorization where configured.
- Institution-scoped academic data retrieval.
- Environment variables for database credentials and provider API keys.

Sensitive credentials and student personal information must not be exposed in API logs, source control, or public documentation.

---

## 12. Testing API Endpoints

The API can be tested through Swagger UI.

**Steps:**

1. Start the FastAPI backend.
2. Open `http://127.0.0.1:8000/docs`.
3. Authenticate using the application's login flow.
4. Use the Authorize option to provide the JWT access token.
5. Select the required API endpoint.
6. Enter the required path parameters, query parameters, or request body.
7. Execute the request.
8. Review the response status and returned data.

Important test cases include:

- Successful authenticated requests.
- Requests without authentication.
- Invalid request parameters.
- Invalid file uploads.
- Missing academic references.
- Insufficient historical data for ML predictions.
- AI questions with missing academic information.
- Report generation and file downloads.

---

## 13. API Design Summary

The School Intelligence API follows a modular architecture.

| API Module | Responsibility |
|---|---|
| Authentication | Login and current-user information |
| Dashboard | Academic overview and summary |
| Analytics | Student, subject, and declining-performance analysis |
| Attendance | Attendance and performance relationship analysis |
| Imports | Academic data uploads and validation |
| AI Assistant | Academic question answering using retrieved data |
| Reports | Academic reports and PDF/Excel exports |
| Machine Learning | Historical feature processing and underperformance predictions |

The complete and current API contract, including registered routes, request schemas, query parameters, response models, and authentication requirements, is available through the FastAPI Swagger documentation at `/docs`.