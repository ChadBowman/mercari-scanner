FROM python:3.9-slim
MAINTAINER Chad Bowman <chad.bowman0+github@gmail.com>

COPY . /app/
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install .

ENTRYPOINT [ "python3", "-m", "mercariscanner" ]
