FROM python:3.7

COPY ./requirements.txt requirements.txt

RUN pip install -U pip && \
    pip install --no-cache-dir -r /requirements.txt

COPY . code
WORKDIR /code
EXPOSE 9740

CMD gunicorn --workers=2 -b 0.0.0.0:9740 app:server --access-logfile -