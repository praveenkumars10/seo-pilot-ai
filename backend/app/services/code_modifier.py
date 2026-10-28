import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from backend.app.config import settings

logger = logging.getLogger(__name__)

class CodeModifierService:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.backup_dir = self.repo_path / ".seopilot_backups"

    def apply_plan(
        self,
        changes: List[Dict[str, Any]],
        run_tests: bool = True,
        test_commands: List[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a pre-approved ChangePlan:
        1. Backs up target files.
        2. Applies changes cleanly.
        3. Executes verification tests.
        4. If tests fail and auto-rollback is enabled, restores backups.
        5. Returns execution log and status.
        """
        if not self.repo_path.exists():
            return {
                "success": False,
                "error": f"Repository path does not exist: {self.repo_path}",
                "execution_log": "Directory not found.",
                "rolled_back": False
            }

        timestamp = int(time.time())
        current_backup_dir = self.backup_dir / f"backup_{timestamp}"
        current_backup_dir.mkdir(parents=True, exist_ok=True)

        log_lines: List[str] = []
        log_lines.append(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Commencing batch execution of {len(changes)} change(s).")

        applied_files: List[Tuple[Path, Path]] = []  # (target_path, backup_path)

        try:
            # Step 1: Backup and Apply
            for item in changes:
                file_rel = item.get("file_path", "").lstrip("/\\")
                target_path = (self.repo_path / file_rel).resolve()

                # Path traversal security enforcement
                if not target_path.is_relative_to(self.repo_path):
                    raise PermissionError(f"Security Policy Violation: Path traversal blocked for '{file_rel}'.")

                action = item.get("action", "modify")
                orig_snippet = item.get("original_snippet", "")
                new_snippet = item.get("new_snippet", "")

                backup_target = (current_backup_dir / file_rel).resolve()
                backup_target.parent.mkdir(parents=True, exist_ok=True)

                if target_path.exists():
                    shutil.copy2(target_path, backup_target)
                    applied_files.append((target_path, backup_target))
                    log_lines.append(f"Backed up existing file: {file_rel}")
                else:
                    # Note for deletion upon rollback if it was newly created
                    applied_files.append((target_path, None))
                    log_lines.append(f"Creating new asset: {file_rel}")

                # Ensure parent directory exists for new files
                target_path.parent.mkdir(parents=True, exist_ok=True)

                if action == "create":
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(new_snippet)
                    log_lines.append(f"Successfully created: {file_rel}")

                elif action == "modify":
                    if not target_path.exists():
                        raise FileNotFoundError(f"Target file {file_rel} does not exist to modify.")

                    with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    if orig_snippet and orig_snippet in content:
                        modified_content = content.replace(orig_snippet, new_snippet, 1)
                    else:
                        # Append or write if original snippet empty or not exact
                        if not orig_snippet:
                            modified_content = content + "\n" + new_snippet
                        else:
                            raise ValueError(f"Target snippet in {file_rel} not found. File may have changed.")

                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    log_lines.append(f"Applied modification to: {file_rel}")

            # Step 2: Verification Tests
            tests_passed = True
            test_output = ""
            if run_tests and test_commands:
                log_lines.append("Running verification test suite...")
                for cmd in test_commands:
                    log_lines.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=str(self.repo_path),
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    test_output += f"\n$ {cmd}\nExit Code: {proc.returncode}\n{proc.stdout}\n{proc.stderr}\n"
                    if proc.returncode != 0:
                        tests_passed = False
                        log_lines.append(f"TEST FAILED: '{cmd}' returned exit code {proc.returncode}")
                        break
                    else:
                        log_lines.append(f"Test passed: '{cmd}'")

            # Step 3: Handle Rollback if Tests Failed
            if not tests_passed:
                if settings.AUTO_ROLLBACK_ON_TEST_FAILURE:
                    log_lines.append("AUTOMATIC ROLLBACK TRIGGERED: Restoring all files to pre-batch state.")
                    self._restore_files(applied_files)
                    log_lines.append("Rollback successfully completed.")
                    return {
                        "success": False,
                        "error": "Automated verification tests failed after applying changes.",
                        "test_output": test_output,
                        "execution_log": "\n".join(log_lines),
                        "rolled_back": True
                    }
                else:
                    return {
                        "success": False,
                        "error": "Tests failed but auto-rollback was disabled.",
                        "test_output": test_output,
                        "execution_log": "\n".join(log_lines),
                        "rolled_back": False
                    }

            log_lines.append("All approved modifications successfully applied and validated!")
            return {
                "success": True,
                "execution_log": "\n".join(log_lines),
                "test_output": test_output,
                "rolled_back": False,
                "backup_dir": str(current_backup_dir)
            }

        except Exception as exc:
            log_lines.append(f"EXCEPTION ENCOUNTERED: {str(exc)}")
            log_lines.append("Initiating safety rollback...")
            self._restore_files(applied_files)
            log_lines.append("Rollback finished.")
            return {
                "success": False,
                "error": str(exc),
                "execution_log": "\n".join(log_lines),
                "rolled_back": True
            }

    def _restore_files(self, applied_files: List[Tuple[Path, Path]]):
        for target_path, backup_path in reversed(applied_files):
            try:
                if backup_path and backup_path.exists():
                    shutil.copy2(backup_path, target_path)
                elif backup_path is None and target_path.exists():
                    # It was newly created, delete it
                    target_path.unlink()
            except Exception as e:
                logger.error(f"Error restoring {target_path}: {e}")

