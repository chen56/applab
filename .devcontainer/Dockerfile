# Use a standard Python devcontainer image
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install uv globally (into /usr/local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | BINDIR=/usr/local/bin sh

# Use vscode user (already present in the base image)
USER vscode

# Set environment variables
# Use a mirror for faster Python downloads (per project pyproject.toml)
ENV UV_PYTHON_INSTALL_MIRROR="https://registry.npmmirror.com/-/binary/python-build-standalone/"

# Set working directory
WORKDIR /workspace
