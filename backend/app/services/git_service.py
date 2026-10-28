import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import git

logger = logging.getLogger(__name__)

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def get_repo_status(self) -> Dict[str, Any]:
        """Inspect repository status, branch, remotes, and uncommitted diffs."""
        if not (self.repo_path / ".git").exists():
            return {
                "is_repo": False,
                "branch": None,
                "remotes": [],
                "has_uncommitted_changes": False,
                "untracked_files": [],
                "modified_files": []
            }

        try:
            repo = git.Repo(self.repo_path)
            branch = repo.active_branch.name if not repo.head.is_detached else "DETACHED_HEAD"
            remotes = [{"name": r.name, "url": r.url} for r in repo.remotes]
            untracked = repo.untracked_files
            modified = [item.a_path for item in repo.index.diff(None)]

            return {
                "is_repo": True,
                "branch": branch,
                "remotes": remotes,
                "has_uncommitted_changes": bool(untracked or modified),
                "untracked_files": untracked[:20],
                "modified_files": modified[:20]
            }
        except Exception as e:
            logger.error(f"Error inspecting git repo at {self.repo_path}: {e}")
            return {
                "is_repo": False,
                "error": str(e)
            }

    def init_repo(self) -> bool:
        """Initialize git repository if missing."""
        try:
            git.Repo.init(self.repo_path)
            return True
        except Exception as e:
            logger.error(f"Failed to init git repository: {e}")
            return False

    def commit_approved_changes(
        self,
        files: List[str],
        commit_message: str,
        author_name: str = "SEO Pilot AI",
        author_email: str = "agent@seopilot.ai"
    ) -> Dict[str, Any]:
        """
        Stage specified approved files and commit them safely.
        Never stage credentials, .env, or sensitive files.
        """
        try:
            repo = git.Repo(self.repo_path)
            safe_files = []
            for f in files:
                f_norm = f.replace("\\", "/").lstrip("/")
                if any(bad in f_norm.lower() for bad in [".env", "secret", "credential", "token", ".key"]):
                    logger.warning(f"Prevented committing sensitive file: {f_norm}")
                    continue
                safe_files.append(f_norm)

            if not safe_files:
                return {"success": False, "error": "No safe files to commit."}

            # Stage files
            repo.index.add(safe_files)
            
            # Create commit
            commit = repo.index.commit(
                message=commit_message,
                author=git.Actor(author_name, author_email),
                committer=git.Actor(author_name, author_email)
            )

            return {
                "success": True,
                "commit_hash": commit.hexsha,
                "commit_message": commit_message,
                "files_committed": safe_files
            }
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            return {"success": False, "error": str(e)}

    def push_to_remote(self, remote_name: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """Push committed changes to remote repository if configured."""
        try:
            repo = git.Repo(self.repo_path)
            if not repo.remotes:
                return {
                    "success": False,
                    "error": "No remote configured. Please add a remote URL first."
                }

            remote = repo.remote(name=remote_name)
            target_branch = branch or repo.active_branch.name
            
            # Push safely
            push_info = remote.push(refspec=f"{target_branch}:{target_branch}")
            
            error_details = []
            for info in push_info:
                if info.flags & git.PushInfo.ERROR:
                    error_details.append(info.summary)

            if error_details:
                return {
                    "success": False,
                    "error": f"Push errors encountered: {', '.join(error_details)}"
                }

            return {
                "success": True,
                "message": f"Successfully pushed branch '{target_branch}' to remote '{remote_name}'"
            }
        except Exception as e:
            logger.error(f"Git push failed: {e}")
            return {"success": False, "error": str(e)}

    def get_commit_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve recent commit history."""
        try:
            repo = git.Repo(self.repo_path)
            commits = []
            for c in repo.iter_commits(max_count=limit):
                commits.append({
                    "hash": c.hexsha[:8],
                    "full_hash": c.hexsha,
                    "message": c.message.strip(),
                    "author": f"{c.author.name} <{c.author.email}>",
                    "timestamp": c.committed_datetime.isoformat(),
                    "files_changed": list(c.stats.files.keys())
                })
            return commits
        except Exception:
            return []
