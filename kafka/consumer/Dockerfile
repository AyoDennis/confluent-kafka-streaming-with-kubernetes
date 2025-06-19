FROM python:3.9-slim

WORKDIR /team

COPY ../requirements.txt ./consumer .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "consumer.py"]