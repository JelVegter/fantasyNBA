.DEFAULT: help
help:
	@echo "make setup"
	@echo "	1. installs virtualenv"
	@echo "	2. creates venv"
	@echo "	3. installs requirements.txt"
	@echo "	4. installs setup.py packages"
	@echo "make pytest"
	@echo "       run tests"
	@echo "make lint"
	@echo "       run pylint"
	@echo "make format"
	@echo "       run isort and black"
	@echo "make dup"
	@echo "       run docker-compose up"
	@echo "make dbuild"
	@echo "       run docker-compose build and up"
	@echo "make help"
	@echo "       print help"

setup: requirements.txt setup.py
	pip install virtualenv==20.13.2
	python -m virtualenv venv
	(	\
		source venv/bin/activate; \
		pip install -e .; \
		pip install -r requirements.txt \
	)

rmdep:
	pip install pipdeptree; \
	pipdeptree -f --warn silence | grep -E '^[a-zA-Z0-9\-]+' > requirements.txt; \

pytest:
	python -m pytest

lint:
	python -m pylint --errors-only fantasy_nba/*.py

format:
	python -m isort .
	python -m black --line-length 99 .

dup:
	docker-compose up

dbuild:
	docker-compose up --build

ddown:
	docker-compose down

clean:
	(find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf)
	rm -rf venv
	
active:
	source venv/bin/activate