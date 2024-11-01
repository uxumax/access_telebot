# Use the official Python image from the Docker Hub
FROM python:3.11.10-slim-bookworm

# Set essential env python variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create non-root user
RUN useradd -m user

# Set workdir
WORKDIR /home/user/workspace
