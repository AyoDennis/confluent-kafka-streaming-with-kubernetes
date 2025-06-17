FROM python:3.13-alpine

WORKDIR /team

COPY requirements.txt /team
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./producer.py" ]