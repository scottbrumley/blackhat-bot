FROM python:alpine3.16 as development-env
COPY requirements.txt .
RUN apk --update add --no-cache --virtual .build-dependencies python3-dev build-base libffi-dev wget git \
&& pip install --no-cache-dir -r requirements.txt \
&& apk del .build-dependencies
RUN mkdir -p /usr/src/app/test
ADD blackhat-bot.py /usr/src/app
COPY test/test-blackhat-bot.py /usr/src/app/test
WORKDIR /usr/src/app/test
CMD [ "python", "./test-blackhat-bot.py" ]


FROM python:alpine3.16 as production-env
COPY requirements.txt .
RUN apk --update add --no-cache --virtual .build-dependencies python3-dev build-base libffi-dev wget git \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del .build-dependencies
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD blackhat-bot.py /usr/src/app
CMD [ "python", "./blackhat-bot.py" ]
