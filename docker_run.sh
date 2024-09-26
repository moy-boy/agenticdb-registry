#!/bin/bash

# Uncomment if needed
# docker rmi agenticdb:latest
# docker builder prune --all --force

# Remove all containers based on agenticdb:latest, both stopped and running
docker ps -a -q --filter "ancestor=agenticdb:latest" | xargs -r docker rm -f

# Build the new image with the tag agenticdb:latest
docker build --no-cache -t agenticdb:latest .

# Run the newly built container with the name agenticdb_container and expose port 8000
docker run -d --name agenticdb_container -p 8000:8000 agenticdb:latest
