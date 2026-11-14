# AI Methodology – School Intelligence

## 1. Overview

The School Intelligence platform includes a Generative AI-powered Academic Assistant.

The purpose of the assistant is to help teachers and administrators understand academic information using natural-language questions.

The assistant can support questions related to:

- Student academic performance.
- Subject-wise examination results.
- Attendance information.
- Academic performance trends.
- Students who may need academic support.
- Machine learning prediction explanations.
- Teacher intervention suggestions.
- Missing or insufficient academic information.

The application uses the Groq API as its language-model provider.

The AI assistant is designed to generate responses using academic information retrieved from the application's PostgreSQL database and backend services.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL |
| Database access | SQLAlchemy |
| AI provider | Groq |
| Language model | `openai/gpt-oss-120b` |
| Academic retrieval | SQL queries and backend services |
| Entity resolution | Custom Python service |
| Authentication | JWT |
| Configuration | Environment variables |

The language model and API configuration are managed through application settings.

The Groq API key is stored in the backend environment configuration and must not be exposed in frontend code or committed to the repository.

## 3. AI Assistant Architecture

The Academic Assistant follows a retrieval-before-generation workflow.

The main processing stages are:

1. The user submits a natural-language academic question.
2. The FastAPI endpoint authenticates the request.
3. The academic retrieval service identifies the type of question.
4. Entity resolution identifies relevant academic entities such as students, subjects, examinations and academic periods.
5. The appropriate backend service retrieves relevant academic information from PostgreSQL.
6. The retrieved information is passed to the language model as context.
7. The language model generates a natural-language explanation.
8. The API returns the response to the frontend.

### Processing flow

```text
User Question
     |
     v
FastAPI AI Assistant Endpoint
     |
     v
Authentication and User Context
     |
     v
Academic Retrieval Service
     |
     v
Intent Identification
     |
     v
Entity Resolution
     |
     v
Academic Database / Backend Services
     |
     v
Retrieved Academic Context
     |
     v
Groq Language Model
     |
     v
Grounded Natural-Language Response
```

## 4. Retrieval Methodology

The application uses structured academic retrieval through PostgreSQL and backend services.

It does not depend on a vector database for the current Academic Assistant implementation.

Academic information is retrieved using SQL queries and application-level retrieval logic.

The retrieval process is responsible for selecting the relevant records before the language model generates an answer.

### Retrieved information may include

- Student examination marks.
- Subject-wise academic performance.
- Historical academic averages.
- Attendance summaries.
- Academic period information.
- Examination details.
- ML prediction features and results.
- Data sufficiency information.

The academic support service uses SQL-based aggregation to combine relevant marks and attendance information where required.

## 5. Intent Identification

The academic retrieval service identifies the purpose of the user's question and routes it to the appropriate retrieval workflow.

Examples of supported question categories include:

| Question category | Purpose |
|---|---|
| Student performance | Retrieve examination and subject performance |
| Attendance analysis | Retrieve attendance summaries |
| Academic trends | Analyze historical performance |
| ML prediction explanation | Retrieve prediction results and model-related information |
| Academic data quality | Explain missing or insufficient academic information |
| Teacher intervention | Generate recommendations based on retrieved academic evidence |

Correct intent identification is important because different questions require different academic data.

For example, a question asking why a particular student was flagged by the ML model must retrieve the student's prediction information rather than only retrieving general attendance analytics.

## 6. Entity Resolution

Entity resolution identifies the academic entities mentioned in the user's question.

The application includes an entity resolution service for identifying:

- Academic periods.
- Classes.
- Students.
- Subjects.
- Examinations.

Examples:

- A student can be identified using an admission number or full name.
- A subject can be identified using its name or code.
- A class can be resolved using grade and section information.
- An examination can be resolved using its name and available examination information.
- An academic period can be resolved using its year information.

Resolved entities are validated against the authenticated user's institution context before institution-scoped academic information is retrieved.

If the required entity cannot be resolved, the assistant should request clarification instead of inventing an entity.

## 7. Academic Context and Prompt Design

The retrieved academic information is supplied to the language model as context.

The assistant uses system instructions to guide the model to:

1. Answer using the retrieved academic information.
2. Avoid inventing student records or academic statistics.
3. Explain when information is missing or insufficient.
4. Distinguish actual academic values from model scores.
5. Avoid interpreting an uncalibrated model score as a guaranteed probability.
6. Provide explanations relevant to the user's academic question.
7. Present recommendations as suggestions rather than guaranteed outcomes.

The language model is responsible for explaining retrieved information in natural language. It is not the source of truth for academic records.

## 8. Machine Learning Integration

The AI assistant can explain academic underperformance predictions using information retrieved through the ML prediction workflow.

The prediction explanation can include:

- Previous examination percentage.
- Historical average percentage.
- Marks trend.
- Historical attendance percentage.
- Recent attendance information.
- Previous examination count.
- Underperformance classification.
- Model score.
- Risk category.
- Risk indicators.
- Positive indicators.
- Data sufficiency information.

The assistant must distinguish between:

- The model's classification.
- The uncalibrated model score.
- The configured classification threshold.
- The underlying historical academic features.

The model score must not be described as a verified probability.

## 9. Missing and Insufficient Data Handling

The assistant must identify when the requested academic information is unavailable or insufficient.

Examples include:

- No student identified in the question.
- Student records cannot be resolved.
- No historical examination marks are available.
- Attendance records are missing.
- Required prediction features cannot be generated.
- The target examination cannot be identified.

For an individual ML prediction, the assistant needs the relevant student, subject, target examination and sufficient historical information.

When these requirements are not satisfied, the assistant should explain what information is missing and avoid presenting an unsupported prediction.

## 10. Teacher Intervention Recommendations

The Academic Assistant can provide suggested interventions based on retrieved academic evidence.

Examples include:

- Subject-specific revision support.
- Additional practice exercises.
- Regular progress monitoring.
- Attendance follow-up.
- Targeted teacher support.
- Communication with parents or guardians where appropriate.

Recommendations must be related to the retrieved academic context.

They should be reviewed by teachers and administrators before being applied.

## 11. API Integration

The Academic Assistant is exposed through the authenticated FastAPI endpoint:

`POST /api/v1/ai/academic-assistant`

The endpoint receives a user's academic question, processes the retrieval workflow and returns an AI-generated response.

The frontend communicates with this endpoint through the application's API service.

Authentication is required to access the protected endpoint.

## 12. Configuration

The AI provider settings are maintained in the backend configuration.

Relevant settings include:

- `GROQ_API_KEY`
- `GROQ_MODEL`
- `GROQ_MAX_TOKENS`

The API key must be configured through the backend environment file.

Secrets must not be committed to Git or included in documentation.

## 13. Limitations

1. AI response quality depends on the accuracy and completeness of retrieved academic information.
2. Incorrect intent identification can result in retrieval of irrelevant information.
3. Entity resolution may require clarification when names or examination details are ambiguous.
4. The language model may occasionally produce incomplete or incorrectly interpreted explanations.
5. The assistant cannot reliably answer questions when required academic records are unavailable.
6. Groq API availability and configuration affect AI response generation.
7. AI-generated recommendations are suggestions and do not guarantee improved academic performance.
8. The assistant is not a replacement for teacher or administrator judgment.

## 14. Conclusion

The School Intelligence Academic Assistant combines structured academic data retrieval with Generative AI.

SQL-based retrieval provides the academic information, while the Groq language model converts the retrieved context into understandable explanations and recommendations.

This design keeps academic records grounded in the application's database and helps teachers and administrators interact with academic information through natural language.