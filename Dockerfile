FROM python:3.8
RUN apt update
#RUN apt install apt-file
#RUN apt update
RUN apt install git curl vim -y
RUN mkdir /kopf-operator
WORKDIR /kopf-operator
#Install dependencies
COPY requirements.txt .
RUN pip3.8 install -r requirements.txt
COPY ./ .

CMD ["/usr/local/bin/python3.8", "-u", "-m kopf", "run src/kube/main_operator.py"]
