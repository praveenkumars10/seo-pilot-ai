import pytest
from pathlib import Path
import git
from backend.app.services.git_service import GitService

def test_git_service_redacts_env_secrets(tmp_path):
    repo = git.Repo.init(tmp_path)
    
    # Configure git user for tests
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test Runner")
        config.set_value("user", "email", "runner@test.local")

    # Create dummy safe file and sensitive .env file
    safe_file = tmp_path / "index.html"
    safe_file.write_text("<h1>Safe Content</h1>", encoding="utf-8")

    secret_file = tmp_path / ".env"
    secret_file.write_text("SECRET_API_KEY=super-secret-token", encoding="utf-8")

    service = GitService(repo_path=str(tmp_path))
    status = service.get_repo_status()
    assert status["is_repo"] is True

    # Attempt to commit both files
    res = service.commit_approved_changes(
        files=["index.html", ".env"],
        commit_message="Test commit"
    )

    assert res["success"] is True
    assert "index.html" in res["files_committed"]
    assert ".env" not in res["files_committed"]  # Sensitive file blocked!
