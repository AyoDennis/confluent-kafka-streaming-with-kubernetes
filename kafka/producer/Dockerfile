FROM python:3.9-slim

WORKDIR /team

COPY ../requirements.txt ./producer .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "producer.py"]