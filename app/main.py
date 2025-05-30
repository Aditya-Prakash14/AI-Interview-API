"""
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

import os
from app.config import settings
from app.database import create_tables
from app.api import auth, interview, admin

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI-powered interview assessment platform with audio processing and NLP scoring",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware with production settings
allowed_origins = ["*"] if settings.debug else [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
    # Add your production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(interview.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables on startup"""
    create_tables()
    print(f"🚀 {settings.project_name} v{settings.version} started successfully!")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 Admin Panel: http://{settings.host}:{settings.port}/admin")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": settings.version,
        "status": "healthy",
        "docs_url": "/docs",
        "endpoints": {
            "authentication": f"{settings.api_v1_prefix}/auth",
            "interview": f"{settings.api_v1_prefix}/interview",
            "admin": f"{settings.api_v1_prefix}/admin"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
