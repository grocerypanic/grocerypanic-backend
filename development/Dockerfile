FROM python:3.7-slim
MAINTAINER niall@niallbyrne.ca
LABEL PROJECT=panic

ENV PYTHONUNBUFFERED 1
ENV GITLEAKSVERSION="v7.2.0"

# Mark Container
RUN echo "panic" > /etc/container_release

# Install Dependencies
RUN apt-get update      && \
    apt-get upgrade -y  && \
    apt-get install -y     \
    bash                   \
    build-essential        \
    curl                   \
    jq                     \
    libpq-dev              \
    openssh-client         \
    postgresql-client      \
    shellcheck             \
    sudo                   \
    tig                    \
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
USER user

# Install latest gcloud sdk
RUN curl --fail -sL https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > gcloud.tar.gz \
  && mkdir -p /home/user/gcloud \
  && tar -C /home/user/gcloud -xf gcloud.tar.gz \
  && rm gcloud.tar.gz

# Initialize The gcloud sdk
RUN /home/user/gcloud/google-cloud-sdk/install.sh

# Copy the codebase
COPY . /app

# Setup The Dev CLI
RUN scripts/commander.sh setup
