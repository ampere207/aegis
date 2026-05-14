FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN apt-get update && apt-get install -y build-essential git libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --without dev --no-root
RUN mkdir -p /repos_storage
COPY . /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
