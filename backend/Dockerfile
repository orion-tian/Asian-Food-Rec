FROM nikolaik/python-nodejs:python3.7-nodejs18-slim

RUN npm i -g pnpm

ARG DB_NAME
ENV DB_NAME $DB_NAME

ENV CONTAINER_HOME=/var/www

WORKDIR $CONTAINER_HOME

ADD ./frontend/package.json ./frontend/pnpm-lock.yaml $CONTAINER_HOME

RUN pnpm install

ADD ./frontend $CONTAINER_HOME

RUN pnpm build
RUN npx next export -o ./frontend-build

ADD ./backend/requirements.txt $CONTAINER_HOME

RUN pip install -r $CONTAINER_HOME/requirements.txt

ADD ./backend $CONTAINER_HOME
