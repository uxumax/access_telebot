# Use the official Python image from the Docker Hub
FROM python:3.11.10-slim-bookworm

# This paragraph for serveo ssh back tunnel 
# Comment if you don't use it
RUN apt-get update && \
    apt-get install -y openssh-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
EXPOSE 22

# Set essential env python variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create non-root user
RUN useradd -m user

# Set workdir
WORKDIR /home/user/workspace
