# Siphon

An all-in-one agricultural tracker for commodities, weather, roads, and water levels.  
Currently supports live price tracking for **cotton**, **wheat**, **barley**, and **beef**, with historical data logging and a modern web dashboard.

---

## Features

- **Multi-Commodity Support**: Tracks Cotton, Wheat, Barley, and Beef prices
- **Historical Price Logging**: Automatically stores all prices in a SQLite database
- **Live REST API**: Built with FastAPI to serve both current and historical price data
- **Modern Web Dashboard**: Beautiful React-based UI with real-time price cards showing current prices, percentage changes, and visual indicators
- **Auto Fetch on Startup**: Scrapes latest prices when the backend launches
- **Docker Support**: Fully containerized with Docker Compose for easy deployment
- **Production Ready**: Includes Nginx reverse proxy and SSL certificate support

---

## Web Dashboard

The modern React-based dashboard features:
- **Real-time Price Cards**: Each commodity displayed in an attractive card format
- **Visual Price Indicators**: Arrows and color coding for price changes (green for up, red for down)
- **Percentage Changes**: Clear display of price movement percentages
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Old Tucka Agriculture Branding**: Professional agricultural theme

### Development Mode
To run the frontend in development mode:
```bash
cd frontend
npm install
npm start
# Opens http://localhost:3000
```

The dashboard fetches live data from the FastAPI backend and updates automatically.

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
├── backend/                    # FastAPI backend
│   ├── main.py                # FastAPI app
│   ├── commodity_scraper.py   # Commodity-specific scrapers
│   ├── fetcher.py             # Fetch+insert wrapper
│   ├── models.py              # SQLAlchemy models
│   ├── db.py                  # DB setup and insert logic
│   ├── currency.py            # Currency conversion utilities
│   ├── requirements.txt       # Python dependencies
│   └── data/prices.db         # SQLite database
├── frontend/                  # React dashboard
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   └── App.css           # Styling
│   ├── public/               # Static assets including brand images
│   └── package.json          # Node.js dependencies
├── nginx/                     # Reverse proxy configuration
├── certbot/                   # SSL certificate management
├── docker-compose.yml         # Service orchestration
└── README.md                  # This file
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
- [x] Modern React dashboard with price cards
- [x] Visual price change indicators
- [x] Production deployment with Nginx
- [ ] Historical price charts and trends
- [ ] Weather & water level data integration
- [ ] SMS/Email price alerts
- [ ] Mobile app version
- [ ] User authentication and personalized dashboards

---
