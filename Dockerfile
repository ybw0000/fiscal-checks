FROM python:3.12.3-bullseye AS builder

WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip && pip install uv && uv pip sync --prefix=/install /requirements.txt --system

FROM python:3.12.3-bullseye

WORKDIR /app

COPY --from=builder /install /usr/local
