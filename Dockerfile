FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install ".[test]"

COPY . .

# гарантируем, что скрипты исполняемые и без CRLF —
# если репо клонили на Windows, git мог сбросить chmod и подкинуть \r
RUN sed -i 's/\r$//' scripts/*.sh && chmod +x scripts/*.sh

EXPOSE 8000

CMD ["./scripts/entrypoint.sh"]
