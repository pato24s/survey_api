FROM python:3

EXPOSE 5000

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD ["flask", "db", "init"]

CMD ["flask", "db", "migrate"]

CMD ["flask", "db", "upgrade"]

CMD ["python", "app.py"]