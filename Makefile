check:
	-isort .
	-black .
	-ruff check . --fix
	-ruff format .
	-mypy .
update:
	poetry update
	pre-commit autoupdate
