# CONTRIBUTING.md

First of all, thank you for considering contributing to our project. We value your time and your interest in this project, and we appreciate every contribution that helps us improve it. Below are some guidelines for contributing.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Getting Started](#getting-started)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Pre-commit Checks](#pre-commit-checks)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Contact](#contact)

## Development Environment Setup

For a smoother development experience, we recommend the following extensions for VSCode and plugins for PyCharm:

**VSCode Extensions**:

- Black Formatter
- Code Spell Checker
- dotenv
- GitHub Actions
- GitLens
- isort
- Live Preview
- Live Server
- Live Share
- Makefile Tools
- Markdown Preview Enhanced
- Material Icon Theme
- mypy
- Path Intellisense
- Prettier
- Pylance
- Python
- ruff
- YAML

**PyCharm Plugins**:

- .env files
- .ignore
- Atom Material Icons
- JSON Parser
- Makefile Language
- Material Theme UI
- mypy
- Pydantic
- Rainbow Brackets
- Requirements
- String Manipulation
- reStructuredText

Please refer to the respective extension and plugin documentation for installation and usage instructions.

## Getting Started

1. Ensure you have forked the repository and cloned your fork to your local machine. This will allow you to make and test your changes before pushing them for consideration.
2. Create a new branch for your feature or bugfix. This keeps your changes separate from the main project and makes it easier to merge your changes in later.

   ```bash
   git checkout -b feature/AmazingFeature
   ```

## Code Style

We follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code. Please ensure your contributions adhere to this standard.

We recommend using a linter to check your code quality. You can check the documentation for [Visual Studio Code](https://code.visualstudio.com/docs/python/linting#_linting) or [JetBrains PyCharm](https://www.jetbrains.com/help/pycharm/using-docstrings-to-specify-types.html) for more information.

For autocompletion, we recommend the [TabNine](https://www.tabnine.com/install) plugin.

## Documentation

When adding new code, please use docstring with **reStructuredText** format by adding triple double quotes **"""** after function definition. Add a brief function description, also for the parameters including the return value and its corresponding data type.

## Pre-commit Checks

Before committing your code, you must have `make` installed on your system. For Windows users, we recommend using [Chocolatey](https://chocolatey.org/), a package manager that simplifies the process of installing and managing software.

To install Chocolatey, open an administrative PowerShell and execute:

   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
   ```

After installing Chocolatey, you can install `make` by running:

   ```powershell
   choco install make
   ```

Once `make` is installed, you can run the following command in the root of your project to execute the checks defined in the `Makefile`:

   ```bash
   make check
   ```

Please ensure that all checks pass before submitting a pull request.

## Commit Messages

Please use clear and meaningful commit messages. This helps us understand the changes you've made and the reasoning behind them. If your commit resolves a specific issue, reference it in your commit message.

## Pull Requests

1. Commit your changes to your branch.

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

2. Push your branch to your fork of the repository on GitHub.

   ```bash
   git push origin feature/AmazingFeature
   ```

3. Open a Pull Request from your fork to our repository. Please provide a detailed explanation of your changes and reference any related issues.

## Contact

If you have any questions or need further clarification on anything, feel free to reach out. We are here to help!

Back to [README](README.md).
