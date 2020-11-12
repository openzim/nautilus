FROM python:3.8

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

VOLUME /src/data

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r /src/requirements.txt

COPY filenames.map /src
COPY xls2collection.py /src
COPY source.xlsx /src

CMD ["./xls2collection.py", "source.xlsx"]

