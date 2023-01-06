FROM python:3.9-alpine

RUN adduser -D frontend
WORKDIR /home/frontend/

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY frontend.py config.py start_front.sh ./
RUN chown -R frontend:frontend ./

USER frontend

EXPOSE 3000
ENTRYPOINT ["./start_front.sh"]


