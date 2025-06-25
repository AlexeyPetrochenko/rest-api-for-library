FROM python:3.12.4-slim-bookworm

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="/app/.venv/bin:$PATH"

# https://python-poetry.org/docs/faq#poetry-busts-my-docker-cache-because-it-requires-me-to-copy-my-source-files-in-before-installing-3rd-party-dependencies
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry install --only main --no-root --no-directory
COPY app /app/app
RUN poetry install --only main

COPY alembic.ini /app/
COPY migrations /app/migrations


CMD ["uvicorn", "app.web.app:create_app", "--host", "0.0.0.0", "--factory"]


