ARG PYTHON_VERSION=3.7
FROM python:$PYTHON_VERSION-slim AS base
MAINTAINER niall@niallbyrne.ca
LABEL PROJECT=panic

ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE "false"
ENV PYTHONUNBUFFERED 1
ENV GITLEAKSVERSION="v7.2.0"

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

# Setup directories
RUN mkdir -p /home/user /app
WORKDIR /app

# Create the runtime user, and change permissions
RUN useradd user -d /home/user        \
                 -s /bin/bash         \
                 -M                   \
 && chown -R user:user /home/user     \
 && chown -R user:user /app           \
 && echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Include the local binary folder in PATH
ENV PATH "/home/user/.local/bin/:${PATH}"

USER user

# Install Latest Poetry
RUN pip install poetry wheel       && \
    pip install --upgrade pip

# Copy the codebase
COPY . /app

# Install the Poetry Dependencies
RUN scripts/commander.sh setup

# ======================================================

# Deployment Environment
FROM base AS deployment

# Install latest gcloud sdk
RUN sudo curl --fail -sL https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > gcloud.tar.gz \
  && mkdir -p /home/user/gcloud \
  && tar -C /home/user/gcloud -xf gcloud.tar.gz \
  && rm gcloud.tar.gz

# Initialize The gcloud sdk
RUN sudo /home/user/gcloud/google-cloud-sdk/install.sh
