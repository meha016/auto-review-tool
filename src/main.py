from fastapi import FastAPI, HTTPException, Header
from src.models import ReviewRequest, ReviewResponse
from src.services.github_service import fetch_repository_contents
from src.services.openai_service import analyze_code
from src.utils.error_handling import global_exception_handler, http_exception_handler, logger

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)


@app.post("/review", response_model=ReviewResponse)
async def review_assignment(
        request: ReviewRequest,
        github_token: str = Header(...),
        openai_key: str = Header(...)):
    try:

        logger.info("Fetching repository contents...")
        repo_contents = await fetch_repository_contents(request.github_repo_url, github_token)

        logger.info("Analyzing repository with OpenAI...")
        review = await analyze_code(
            repo_contents,
            request.assignment_description,
            request.candidate_level,
            openai_key
        )

        logger.info("Analysis complete.")
        return review

    except Exception as e:
        logger.error(f"Unhandled exception in /review endpoint: {str(e)}")
        raise

