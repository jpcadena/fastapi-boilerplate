check:
	-isort .
	-black .
	-ruff check . --fix
	-ruff format .
	-mypy --pretty .
update:
	-poetry update
	-pre-commit autoupdate
