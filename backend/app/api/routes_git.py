from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
from backend.app.services.git_service import GitService

router = APIRouter(prefix="/git", tags=["Git & GitHub"])

@router.get("/status")
def get_git_status(repo_path: str = Query(...)):
    service = GitService(repo_path=repo_path)
    return service.get_repo_status()

@router.get("/commits")
def get_git_commits(repo_path: str = Query(...), limit: int = Query(15, ge=1, le=50)):
    service = GitService(repo_path=repo_path)
    return service.get_commit_history(limit=limit)

@router.post("/push")
def push_git_remote(
    repo_path: str = Body(..., embed=True),
    remote_name: str = Body("origin", embed=True),
    branch: Optional[str] = Body(None, embed=True)
):
    service = GitService(repo_path=repo_path)
    result = service.push_to_remote(remote_name=remote_name, branch=branch)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result
