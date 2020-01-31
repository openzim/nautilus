FROM openzim/zimwriterfs:1.3.7

# Install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends locales-all python3-pip curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install setuptools

COPY nautiluszim /src/nautiluszim
COPY get_js_deps.sh requirements.txt setup.py README.md LICENSE MANIFEST.in /src/
RUN cd /src/ && python3 ./setup.py install

CMD ["nautiluszim", "--help"]
