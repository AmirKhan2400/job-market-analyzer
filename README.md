# AI Job Market Analyzer

An AI-powered backend application for analyzing AI/ML job opportunities against a user's technical profile.

The project extracts structured information from job postings, evaluates skill compatibility, identifies skill gaps, and generates personalized recommendations.

It was built as a practical project for learning and demonstrating **production-oriented AI engineering, backend development, database design, testing, and containerized deployment**.

## Features

* Analyze AI/ML job postings against a user's profile
* Extract structured job information using an LLM
* Calculate skill matches between a job and user profile
* Identify missing or insufficient skills
* Generate an AI-powered recommendation and reason to apply
* Store analysis results in PostgreSQL
* Retrieve previously analyzed jobs
* Load user profiles from YAML
* Support multiple LLM providers
* Gemini as the primary LLM provider
* OpenRouter as an alternative LLM provider
* Automatic database migrations with Alembic
* Persistent PostgreSQL storage with Docker volumes
* Containerized application using Docker Compose
* Unit, integration, repository, service, and API tests

## Architecture

The application follows a layered architecture with separation between the API, business logic, domain models, persistence, and external AI providers.

```text
                        ┌─────────────────┐
                        │     Client      │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   FastAPI API   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    Services     │
                        │                 │
                        │ Analysis        │
                        │ Matching        │
                        │ Profile         │
                        │ Recommendation  │
                        └───────┬─────────┘
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │   AI Service    │         │  Repositories   │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ LLM Providers   │         │   PostgreSQL    │
        │                 │         │                 │
        │ Gemini          │         │ SQLAlchemy      │
        │ OpenRouter      │         │ Alembic         │
        └─────────────────┘         └─────────────────┘
```

The project separates external AI-provider implementations behind an abstraction, allowing the application to work with different LLM providers without coupling the business logic directly to a specific provider.

## Tech Stack

### Backend

* Python 3.13
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### AI

* Google Gemini
* OpenRouter
* LLM provider abstraction
* Prompt-based LLM processing

### Database

* PostgreSQL 17
* SQLAlchemy 2
* Psycopg 3
* Alembic

### Development

* uv
* pytest
* Ruff
* Docker
* Docker Compose

## How It Works

A typical analysis follows this flow:

```text
User Profile (YAML)
        │
        ▼
Job Posting
        │
        ▼
   FastAPI API
        │
        ▼
 Analysis Service
        │
        ├───────────────┐
        ▼               ▼
 Job Extraction     Profile Data
        │               │
        └───────┬───────┘
                ▼
          Match Service
                │
                ▼
       Missing Skills
                │
                ▼
    Recommendation Service
                │
                ▼
          AI Provider
                │
        ┌───────┴────────┐
        ▼                ▼
      Gemini         OpenRouter
                │
                ▼
        Analysis Result
                │
                ▼
           PostgreSQL
```

## Project Structure

```text
job-market-analyzer/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
├── uv.lock
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── f3884a0ce397_initial_schema.py
│
├── data/
├── docs/
│   └── diagrams/
├── examples/
│   └── profile.yaml
├── exports/
│
├── src/
│   └── job_market_analyzer/
│       ├── api/
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── database/
│       │   ├── models.py
│       │   └── session.py
│       ├── domain/
│       │   ├── analysis.py
│       │   ├── job.py
│       │   └── profile.py
│       ├── mappers/
│       │   └── analysis_mapper.py
│       ├── prompts/
│       │   └── recommendation.txt
│       ├── providers/
│       │   └── llm/
│       ├── repositories/
│       │   └── analysis_repository.py
│       ├── services/
│       │   ├── ai/
│       │   ├── analysis/
│       │   ├── match/
│       │   ├── profile/
│       │   └── recommendation/
│       ├── config.py
│       ├── dependencies.py
│       └── main.py
│
└── tests/
    ├── api/
    ├── integration/
    └── unit/
```

## Getting Started

### Requirements

* Python 3.13
* uv
* Docker
* Docker Compose

The project requires Python 3.13:

```text
>=3.13,<3.14
```

### 1. Clone the Repository

```bash
git clone https://github.com/AmirKhan2400/job-market-analyzer.git
cd job-market-analyzer
```

### 2. Configure Environment Variables

