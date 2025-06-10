# 📦 GitHub Repository Downloader

🚀 Python tool for bulk downloading and maintaining GitHub repositories. Includes functionality to list organization repositories and process multiple repositories with all their branches and tags.

## 📁 Project Structure

```
github_repo_downloader/
├── src/
│   ├── list_org_repos.py      # Lists all repositories from an organization
│   └── downloader.py          # Downloads/updates repositories from input file
├── requirements.txt           # Python dependencies
├── repos.txt                 # Example file with repository URLs
├── CLAUDE.md                 # Guide for Claude Code
└── README.md                 # This documentation
```

## ✨ Key Features

- 🏢 **Organization listing**: Get all repositories from a GitHub organization
- 📥 **Bulk download**: Process multiple repositories from an input file
- 🔄 **Smart updating**: Detects existing repositories and updates them automatically
- 🌳 **Complete support**: Downloads all branches, tags, and references
- 📊 **Visual progress**: Progress bars with `tqdm` for real-time tracking
- ⚡ **Error handling**: Continues processing even if an individual repository fails
- 🔗 **Flexible formats**: Support for SSH and HTTPS URLs

## 📋 Requirements

- 🐍 Python 3.8 or higher
- 🛠️ Git installed on the system
- 🔑 GitHub personal access token (recommended to avoid API limits)
- 🔐 SSH key configured for GitHub (for SSH URLs)

## ⚙️ Installation

1. 📥 Clone this repository:
```bash
git clone <repository-url>
cd github_repo_downloader
```

2. 📦 Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### 1️⃣ List organization repositories

Generate a list of all repositories from an organization:

```bash
python src/list_org_repos.py --org organization_name --token your_github_token
```

**Options:**
- `--org`: Organization name (required)
- `--token`: GitHub personal access token (required)
- `--output`: File to save the list (optional, defaults to screen output)

**Example:**
```bash
# Display on screen
python src/list_org_repos.py --org microsoft --token ghp_xxxxxxxxxxxx

# Save to file
python src/list_org_repos.py --org microsoft --token ghp_xxxxxxxxxxxx --output microsoft_repos.txt
```

### 2️⃣ Download/update repositories

Process multiple repositories from an input file:

```bash
python src/downloader.py --input repos.txt --output ./repos --token your_github_token
```

**Options:**
- `--input`: File with repository list (required)
- `--output`: Destination directory (optional, default: `./repos`)
- `--token`: GitHub token (optional, but recommended)

**Input file format:**
```
git@github.com:user/repo1.git
https://github.com/user/repo2.git
git@github.com:org/repo3.git
```

## ⚙️ System Behavior

### 🔄 Repository Processing

1. **New repositories**: Clones completely with all branches and tags
2. **Existing repositories**: 
   - Updates all remote branches
   - Downloads new tags
   - Cleans untracked files
   - Keeps default branch active

### 📂 Directory Naming

Repositories are saved using the format: `user_repository`
- `microsoft/vscode` → `microsoft_vscode/`
- `facebook/react` → `facebook_react/`

### ❌ Error Handling

- Errors in individual repositories don't stop the complete process
- Descriptive error messages are shown for each error
- The script continues with the next repository automatically

## 📚 Dependencies

```
PyGithub>=1.59.0    # GitHub API interaction
GitPython>=3.1.0    # Git operations in Python
tqdm>=4.64.0        # Progress bars
flake8>=7.0.0       # Code linting
black>=24.0.0       # Code formatting
pytest>=8.0.0       # Unit testing framework
pytest-mock>=3.12.0 # Mocking for tests
```

## 🧪 Testing

The project includes comprehensive unit tests for the core functionality:

### Running Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_downloader.py -v

# Run tests with coverage
python -m pytest --cov=src
```

### Test Coverage
- ✅ URL parsing functions (SSH and HTTPS formats)
- ✅ File reading and validation
- ✅ Repository name extraction
- ✅ Default branch detection
- ✅ Command line argument parsing
- ✅ Error handling scenarios

## 🔍 Code Quality

### Linting
The project uses `flake8` for code linting and `black` for code formatting:

```bash
# Check code style with flake8
flake8 src/

# Format code with black
black src/

# Check what black would change (without modifying)
black --check src/
```

### Configuration Files
- `.flake8`: Flake8 configuration with line length and ignore rules
- `pyproject.toml`: Black formatter configuration
- `pytest.ini`: Pytest configuration and test discovery settings

## 💼 Typical Use Cases

### 💾 Complete Organization Backup
```bash
# 1. List all organization repos
python src/list_org_repos.py --org my-org --token $GITHUB_TOKEN --output my-org-repos.txt

# 2. Download all repositories
python src/downloader.py --input my-org-repos.txt --output ./backup-org --token $GITHUB_TOKEN
```

### 🔄 Regular Synchronization
```bash
# Update existing repositories (run periodically)
python src/downloader.py --input repos.txt --output ./repos --token $GITHUB_TOKEN
```

### 📦 Repository Migration
```bash
# Download specific repositories for migration
python src/downloader.py --input repositories-to-migrate.txt --output ./migration
```

## ⚠️ Important Notes

- 🔑 **GitHub Tokens**: Recommended to avoid rate limiting
- 🔐 **SSH Keys**: Required for URLs in format `git@github.com:...`
- 💾 **Disk space**: Consider total size before downloading large organizations
- 🌐 **Connectivity**: Requires stable Internet connection for Git operations
- 🔒 **Permissions**: Token must have read permissions for private repositories

## 🔧 Troubleshooting

### 🔐 SSH Authentication Error
```bash
# Verify SSH configuration
ssh -T git@github.com
```

### ⏱️ API Limits
```bash
# Use token to increase limits
export GITHUB_TOKEN=your_token_here
python src/downloader.py --input repos.txt --token $GITHUB_TOKEN
```

### 📦 Large Repositories
```bash
# Run in smaller batches for very large organizations
head -10 all-repos.txt > batch1.txt
python src/downloader.py --input batch1.txt --output ./repos
```