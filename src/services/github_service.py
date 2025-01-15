import httpx
from fastapi import HTTPException

GITHUB_API_BASE_URL = "https://api.github.com"


async def fetch_repository_contents(repo_url: str, token: str) -> list:
    """
    Recursively fetch the contents of a GitHub repository using the GitHub API.

    :param repo_url: URL of the GitHub repository.
    :param token: Personal access token for GitHub API.
    :return: List of all files in the repository.
    """
    try:
        repo_url = str(repo_url)
        owner, repo = repo_url.rstrip('/').split('/')[-2:]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    async def fetch_contents(path=""):
        """Рекурсивная функция для получения содержимого репозитория."""
        async with httpx.AsyncClient() as client:
            url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/{path}"
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found.")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch repository contents.")

            items = response.json()
            all_files = []

            for item in items:
                if item["type"] == "file":
                    all_files.append({"name": item["name"], "path": item["path"]})
                elif item["type"] == "dir":
                    sub_files = await fetch_contents(item["path"])
                    all_files.extend(sub_files)

            return all_files

    return await fetch_contents()
