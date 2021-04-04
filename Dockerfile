FROM python:3.9-slim
MAINTAINER Chad Bowman <chad.bowman0+github@gmail.com>

COPY . /app/
WORKDIR /app

RUN pip --version
RUN pip install --upgrade pip
RUN pip install -e .

ENTRYPOINT [ "python", "mercari-scanner/mercari_scanner.py" ]
