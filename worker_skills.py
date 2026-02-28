"""Worker specialization and skill-based task claiming."""

from typing import List, Set
from dataclasses import dataclass


@dataclass
class WorkerSkills:
    """Defines worker capabilities."""

    # Skill categories
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    WEB_SEARCH = "web_search"
    DATA_PROCESSING = "data_processing"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    GENERAL = "general"

    # All available skills
    ALL_SKILLS = {
        RESEARCH, CODING, ANALYSIS, WEB_SEARCH,
        DATA_PROCESSING, DOCUMENTATION, TESTING, GENERAL
    }


class SkillMatcher:
    """Matches workers to tasks based on skills."""

    @staticmethod
    def can_claim(worker_skills: Set[str], required_skills: Set[str]) -> bool:
        """Check if worker can claim task based on skills.

        Args:
            worker_skills: Set of worker's skills
            required_skills: Set of skills required by task

        Returns:
            True if worker can claim task
        """
        if not required_skills:
            # No specific skills required, any worker can claim
            return True

        if WorkerSkills.GENERAL in worker_skills:
            # General workers can claim any task
            return True

        # Check if worker has all required skills
        return required_skills.issubset(worker_skills)

    @staticmethod
    def skill_match_score(worker_skills: Set[str], required_skills: Set[str]) -> float:
        """Calculate how well worker skills match task requirements.

        Args:
            worker_skills: Set of worker's skills
            required_skills: Set of skills required by task

        Returns:
            Score from 0.0 to 1.0 (higher is better match)
        """
        if not required_skills:
            return 1.0  # Perfect match for tasks with no requirements

        if WorkerSkills.GENERAL in worker_skills:
            return 0.5  # General workers can do it, but not specialized

        if not required_skills.issubset(worker_skills):
            return 0.0  # Worker doesn't have required skills

        # Calculate overlap
        overlap = len(required_skills.intersection(worker_skills))
        total_required = len(required_skills)

        # Perfect match if worker has exactly the required skills
        return overlap / total_required

    @staticmethod
    def suggest_worker_for_task(
        task_skills: Set[str],
        available_workers: List[tuple[str, Set[str]]]
    ) -> List[tuple[str, float]]:
        """Suggest workers for a task, ranked by skill match.

        Args:
            task_skills: Required skills for task
            available_workers: List of (worker_name, worker_skills) tuples

        Returns:
            List of (worker_name, score) sorted by score descending
        """
        suggestions = []
        for worker_name, worker_skills in available_workers:
            if SkillMatcher.can_claim(worker_skills, task_skills):
                score = SkillMatcher.skill_match_score(worker_skills, task_skills)
                suggestions.append((worker_name, score))

        # Sort by score descending
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions


# Predefined worker profiles
WORKER_PROFILES = {
    "researcher": {
        WorkerSkills.RESEARCH,
        WorkerSkills.WEB_SEARCH,
        WorkerSkills.ANALYSIS,
        WorkerSkills.DOCUMENTATION
    },
    "developer": {
        WorkerSkills.CODING,
        WorkerSkills.TESTING,
        WorkerSkills.DOCUMENTATION
    },
    "analyst": {
        WorkerSkills.ANALYSIS,
        WorkerSkills.DATA_PROCESSING,
        WorkerSkills.DOCUMENTATION
    },
    "general": {
        WorkerSkills.GENERAL
    },
    "web_specialist": {
        WorkerSkills.WEB_SEARCH,
        WorkerSkills.RESEARCH,
        WorkerSkills.DOCUMENTATION
    }
}


def get_worker_profile(profile_name: str) -> Set[str]:
    """Get predefined worker skill profile.

    Args:
        profile_name: One of: researcher, developer, analyst, general, web_specialist

    Returns:
        Set of skills for that profile
    """
    return WORKER_PROFILES.get(profile_name, {WorkerSkills.GENERAL})
