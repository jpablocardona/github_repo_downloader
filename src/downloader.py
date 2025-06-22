#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from github import Github
from git import Repo
from tqdm import tqdm


def setup_logging() -> logging.Logger:
    """Setup logging configuration with both console and file output."""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Create log filename with current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"downloader_{timestamp}.log")

    # Configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized. Log file: {log_filename}")
    return logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download or update GitHub repositories"
    )
    parser.add_argument("--input", required=True, help="Text file with repository list")
    parser.add_argument(
        "--output", default="./repos", help="Output directory for repositories"
    )
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete output directory before starting download",
    )
    return parser.parse_args()


def read_repos_file(file_path: str, logger: logging.Logger) -> List[str]:
    """Read the repositories file and return the list of repos."""
    try:
        logger.info(f"Reading repositories file: {file_path}")
        with open(file_path, "r") as f:
            repos = [line.strip() for line in f if line.strip()]
        logger.info(f"Found {len(repos)} repositories to process")
        return repos
    except FileNotFoundError:
        logger.error(f"Error: File {file_path} not found")
        sys.exit(1)


def get_repo_name_from_url(url: str) -> str:
    """Extract repository name from SSH or HTTPS URL."""
    parsed = urlparse(url)
    if parsed.scheme == "git":
        # SSH format: git@github.com:user/repo.git
        path = parsed.path.split(":")[-1]
    else:
        # HTTPS format: https://github.com/user/repo.git
        path = parsed.path

    # Remove .git from the end if it exists
    if path.endswith(".git"):
        path = path[:-4]

    return path


def get_default_branch(git_repo: Repo) -> Optional[str]:
    """Get the default branch of the repository."""
    try:
        remote = git_repo.remote()
        remote.fetch()
        return remote.refs[0].name.replace("origin/", "")
    except Exception:
        try:
            return git_repo.active_branch.name
        except Exception:
            return None


def clean_untracked_files(git_repo: Repo, logger: logging.Logger) -> None:
    """Remove untracked files and folders in the local repository."""
    try:
        logger.info("Cleaning untracked files...")
        git_repo.git.clean("-fd")
        logger.info("Untracked files cleaned successfully")
    except Exception as e:
        logger.error(f"Error cleaning untracked files: {str(e)}")


def create_local_branches(git_repo: Repo, logger: logging.Logger) -> List[str]:
    """Create local tracking branches for all remote branches."""
    processed_branches = []
    try:
        remote = git_repo.remote()
        logger.info("Fetching all remote references...")
        remote.fetch()
        remote.fetch(tags=True)
        logger.info("Remote references fetched successfully")

        # Get all remote branches
        remote_branches = [ref for ref in remote.refs if ref.name != "origin/HEAD"]
        logger.info(f"Found {len(remote_branches)} remote branches")

        # Create local tracking branches for all remote branches
        for ref in remote_branches:
            branch_name = ref.name.replace("origin/", "")
            try:
                # Check if local branch already exists
                existing_branches = [b.name for b in git_repo.branches]

                if branch_name not in existing_branches:
                    logger.info(f"Creating local branch: {branch_name}")
                    git_repo.git.checkout("-b", branch_name, ref.name)
                    processed_branches.append(f"{branch_name} (new)")
                else:
                    logger.info(f"Updating existing branch: {branch_name}")
                    clean_untracked_files(git_repo, logger)
                    git_repo.git.checkout(branch_name)
                    git_repo.git.pull("origin", branch_name)
                    processed_branches.append(f"{branch_name} (updated)")

            except Exception as e:
                logger.error(f"Error processing branch {branch_name}: {str(e)}")
                processed_branches.append(f"{branch_name} (failed)")

        logger.info("All branches processed for offline access")

        # Log summary of processed branches
        if processed_branches:
            logger.info(f"Branches processed ({len(processed_branches)} total):")
            for branch in processed_branches:
                logger.info(f"  - {branch}")

        return processed_branches

    except Exception as e:
        logger.error(f"Error in create_local_branches: {str(e)}")
        return processed_branches


