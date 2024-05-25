FROM python:3.11-slim-bookworm
LABEL org.opencontainers.image.source https://github.com/openzim/nautilus

# Install necessary packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      # locales required if tool has any i18n support
      locales-all wget \
      libmagic1 \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip install --no-cache-dir -U \
      pip \
&& wget -nv -L https://nodejs.org/dist/v12.16.3/node-v12.16.3-linux-x64.tar.gz \
&& tar -C /usr/local --strip-components 1 -xf node-v12.16.3-linux-x64.tar.gz \
&& rm node-v12.16.3-linux-x64.tar.gz \
&& npm install -g handlebars

# Copy pyproject.toml and its dependencies
COPY pyproject.toml README.md /src/
COPY src/nautiluszim/__about__.py /src/src/nautiluszim/__about__.py

# Install Python dependencies
RUN pip install --no-cache-dir /src

# Copy code + associated artifacts
COPY src /src/src
COPY *.md /src/

# Install + cleanup
RUN pip install --no-cache-dir /src \
 && rm -rf /src

CMD ["nautiluszim", "--help"]
