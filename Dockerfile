FROM python:alpine3.16

COPY requirements.txt .

RUN apk --update add --no-cache --virtual .build-dependencies python3-dev build-base libffi-dev wget git \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-dependencies


RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ADD blackhat-bot.py /usr/src/app

CMD [ "python", "./blackhat-bot.py" ]
