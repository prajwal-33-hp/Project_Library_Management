FROM python:3.11-slim

WORKDIR /app

COPY library/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY library/ .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
