"""Background job system for long-running tasks."""

import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class Job:
    """Background job data model."""
    job_id: str
    command: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    exit_code: Optional[int] = None
    output_file: Optional[str] = None
    error_file: Optional[str] = None
    pid: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BackgroundJobManager:
    """Manages background jobs (daemon operations)."""

    def __init__(self, state_dir: Path):
        """Initialize job manager.

        Args:
            state_dir: Root state directory
        """
        self.state_dir = state_dir
        self.jobs_dir = state_dir / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

        self.active_jobs: Dict[str, threading.Thread] = {}
        self.job_callbacks: Dict[str, Callable] = {}

    def _generate_job_id(self) -> str:
        """Generate unique job ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        count = len(list(self.jobs_dir.glob("job_*.json")))
        return f"job_{timestamp}_{count:04d}"

    def _save_job(self, job: Job):
        """Save job to disk."""
        job_file = self.jobs_dir / f"{job.job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job.to_dict(), f, indent=2)

    def _load_job(self, job_id: str) -> Optional[Job]:
        """Load job from disk."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None

        with open(job_file, "r") as f:
            data = json.load(f)
            return Job(**data)

    def _run_job(self, job: Job, callback: Optional[Callable] = None):
        """Run job in background thread."""
        # Update status
        job.status = "RUNNING"
        job.started_at = datetime.now().isoformat()
        self._save_job(job)

        # Prepare output files
        output_file = self.jobs_dir / f"{job.job_id}.stdout"
        error_file = self.jobs_dir / f"{job.job_id}.stderr"
        job.output_file = str(output_file)
        job.error_file = str(error_file)

        try:
            # Run command
            with open(output_file, "w") as out, open(error_file, "w") as err:
                process = subprocess.Popen(
                    job.command,
                    shell=True,
                    stdout=out,
                    stderr=err,
                    text=True
                )

                job.pid = process.pid
                self._save_job(job)

                # Wait for completion
                exit_code = process.wait()

                # Update job
                job.status = "COMPLETED" if exit_code == 0 else "FAILED"
                job.exit_code = exit_code
                job.completed_at = datetime.now().isoformat()
                self._save_job(job)

                # Call callback if provided
                if callback:
                    callback(job)

        except Exception as e:
            job.status = "FAILED"
            job.exit_code = -1
            job.completed_at = datetime.now().isoformat()

            # Write error to stderr file
            with open(error_file, "a") as err:
                err.write(f"\nException: {str(e)}\n")

            self._save_job(job)

            if callback:
                callback(job)

    def spawn_job(
        self,
        command: str,
        callback: Optional[Callable] = None
    ) -> Job:
        """Spawn a new background job.

        Args:
            command: Shell command to execute
            callback: Optional callback function called when job completes

        Returns:
            Job object with job_id
        """
        job_id = self._generate_job_id()

        job = Job(
            job_id=job_id,
            command=command,
            status="PENDING",
            created_at=datetime.now().isoformat()
        )

        self._save_job(job)

        # Start thread
        thread = threading.Thread(
            target=self._run_job,
            args=(job, callback),
            daemon=True
        )
        thread.start()

        self.active_jobs[job_id] = thread
        if callback:
            self.job_callbacks[job_id] = callback

        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job status."""
        return self._load_job(job_id)

    def list_jobs(self, status: Optional[str] = None) -> list[Job]:
        """List all jobs with optional status filter."""
        jobs = []
        for job_file in sorted(self.jobs_dir.glob("job_*.json")):
            with open(job_file, "r") as f:
                data = json.load(f)
                job = Job(**data)

                if status is None or job.status == status:
                    jobs.append(job)

        return jobs

    def get_job_output(self, job_id: str) -> Dict[str, str]:
        """Get job output (stdout and stderr)."""
        job = self.get_job(job_id)
        if not job:
            return {"error": "Job not found"}

        result = {
            "job_id": job_id,
            "status": job.status,
            "exit_code": job.exit_code
        }

        # Read stdout
        if job.output_file and Path(job.output_file).exists():
            result["stdout"] = Path(job.output_file).read_text()
        else:
            result["stdout"] = ""

        # Read stderr
        if job.error_file and Path(job.error_file).exists():
            result["stderr"] = Path(job.error_file).read_text()
        else:
            result["stderr"] = ""

        return result

    def wait_for_job(self, job_id: str, timeout: Optional[float] = None) -> Job:
        """Wait for a job to complete.

        Args:
            job_id: Job ID to wait for
            timeout: Optional timeout in seconds

        Returns:
            Updated Job object
        """
        if job_id in self.active_jobs:
            thread = self.active_jobs[job_id]
            thread.join(timeout=timeout)

        return self.get_job(job_id)

    def cleanup_completed_jobs(self, keep_recent: int = 10):
        """Clean up old completed jobs, keeping recent ones.

        Args:
            keep_recent: Number of recent jobs to keep
        """
        completed_jobs = self.list_jobs(status="COMPLETED")

        if len(completed_jobs) > keep_recent:
            # Sort by completion time
            completed_jobs.sort(
                key=lambda j: j.completed_at or "",
                reverse=True
            )

            # Remove old jobs
            for job in completed_jobs[keep_recent:]:
                job_file = self.jobs_dir / f"{job.job_id}.json"
                if job_file.exists():
                    job_file.unlink()

                # Remove output files
                if job.output_file and Path(job.output_file).exists():
                    Path(job.output_file).unlink()
                if job.error_file and Path(job.error_file).exists():
                    Path(job.error_file).unlink()
