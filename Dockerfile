FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN mkdir -p /app/staticfiles
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN echo '#!/bin/bash\npython manage.py migrate\npython manage.py collectstatic --noinput\nexec gunicorn portfolio_blog.wsgi:application --bind 0.0.0.0:${PORT:-8000}' > /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]