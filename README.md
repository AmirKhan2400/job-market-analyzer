# AI Job Market Analyzer

An AI-powered full-stack application for analyzing AI/ML job opportunities against a user's technical profile.

The project extracts structured information from job postings, evaluates skill compatibility, identifies missing required and preferred skills, generates personalized recommendations, stores analysis history, and provides a React frontend for interactive use.

It was built as a practical project for learning and demonstrating **production-oriented AI engineering, backend development, frontend development, database design, LLM evaluation, testing, containerized deployment, and static frontend hosting**.

## Live Demo

You can try the frontend demo here:

[Try AI Job Market Analyzer](https://amirkhan2400.github.io/job-market-analyzer/)

The demo allows users to submit a job description, enter a candidate profile, analyze skill matches, view missing skills, receive an AI-powered recommendation, and review previous analyses through anonymous per-visitor history.

## Features

* Analyze AI/ML job postings against a user's profile
* Interactive React frontend for job analysis and history review
* Persist user profile data in the browser so users do not re-enter it every time
* Searchable multi-select skill selector with canonical skill values
* Extract structured job information using LLMs
* Separate required skills and preferred skills during extraction
* Calculate skill matches between a job and user profile
* Identify missing required and preferred skills
* Generate an AI-powered recommendation and reason to apply
* Store analysis results in PostgreSQL
* Retrieve anonymous per-visitor analysis history using a server-issued visitor cookie
* Support multiple LLM providers through an AI provider abstraction
* Requesty as the primary AI gateway
* Requesty Fallback Policy support for model-level routing
* Dedicated Requesty policy for job extraction
* OpenRouter Preset support for gateway-level fallback routing
* Dedicated OpenRouter preset for job extraction
* Strict structured-output JSON Schema handling for compatible providers
* Optional Telegram notification support for Gemini request failures
* LLM benchmark/evaluation subsystem under `evals/`
* Per-model benchmark configuration for max tokens, pricing, reasoning, and parameter requirements
* Automatic database migrations with Alembic
* Persistent PostgreSQL storage with Docker volumes
* Containerized backend using Docker Compose
* Frontend prepared for GitHub Pages deployment
* Unit, integration, repository, service, API, frontend, and eval-related tests

## Architecture

The application follows a layered architecture with separation between the frontend, API, business logic, domain models, persistence, and external AI providers.

```text
                        ┌─────────────────┐
                        │  React Frontend │
                        │  Vite + TS      │
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
        │ Requesty        │         │ SQLAlchemy      │
        │ OpenRouter      │         │ Alembic         │
        └─────────────────┘         └─────────────────┘
```

The project separates external AI-provider implementations behind an abstraction, allowing the application to work with different LLM providers without coupling the business logic directly to a specific provider.

Requesty is used as the primary AI gateway. The application sends job extraction to a dedicated Requesty Fallback Policy, while recommendation generation can use a separate general policy. The ordered model chain is maintained in the Requesty dashboard, so changing model priority or replacing models does not require an application deployment.

OpenRouter remains as an application-level gateway fallback. OpenRouter job extraction uses a dedicated dashboard preset, while recommendation generation can use a separate general preset. This is separate from Requesty's model-level fallback: Requesty can move between models inside one policy, while `AIService` can fall back to OpenRouter if the Requesty gateway itself is unavailable or fails.

The frontend communicates with the backend through a configurable API base URL. In local development it uses the Vite dev proxy, while production builds can point to a deployed backend server.

## Tech Stack

### Backend

* Python 3.13
* FastAPI
* Uvicorn
* Pydantic
* Pydantic Settings

### Frontend

* React
* TypeScript
* Vite
* React Router
* Tailwind CSS
* oxlint

### AI

* Requesty
* OpenRouter
* LLM provider abstraction
* Prompt-based LLM processing
* Strict structured output using JSON Schema
* LLM benchmarking and evaluation utilities

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
* npm
* GitHub Pages
* GitHub Actions

## How It Works

A typical analysis follows this flow:

```text
User Profile
        │
        ▼
React Frontend
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
     Requesty        OpenRouter
                │
                ▼
        Analysis Result
                │
                ▼
           PostgreSQL
                │
                ▼
       Analysis History
```

The user enters a job description and profile information in the frontend. The backend extracts structured job information, compares the job requirements against the user profile, calculates skill match results, generates a recommendation, and stores the result.

For anonymous history, the API boundary reads or creates a visitor cookie and passes only the resolved visitor identifier into the service layer. HTTP-specific objects remain outside the domain, repository, and service layers.

## Getting Started

### Requirements

* Python 3.13
* uv
* Docker
* Docker Compose
* Node.js 20+
* npm

The backend requires Python 3.13:

```text
>=3.13,<3.14
```

### 1. Clone the Repository

```bash
git clone https://github.com/AmirKhan2400/job-market-analyzer.git
cd job-market-analyzer
```

### 2. Configure Environment Variables

Create a backend `.env` file based on `.env.example`.

```bash
cp .env.example .env
```

Configure the required values:

```env
POSTGRES_PASSWORD=your_postgres_password

DATABASE_URL=postgresql+psycopg://postgres:your_postgres_password@localhost:5432/job_market_analyzer

REQUESTY_API_KEY=your_requesty_api_key
REQUESTY_POLICY=policy/job-analyzer
REQUESTY_EXTRACTION_POLICY=policy/Job-Market-Analyzer

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_PRESET=@preset/job-analyzer
OPENROUTER_EXTRACTION_PRESET=@preset/job-market-analyzer-job-extraction

BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
VISITOR_COOKIE_SECURE=false
VISITOR_COOKIE_SAMESITE=lax

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Create a frontend `.env` file from the frontend example:

```bash
cd frontend
cp .env.example .env
```

For local frontend development:

```env
VITE_API_BASE_URL=/api
VITE_BASE_PATH=/
```

For GitHub Pages deployment:

```env
VITE_API_BASE_URL=https://your-backend-domain.com/api
VITE_BASE_PATH=/job-market-analyzer/
```

### 3. Install Dependencies

Backend dependencies:

```bash
uv sync
```

Frontend dependencies:

```bash
cd frontend
npm install
```

### 4. Run the Application

Run the backend:

```bash
uv run uvicorn job_market_analyzer.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Run the frontend:

```bash
cd frontend
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

In local development, the frontend sends requests to `/api`, and Vite proxies those requests to the backend at `http://127.0.0.1:8000`.

## API Documentation

The application provides interactive API documentation through FastAPI's Swagger UI.

Once the backend is running, open:

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

## LLM Evaluation and Benchmarking

The project includes a standalone evaluation subsystem under:

```text
evals/
```

This subsystem was built to compare LLMs for the specific workloads used by the application instead of choosing models based only on popularity or general benchmark scores.

The evaluation system focuses on two application tasks:

* **Job extraction**: converting raw job descriptions into structured `JobOffer` data
* **Recommendation generation**: producing concise advice based on the user's match result

For job extraction, the benchmark uses a manually reviewed dataset of real AI/ML job postings. Each case contains the original job description and expected required/preferred skills. The evaluator sends each case to the selected models, validates the structured JSON output, compares extracted skills against the expected ground truth, and records metrics such as:

* schema validity rate
* required skills precision
* required skills recall
* required skills F1
* preferred skills precision
* preferred skills recall
* preferred skills F1
* combined skills F1
* latency
* token usage
* estimated cost

The benchmark runner stores detailed outputs for analysis, including raw model responses, parsed predictions, summary CSV files, charts, and markdown reports.

```text
evals/results/
├── extraction_raw.csv
├── extraction_predictions.jsonl
├── extraction_summary.csv
├── model_summary.csv
├── report.md
└── charts/
```

The evaluation results were used to make routing decisions for the production AI gateways. Instead of hardcoding one model directly in the application, the best-performing models and fallback order are configured through:

* Requesty Fallback Policies
* OpenRouter Presets

This allows the application code to stay stable while model routing can be adjusted from the provider dashboards based on measured extraction quality, reliability, latency, and cost.

The benchmark also helped identify practical production issues, including:

* models that do not reliably support strict JSON Schema output
* providers that return empty or truncated responses
* models with poor required/preferred skill extraction accuracy
* high-latency or high-cost models
* OpenRouter routing failures when required parameters are unsupported

Based on the benchmark results, job extraction uses a dedicated Requesty policy and OpenRouter preset optimized for structured extraction quality:

```env
REQUESTY_EXTRACTION_POLICY=policy/Job-Market-Analyzer
OPENROUTER_EXTRACTION_PRESET=@preset/job-market-analyzer-job-extraction
```

This keeps job extraction separate from recommendation generation, because extraction is a structured-output task while recommendation generation is a natural-language generation task.

The evaluation subsystem is intentionally separate from the production FastAPI application. Production code does not import from `evals/`, and evaluation tools do not add API routes, database tables, or runtime behavior to the deployed app.

## Testing

Run the complete backend test suite:

```bash
uv run pytest
```

Run backend linting:

```bash
uv run ruff check .
```

Run frontend linting:

```bash
cd frontend
npm run lint
```

Build the frontend:

```bash
cd frontend
npm run build
```

The test suite is organized into:

```text
tests/
├── api/
├── evals/
├── integration/
├── services/
└── unit/
```

Tests cover:

* API endpoints
* Domain logic
* Services
* Repositories
* AI services
* Requesty provider
* OpenRouter provider
* Profile handling
* Skill matching
* Recommendation generation
* Anonymous visitor history
* Strict structured-output schema generation
* LLM evaluation utilities
* Benchmark runner behavior

## Environment Variables

The application uses Pydantic Settings for backend configuration.

| Variable | Description |
| --- | --- |
| `POSTGRES_PASSWORD` | PostgreSQL database password |
| `DATABASE_URL` | SQLAlchemy database connection URL |
| `REQUESTY_API_KEY` | Requesty API key |
| `REQUESTY_POLICY` | Requesty recommendation/general Fallback Policy name |
| `REQUESTY_EXTRACTION_POLICY` | Requesty job-extraction Fallback Policy name |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OPENROUTER_PRESET` | OpenRouter recommendation/general dashboard preset name |
| `OPENROUTER_EXTRACTION_PRESET` | OpenRouter job-extraction dashboard preset name |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `VISITOR_COOKIE_SECURE` | Whether visitor cookies require HTTPS |
| `VISITOR_COOKIE_SAMESITE` | SameSite policy for visitor cookies |
| `TELEGRAM_BOT_TOKEN` | Optional Telegram bot token for failure notifications |
| `TELEGRAM_CHAT_ID` | Optional Telegram chat ID for failure notifications |

Frontend configuration uses Vite environment variables.

| Variable | Description |
| --- | --- |
| `VITE_API_BASE_URL` | Backend API base URL used by the frontend |
| `VITE_BASE_PATH` | Base path used when building the frontend for static hosting |

The repository contains `.env.example` files as safe configuration templates.

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

The frontend also provides a simple profile form for interactive analysis. Profile data is persisted in the browser so users do not need to re-enter their name and skills every time.

## Current Scope

The current version focuses on the core full-stack job-analysis workflow:

* interactive frontend
* job extraction
* skill matching
* recommendation generation
* anonymous per-visitor history
* PostgreSQL persistence
* LLM provider routing
* benchmark/evaluation tooling
* local Docker-based development
* frontend deployment through GitHub Pages

The project is designed as a practical foundation for analyzing job opportunities and identifying the technical skills required to become a stronger candidate for AI engineering roles.

## Future Improvements

Potential future improvements include:

* Job board/API integrations
* Automated job collection
* More advanced skill normalization and alias matching
* Historical market trend analysis
* Improved job ranking and prioritization
* Authentication and user accounts
* Background job processing
* Observability and structured logging
* Production backend deployment hardening
* More comprehensive end-to-end testing
* LLM-as-judge evaluation for recommendation quality
* Exportable reports for analyzed jobs
* Admin dashboard for benchmark comparison

## License

This project is currently intended as a personal portfolio and learning project.
