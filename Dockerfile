# Use a lightweight Python image
FROM python:3.9-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repository, install Python dependencies, and create config directory
RUN \
    git clone https://github.com/shibdib/Firetail.git /firetail && \
    pip install -r /firetail/requirements.txt && \
    mkdir /config

# Set environment variables
ENV CONFIG=/config LOG=/config/bot.log

# Define entrypoint for the container
ENTRYPOINT ["python3", "/firetail/firetail"]
