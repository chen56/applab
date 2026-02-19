# Use a standard Python devcontainer image
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Node.js (NodeSource script internally uses apt, which may still warn)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

# Install git-lfs
RUN apt-get update && apt-get install -y git-lfs

# Install global npm packages (individual layers for caching)
RUN npm install -g @google/gemini-cli@0.29.2
RUN npm install -g @qwen-code/qwen-code@0.10.2
RUN npm install -g @tencent-ai/codebuddy-code@2.50.5

# Reset DEBIAN_FRONTEND
ENV DEBIAN_FRONTEND=dialog

# Use vscode user (already present in the base image)
USER vscode

# Set environment variables
# Use a mirror for faster Python downloads (per project pyproject.toml)
ENV UV_PYTHON_INSTALL_MIRROR="https://registry.npmmirror.com/-/binary/python-build-standalone/"

# Set working directory
WORKDIR /workspace
