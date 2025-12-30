# Job Search Agent

An AI-powered job search assistant designed to extract intent from CVs, find relevant job opportunities, and optimize applications. Specifically tailored for the Azerbaijan job market.

## 🚀 Architecture Overview

The project follows a modular architecture using **LangGraph** for stateful orchestration and a **Gateway** pattern for LLM management.

```text
src/job_search_agent/
├── api/                    # FastAPI implementation
├── core/
│   ├── llm_gateways/       # LLM management (Cost Control, Routing, Observability)
│   │   ├── gateway.py      # Main LLM Gateway
│   │   ├── cost_controller.py # Budget and usage tracking
│   │   └── observability.py # LangSmith & structured logging
│   └── orchestration/      # LangGraph workflow logic
│       ├── agents/         # Specialized AI Agents (Resume, Ranking, Optimizer)
│       ├── graph.py        # LangGraph state and node definitions
│       └── orchestrator.py # High-level orchestration wrapper
├── models/                 # Pydantic data models (JobVacancy, Resume, etc.)
├── configs/                # Application settings and environment management
└── utils/                  # Shared helper functions (Cosine Similarity, etc.)
```

## 🛠 Key Features

### 1. Stateful Orchestration (LangGraph)
The application uses a directed graph to manage the job search workflow:
- **Parse CV**: Extracts structured data from raw text.
- **Rank Jobs**: Searches and ranks vacancies using multilingual embeddings.
- **Optimize Job**: Generates tailored cover letters and CV improvement tips.

### 2. LLM Gateway & Cost Control
- **Model Routing**: Automatically routes requests to different models (Gemini 1.5 Flash/Pro) based on complexity.
- **Budget Enforcement**: Tracks token usage and enforces a daily USD budget to prevent unexpected costs.
- **Observability**: Integrated with **LangSmith** for full-trace debugging and performance monitoring.

### 3. Multilingual Support
- Optimized for the **Azerbaijan job market**.
- Supports CVs and job descriptions in **Azerbaijani** and **English**.
- Uses multilingual sentence embeddings for accurate job matching across languages.

## 📦 Installation & Usage

This project uses `uv` for dependency management.

### Setup
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_google_api_key
   GEMINI_PROJECT_ID=your_project_id
   
   # Optional: LangSmith Tracing
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=job-search-agent
   ```

### Running the API
```bash
uv run uvicorn job_search_agent.api.main:app --reload
```

### API Endpoints
- `POST /process-cv`: Upload CV text to parse and find matching jobs.
- `POST /optimize-job`: Generate a cover letter and optimization tips for a specific job.
- `GET /usage`: Get a detailed report of LLM costs and token usage.

## 🌍 Market Focus
The system is optimized for local platforms like `jobsearch.az`, `glorri.com`, and `hellojob.az`, ensuring high relevance for candidates in Azerbaijan.
