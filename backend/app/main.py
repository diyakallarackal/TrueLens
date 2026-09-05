from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db
from app.api import analyze, history, health, capabilities


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    init_db()
    yield


app = FastAPI(
    title="TrueLens Media Verification API",
    description="Backend engine for detecting AI-generated and manipulated images & audio through real digital forensics.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler ensuring backend stack traces are never exposed to users.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred during request processing.",
            "error_type": exc.__class__.__name__,
        },
    )


# Include API routers (both /api prefix and un-prefixed for serverless resilience)
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(health.router, tags=["Health Alias"])

app.include_router(capabilities.router, prefix="/api", tags=["Capabilities"])
app.include_router(capabilities.router, tags=["Capabilities Alias"])

app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(analyze.router, tags=["Analysis Alias"])

app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(history.router, tags=["History Alias"])


@app.get("/")
async def root():
    return {
        "message": "TrueLens Media Verification Platform API",
        "docs": "/docs",
        "health": "/api/health",
        "capabilities": "/api/capabilities"
    }
