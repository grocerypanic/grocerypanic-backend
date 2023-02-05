ARG BUILD_ARG_PYTHON_VERSION=3.7

FROM python:${BUILD_ARG_PYTHON_VERSION}-slim AS base
MAINTAINER niall@niallbyrne.ca
LABEL PROJECT=panic

ARG BUILD_ARG_CONTAINER_GID=1000
ARG BUILD_ARG_CONTAINER_UID=1000

ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE "false"
ENV PYTHONUNBUFFERED 1
ENV GITLEAKSVERSION "v7.2.0"

# Mark Container
RUN echo "panic" > /etc/container_release

# Install Dependencies
RUN apt-get update                       && \
    apt-get upgrade -y                   && \
    apt-get install -y                      \
    bash                                    \
    build-essential                         \
    curl                                    \
    gdb                                     \
    golang-github-pelletier-go-toml         \
    jq                                      \
    libpq-dev                               \
    openssh-client                          \
    postgresql-client                       \
    procps                                  \
    shellcheck                              \
    sudo                                    \
    tig                                     \
    vim

# Install Git Leaks
RUN curl --fail -sL "https://github.com/zricethezav/gitleaks/releases/download/${GITLEAKSVERSION}/gitleaks-linux-amd64"    \
    -o /usr/bin/gitleaks                                                                                                && \
    chmod +x /usr/bin/gitleaks

# Install cloud sql proxy
RUN curl --fail -sL https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 > /usr/bin/cloud_sql_proxy \
  && chmod +x /usr/bin/cloud_sql_proxy

# Create the runtime user, and enforce permissions
RUN groupadd user -g "${BUILD_ARG_CONTAINER_GID}"
RUN useradd user -d /home/user                    \
                 -s /bin/bash                     \
                 -u "${BUILD_ARG_CONTAINER_UID}"  \
                 -g "${BUILD_ARG_CONTAINER_GID}"  \
                 -m

# Setup directories
RUN mkdir -p /app
RUN chown -R user:user /app
WORKDIR /app

# Add user to sudoers, and make the default user
RUN echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Include the local binary folder in PATH
ENV PATH "/home/user/.local/bin/:${PATH}"

USER user

# Install Poetry and Wheel
RUN pip install "poetry<1.2" wheel       && \
    pip install --upgrade pip

# Copy the codebase
COPY . /app

# Enforce git repository permissions
USER root
RUN chown -R user:user /app
USER user

# Install the Poetry Dependencies
RUN scripts/commander.sh setup

# ======================================================

# Admin Environment
FROM base AS admin

# Install latest gcloud sdk
RUN sudo curl --fail -sL https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > gcloud.tar.gz \
  && mkdir -p /home/user/gcloud \
  && tar -C /home/user/gcloud -xf gcloud.tar.gz \
  && rm gcloud.tar.gz

# Initialize The gcloud sdk
RUN sudo /home/user/gcloud/google-cloud-sdk/install.sh
