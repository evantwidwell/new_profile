# Install uv
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml

# Copy the project into the intermediate image
COPY . /app

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN mkdir -p /app/staticfiles

# Install curl for downloading parquet files
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the environment, but not the source code
COPY --from=builder /usr/local /usr/local

# Copy the project files
COPY . .

# Make sure we use the system Python with installed packages
ENV PATH="/usr/local/bin:$PATH"

RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
echo "Database host: $PGHOST"\n\
echo "Database name: $PGDATABASE"\n\
python manage.py migrate\n\
python manage.py collectstatic --noinput\n\
exec gunicorn portfolio_blog.wsgi:application --bind 0.0.0.0:${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]