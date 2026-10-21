FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pytest.ini .
COPY src/ src/
COPY tests/ tests/

CMD ["pytest", "tests/test_harness.py", "-v"]
