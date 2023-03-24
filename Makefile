install:
	pip install poetry && \
	poetry install

start:
	poetry run python main_tg.py