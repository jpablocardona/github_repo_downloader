#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest.mock as mock
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from downloader import (
    get_repo_name_from_url,
    read_repos_file,
    get_default_branch,
    clean_untracked_files,
    parse_args,
)


class TestGetRepoNameFromUrl:
    """Test cases for get_repo_name_from_url function."""

    def test_ssh_url_with_git_extension(self):
        """Test SSH URL with .git extension."""
        url = "git@github.com:user/repo.git"
        result = get_repo_name_from_url(url)
        assert result == "git@github.com:user/repo"

    def test_ssh_url_without_git_extension(self):
        """Test SSH URL without .git extension."""
        url = "git@github.com:user/repo"
        result = get_repo_name_from_url(url)
        assert result == "git@github.com:user/repo"

    def test_https_url_with_git_extension(self):
        """Test HTTPS URL with .git extension."""
        url = "https://github.com/user/repo.git"
        result = get_repo_name_from_url(url)
        assert result == "/user/repo"

    def test_https_url_without_git_extension(self):
        """Test HTTPS URL without .git extension."""
        url = "https://github.com/user/repo"
        result = get_repo_name_from_url(url)
        assert result == "/user/repo"

    def test_organization_repo(self):
        """Test organization repository URL."""
        url = "https://github.com/microsoft/vscode.git"
        result = get_repo_name_from_url(url)
        assert result == "/microsoft/vscode"


class TestReadReposFile:
    """Test cases for read_repos_file function."""

    def test_read_valid_file(self):
        """Test reading a valid repos file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("git@github.com:user/repo1.git\n")
            f.write("https://github.com/user/repo2.git\n")
            f.write("\n")  # Empty line should be filtered
            f.write("git@github.com:org/repo3.git\n")
            temp_path = f.name

        try:
            result = read_repos_file(temp_path)
            expected = [
                "git@github.com:user/repo1.git",
                "https://github.com/user/repo2.git",
                "git@github.com:org/repo3.git",
            ]
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_read_file_with_whitespace(self):
        """Test reading file with whitespace around URLs."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("  git@github.com:user/repo1.git  \n")
            f.write("\thttps://github.com/user/repo2.git\t\n")
            temp_path = f.name

        try:
            result = read_repos_file(temp_path)
            expected = [
                "git@github.com:user/repo1.git",
                "https://github.com/user/repo2.git",
            ]
            assert result == expected
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        with pytest.raises(SystemExit):
            read_repos_file("nonexistent_file.txt")


class TestGetDefaultBranch:
    """Test cases for get_default_branch function."""

    @patch("src.downloader.Repo")
    def test_get_default_branch_success(self, mock_repo_class):
        """Test successful default branch retrieval."""
        mock_repo = MagicMock()
        mock_remote = MagicMock()
        mock_ref = MagicMock()
        mock_ref.name = "origin/main"
        mock_remote.refs = [mock_ref]
        mock_repo.remote.return_value = mock_remote

        result = get_default_branch(mock_repo)
        assert result == "main"
        mock_remote.fetch.assert_called_once()

    @patch("src.downloader.Repo")
    def test_get_default_branch_fallback_to_active(self, mock_repo_class):
        """Test fallback to active branch when remote fetch fails."""
        mock_repo = MagicMock()
        mock_repo.remote.side_effect = Exception("Remote error")
        mock_repo.active_branch.name = "master"

        result = get_default_branch(mock_repo)
        assert result == "master"

    @patch("src.downloader.Repo")
    def test_get_default_branch_all_fail(self, mock_repo_class):
        """Test when both remote and active branch fail."""
        mock_repo = MagicMock()
        mock_repo.remote.side_effect = Exception("Remote error")

        # Mock the active_branch property to raise an exception
        type(mock_repo).active_branch = mock.PropertyMock(
            side_effect=Exception("Active branch error")
        )

        result = get_default_branch(mock_repo)
        assert result is None


class TestCleanUntrackedFiles:
    """Test cases for clean_untracked_files function."""

    @patch("src.downloader.Repo")
    def test_clean_success(self, mock_repo_class):
        """Test successful cleaning of untracked files."""
        mock_repo = MagicMock()
        mock_git = MagicMock()
        mock_repo.git = mock_git

        clean_untracked_files(mock_repo)
        mock_git.clean.assert_called_once_with("-fd")

    @patch("src.downloader.Repo")
    @patch("builtins.print")
    def test_clean_with_error(self, mock_print, mock_repo_class):
        """Test cleaning with error handling."""
        mock_repo = MagicMock()
        mock_git = MagicMock()
        mock_git.clean.side_effect = Exception("Clean error")
        mock_repo.git = mock_git

        clean_untracked_files(mock_repo)
        mock_print.assert_called_once_with(
            "Error cleaning untracked files: Clean error"
        )


class TestParseArgs:
    """Test cases for parse_args function."""

    @patch("sys.argv", ["downloader.py", "--input", "repos.txt"])
    def test_parse_args_minimal(self):
        """Test parsing minimal required arguments."""
        args = parse_args()
        assert args.input == "repos.txt"
        assert args.output == "./repos"
        assert args.token is None

    @patch(
        "sys.argv",
        [
            "downloader.py",
            "--input",
            "test.txt",
            "--output",
            "/tmp/repos",
            "--token",
            "ghp_token123",
        ],
    )
    def test_parse_args_all_options(self):
        """Test parsing all arguments."""
        args = parse_args()
        assert args.input == "test.txt"
        assert args.output == "/tmp/repos"
        assert args.token == "ghp_token123"

    @patch("sys.argv", ["downloader.py"])
    def test_parse_args_missing_required(self):
        """Test parsing with missing required argument."""
        with pytest.raises(SystemExit):
            parse_args()


if __name__ == "__main__":
    pytest.main([__file__])
