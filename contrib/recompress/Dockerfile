FROM python:3.8-buster

RUN curl -O http://mirror.download.kiwix.org/dev/ffmpeg-release-amd64-static.tar.xz
RUN tar xf ffmpeg-release-amd64-static.tar.xz
RUN mv ffmpeg-4.2.2-amd64-static/ff* /usr/local/bin/
RUN rm -rf ffmpeg-4.2.2-amd64-static ffmpeg-release-amd64-static.tar.xz

# image optimisation
RUN apt-get update -y \
    && apt-get install --no-install-recommends -y zip ghostscript qpdf pngquant jpegoptim gifsicle imagemagick \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# basic libraries
RUN pip3 install -U pip
RUN pip3 install humanfriendly jinja2 youtube-dl ipython requests python_dateutil openpyxl

# install external dependencies if present
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

# install scripts
COPY scripts/* /usr/local/bin/
RUN chmod +x /usr/local/bin/*

RUN mkdir -p /data
WORKDIR /data

CMD ["bash"]