def process_repository(
    github_client: Github, repo_url: str, output_dir: str, logger: logging.Logger
) -> None:
    """Process a repository: download if it doesn't exist or update if it already
    exists."""
    try:
        repo_name = get_repo_name_from_url(repo_url)
        repo_dir = os.path.join(output_dir, repo_name.replace("/", "_"))

        logger.info(f"{'='*60}")
        logger.info(f"Processing repository: {repo_name}")
        logger.info(f"Repository URL: {repo_url}")
        logger.info(f"Local directory: {repo_dir}")

        if os.path.exists(repo_dir):
            logger.info(f"Repository exists locally - UPDATING {repo_name}")
            git_repo = Repo(repo_dir)

            # Ensure all branches are available locally for offline access
            create_local_branches(git_repo, logger)

            # Checkout default branch
            default_branch = get_default_branch(git_repo)
            if default_branch:
                logger.info(f"Checking out default branch: {default_branch}")
                clean_untracked_files(git_repo, logger)
                git_repo.git.checkout(default_branch)

        else:
            logger.info(f"Repository not found locally - DOWNLOADING {repo_name}")
            os.makedirs(repo_dir, exist_ok=True)

            logger.info("Cloning repository...")
            Repo.clone_from(repo_url, repo_dir)
            logger.info("Repository cloned successfully")

            git_repo = Repo(repo_dir)

            # Create local branches for all remote branches for offline access
            create_local_branches(git_repo, logger)

            # Checkout default branch
            default_branch = get_default_branch(git_repo)
            if default_branch:
                logger.info(f"Checking out default branch: {default_branch}")
                clean_untracked_files(git_repo, logger)
                git_repo.git.checkout(default_branch)

        # Get final list of all local branches for summary
        all_branches = [branch.name for branch in git_repo.branches]
        logger.info(f"Repository {repo_name} - Final branch summary:")
        logger.info(f"  Total local branches: {len(all_branches)}")
        logger.info(f"  Branch names: {', '.join(sorted(all_branches))}")

        logger.info(f"✅ Repository {repo_name} processed successfully")
        logger.info("Repository ready for offline use with all branches")

    except Exception as e:
        logger.error(f"❌ Error processing {repo_url}: {str(e)}")
        # Don't stop the script, continue with the next repo


def get_github_token(args) -> Optional[str]:
    """Get GitHub token from arguments or environment variables."""
    # Load environment variables from .env if it exists
    load_dotenv()

    # Return token from args or environment variable
    return args.token or os.getenv("GITHUB_TOKEN")


def main() -> None:
    # Setup logging first
    logger = setup_logging()

    try:
        logger.info("GitHub Repository Downloader started")
        logger.info("=" * 60)

        args = parse_args()
        logger.info(f"Input file: {args.input}")
        logger.info(f"Output directory: {args.output}")
        logger.info(f"Clean mode: {args.clean}")

        # Handle clean parameter - delete output directory if requested
        if args.clean and os.path.exists(args.output):
            logger.info(
                f"Clean mode enabled - removing existing directory: {args.output}"
            )
            try:
                shutil.rmtree(args.output)
                logger.info(f"Directory {args.output} removed successfully")
            except Exception as e:
                logger.error(f"Error removing directory {args.output}: {str(e)}")
                raise

        os.makedirs(args.output, exist_ok=True)
        logger.info(f"Output directory created/verified: {args.output}")

        token = get_github_token(args)
        if token:
            logger.info("GitHub token loaded - API rate limits will be higher")
        else:
            logger.warning("No GitHub token provided - API rate limits may apply")

        github_client = Github(token) if token else Github()

        repos = read_repos_file(args.input, logger)

        logger.info(f"Starting processing of {len(repos)} repositories...")
        for repo in tqdm(repos, desc="Processing repositories"):
            process_repository(github_client, repo, args.output, logger)

        logger.info("=" * 60)
        logger.info(
            f"Processing completed! All repositories downloaded to: {args.output}"
        )
        logger.info(
            "All repositories are ready for offline use with complete branch history"
        )

    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
