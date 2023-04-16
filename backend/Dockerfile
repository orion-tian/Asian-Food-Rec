FROM nikolaik/python-nodejs:python3.7-nodejs18-slim

RUN npm i -g pnpm

ENV CONTAINER_HOME=/var/www

ADD ./frontend $CONTAINER_HOME
ADD ./backend $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

ARG DB_NAME
ENV DB_NAME $DB_NAME

RUN pnpm install
RUN pnpm build
RUN npx next export -o ./frontend-build

RUN pip install -r $CONTAINER_HOME/requirements.txt
