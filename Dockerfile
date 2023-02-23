FROM python:3.8

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY . /app/

CMD python manage.py runserver 0.0.0.0:8000
EXPOSE 8000