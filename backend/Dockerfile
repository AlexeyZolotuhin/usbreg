FROM python:3.9
WORKDIR /app_backend
ENV FLASK_APP backend.py
ENV UPLOAD_FOLDER /tmp_upload
ENV SECRET_KEY you-will-never-guess
ENV DATABASE_URL mysql+pymysql://root:1111Aa@usb-mysql/usbstrela
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3",  "backend.py"]
