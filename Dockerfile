FROM python:3.6-slim

# Install required system packages
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/shibdib/Firetail.git /firetail

# Create config directory
RUN mkdir /config

RUN pip install discord.py==1.2.5

# Set environment variables
ENV CONFIG=/config LOG=/config/bot.log PYTHONPATH=/firetail

# Expose the port for Cloud Run
EXPOSE 8080

# Define entrypoint
ENTRYPOINT ["python3", "/firetail/firetail/__main__.py"]
