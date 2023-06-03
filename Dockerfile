FROM python:3.11-slim-buster

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install curl -y \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./

RUN ls -l /app

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev

COPY . ./

#CMD alembic upgrade head && \
#    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0
