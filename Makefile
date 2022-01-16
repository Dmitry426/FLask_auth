dev: pre-commit

pre-commit:
	pre-commit install
	pre-commit autoupdate

isort:
	isort . --profile black

black:
	black .

mypy:
	mypy -p app

flake8:
	flake8 .

pylint:
	pylint app

lint: isort black mypy flake8 pylint
