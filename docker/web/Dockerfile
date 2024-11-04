# Use the official Python image from the Docker Hub
FROM python:3.11.10-slim-bookworm

# Install xgettext for making bot messages translations
RUN apt-get update && \
    apt-get install -y gettext && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set essential env python variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create non-root user
RUN useradd -m user

# Set workdir
WORKDIR /home/user/workspace
