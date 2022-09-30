FROM python:3.8

# Install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends locales-all unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN wget -nv -L https://nodejs.org/dist/v12.16.3/node-v12.16.3-linux-x64.tar.xz && \
    tar -C /usr/local --strip-components 1 -xf node-v12.16.3-linux-x64.tar.xz && \
    rm node-v12.16.3-linux-x64.tar.xz && npm install -g handlebars

COPY nautiluszim /src/nautiluszim
COPY get_js_deps.sh requirements.txt setup.py README.md LICENSE MANIFEST.in /src/
RUN pip3 install --no-cache-dir -r /src/requirements.txt && cd /src/ && python3 ./setup.py install

CMD ["nautiluszim", "--help"]
