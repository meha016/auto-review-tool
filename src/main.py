from fastapi import FastAPI, HTTPException, Header
from src.models import ReviewRequest, ReviewResponse
from src.services.github_service import fetch_repository_contents
from src.services.openai_service import analyze_code

app = FastAPI()


@app.post("/review", response_model=ReviewResponse)
async def review_assignment(
        request: ReviewRequest,
        github_token: str = Header(...),
        openai_key: str = Header(...)):
    try:
        repo_contents = await fetch_repository_contents(request.github_repo_url, github_token)

        review = await analyze_code(
            repo_contents,
            request.assignment_description,
            request.candidate_level,
            openai_key
        )

        return review
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
