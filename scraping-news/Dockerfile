FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

COPY src/ ./src/
COPY robots.txt .
RUN mkdir -p output

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["--help"]
