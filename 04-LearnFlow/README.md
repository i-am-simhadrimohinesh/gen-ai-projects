# LearnFlow — Adaptive AI Learning Platform

LearnFlow is an adaptive AI-powered learning platform designed to help learners build skills through personalized learning journeys, structured roadmaps, topic-based learning content, and assessments.

## Features

- Create learning journeys based on subject, reason, goal, existing knowledge, and requested topics
- AI-generated learning roadmaps
- Topic-based learning
- AI-generated learning notes for each roadmap topic
- Parallel subtopic content generation using LangGraph
- Markdown-based learning content
- Download learning notes as text
- Topic completion tracking
- AI-generated 10-question MCQ assessments
- Assessment validation and retry
- Multiple assessments per journey
- Assessment history and re-attempts
- Automatic assessment evaluation
- Topic-level learner knowledge tracking
- Best-score based weak-topic identification
- Future assessments can prioritize weak topics
- PostgreSQL persistence
- LangSmith-compatible AI workflow development

## Architecture

```text
                         LearnFlow
                            │
             ┌──────────────┴──────────────┐
             │                             │
         Streamlit                    FastAPI
         Frontend                     Backend
             │                             │
             └────────────── HTTP ─────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              Journey Planner       Notes Generator       Assessment Generator
                    │                      │                      │
                 LangGraph              LangGraph              LangGraph
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
                                  LangChain Chat Model
                                           │
                                      Google Gemini
                                           │
                                      PostgreSQL
```

## Learning Flow

```text
Create Journey
      │
      ▼
Generate Roadmap
      │
      ▼
Select Roadmap Topic
      │
      ▼
Generate Subtopics
      │
      ▼
Generate Learning Content
      │
      ├── Subtopic 1 ──┐
      ├── Subtopic 2 ──┤
      ├── Subtopic 3 ──┤── Parallel generation
      └── Subtopic N ──┘
              │
              ▼
        Merge Content
              │
              ▼
        Learn Topic
              │
              ▼
      Mark Topic Complete
              │
              ▼
   Generate Assessment
              │
              ▼
        Submit Answers
              │
              ▼
       Evaluate Attempt
              │
              ▼
     Update Learner Knowledge
              │
              ▼
 Future Assessments Prioritize
       Weak Topics
```

## Project Structure

```text
learnflow/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workflows/
│   │       ├── journey_planner/
│   │       ├── notes_generator/
│   │       └── assessment_generator/
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── app.py
│   ├── api_client.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- LangChain
- LangGraph
- Google Gemini
- LangSmith
- Uvicorn

### Frontend

- Streamlit

### Development

- Pytest
- Docker
- Git

## AI Workflow Design

### Journey Planner

Generates and validates a roadmap based on the learner's requirements.

```text
START
  │
  ▼
Generate Roadmap
  │
  ▼
Validate Roadmap
  │
  ├── Valid ──────► END
  │
  └── Invalid ────► Retry
```

### Notes Generator

Learning content is generated lazily when the learner selects a roadmap topic.

The workflow first creates focused subtopics and then generates content for those subtopics independently. The generated content is finally merged in the original subtopic order.

```text
START
  │
  ▼
Generate Subtopics
  │
  ├──── Subtopic 1 ────┐
  ├──── Subtopic 2 ────┤
  ├──── Subtopic 3 ────┤
  └──── Subtopic N ────┘
                       │
                       ▼
                Merge Content
                       │
                       ▼
                    Validate
                       │
                       ▼
                     END
```

The parallel generation uses LangGraph node execution. It does not use the Gemini Batch API.

### Assessment Generator

Assessments are generated only from topics that the learner has completed.

```text
Completed Topics
      │
      ▼
Assessment Context
      │
      ├── Completed Topics
      └── Weak Topics
              │
              ▼
      Generate 10 MCQs
              │
              ▼
        Validate
              │
       ┌──────┴──────┐
       │             │
     Valid         Invalid
       │             │
       ▼             ▼
      END           Retry
```

## Assessment Model

An assessment represents a fixed generated question set.

An attempt represents one submission against that question set.

```text
Journey
  │
  └── Assessments
        │
        ├── Assessment Questions
        │
        └── Assessment Attempts
              │
              └── Assessment Answers

Journey
  │
  └── Learner Knowledge
```

Every submitted attempt is stored.

Learner knowledge stores the best score achieved for each topic rather than replacing the learner's knowledge with a lower score from a later attempt.

## Configuration

Create a `.env` file based on `.env.example`.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
DATABASE_URL=postgresql://username:password@localhost:5432/learnflow
```

Do not commit `.env` or API keys to Git.

## Running Locally

### 1. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create `.env` in the project root and configure the required database and Gemini settings.

### 4. Start the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

FastAPI will be available at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

### 5. Install frontend dependencies

Open another terminal:

```bash
cd frontend
python -m pip install -r requirements.txt
```

### 6. Start the frontend

```bash
streamlit run app.py
```

## Running Tests

From the project root:

```bash
python -m pytest
```

Backend tests are located under:

```text
backend/tests/
```

## Docker

Docker support is included for running the frontend, backend, and PostgreSQL as separate services.

```text
                    Docker Compose
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
     Frontend         Backend       PostgreSQL
    Streamlit         FastAPI
```

Build and start the services with:

```bash
docker compose up --build
```

## Design Principles

1. **Keep workflows focused** — Each LangGraph workflow has a specific responsibility.
2. **Use deterministic logic where possible** — Validation, persistence, scoring, and business rules are handled by application code.
3. **Use AI where it adds value** — LLMs handle roadmap, learning content, and assessment generation.
4. **Generate learning content lazily** — Topic notes are generated when needed instead of generating the entire journey upfront.
5. **Preserve generated data** — Generated assessments are stored as fixed question sets so historical attempts remain consistent.
6. **Minimize unnecessary context** — New assessments use completed-topic and weak-topic information rather than previous assessment questions.
7. **Keep the architecture simple** — The project avoids unnecessary abstraction layers while remaining suitable for future growth.

## Future Enhancements

- AI Tutor
- Audio-based interaction
- Richer learning progress tracking
- Additional learning resources
- More advanced adaptive assessment strategies
- Multi-user support
- Production deployment and monitoring

## License

This project is currently intended as a learning and portfolio project.
