install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

smoke:
	python -m reporting_pipeline.cli smoke

deliver:
	python -m reporting_pipeline.cli deliver

reverse-test:
	python -m reporting_pipeline.cli reverse-test

validate: lint test smoke reverse-test
