#!/bin/bash

# Siphon Agricultural Price Tracker - Health Check Script

echo "Running health checks for Siphon..."

# Check if containers are running
echo "Checking container status..."
containers=("siphon-frontend" "siphon-scraper" "siphon-proxy" "siphon-db-gui")

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "^$container$"; then
        echo "$container is running"
    else
        echo "$container is not running"
        exit 1
    fi
done

# Check API health
echo "Testing API health..."
api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/prices)
if [ "$api_response" -eq 200 ]; then
    echo "API is healthy (HTTP $api_response)"
else
    echo "API health check failed (HTTP $api_response)"
    exit 1
fi

# Check frontend
echo "Testing frontend..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
if [ "$frontend_response" -eq 200 ]; then
    echo "Frontend is healthy (HTTP $frontend_response)"
else
    echo "Frontend health check failed (HTTP $frontend_response)"
    exit 1
fi

# Check SSL certificate (if domain is configured)
if command -v openssl &> /dev/null; then
    echo "Checking SSL certificate..."
    if echo | openssl s_client -servername siphonag.com -connect siphonag.com:443 2>/dev/null | openssl x509 -noout -dates; then
        echo "SSL certificate is valid"
    else
        echo "SSL certificate check failed or not configured"
    fi
fi

# Check data freshness
echo "Checking data freshness..."
data_count=$(curl -s http://localhost/api/prices | jq length 2>/dev/null || echo "0")
if [ "$data_count" -gt 0 ]; then
    echo "API returning $data_count commodity prices"
else
    echo "No price data available"
fi

# Check disk space
echo "Checking disk usage..."
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 90 ]; then
    echo "Disk usage is acceptable ($disk_usage%)"
else
    echo "High disk usage ($disk_usage%)"
fi

# Check logs for errors
echo "Checking recent logs for errors..."
error_count=$(docker-compose logs --tail=100 | grep -i error | wc -l)
if [ "$error_count" -eq 0 ]; then
    echo "No recent errors in logs"
else
    echo "Found $error_count error messages in recent logs"
fi

echo "Health check completed!"