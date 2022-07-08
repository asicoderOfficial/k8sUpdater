FROM python:3.8
RUN apt update
RUN apt install git curl vim -y
RUN mkdir /kopf-operator
WORKDIR /kopf-operator
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./ .