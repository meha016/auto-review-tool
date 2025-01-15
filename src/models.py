from pydantic import BaseModel, HttpUrl
from typing import List


class ReviewRequest(BaseModel):
    """
    Model for validating incoming code review requests.
    """
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str  # Junior, Middle, Senior


class ReviewResponse(BaseModel):
    """
    Model for API response structure.
    """
    found_files: List[str]
    downsides: List[str]
    suggestions: List[str]
    rating: str
    conclusions: str
