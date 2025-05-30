"""
Production FastAPI application with enhanced security and monitoring
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn

# Use production config
try:
    from app.config_prod import settings
except ImportError:
    from app.config import settings
from app.database import create_tables, get_db
from app.api import auth, interview, admin
from app.utils.security import create_admin_user

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
request_counts = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting AI Interview API in production mode")

    # Initialize database
    create_tables()
    logger.info("📊 Database tables created/verified")

    # Create admin user
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        create_admin_user(db)
        db.close()
        logger.info("👤 Admin user initialized")
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")

    logger.info(f"✅ {settings.project_name} v{settings.version} started successfully!")
    logger.info(f"📚 API Documentation: https://your-domain.com/docs")

    yield

    # Shutdown
    logger.info("🛑 Shutting down AI Interview API")

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Production AI-powered interview assessment platform with audio processing and NLP scoring",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
    # Security headers
    swagger_ui_parameters={"persistAuthorization": True} if settings.debug else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else [
        "your-domain.com",
        "*.onrender.com",  # Render domains
        "*.railway.app",   # Railway domains (if migrating)
        "*.herokuapp.com"  # Heroku domains (if migrating)
    ]
)

# CORS middleware with production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    start_time = time.time()

    # Simple rate limiting (use Redis in production)
    client_ip = request.client.host
    current_time = int(time.time())
    window_start = current_time - settings.rate_limit_window

    # Clean old entries
    if client_ip in request_counts:
        request_counts[client_ip] = [
            timestamp for timestamp in request_counts[client_ip]
            if timestamp > window_start
        ]
    else:
        request_counts[client_ip] = []

    # Check rate limit
    if len(request_counts[client_ip]) >= settings.rate_limit_requests:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"}
        )

    # Add current request
    request_counts[client_ip].append(current_time)

    # Process request
    response = await call_next(request)

    # Log request
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"IP: {client_ip}"
    )

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# Include API routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(interview.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": settings.version,
        "status": "healthy",
        "environment": "production" if settings.is_production else "development",
        "docs_url": "/docs" if settings.debug else "Contact admin for API documentation",
        "endpoints": {
            "authentication": f"{settings.api_v1_prefix}/auth",
            "interview": f"{settings.api_v1_prefix}/interview",
            "admin": f"{settings.api_v1_prefix}/admin"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Test database connection
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()

        return {
            "status": "healthy",
            "version": settings.version,
            "environment": "production" if settings.is_production else "development",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint for monitoring"""
    if not settings.debug:
        # In production, you might want to secure this endpoint
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "active_connections": len(request_counts),
        "total_requests": sum(len(requests) for requests in request_counts.values()),
        "uptime": time.time(),
        "memory_usage": "N/A",  # Add memory monitoring if needed
    }

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    logger.warning(f"404 Not Found: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "status_code": 404,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"500 Internal Server Error: {request.method} {request.url.path} - {exc}")
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
        "app.main_prod:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        workers=1 if settings.debug else 4
    )
