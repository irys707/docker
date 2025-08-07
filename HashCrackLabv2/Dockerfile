FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    hashcat \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m appuser
USER appuser

CMD ["python", "run.py"]

# ADD THIS TO THE BOTTOM OF YOUR Dockerfile

# Install gosu for user switch
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
