# Job Search Agent

An AI-powered job search assistant designed to extract intent from CVs and find relevant job opportunities, specifically tailored for the Azerbaijan job market.

## 🚀 Architecture Overview

The project follows a modular architecture designed for scalability and maintainability, separating concerns between AI logic, data models, and external tools.

```text
src/job_search_agent/
├── agents/             # Core AI Agents logic
│   ├── base.py         # Abstract base class for all agents (handles LLM init)
│   └── resume_agent.py # Agent for parsing and extracting intent from CVs
├── models/             # Pydantic data models for type-safe data handling
│   ├── job_vacancy.py  # Structure for job postings
│   └── resume_models.py  # Structure for parsed CV data
├── prompts/            # LLM prompt templates (separated from logic)
│   └── resume_prompts.py # Specialized prompts for CV extraction
├── tools/              # External integrations and search utilities
│   └── search_tool/    # Implementation of job search across various platforms
├── configs/            # Application settings and environment management
└── utils/              # Helper functions and utilities
```

## 🛠 Key Components

### 1. Agents
- **BaseAgent**: A template class that standardizes how LLMs (like Gemini) are initialized using `Settings`.
- **ResumeAgent**: Uses structured output to parse CVs into refined job titles and skills, applying specific rules for the local market (e.g., normalizing junior titles).

### 2. Search Tools
- Implements a plugin-based architecture for searching different job boards.
- **DuckDuckGoSearchTool**: Performs targeted site searches (e.g., `site:jobsearch.az`) to find the most recent vacancies.

### 3. Settings & Security
- Uses `pydantic-settings` to manage configuration via `.env` files.
- Sensitive data like `GOOGLE_API_KEY` is handled using `SecretStr` to prevent accidental logging.

## 📦 Installation & Usage

This project uses `uv` for lightning-fast dependency management.

### Setup
```bash
# Install dependencies
uv sync
```

### Running the Resume Parser
```bash
uv run python -m job_search_agent.agents.resume_agent
```

## 🌍 Market Focus
The system is optimized for the **Azerbaijan job market**, including:
- Support for Azerbaijani and English CVs.
- Normalization of local job titles.
- Integration with trusted local job boards like `jobsearch.az` and `glorri.com`.
