FROM python:3.10

SHELL ["bash", "-c"]

# Installing poetry
RUN pip install poetry

COPY /poetry.lock /app/poetry.lock
COPY /pyproject.toml /app/pyproject.toml

WORKDIR /app

RUN poetry config virtualenvs.create false --local && poetry install

COPY / /app

ENV PYTHONPATH=/app/src \
	BOT_TOKEN=${BOT_TOKEN} \
	REDIS_HOST=${REDIS_HOST} \
	REDIS_PORT=${REDIS_PORT} \
	TELEGRAPH_TOKEN=${TELEGRAPH_TOKEN} \
	TELEGRAPH_AUTHOR_NAME=${TELEGRAPH_AUTHOR_NAME} \
	TELEGRAPH_AUTHOR_URL=${TELEGRAPH_AUTHOR_URL}

CMD ["python", "-m", "app"]