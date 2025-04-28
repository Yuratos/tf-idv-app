FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /tmp/python-cache && \
    chmod 777 /tmp/python-cache

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPYCACHEPREFIX=/tmp/python-cache

COPY . .


EXPOSE 8082

RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /tmp/uvicorn && \
    chmod 777 /tmp/uvicorn
USER appuser

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"] 
