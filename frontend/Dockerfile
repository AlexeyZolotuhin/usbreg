FROM python:3.9
WORKDIR /app_frontend
ENV FLASK_APP backend.py
ENV UPLOAD_FOLDER /tmp_upload
ENV SECRET_KEY you-will-never-guess
ENV BACKEND_ADDRESS http://backend:4000
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3",  "frontend.py"]
