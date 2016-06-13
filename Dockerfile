FROM django:python2

MAINTAINER Jad Chamoun <jad.chamoun@vinelab.com>

COPY . /code

WORKDIR /code

RUN pip install djangorestframework

CMD ["python","manage.py","runserver","0.0.0.0:8000"]