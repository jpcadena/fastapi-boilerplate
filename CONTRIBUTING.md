# CONTRIBUTING.md

First of all, thank you for considering contributing to our project. We value your time and your interest in this project, and we appreciate every contribution that helps us improve it. Below are some guidelines for contributing.

## Table of Contents

- [Getting Started](#getting-started)
- [Pull Requests](#pull-requests)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Documentation](#documentation)
- [Contact](#contact)

## Getting Started

1. Ensure you have forked the repository and cloned your fork to your local machine. This will allow you to make and test your changes before pushing them for consideration.
2. Create a new branch for your feature or bugfix. This keeps your changes separate from the main project and makes it easier to merge your changes in later.

```
git checkout -b feature/AmazingFeature
```

## Pull Requests

1. Commit your changes to your branch.
```bash
git commit -m 'Add some AmazingFeature'
```

2. Push your branch to your fork of the repository on GitHub.
```bash
git push origin feature/AmazingFeature
```

3. Open a Pull Request from your fork to our repository. Please provide a
   detailed explanation of your changes and reference any related issues.

## Code Style

We follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code. Please ensure your contributions adhere to this standard.

We recommend using a linter to check your code quality. You can check the documentation for [Visual Studio Code](https://code.visualstudio.com/docs/python/linting#_run-linting) or [Jetbrains Pycharm](https://github.com/leinardi/pylint-pycharm/blob/master/README.md) for more information.

For autocompletion, we recommend the [Tabnine](https://www.tabnine.com/install) plugin.

## Commit Messages

Please use clear and meaningful commit messages. This helps us understand the changes you've made and the reasoning behind them. If your commit resolves a specific issue, reference it in your commit message.

## Documentation

When adding new code, please use docstrings with **reStructuredText** format by adding triple double quotes **"""** after function definition. Add a brief function description, also for the parameters including the return value and its corresponding data type.

## Contact

If you have any questions or need further clarification on anything, feel free to reach out. We are here to help!

Back to [README](README.md).
