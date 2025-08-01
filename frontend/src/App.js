import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedCommodities, setExpandedCommodities] = useState({});

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

  const toggleCommodity = (commodityName) => {
    const isExpanded = !expandedCommodities[commodityName];
    
    // Close all commodities and only open the clicked one (if it wasn't already open)
    if (isExpanded) {
      setExpandedCommodities({ [commodityName]: true });
    } else {
      setExpandedCommodities({});
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
          <div className="commodity-selector">
            {prices.length === 0 ? (
              <div className="no-data">
                <span className="no-data-icon">📊</span>
                <h3>No Data Available</h3>
                <p>Market data is currently unavailable. Please try again later.</p>
              </div>
            ) : (
              <div className="commodities-container">
                {prices.map((item, index) => (
                  <div key={index} className="commodity-column">
                    <div 
                      className={`commodity-item ${expandedCommodities[item.commodity] ? 'active' : ''}`}
                      onClick={() => toggleCommodity(item.commodity)}
                    >
                      <span className="commodity-name-selector">
                        {item.commodity.split(' ')[0]} {/* Show first word (Wheat, Barley, etc.) */}
                      </span>
                      <span className="dropdown-arrow">
                        {expandedCommodities[item.commodity] ? '▲' : '▼'}
                      </span>
                    </div>
                    
                    {expandedCommodities[item.commodity] && (
                      <div className="expanded-commodity-card">
                        <div className="price-card expanded">
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
                            <div className="timestamp-section">
                              <span className="timestamp">
                                {new Date(item.timestamp).toLocaleDateString()}
                              </span>
                              <span className="time">
                                {new Date(item.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
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
