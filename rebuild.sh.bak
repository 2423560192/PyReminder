#!/bin/bash

# Stop all containers
docker-compose down

# Remove all related containers, networks, volumes, and images
docker-compose rm -f -s -v

# Clean Docker build cache
docker builder prune -f

# Rebuild and start containers
docker-compose build --no-cache
docker-compose up -d

echo "Containers rebuilt successfully!" 