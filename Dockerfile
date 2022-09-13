# pull the official base image
FROM python:3.10-alpine

# set work directory
WORKDIR /usr/src/custodian

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip 
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      build-base gcc python3-dev  musl-dev libffi-dev openssl-dev cargo
RUN apk add vim
RUN pip install azure-cli
COPY ./requirements.txt /usr/src/custodian
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/custodian

EXPOSE 8000

CMD ["python", "manage.py", "runserver  --http_timeout=3600", "0.0.0.0:8000"]

