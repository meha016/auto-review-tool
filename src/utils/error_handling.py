import logging

import openai
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


def handle_github_error(response):
    if response.status_code == 404:
        logger.error("GitHub repository not found.")
        raise HTTPException(status_code=404, detail="GitHub repository not found.")
    elif response.status_code == 403:
        logger.error("GitHub rate limit exceeded.")
        raise HTTPException(status_code=429, detail="GitHub rate limit exceeded.")
    else:
        logger.error(f"GitHub API error: {response.text}")
        raise HTTPException(status_code=response.status_code, detail="GitHub API error.")


def handle_openai_error(exc):
    if isinstance(exc, openai.RateLimitError):
        logger.error("OpenAI rate limit exceeded.")
        raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded.")
    elif isinstance(exc, openai.OpenAIError):
        logger.error(f"OpenAI API error: {str(exc)}")
        raise HTTPException(status_code=500, detail="OpenAI API error.")
    else:
        logger.error(f"Unhandled OpenAI exception: {str(exc)}")
        raise HTTPException(status_code=500, detail="Internal server error.")
