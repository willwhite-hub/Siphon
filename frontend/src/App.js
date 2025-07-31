import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/prices')
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

                  <div className="card-footer">
                    <span className="timestamp">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                    <span className="time">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </span>
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
