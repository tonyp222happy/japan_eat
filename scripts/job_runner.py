#!/usr/bin/env python3
"""
Hyakumeiten Job Runner
Manages job execution with worktrees, checkpoints, verification, and retry logic.

Usage:
    python scripts/job_runner.py run J001
    python scripts/job_runner.py status
    python scripts/job_runner.py list
"""

import json
import os
import subprocess
import sys
import time
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

JOBS_DIR = Path.home() / "hyakumeiten-scraper" / "jobs"
REPO_DIR = Path.home() / "hyakumeiten-scraper"
WORKTREES_DIR = REPO_DIR / ".worktrees"


@dataclass
class JobResult:
    job_id: str
    status: str  # "success" | "failed" | "stopped"
    started_at: str
    finished_at: str
    duration_seconds: float
    retry_count: int = 0
    error_fingerprint: str = ""
    cost_estimate: float = 0.0
    verifier_output: str = ""
    commit_hash: str = ""
    worktree_path: str = ""


def load_job_spec(job_id: str) -> dict:
    spec_path = JOBS_DIR / job_id / "spec.yaml"
    if not spec_path.exists():
        raise FileNotFoundError(f"Job spec not found: {spec_path}")
    with open(spec_path) as f:
        return yaml.safe_load(f)


def save_job_result(result: JobResult):
    result_path = JOBS_DIR / result.job_id / "result.json"
    with open(result_path, "w") as f:
        json.dump(asdict(result), f, indent=2)
    print(f"  Result saved to {result_path}")


def create_worktree(job_id: str) -> str:
    branch = f"job/{job_id}"
    worktree_path = WORKTREES_DIR / job_id
    WORKTREES_DIR.mkdir(exist_ok=True)

    # Remove existing worktree if any
    if worktree_path.exists():
        subprocess.run(
            ["git", "worktree", "remove", "-f", str(worktree_path)],
            cwd=REPO_DIR, check=True
        )

    # Create checkpoint commit on main
    subprocess.run(
        ["git", "add", "-A"],
        cwd=REPO_DIR, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", f"Checkpoint before {job_id}"],
        cwd=REPO_DIR, capture_output=True
    )

    # Create branch and worktree
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(worktree_path), "HEAD"],
        cwd=REPO_DIR, check=True, capture_output=True
    )
    return str(worktree_path)


def run_verifier(spec: dict, worktree_path: str) -> tuple[bool, str]:
    """Run verifier commands. Returns (success, output)."""
    verifier = spec.get("verifier", {})
    commands = verifier.get("commands", [])
    if not commands:
        return True, "No verifier commands configured"

    all_output = []
    for cmd in commands:
        result = subprocess.run(
            cmd, shell=True, cwd=worktree_path,
            capture_output=True, text=True, timeout=120
        )
        output = f"$ {cmd}\n{result.stdout}{result.stderr}"
        all_output.append(output)
        if result.returncode != 0:
            return False, "\n---\n".join(all_output)

    return True, "\n---\n".join(all_output)


def compute_error_fingerprint(error_output: str) -> str:
    """Create a stable fingerprint from error output for dedup."""
    lines = error_output.strip().split("\n")
    # Take first 3 non-empty lines as fingerprint
    fingerprint_lines = [l.strip() for l in lines if l.strip()][:3]
    return " | ".join(fingerprint_lines)


