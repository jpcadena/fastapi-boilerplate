check:
	-isort .
	-black .
	-ruff . --fix
	-mypy .
update:
	poetry update
	pre-commit autoupdate
