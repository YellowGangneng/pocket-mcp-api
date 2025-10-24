# syntax=docker/dockerfile:1.7

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/
COPY pocket /app/pocket
COPY main.py /app/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV MODULE_NAME=pocket.app.main
ENV VARIABLE_NAME=app
