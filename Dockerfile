FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE ${PORT}

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}", "--workers", "2"]
