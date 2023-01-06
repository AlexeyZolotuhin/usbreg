FROM python:3.9-alpine

RUN adduser -D backend
WORKDIR /home/backend/

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY backend.py config.py start_back.sh ./
COPY migrations migrations

USER backend

EXPOSE 4000
ENTRYPOINT ["./start_back.sh"]
