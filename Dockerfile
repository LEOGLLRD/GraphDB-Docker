FROM eclipse-temurin:11-jdk-noble

ARG version=10.6.4
ARG download_url="https://maven.ontotext.com/repository/owlim-releases/com/ontotext/graphdb/graphdb/${version}/graphdb-${version}-dist.zip"
ARG download_url_checksum="${download_url}.md5"

# Downloading the required packages
RUN apt-get update && \
    apt-get install -u unzip && \
    apt-get install -y python3 python3-pip python3.12-venv net-tools less && \
    python3 -m venv /config/graphdb/python_env_graphdb

RUN adduser graphdb

# Downloading GraphDB
RUN curl -fsSL "${download_url}" > graphdb-${version}-dist.zip && \
    bash -c 'md5sum -c - <<<"$(curl -fsSL ${download_url_checksum})  graphdb-${version}-dist.zip"' && \
    unzip graphdb-${version}-dist.zip && \
    rm -f graphdb-${version}-dist.zip && \
    mkdir -p /exec && chmod -R 755 /exec


RUN mv graphdb-${version} graphdb && \
    chown -R graphdb /graphdb && \
    chown -R graphdb /exec && \
    mkdir "/opt/graphdb" && \
    chown -R graphdb /opt/graphdb && \
    mkdir -p "/shared-volume/graphdb" && \
    chown -R graphdb /shared-volume/graphdb && \
    # Creating folder for installations from the bash scripts
    mkdir -p /config/graphdb && \
    chown -R graphdb /config/graphdb

COPY entrypoint.sh evo.sh /exec/

USER graphdb

ENTRYPOINT ["/exec/entrypoint.sh"]

CMD ["-Dgraphdb.home=/opt/graphdb/home", "-Dgraphdb.distribution=docker"]

EXPOSE 7200
EXPOSE 7300