.DEFAULT: help
help:
	@echo "make install"
	@echo "       install all the dependencies specified in pyproject.toml and poetry.lock"
	@echo "make build"
	@echo "       packages the application in wheel format"
	@echo "make pytest"
	@echo "       run tests"
	@echo "make lint"
	@echo "       run pylint
	@echo "make format"
	@echo "       run isort and black"
	@echo "make dup"
	@echo "       run docker-compose up"
	@echo "make dbuild"
	@echo "       run docker-compose build and up"
	@echo "make help"
	@echo "       print help"

venv:
	pip install virtualenv
	pip install --upgrade virtualenv
	cd venv/bin
	. activate
	# python -m virtualenv venv

setup: requirements.txt
	source venv/bin/activate
	pip install -r requirements.txt

rm_dep: venv
	pip install pipdeptree
	rm requirements.txt
	pipdeptree -f --warn silence | grep -E '^[a-zA-Z0-9\-]+' > requirements.txt

pytest:
	python -m pytest

lint:
	python -m pylint fantasy_nba/*.py

format:
	python -m isort .
	python -m black --line-length 99 .

dup:
	docker-compose up

dbuild:
	docker-compose up --build

clean:
	rm -rf venv
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

activate:
	source venv/bin/activate