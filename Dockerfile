FROM python:3.8-slim

# Set the working directory
WORKDIR /firetail

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the Firetail repository into the container
COPY . /firetail

# Install Python dependencies
RUN pip install --no-cache-dir -r /firetail/requirements.txt

# Expose the required port
EXPOSE 8080

# Run the bot
CMD ["python3", "/firetail/firetail"]
