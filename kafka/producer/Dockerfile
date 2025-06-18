# # FROM confluentinc/cp-kafka:latest-ubi9

# FROM confluentinc/cp-kafka:7.8.0


# WORKDIR /team

# COPY . .

# RUN pip install --no-cache-dir -r requirements.txt

# CMD [ "python", "producer/producer.py" ]


# Build stage - use Python image to install dependencies
FROM python:3.9-slim

WORKDIR /team
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "producer/producer.py"]