FROM python:3.10.7-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc vim procps

# create the app user
RUN addgroup --system app && adduser --system --group app

# create directory for the app user
RUN mkdir -p ${HOME}
RUN mkdir ${APP_HOME}

WORKDIR ${APP_HOME}

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ${APP_HOME}/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . ${APP_HOME}

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

EXPOSE 5000

# run entrypoint.prod.sh
ENTRYPOINT ["./entrypoint.sh"]