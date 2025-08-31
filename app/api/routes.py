from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from fastapi.responses import PlainTextResponse, JSONResponse

from typing import List, Optional
from ..services.services import GitHubService, CodeAnalysisService
from ..security.rate_limiter import limiter

router = APIRouter()

# Request schema
class RepoRequest(BaseModel):
    repo_url: str
    branch: str
    max_files: int = 1000
    ignore_tests: bool = True
    ignore_patterns: List[str] = []


@router.get("/branches")
@limiter.limit("10/minute")
async def get_branches(repo_url: str, request: Request):
    service = GitHubService()
    try:
        data = service.get_branches(repo_url)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch branches from GitHub"
        )

@router.post("/process")
@limiter.limit("10/minute")
async def process_repo(req: RepoRequest, request: Request):
    try:
        analyzer = CodeAnalysisService(
            max_files = req.max_files,
            ignore_tests = req.ignore_tests,
            ignore_patterns = req.ignore_patterns,
        )
        report = analyzer.run_analysis(req.repo_url, req.branch)
        return JSONResponse({"status": 200, "report":report})
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch branches from GitHub"
        )
