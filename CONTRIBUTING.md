# Contributing to Preswald

Thank you for your interest in contributing to **Preswald**! This document outlines the project structure, how to set up your development environment, and the guidelines for contributing. Whether you’re fixing bugs, adding new features, or improving documentation, we appreciate your time and effort.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Setup Guide](#setup-guide)
3. [Development Workflow](#development-workflow)
4. [Style Guide](#style-guide)
5. [Pull Request Guidelines](#pull-request-guidelines)
6. [Issue Reporting Guidelines](#issue-reporting-guidelines)
7. [Community Support](#community-support)
8. [Acknowledgments](#acknowledgments)

## Project Structure

**Preswald** uses a modern tech stack to deliver its functionality:

- **Backend**: Python with FastAPI.
- **Frontend**: React + Vite.

The project structure looks like this:

```
preswald/
├── preswald/        # Core Python FastAPI backend
├── frontend/       # React + Vite frontend application
├── examples/       # Sample apps to showcase Preswald's capabilities
├── tests/          # Unit and integration tests
├── setup.py        # Python package configuration
└── README.md       # Project overview
```

## Setup Guide

### 1. Fork and Clone the Repository

1. **Fork the repository** on GitHub.
2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/StructuredLabs/preswald.git
   cd preswald
   ```

### 2. Set Up a Python Environment

We recommend using Conda to manage dependencies:

1. Create and activate a Conda environment:
   ```bash
   conda create -n preswald python=3.11 -y
   conda activate preswald
   ```
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

### 3. Build the Frontend and Backend

1. Build the frontend assets:
   ```bash
   python setup.py build_frontend
   ```
2. Build the backend:
   ```bash
   python -m build
   ```

### 4. Run the Example App

Verify your setup by running the sample app:

```bash
preswald run examples/earthquakes.py
```

## Development Workflow

Here’s a quick summary of the contributing workflow:

1. **Fork and clone the repository.**
2. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and follow the [Style Guide](#style-guide).
4. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** on the main repository.

## Style Guide

Follow these style guidelines to maintain consistency:

- **Python**: Use [PEP 8](https://peps.python.org/pep-0008/).
- **React**: Follow [React Best Practices](https://react.dev/learn).
- **Formatting/Linting**:
  - Python: Use `black`, `isort`, and `ruff`.
    ```bash
    black .
    isort .
    ruff .
    ```
    These are set up in the pre-commit hook - will run upon `git commit` on staged files
  - JavaScript: Use ESLint with the provided configuration.
    ```bash
    npm run lint
    ```

## Pull Request Guidelines

When submitting a PR:

1. Use a descriptive branch name (e.g., `feature/add-widget` or `fix/typo-readme`).
2. Write a clear and concise PR title and description.
   - **Title**: Start with a type prefix, such as `feat`, `fix`, or `docs`.
   - **Description**: Include context, screenshots (if applicable), and links to relevant issues.
3. Ensure your PR includes:
   - Relevant tests for your changes.
   - Updates to the documentation if applicable.

Example PR description:

```
feat: add new user authentication system

This PR adds user authentication via JWT tokens. Includes:
- Backend API endpoints for login and signup.
- React context integration for frontend.
- Unit tests for new functionality.

Fixes #42
```

## Issue Reporting Guidelines

When reporting an issue:

1. Use a clear and concise title.
2. Provide relevant details, such as:
   - Steps to reproduce the issue.
   - Expected vs. actual behavior.
   - Environment details (OS, Python version, browser).
   - Screenshots or logs, if applicable.

Example issue template:

```
**Describe the bug**
A clear and concise description of the issue.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain the issue.

**Environment**
- OS: [e.g., Windows, macOS, Linux]
- Python version: [e.g., 3.9]
- Browser: [e.g., Chrome, Firefox]
```

## Community Support

If you have questions or need help:

- Email us at **[founders@structuredlabs.com](mailto:founders@structuredlabs.com)**.
- Join the **Structured Users Slack** for discussions and support:  
  [Structured Users Slack Invite](https://structured-users.slack.com/join/shared_invite/zt-265ong01f-UHP6BP3FzvOmMQDIKty_JQ#/shared-invite/email).

## Acknowledgments

We’re deeply grateful for your contributions! Every bug report, feature suggestion, and PR helps us build a better **Preswald**. Let’s create something amazing together! 🚀