Create a `.env` file based on `.env.example`.

```bash
cp .env.example .env
```

Configure the required values:

```env
POSTGRES_PASSWORD=your_postgres_password

DATABASE_URL=postgresql+psycopg://postgres:your_postgres_password@localhost:5432/job_market_analyzer

GEMINI_API_KEY=your_gemini_api_key

OPENROUTER_API_KEY=your_openrouter_api_key
```

### 3. Install Dependencies

Using uv:

```bash
uv sync
```

### 4. Run the Application

```bash
uv run uvicorn job_market_analyzer.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

## API Documentation

The application provides interactive API documentation through FastAPI's Swagger UI.

Once the application is running, open:

```text
http://localhost:8000/docs
```

## Running with Docker

The project includes Docker and Docker Compose configuration for running the FastAPI application together with PostgreSQL.

Start the application:

```bash
docker compose up --build
```

The container architecture is:

```text
┌──────────────────────────────────┐
│          Docker Compose          │
│                                  │
│  ┌──────────────┐                │
│  │     App      │                │
│  │   FastAPI    │                │
│  └───────┬──────┘                │
│          │                       │
│          │ Docker Network        │
│          ▼                       │
│  ┌──────────────┐                │
│  │  PostgreSQL  │                │
│  └───────┬──────┘                │
│          │                       │
│          ▼                       │
│    postgres_data                 │
│       volume                     │
└──────────────────────────────────┘
```

### Persistent Database Storage

PostgreSQL uses a named Docker volume:

```text
postgres_data
```

The volume stores the PostgreSQL data outside the database container.

Therefore:

```text
Container deleted
       ↓
Volume remains
       ↓
Database data remains
```

Normal container recreation does not delete the database data.

To intentionally remove the database volume:

```bash
docker compose down -v
```

### Automatic Database Migrations

The application automatically runs:

```bash
alembic upgrade head
```

when the application container starts.

The startup flow is:

```text
Docker Compose starts
        ↓
PostgreSQL container starts
        ↓
PostgreSQL healthcheck
        ↓
PostgreSQL becomes healthy
        ↓
Application container starts
        ↓
alembic upgrade head
        ↓
Database schema is updated
        ↓
Uvicorn starts
```

Docker Compose uses a PostgreSQL healthcheck and waits for the database service to become healthy before starting the application.

## Database Migrations

Alembic is used to manage database schema changes.

Apply existing migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

Create a new migration after changing database models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

When running through Docker Compose, pending migrations are automatically applied when the application container starts.

## Testing

Run the complete test suite:

```bash
uv run pytest
```

The test suite is organized into:

```text
tests/
├── api/
├── integration/
└── unit/
```

Tests cover:

* API endpoints
* Domain logic
* Services
* Repositories
* AI services
* Gemini provider
* OpenRouter provider
* Profile handling
* Skill matching
* Recommendation generation

## Environment Variables

The application uses Pydantic Settings for configuration.

| Variable             | Description                        |
| -------------------- | ---------------------------------- |
| `POSTGRES_PASSWORD`  | PostgreSQL database password       |
| `DATABASE_URL`       | SQLAlchemy database connection URL |
| `GEMINI_API_KEY`     | Google Gemini API key              |
| `OPENROUTER_API_KEY` | OpenRouter API key                 |

The repository contains `.env.example` as a safe configuration template.

## Architecture Diagrams

Architecture documentation is available in:

```text
docs/diagrams/
```

The project currently includes:

* Component Architecture Diagram
* Application Flowchart

## Example Profile

An example YAML profile is provided at:

```text
examples/profile.yaml
```

This demonstrates the expected structure for a user's technical profile.

## Current Scope

The current version focuses on the backend and core job-analysis workflow.

The project is designed as a practical foundation for analyzing job opportunities and identifying the technical skills required to become a stronger candidate for AI engineering roles.

## Future Improvements

Potential future improvements include:

* Job board/API integrations
* Automated job collection
* More advanced skill normalization
* Historical market trend analysis
* Improved job ranking and prioritization
* Authentication and user accounts
* Background job processing
* Observability and structured logging
* Production deployment
* More comprehensive end-to-end testing

## License

This project is currently intended as a personal portfolio and learning project.
