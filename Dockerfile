# Use Python 3.12 image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

ENV PYTHONPATH=/app

# Install curl
RUN apt-get update && apt-get install -y curl python3-distutils build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry --version

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /app/

RUN poetry install --without dev --no-root && poetry add python-dotenv

# Install dependencies
RUN poetry install --without dev --no-root

# Install uvicorn
RUN poetry add uvicorn

# Copy all application code
COPY . /app/

# Expose local port
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
