.PHONY: install run test lint format

install:
	python -m pip install -r requirements.txt

run:
	streamlit run app/streamlit_app.py

test:
	pytest

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

