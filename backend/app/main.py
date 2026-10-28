import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.api.routes_websites import router as websites_router
from backend.app.api.routes_audits import router as audits_router
from backend.app.api.routes_approvals import router as approvals_router
from backend.app.api.routes_ai import router as ai_router
from backend.app.api.routes_google import router as google_router
from backend.app.api.routes_git import router as git_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("seopilot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    await init_db()
    logger.info("SEO Pilot AI backend started successfully.")
    yield
    logger.info("Shutting down SEO Pilot AI backend...")

app = FastAPI(
    title="SEO Pilot AI API",
    description="Autonomous AI SEO Engineering & Website Optimization Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{settings.FRONTEND_PORT}",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under /api
app.include_router(websites_router, prefix="/api")
app.include_router(audits_router, prefix="/api")
app.include_router(approvals_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(google_router, prefix="/api")
app.include_router(git_router, prefix="/api")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SEO Pilot AI Backend",
        "version": "1.0.0",
        "database": "sqlite_async",
        "approval_gatekeeper": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
