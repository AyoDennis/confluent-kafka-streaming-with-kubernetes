FROM confluentinc/cp-kafka:latest-ubi9


WORKDIR /team

COPY requirements.txt /team
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "producer.py" ]
