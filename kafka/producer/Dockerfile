FROM python:3.9-slim

WORKDIR /team
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "producer/producer.py"]