def run_job(job_id: str):
    spec = load_job_spec(job_id)
    verifier = spec.get("verifier", {})
    max_retries = verifier.get("max_retries", 3)
    stop_on_cost = verifier.get("stop_on_cost", 5.0)

    result = JobResult(
        job_id=job_id,
        status="failed",
        started_at=datetime.now().isoformat(),
        finished_at="",
        duration_seconds=0,
    )

    print(f"\n{'='*60}")
    print(f"  Job {job_id}: {spec.get('title', 'Untitled')}")
    print(f"{'='*60}")

    # Create worktree
    print(f"\n  Creating worktree...")
    worktree_path = create_worktree(job_id)
    result.worktree_path = worktree_path
    print(f"  Worktree: {worktree_path}")

    start = time.time()
    for attempt in range(1, max_retries + 1):
        print(f"\n  Attempt {attempt}/{max_retries}")

        # TODO: Call OpenCode/Hermes agent here
        # For now, run verifier directly on worktree
        print(f"  Running verifier...")
        success, output = run_verifier(spec, worktree_path)
        result.verifier_output = output
        result.retry_count = attempt - 1

        if success:
            print(f"  ✓ Verifier passed")
            # Commit worktree changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=worktree_path, check=True, capture_output=True
            )
            commit_result = subprocess.run(
                ["git", "commit", "-m", f"{job_id}: {spec.get('title', 'completed')}"],
                cwd=worktree_path, capture_output=True, text=True
            )
            if commit_result.returncode == 0:
                result.commit_hash = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=worktree_path, capture_output=True, text=True
                ).stdout.strip()

            result.status = "success"
            break

        # Check error fingerprint for retry loop detection
        fingerprint = compute_error_fingerprint(output)
        result.error_fingerprint = fingerprint

        # Estimate cost (simplified: time-based)
        result.cost_estimate = (time.time() - start) * 0.001  # placeholder
        if result.cost_estimate > stop_on_cost:
            print(f"  ✗ Cost limit exceeded (${result.cost_estimate:.2f} > ${stop_on_cost:.2f})")
            result.status = "stopped"
            break

        if attempt < max_retries:
            print(f"  ✗ Verifier failed, retrying...\n  Error: {fingerprint[:100]}")
            time.sleep(2)
        else:
            print(f"  ✗ All {max_retries} attempts failed")
            print(f"  Error fingerprint: {fingerprint}")

    result.finished_at = datetime.now().isoformat()
    result.duration_seconds = round(time.time() - start, 1)

    save_job_result(result)

    # Cleanup worktree
    subprocess.run(
        ["git", "worktree", "remove", "-f", worktree_path],
        cwd=REPO_DIR, capture_output=True
    )
    print(f"  Worktree removed: {worktree_path}")

    return result.status == "success"


def list_jobs():
    """List all jobs and their status."""
    print(f"\n{'ID':<8} {'Status':<10} {'Title':<40} {'Result'}")
    print("-" * 90)
    for job_dir in sorted(JOBS_DIR.iterdir()):
        if not job_dir.is_dir() or job_dir.name.startswith("."):
            continue
        job_id = job_dir.name

        spec_path = job_dir / "spec.yaml"
        result_path = job_dir / "result.json"

        spec = {}
        if spec_path.exists():
            with open(spec_path) as f:
                spec = yaml.safe_load(f) or {}

        result = {}
        if result_path.exists():
            with open(result_path) as f:
                result = json.load(f)

        title = spec.get("title", "-")[:38]
        status = result.get("status", spec.get("status", "pending"))
        cost = result.get("cost_estimate", 0)
        retries = result.get("retry_count", 0)
        result_str = f"${cost:.2f} ({retries} retries)" if cost or retries else "-"

        print(f"{job_id:<8} {status:<10} {title:<40} {result_str}")


def show_status(job_id: str):
    """Show detailed job status."""
    result_path = JOBS_DIR / job_id / "result.json"
    if not result_path.exists():
        print(f"No result found for {job_id}")
        return
    with open(result_path) as f:
        result = json.load(f)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/job_runner.py <command> [args]")
        print("  run <job_id>   - Execute a job")
        print("  status <job_id> - Show job result")
        print("  list           - List all jobs")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run" and len(sys.argv) > 2:
        success = run_job(sys.argv[2])
        sys.exit(0 if success else 1)
    elif command == "status" and len(sys.argv) > 2:
        show_status(sys.argv[2])
    elif command == "list":
        list_jobs()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
