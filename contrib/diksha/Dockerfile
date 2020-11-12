FROM python:3.8

VOLUME /src/data

WORKDIR /src
COPY requirements.txt /src
RUN pip install -r /src/requirements.txt

COPY filenames.map /src
COPY xls2collection.py /src
COPY source.xlsx /src

CMD ["./xls2collection.py", "source.xlsx"]

