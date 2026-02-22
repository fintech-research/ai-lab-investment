FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Remove the Yarn repository whose GPG key is no longer valid,
# which causes apt-get update to fail during feature installation.
RUN rm -f /etc/apt/sources.list.d/yarn.list /usr/share/keyrings/yarnkey.gpg

# Install just via official install script
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin
