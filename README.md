# Job Search Agent

An AI-powered job search assistant designed to extract intent from CVs, find relevant job opportunities, and optimize applications. Specifically tailored for the Azerbaijan job market.

## 🚀 Architecture Overview

The project follows a modular architecture using **LangChain** for stateful orchestration and a **Gateway** pattern for LLM management.

```text
src/job_search_agent/
├── api/                    # FastAPI implementation (Routes, Lifespan)
├── core/
│   ├── llm_gateways/       # LLM management (Cost Control, Routing, Observability, Logs)
│   │   ├── gateway.py      # Main LLM Gateway
│   │   ├── model_router.py # Model allocation based on complexity
│   │   ├── cost_controller.py # Budget and usage tracking
│   │   └── observability.py # LangSmith integration
│   └── orchestration/      # LangGraph workflow logic
│       ├── agents/         # Specialized AI Agents (Resume, Ranking, Optimizer)
│       └── graph.py        # LangGraph state and node definitions
├── models/                 # Pydantic data models (JobVacancy, Resume, etc.)
├── configs/                # Application settings and pricing configurations
└── utils/                  # Shared helper functions
```

## 🛠 Prerequisites

This project uses `uv` for lightning-fast Python package management. If you don't have it installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 📥 Getting Started

### 1. Download the Project
```bash
git clone https://github.com/murafalizade/job-search-agent.git
cd job-search-agent
```

### 2. Installation
Install dependencies and create a virtual environment automatically:
```bash
uv sync
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# Gemini Configuration
GEMINI_PROJECT_ID="your_project_id"
GOOGLE_API_KEY="your_google_api_key"

# Search Engine (Required for finding jobs)
TAVILY_API_KEY="your_tavily_key"  # Optional: Falls back to DuckDuckGo if not provided

# Optional: LangSmith Tracing (Recommended for debugging)
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="your_langsmith_key"
LANGCHAIN_PROJECT="job-search-agent"
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# Optional: API Documentation Paths
API_DOCS_URL="/docs"
API_REDOC_URL="/redoc"
```

## 🚀 Running the Application

To start the FastAPI server:
```bash
uv run uvicorn job_search_agent.api.main:app --reload
```

### 📖 API Documentation (Swagger)
Once the server is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (or your configured `API_DOCS_URL`)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (or your configured `API_REDOC_URL`)

## ⚙️ Configuration Management

### 1. Changing Model Configs & Pricing
The application uses a dynamic configuration for model routing, pricing, and rate limits. You can modify these settings without changing code by editing:
`src/job_search_agent/configs/pricing/current.json`

This file allows you to:
- **Add/Remove Models**: Define which Gemini models are available.
- **Set Task Complexity**: Assign models to "basic", "mid", or "advanced" tasks.
- **Update Pricing**: Set input/output costs for usage tracking.
- **Define Rate Limits**: Configure RPM (Requests Per Minute) and RPD (Requests Per Day) for different tiers.

### 2. Changing Swagger URL
To change the Swagger or ReDoc URL, simply update the `API_DOCS_URL` or `API_REDOC_URL` in your `.env` file. The application will automatically pick up these changes.

## 🐞 Debugging & Observability

### 1. LangSmith Tracing
If `LANGCHAIN_TRACING_V2` is enabled, all agent interactions, tool calls, and LLM prompts are tracked in LangSmith. This is the best way to debug agentic logic.

### 2. Local Logs
The application records structured traces and execution logs in:
`logs/agent_trace.log`

### 3. Debugging with VS Code
To debug with VS Code, add this configuration to your `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "job_search_agent.api.main:app",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

## 🛠 Key Features

### 1. Stateful Orchestration (LangGraph)
The application uses a directed graph to manage the job search workflow:
- **Parse CV**: Extracts structured data from raw text.
- **Rank Jobs**: Searches and ranks vacancies using multilingual embeddings.
- **Optimize Job**: Generates tailored cover letters and CV improvement tips.

### 2. Search Tool Fallback
- **Tavily Search**: Used by default for advanced, high-quality search results across trusted job boards.
- **DuckDuckGo Search**: Automatically used as a **free fallback** if no `TAVILY_API_KEY` is provided, ensuring the agent works out of the box without extra costs.

### 3. Multilingual Support
- Optimized for the **Azerbaijan job market**.
- Supports CVs and job descriptions in **Azerbaijani** and **English**.
- Uses multilingual sentence embeddings for accurate job matching across languages.

## 🌍 Market Focus
The system is optimized for local platforms like `jobsearch.az`, ensuring high relevance for candidates in Azerbaijan.

---
