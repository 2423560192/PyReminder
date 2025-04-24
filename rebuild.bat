@echo off
echo Stopping all containers...
docker-compose down

echo Removing all related containers, networks, volumes, and images...
docker-compose rm -f -s -v

echo Cleaning Docker build cache...
docker builder prune -f

echo Rebuilding and starting containers...
docker-compose build --no-cache
docker-compose up -d

echo Containers rebuilt successfully! 