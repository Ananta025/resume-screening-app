import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.analysis_routes import router as analysis_router
from app.api.export_routes import router as export_router
from app.api.jd_routes import router as jd_router
from app.api.resume_routes import router as resume_router
from app.core.config import settings
from app.core.database import create_database_tables


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        logger.warning("Request validation failed: %s", exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "message": "Validation failed"},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        logger.warning("HTTP exception raised: %s", exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "message": "Request failed"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Request, exc: Exception):
        logger.exception("Unhandled application error")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "message": str(exc)},
        )

    @app.on_event("startup")
    async def on_startup() -> None:
        settings.configure_logging()
        logger.info("Starting %s in %s mode", settings.app_name, settings.environment)
        create_database_tables()

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    api_prefix = settings.api_v1_prefix
    app.include_router(resume_router, prefix=api_prefix)
    app.include_router(jd_router, prefix=api_prefix)
    app.include_router(analysis_router, prefix=api_prefix)
    app.include_router(export_router, prefix=api_prefix)

    return app


app = create_app()