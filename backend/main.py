"""
Tree Rings Counter — FastAPI backend
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.analyze import router as analyze_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Tree Rings Counter backend starting up")
    logger.info(
        "Primary model: %s | Fallback threshold: %s",
        os.getenv("PRIMARY_MODEL", "gemini"),
        os.getenv("FALLBACK_CONFIDENCE_THRESHOLD", "0.5"),
    )
    yield
    logger.info("Backend shutting down")


app = FastAPI(
    title="Tree Rings Counter API",
    description="AI-powered tree age estimation from cross-section photos.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Expo web + mobile dev servers
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8081,http://localhost:19006,exp://localhost:8081",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, tags=["Analysis"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": app.version}
