FROM python:3.8
SHELL ["/bin/bash", "-c"]
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y && apt-get install postgresql-client -y

WORKDIR /app

COPY ./monitoring/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

RUN export PYTHONPATH="$PYTHONPATH:/app"

ADD ./monitoring/app .
ADD ./common /app/common
