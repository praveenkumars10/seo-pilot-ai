import pytest
from pathlib import Path
from backend.app.services.code_modifier import CodeModifierService

def test_code_modifier_applies_and_backups_cleanly(tmp_path):
    # Setup test file
    index_file = tmp_path / "index.html"
    index_file.write_text("<html><head><title>Old Title</title></head></html>", encoding="utf-8")

    modifier = CodeModifierService(repo_path=str(tmp_path))

    changes = [
        {
            "file_path": "index.html",
            "action": "modify",
            "original_snippet": "<title>Old Title</title>",
            "new_snippet": "<title>Optimized Title</title>"
        },
        {
            "file_path": "public/robots.txt",
            "action": "create",
            "new_snippet": "User-agent: *\nAllow: /\n"
        }
    ]

    res = modifier.apply_plan(changes, run_tests=False)
    assert res["success"] is True

    # Verify changes on disk
    updated_content = index_file.read_text(encoding="utf-8")
    assert "<title>Optimized Title</title>" in updated_content

    robots_file = tmp_path / "public" / "robots.txt"
    assert robots_file.exists()
    assert "User-agent: *" in robots_file.read_text(encoding="utf-8")

def test_code_modifier_automatic_rollback_on_test_failure(tmp_path):
    index_file = tmp_path / "index.html"
    original_text = "<html><head><title>Original Safe State</title></head></html>"
    index_file.write_text(original_text, encoding="utf-8")

    modifier = CodeModifierService(repo_path=str(tmp_path))

    changes = [
        {
            "file_path": "index.html",
            "action": "modify",
            "original_snippet": "<title>Original Safe State</title>",
            "new_snippet": "<title>Broken State</title>"
        }
    ]

    # Command that deliberately fails (exit 1)
    failing_command = ["python -c \"import sys; sys.exit(1)\""]

    res = modifier.apply_plan(changes, run_tests=True, test_commands=failing_command)
    assert res["success"] is False
    assert res["rolled_back"] is True

    # File should have been rolled back to original safe text!
    restored_text = index_file.read_text(encoding="utf-8")
    assert restored_text == original_text

