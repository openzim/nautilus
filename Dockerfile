FROM python:3.8

# add zimwriterfs
RUN wget http://download.openzim.org/release/zimwriterfs/zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN tar -C /usr/bin --strip-components 1 -xf zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN rm -f zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN chmod +x /usr/bin/zimwriterfs
RUN zimwriterfs --version

# Install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends locales-all wget unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN wget https://nodejs.org/dist/v12.16.3/node-v12.16.3-linux-x64.tar.xz && \
    tar -C /usr/local --strip-components 1 -xf node-v12.16.3-linux-x64.tar.xz && \
    rm node-v12.16.3-linux-x64.tar.xz
RUN npm install -g handlebars

COPY nautiluszim /src/nautiluszim
COPY get_js_deps.sh requirements.txt setup.py README.md LICENSE MANIFEST.in /src/
RUN pip3 install -r /src/requirements.txt
RUN cd /src/ && python3 ./setup.py install

CMD ["nautiluszim", "--help"]
