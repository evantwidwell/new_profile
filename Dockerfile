FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN mkdir -p /app/staticfiles
COPY requirements.txt ./
COPY pip.conf ./
RUN pip install --upgrade pip && pip install --no-cache-dir --prefer-binary --only-binary=psycopg2 -r requirements.txt
COPY . .
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py collectstatic --noinput\n\
exec gunicorn portfolio_blog.wsgi:application --bind 0.0.0.0:${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]