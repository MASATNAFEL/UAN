FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD gunicorn PROYECTO_UAN.wsgi:application --bind 0.0.0.0:$PORT