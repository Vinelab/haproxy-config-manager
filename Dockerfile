FROM django

MAINTAINER Jad Chamoun <jad.chamoun@vinelab.com>

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip install djangorestframework

CMD ["python","manage.py","runserver","0.0.0.0:8000"]