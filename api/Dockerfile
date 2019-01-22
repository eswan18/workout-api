FROM python:3.7-slim

ADD requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

ADD ./src /app/src

WORKDIR /app/src

CMD ["python", "main.py"]
