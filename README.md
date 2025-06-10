# Siphon

An all-in-one agricultural tracker for commodities, weather, roads and water levels. Currently focused on cotton price tracking with plans to expand to other agricultural data.

## Features

- **Cotton Price Tracking**: Automatically scrapes cotton prices from Cotlook A Index
- **REST API**: FastAPI-based API for accessing price data
- **Scheduled Updates**: Automated weekly price updates via cron job
- **Database GUI**: Web-based SQLite database viewer
- **Docker Support**: Fully containerized with Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/willwhite-hub/Siphon
   cd siphon
   ```

2. **Create data directory** (if it doesn't exist)
   ```bash
   mkdir -p data
   ```

3. **Start the application**
   ```bash
   docker compose up --build
   ```

4. **Verify services are running**
   ```bash
   docker compose ps
   ```

### Services & Access Points

After running `docker-compose up -d`, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **API** | http://localhost:8000 | Main FastAPI application |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Database GUI** | http://localhost:8080 | SQLite database web interface |

## API Usage

### Get Latest Cotton Prices
```bash
curl http://localhost:8000/prices
```

**Example Response:**
```json
{
  "commodity": "Cotton Price (Cotlook A Index)",
  "price": 73.50,
  "change": -0.25,
  "published_at": "2025-06-10T13:00:00",
  "source": "https://www.cotlook.com"
}
```

### Health Check
```bash
curl http://localhost:8000/
```

## Manual Price Update

To manually trigger a price scrape (useful for testing):

```bash
docker exec cotton-scraper python cotton_scraper.py
```

## Project Structure

```
siphon/
├── main.py              # FastAPI application
├── cotton_scraper.py    # Cotlook price scraper
├── models.py           # SQLAlchemy database models
├── db.py               # Database configuration
├── fetcher.py          # Alternative price fetcher (backup)
├── docker-compose.yml  # Docker services configuration
├── Dockerfile          # Container build instructions
├── requirements.txt    # Python dependencies
└── data/              # SQLite database storage
    └── prices.db      # Price history database
```

## Configuration

### Scraping Schedule

The scraper runs automatically every Tuesday at 01:00 (to account for Cotlook's Monday 13:00 GMT updates). To modify the schedule, edit the cron expression in `docker-compose.yml`:

```yaml
# Current: Every Tuesday at 01:00
command: "echo '0 1 * * 2 cd /app && python cotton_scraper.py >> /app/scraper.log 2>&1' > /etc/crontabs/root && crond -f -l 2"
```

### Environment Variables

Create a `.env` file for custom configuration:

```env
DATABASE_URL=sqlite:///./data/prices.db
API_PORT=8000
DB_GUI_PORT=8080
```

## Development

### Running Locally (without Docker)

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database**
   ```bash
   python -c "from db import init_db; init_db()"
   ```

3. **Run the API server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Test the scraper**
   ```bash
   python cotton_scraper.py
   ```

### Adding New Data Sources

To extend Siphon with additional agricultural data:

1. Create a new scraper module (e.g., `weather_scraper.py`)
2. Add corresponding database models in `models.py`
3. Create new API endpoints in `main.py`
4. Update the Docker Compose configuration for scheduling


## Data Sources

- **Cotton Prices**: [Cotlook A Index](https://www.cotlook.com) - Industry standard cotton price benchmark

## Roadmap

- [ ] Weather data integration
- [ ] Road condition monitoring
- [ ] Water level tracking
- [ ] Historical data visualization
- [ ] Price alerts and notifications
- [ ] Mobile app support

---