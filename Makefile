check:
	-isort .
	-black .
	-ruff . --fix
	-mypy .
