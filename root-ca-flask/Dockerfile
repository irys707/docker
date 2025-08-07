FROM python:3.11-slim
RUN apt-get update && apt-get install -y libffi-dev libssl-dev build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
ENV FLASK_ENV=production \
    DATA_PATH=/data/ca \
    FLASK_APP=app.py
VOLUME ["/data/ca"]
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
