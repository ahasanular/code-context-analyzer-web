from typing import List, Dict
from github import Github, GithubException
import re
from code_context_analyzer.analyzer import Analyzer
from code_context_analyzer.repo_system import RepositorySession
# from code_context_analyzer.analyzer.formatter import

class GitHubService:
    URL_PATTERNS = re.compile(
        r'^https?://github\.com/([^/]+)/([^/]+)(?:\.git)?/?$'
    )
    def __init__(self, token: str = ""):
        """
        Initialize the GitHub client.
        If no token is provided, unauthenticated requests will be made
        (rate-limited 60 per hour).
        """
        self.client = Github(token=token) if token else Github()

    def _extract_repo_info(self, github_url: str) -> tuple[str, str]:
        """
        Extract owner and repository name from GitHub URL
        - github_url: GitHub URL
        - return owner and repository name
        - raise : ValueError: If URL is not a valid GitHub repository URL
        """
        match = self.URL_PATTERNS.match(github_url.strip())
        if not match:
            raise ValueError(f"Invalid GitHub URL: {github_url}")

        owner, repo_name = match.groups()
        # Remove .git suffix if present
        repo_name = repo_name.replace('.git', '')
        return owner, repo_name

    def get_branches(self, github_url: str) -> Dict[str, List[str]]:
        """
        Get all branch names and default branch from GitHub repository

        - github_url: GitHub repository URL
        - returns Dict with 'branches' list and 'default_branch' string
        - raises ::
            ValueError: If URL is invalid or repository doesn't exist
            GithubException: For GitHub API errors
        """
        owner, repo_name = self._extract_repo_info(github_url)

        try:
            # Get repository
            repo = self.client.get_repo(f"{owner}/{repo_name}")

            # Get all branches
            branches = [branch.name for branch in repo.get_branches()]

            print(repo.default_branch)
            return {
                "branches": branches,
                "default_branch": repo.default_branch
            }

        except GithubException as e:
            if e.status == 404:
                raise ValueError(
                    f"Repository {owner}/{repo_name} not found") from e
            raise GithubException(f"GitHub API error: {e}") from e


class CodeAnalysisService:
    def __init__(
        self,
        languages: list[str],
        max_files: int = 1000,
        depth: int = 3,
        ignore_tests: bool = True
    ):
        self.languages = languages
        self.max_files = max_files
        self.depth = depth
        self.ignore_tests = ignore_tests

    def run_analysis(self, source_url: str, branch: str) -> str:
        with RepositorySession(source_url, branch) as session:
            analyzer = Analyzer(
                session.path,
                languages=self.languages,
                max_files=self.max_files,
                depth=self.depth,
                ignore_tests=self.ignore_tests
            )
            results = analyzer.run_analysis()
            return results