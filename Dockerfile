FROM python:3.12.10-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

COPY app app
COPY migrations migrations
COPY alembic.ini ./

ENTRYPOINT ["sh", "./entrypoint.sh"]
