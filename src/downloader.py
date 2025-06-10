#!/usr/bin/env python3

import argparse
import os
import sys
from typing import List, Optional
from urllib.parse import urlparse

from github import Github
from git import Repo
from tqdm import tqdm


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
    return parser.parse_args()


def read_repos_file(file_path: str) -> List[str]:
    """Read the repositories file and return the list of repos."""
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
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


def clean_untracked_files(git_repo: Repo) -> None:
    """Remove untracked files and folders in the local repository."""
    try:
        git_repo.git.clean("-fd")
    except Exception as e:
        print(f"Error cleaning untracked files: {str(e)}")


def process_repository(github_client: Github, repo_url: str, output_dir: str) -> None:
    """Process a repository: download if it doesn't exist or update if it already
    exists."""
    try:
        repo_name = get_repo_name_from_url(repo_url)
        repo_dir = os.path.join(output_dir, repo_name.replace("/", "_"))

        if os.path.exists(repo_dir):
            print(f"\nUpdating {repo_name}...")
            git_repo = Repo(repo_dir)
            remote = git_repo.remote()
            remote.fetch()
            remote.fetch(tags=True)
            default_branch = get_default_branch(git_repo)
            for ref in remote.refs:
                if ref.name != "origin/HEAD":
                    try:
                        branch_name = ref.name.replace("origin/", "")
                        clean_untracked_files(git_repo)
                        git_repo.git.checkout(branch_name)
                        git_repo.git.pull("origin", branch_name)
                    except Exception as e:
                        print(f"Error updating branch {branch_name}: {str(e)}")
            if default_branch:
                clean_untracked_files(git_repo)
                git_repo.git.checkout(default_branch)
        else:
            os.makedirs(repo_dir, exist_ok=True)
            print(f"\nDownloading {repo_name}...")
            Repo.clone_from(repo_url, repo_dir)
            git_repo = Repo(repo_dir)
            remote = git_repo.remote()
            default_branch = get_default_branch(git_repo)
            for ref in remote.refs:
                if ref.name != "origin/HEAD":
                    try:
                        branch_name = ref.name.replace("origin/", "")
                        if branch_name != default_branch:
                            clean_untracked_files(git_repo)
                            git_repo.git.checkout("-b", branch_name, ref.name)
                    except Exception as e:
                        print(f"Error downloading branch {branch_name}: {str(e)}")
            remote.fetch(tags=True)
            if default_branch:
                clean_untracked_files(git_repo)
                git_repo.git.checkout(default_branch)
        print(f"✅ Repository {repo_name} processed successfully")
    except Exception as e:
        print(f"❌ Error processing {repo_url}: {str(e)}")
        # Don't stop the script, continue with the next repo


def main() -> None:
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    github_client = Github(args.token) if args.token else Github()
    repos = read_repos_file(args.input)
    for repo in tqdm(repos, desc="Processing repositories"):
        process_repository(github_client, repo, args.output)


if __name__ == "__main__":
    main()
