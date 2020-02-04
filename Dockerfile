FROM python:3.8

# Install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends locales-all wget unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget http://download.openzim.org/release/zimwriterfs/zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN tar -C /usr/local/bin --strip-components 1 -xf zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN rm -f zimwriterfs_linux-x86_64-1.3.7.tar.gz
RUN chmod +x /usr/local/bin/zimwriterfs
RUN zimwriterfs --version

COPY nautiluszim /src/nautiluszim
COPY get_js_deps.sh requirements.txt setup.py README.md LICENSE MANIFEST.in /src/
RUN pip3 install $(grep "zimscraperlib" /src/requirements.txt)
RUN cd /src/ && python3 ./setup.py install

CMD ["nautiluszim", "--help"]
