FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY sql ./sql

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 reporting \
    && mkdir -p /app/output \
    && chown -R reporting:reporting /app

USER reporting

CMD ["python", "-m", "reporting_pipeline.cli", "operate"]
