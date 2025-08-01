import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historicalData, setHistoricalData] = useState({});
  const [expandedCards, setExpandedCards] = useState({});

  useEffect(() => {
    axios.get('http://localhost:8000/api/prices')
      .then(res => {
        console.log("Data received:", res.data);
        // Debug: Log the change values
        res.data.forEach(item => {
          console.log(`${item.commodity}: change = "${item.change}" (type: ${typeof item.change})`);
        });
        setPrices(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch prices:", err);
        setLoading(false);
      });
  }, []);

  const fetchHistoricalData = async (commodity) => {
    try {
      const response = await axios.get(`http://localhost:8000/history/${commodity.toLowerCase()}`);
      
      // Filter to show only one price per day (most recent for each date)
      const dailyPrices = {};
      response.data.forEach(item => {
        const date = new Date(item.timestamp).toDateString();
        if (!dailyPrices[date] || new Date(item.timestamp) > new Date(dailyPrices[date].timestamp)) {
          dailyPrices[date] = item;
        }
      });
      
      // Convert back to array and sort by date (newest first)
      const filteredData = Object.values(dailyPrices)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      
      setHistoricalData(prev => ({
        ...prev,
        [commodity]: filteredData
      }));
    } catch (error) {
      console.error(`Error fetching historical data for ${commodity}:`, error);
      setHistoricalData(prev => ({
        ...prev,
        [commodity]: []
      }));
    }
  };

  const toggleCard = (commodity) => {
    const isExpanded = !expandedCards[commodity];
    
    // Close all cards and only open the clicked one (if it wasn't already open)
    if (isExpanded) {
      setExpandedCards({ [commodity]: true });
      if (!historicalData[commodity]) {
        fetchHistoricalData(commodity);
      }
    } else {
      setExpandedCards({});
    }
  };

  const getChangeColor = (change) => {
    if (!change) return '#6c757d';
    // Convert to string and handle both string and number inputs
    const changeStr = change.toString();
    const numChange = parseFloat(changeStr.replace('%', ''));
    if (isNaN(numChange)) return '#6c757d';
    return numChange >= 0 ? '#28a745' : '#dc3545';
  };

  const getChangeIcon = (change) => {
    if (!change) return '→';
    // Convert to string and handle both string and number inputs
    const changeStr = change.toString();
    const numChange = parseFloat(changeStr.replace('%', ''));
    if (isNaN(numChange)) return '→';
    return numChange > 0 ? '↗' : numChange < 0 ? '↘' : '→';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <img 
            src="/brand_no_background.png" 
            alt="Old Tucka Agriculture" 
            className="brand-logo"
          />
          <h1 className="title">
            Commodity Market Dashboard
          </h1>
          <p className="subtitle">Real-time commodity prices and market trends</p>
        </header>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading market data...</p>
          </div>
        ) : (
          <div className="cards-grid">
            {prices.length === 0 ? (
              <div className="no-data">
                <span className="no-data-icon">📊</span>
                <h3>No Data Available</h3>
                <p>Market data is currently unavailable. Please try again later.</p>
              </div>
            ) : (
              prices.map((item, index) => (
                <div key={index} className="price-card">
                  <div className="card-header">
                    <h3 className="commodity-name">{item.commodity}</h3>
                  </div>
                  
                  <div className="price-section">
                    <div className="price-value">
                      {item.price}
                      <span className="price-unit">{item.unit}</span>
                    </div>
                  </div>

                  <div className="change-section">
                    <span 
                      className="change-value"
                      style={{ color: getChangeColor(item.change) }}
                    >
                      <span className="change-icon">{getChangeIcon(item.change)}</span>
{item.change ? `${item.change}${item.change.toString().includes('%') ? '' : '%'}` : 'N/A'}
                    </span>
                  </div>

                  {expandedCards[item.commodity] && (
                    <div className="historical-section">
                      <h4 className="historical-title">Historical Prices</h4>
                      <div className="historical-list">
                        {historicalData[item.commodity] ? (
                          historicalData[item.commodity].length > 0 ? (
                            historicalData[item.commodity].slice(0, 5).map((historical, idx) => (
                              <div key={idx} className="historical-item">
                                <span className="historical-price">
                                  {historical.price} {historical.unit}
                                </span>
                                <span className="historical-date">
                                  {new Date(historical.timestamp).toLocaleDateString()}
                                </span>
                              </div>
                            ))
                          ) : (
                            <div className="no-historical">No historical data available</div>
                          )
                        ) : (
                          <div className="loading-historical">Loading...</div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="card-footer">
                    <div className="timestamp-section">
                      <span className="timestamp">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                      <span className="time">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <button 
                      className="dropdown-toggle"
                      onClick={() => toggleCard(item.commodity)}
                    >
                      <span className="historical-label">Historical Data</span>
                      {expandedCards[item.commodity] ? '▲' : '▼'}
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        <footer className="footer">
          <p>Data updated every few minutes • Market information for reference only</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
