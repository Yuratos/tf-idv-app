FROM postgres:15

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    netcat-openbsd \
    postgresql-plpython3-15 

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPYCACHEPREFIX=/tmp/python-cache


ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_USER=postgres

COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY init-db.sql /docker-entrypoint-initdb.d/

RUN mkdir -p /var/run/postgresql && \
    chmod 777 /var/run/postgresql

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"] 
