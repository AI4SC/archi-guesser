#FROM  registry.access.redhat.com/ubi9/python-39
FROM python:3.9-slim-buster

ENV DASH_DEBUG_MODE False
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8050
CMD ["gunicorn", "--workers=5", "--threads=1", "-b", "0.0.0.0:8050", "--reload", "app:server"]