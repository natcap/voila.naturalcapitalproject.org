FROM --platform=linux/amd64 mambaorg/micromamba:1.4.1-bullseye-slim

# Need to override the default PROJ_LIB; needs the trailing backslash
ENV PROJ_LIB /usr/local/share/proj/

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
ARG MAMBA_DOCKERFILE_ACTIVATE=1  # (otherwise python will not be found)
RUN micromamba install -y -n base -c conda-forge -f /tmp/environment.yml && \
        micromamba clean --all --yes && \
        pip cache purge

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]
