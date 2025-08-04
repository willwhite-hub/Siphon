# Siphon Agricultural Price Tracker - Deployment Guide

## Pre-deployment Checklist

### Code Ready
- [x] Frontend updated to use relative API paths (`/api/prices`)
- [x] Development proxy removed from package.json
- [x] Production build tested successfully
- [x] All cotton dropdown styling completed
- [x] All commodity scrapers working

### Docker Configuration
- [x] Multi-stage frontend Dockerfile (Node.js build + Nginx serve)
- [x] Backend Dockerfile with Python 3.11 Alpine
- [x] Docker Compose with all services configured
- [x] Nginx reverse proxy with SSL termination
- [x] Certbot for SSL certificate management
- [x] SQLite database with GUI access

### Production Files Created
- [x] `deploy.sh` - Main deployment script
- [x] `health-check.sh` - Health monitoring script
- [x] `.env.production` - Production environment variables
- [x] `DEPLOYMENT.md` - This deployment guide

## Deployment Steps

### 1. Server Preparation
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version

# Clone/update the repository
git pull origin main
```

### 2. SSL Certificate Setup (First Time Only)
```bash
# Create initial certificate directories
sudo mkdir -p ./certbot/conf

# Get initial SSL certificate
sudo docker run --rm -v $(pwd)/certbot/conf:/etc/letsencrypt -v $(pwd)/certbot/www:/var/www/certbot certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d siphonag.com -d www.siphonag.com
```

### 3. Deploy Application
```bash
# Run deployment script
./deploy.sh
```

### 4. Verify Deployment
```bash
# Run health check
./health-check.sh

# Check logs
docker-compose logs -f
```

## Service URLs

- **Website**: https://siphonag.com
- **API**: https://siphonag.com/api/prices
- **Database GUI**: http://your-server-ip:8080

## Monitoring Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart services
docker-compose restart [service-name]

# Update and redeploy
git pull && ./deploy.sh
```

## Troubleshooting

### Container Issues
```bash
# Rebuild specific service
docker-compose up -d --build [service-name]

# Remove all containers and rebuild
docker-compose down && docker system prune -f && docker-compose up -d --build
```

### SSL Issues
```bash
# Renew certificates manually
docker-compose exec certbot certbot renew

# Check certificate status
openssl x509 -in ./certbot/conf/live/siphonag.com/fullchain.pem -text -noout
```

### Database Issues
```bash
# Access database directly
docker exec -it siphon-scraper python -c "from db import SessionLocal; from models import Price; db = SessionLocal(); print('Records:', db.query(Price).count())"

# Reset database
rm ./data/prices.db
docker-compose restart scraper
```

## Architecture Overview

```
Internet → Nginx Proxy → Frontend (React) + Backend (FastAPI)
                    ↓
              SQLite Database
                    ↓
            Scheduled Price Scraping
```

## Security Features

- HTTPS/SSL encryption
- Secure headers in Nginx
- No hardcoded secrets
- Container isolation
- Database access controls

## Backup Strategy

```bash
# Backup database
cp ./data/prices.db ./backups/prices-$(date +%Y%m%d).db

# Backup SSL certificates
tar -czf ./backups/ssl-$(date +%Y%m%d).tar.gz ./certbot/conf/
```

## Performance Optimization

- Multi-stage Docker builds for minimal image sizes
- Nginx static file serving
- SQLite for fast local database access
- Container resource limits can be added to docker-compose.yml if needed

## Post-Deployment Verification

1. Website loads at https://siphonag.com
2. All 4 commodity dropdowns working (Cotton, Wheat, Barley, Beef)
3. Cotton shows Cotlook A Index + Futures contracts
4. API returns JSON data at /api/prices
5. Database GUI accessible on port 8080
6. SSL certificate valid and auto-renewing
7. Price data updating automatically

Ready for production deployment!