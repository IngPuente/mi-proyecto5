# Etapa 1 - Build
FROM python:3.10-slim AS build

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 2 - Runtime
FROM python:3.10-slim

WORKDIR /app
COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY app/ .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
