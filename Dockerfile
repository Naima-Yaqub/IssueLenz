# Use a Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y curl bash

# Copy the Python dependencies file (requirements.txt)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies using pip
RUN pip install -r /app/requirements.txt

# Set up environment variables from .env file
COPY .env /app/.env

# Copy the entire project into the container
COPY . /app/

# Ensure the scripts have the correct permissions
RUN chmod +x /app/issues_summarizer/*.py

# Copy the start script and give it execution permissions
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set the entrypoint command
CMD ["/app/start.sh"]
