FROM --platform=linux/amd64 mambaorg/micromamba:1.4.1-bullseye-slim

# Need to override the default PROJ_LIB; needs the trailing backslash
ENV PROJ_LIB /usr/local/share/proj/
ENV VOILA_APP_IP 0.0.0.0

####
# Instructions for including GCS FUSE from https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse#run-clone-sample-repository-python
USER root
RUN set -e; \
    apt-get update -y && apt-get install -y tini lsb-release curl gnupg2; \
    gcsFuseRepo=gcsfuse-`lsb_release -c -s`; \
    echo "deb http://packages.cloud.google.com/apt $gcsFuseRepo main" | \
    tee /etc/apt/sources.list.d/gcsfuse.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key add -; \
    apt-get update; \
    apt-get install -y gcsfuse \
    && apt-get clean \
    && mkdir /mnt/gcs

# Set fallback mount directory
ENV MNT_DIR /mnt/gcs

ENV BUCKET jupyter-app-temp-storage

# Copy local code to the container image.
ADD gcsfuse_run.sh /opt/

# Ensure the script is executable
RUN chmod +x /opt/gcsfuse_run.sh

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)

ADD demo.ipynb /opt/app.ipynb
ADD *.py /opt/
WORKDIR /opt/
RUN micromamba install -y -n base -c conda-forge -f /tmp/environment.yml && \
        micromamba clean --all --yes && \
        pip cache purge && \
        jupyter trust /opt/app.ipynb

# Use tini to manage zombie processes and signal forwarding
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Pass the startup script as arguments to Tini
CMD ["/opt/gcsfuse_run.sh"]
