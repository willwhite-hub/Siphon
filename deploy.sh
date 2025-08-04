#!/bin/bash

# Siphon Agricultural Price Tracker - Production Deployment Script

echo "Starting Siphon deployment..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Remove old images to ensure fresh build
echo "Cleaning up old images..."
docker system prune -f

# Build and start all services
echo "Building and starting services..."
docker-compose up -d --build

# Check service status
echo "Checking service status..."
docker-compose ps

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 30

# Test API endpoint
echo "Testing API endpoint..."
if curl -f http://localhost/api/prices > /dev/null 2>&1; then
    echo "API is responding correctly"
else
    echo "API test failed"
    exit 1
fi

# Test frontend
echo "Testing frontend..."
if curl -f http://localhost > /dev/null 2>&1; then
    echo "Frontend is serving correctly"
else
    echo "Frontend test failed"
    exit 1
fi

echo "Deployment completed successfully!"
echo "Your application is available at: https://siphonag.com"
echo "Database GUI available at: http://localhost:8080"

# Show logs
echo "Recent logs:"
docker-compose logs --tail=10