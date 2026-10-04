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

excel:
	python -m reporting_pipeline.cli excel-demo

operate:
	python -m reporting_pipeline.cli operate

reverse-test:
	python -m reporting_pipeline.cli reverse-test

container:
	docker build -t automated-reporting-pipeline .
	docker run --rm automated-reporting-pipeline

validate: lint test smoke excel operate reverse-test
