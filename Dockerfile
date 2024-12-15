FROM python:3.12.3-bullseye AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app

WORKDIR /app

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

RUN chmod +x entrypoint.sh
RUN chmod +x migrate-db.sh
RUN chmod +x downgrade-db.sh

EXPOSE 8000

CMD ./entrypoint.sh
