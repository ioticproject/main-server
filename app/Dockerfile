FROM python:3.8.6-alpine3.11

WORKDIR /var/www/
ADD . /var/www/
RUN pip install -r requirements.txt

CMD python app.py