FROM ubuntu:24.04 AS dev-base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    gfortran \
    python3 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/

FROM dev-base AS dev
WORKDIR /workspaces/VolumeLibrary
