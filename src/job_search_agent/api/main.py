import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from job_search_agent.core.llm_gateways.observability import init_langsmith
from job_search_agent.api.routes import core, monitoring
from job_search_agent.configs.setting import get_settings

settings = get_settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Job Search Agent API...")
    init_langsmith()
    yield
    logger.info("Shutting down Job Search Agent API...")

app = FastAPI(
    title="Job Search Agent API",
    description="""
    An advanced AI-powered API for the Azerbaijan job market.
    
    Features:
    CV Parsing: Extract skills and intent from raw text.
    Job Matching: Find and rank jobs using multilingual embeddings.
    Application Optimization: Generate tailored cover letters and CV tips.
    Cost Tracking: Monitor LLM usage and expenses in real-time.
    """,
    version="1.1.0",
    lifespan=lifespan,
    docs_url=settings.API_DOCS_URL,
    redoc_url=settings.API_REDOC_URL,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(core.router)
app.include_router(monitoring.router)
