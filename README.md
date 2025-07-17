# Siphon

An all-in-one agricultural tracker for commodities, weather, roads, and water levels.  
Currently supports live price tracking for **cotton**, **wheat**, **barley**, and **beef**, with historical data logging and a web UI.

---

## Features

- **Multi-Commodity Support**: Tracks Cotton, Wheat, Barley, and Beef prices
- **Historical Price Logging**: Automatically stores all prices in a SQLite database
- **Live REST API**: Built with FastAPI to serve both current and historical price data
- **Web UI (React)**: Frontend app to display prices in a table (charts coming soon)
- **Auto Fetch on Startup**: Scrapes latest prices when the backend launches
- **Docker Support**: Fully containerized with Docker Compose for easy deployment

---

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Git
- Node.js + npm (for frontend development)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/willwhite-hub/Siphon
   cd siphon
   ```

2. **Create data directory**
   ```bash
   mkdir -p data
   ```

3. **Start the app**
   ```bash
   docker compose up --build
   ```

4. **Visit your services**
   | Service         | URL                      | Description                      |
   |-----------------|--------------------------|----------------------------------|
   | API             | http://localhost:8000    | FastAPI application              |
   | API Docs        | http://localhost:8000/docs | Swagger-style interactive docs |
   | Database Viewer | http://localhost:8080    | SQLite web interface             |
   | Frontend (dev)  | http://localhost:3000    | React app (run separately)       |

---

## API Usage

### Get Current Prices
```bash
curl http://localhost:8000/prices
```

### Get Historical Prices for a Commodity
```bash
curl http://localhost:8000/history/cotton
curl http://localhost:8000/history/wheat
```

### Health Check
```bash
curl http://localhost:8000/
```

---

## React Frontend

### Run the UI
1. Open a new terminal:
   ```bash
   cd frontend
   npm install
   npm start
   ```

2. Open: [http://localhost:3000](http://localhost:3000)

The React app fetches from `/prices` and displays them in a table. CORS is enabled in FastAPI to allow cross-origin requests from localhost:3000.

---

## Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize DB
python -c "from db import init_db; init_db()"

# Run FastAPI app
uvicorn main:app --reload
```

---

## Project Structure

```
siphon/
├── main.py               # FastAPI app
├── commodity_scraper.py  # Commodity-specific scrapers
├── fetcher.py            # Fetch+insert wrapper
├── models.py             # SQLAlchemy models
├── db.py                 # DB setup and insert logic
├── frontend/             # React frontend
├── docker-compose.yml    # Service orchestration
├── Dockerfile            # Backend Docker image
└── data/prices.db        # SQLite DB with price history
```

---

## Data Sources

- **Cotton**: [Cotlook A Index](https://www.cotlook.com)
- **Wheat/Barley**: [NSW DPI](https://www.dpi.nsw.gov.au/agriculture/commodity-report)
- **Beef**: [ABARES](https://www.agriculture.gov.au/abares/data/weekly-commodity-price-update)

---

## Roadmap

- [x] Multi-commodity scraper
- [x] Store historical prices in SQLite
- [x] React UI for live prices
- [ ] Historical price charts
- [ ] Weather & water level data
- [ ] SMS/Email price alerts
- [ ] Mobile app version

---
