FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# docker build -t dev-mspr-601-api .
# docker run --name dev_mspr_601_api -p 5001:5000 -v ./:/app -d dev-mspr-601-api python3 /app/app.py