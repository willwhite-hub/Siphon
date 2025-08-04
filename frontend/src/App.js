import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedCommodities, setExpandedCommodities] = useState({});

  useEffect(() => {
    axios.get('/api/prices')
      .then(res => {
        console.log("Data received:", res.data);
        // Debug: Log the change values
        res.data.forEach(item => {
          console.log(`${item.commodity}: change = "${item.change}" (type: ${typeof item.change})`);
        });
        
        // Group cotton commodities together
        const groupedData = [];
        const cottonItems = [];
        const otherItems = [];
        
        res.data.forEach(item => {
          if (item.commodity.toLowerCase().includes('cotton')) {
            cottonItems.push(item);
          } else {
            otherItems.push(item);
          }
        });
        
        // Add cotton group if we have cotton items
        if (cottonItems.length > 0) {
          groupedData.push({
            commodity: 'Cotton',
            isGroup: true,
            contracts: cottonItems,
            price: cottonItems[0]?.price || 0,
            unit: cottonItems[0]?.unit || '',
            change: cottonItems[0]?.change || 0,
            timestamp: cottonItems[0]?.timestamp || new Date().toISOString()
          });
        }
        
        // Add other commodities
        groupedData.push(...otherItems);
        
        setPrices(groupedData);
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
                <span className="no-data-icon">$</span>
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
                        {item.isGroup ? item.commodity : item.commodity.split(' ')[0]} {/* Show group name or first word */}
                      </span>
                      <span className="dropdown-arrow">
                        {expandedCommodities[item.commodity] ? '▲' : '▼'}
                      </span>
                    </div>
                    
                    {expandedCommodities[item.commodity] && (
                      <div className="expanded-commodity-card">
                        {item.isGroup ? (
                          // Cotton group with Cotlook A Index at top and futures below
                          <div className="price-card expanded">
                            
                            {(() => {
                              // Separate Cotlook A Index from futures contracts
                              const cotlookContract = item.contracts.find(c => c.commodity.includes('Cotlook A Index'));
                              const futuresContracts = item.contracts.filter(c => !c.commodity.includes('Cotlook A Index'));
                              
                              return (
                                <>
                                  {/* Cotlook A Index at the top */}
                                  {cotlookContract && (
                                    <div className="cotlook-section" style={{ marginBottom: '15px' }}>
                                      <div className="contract-row" style={{ 
                                        padding: '10px 0', 
                                        borderBottom: '2px solid #ddd',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                      }}>
                                        <div style={{ 
                                          fontSize: '16px', 
                                          fontWeight: '600',
                                          color: 'white',
                                          flex: '1'
                                        }}>
                                          Cotlook A Index:
                                        </div>
                                        
                                        <div style={{ 
                                          fontSize: '16px',
                                          fontWeight: '600',
                                          color: 'white',
                                          marginLeft: '10px'
                                        }}>
                                          {cotlookContract.price} {cotlookContract.unit}
                                        </div>
                                        
                                        <div style={{ 
                                          marginLeft: '10px',
                                          minWidth: '60px',
                                          textAlign: 'right'
                                        }}>
                                          <span 
                                            className="change-value"
                                            style={{ 
                                              color: getChangeColor(cotlookContract.change),
                                              fontSize: '0.8rem',
                                              padding: '0.25rem 0.5rem',
                                              borderRadius: '12px'
                                            }}
                                          >
                                            <span className="change-icon" style={{ fontSize: '0.9rem' }}>{getChangeIcon(cotlookContract.change)}</span>
                                            {cotlookContract.change ? `${cotlookContract.change}${cotlookContract.change.toString().includes('%') ? '' : '%'}` : 'N/A'}
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Futures contracts section */}
                                  {futuresContracts.length > 0 && (
                                    <div className="futures-section">
                                      <div style={{ 
                                        fontSize: '14px', 
                                        fontWeight: '600',
                                        color: 'white',
                                        marginBottom: '8px',
                                        textTransform: 'uppercase',
                                        letterSpacing: '0.5px'
                                      }}>
                                        Futures
                                      </div>
                                      
                                      {futuresContracts.map((contract, contractIndex) => {
                                        // Format contract name for futures
                                        let displayName = '';
                                        
                                        if (contract.commodity.includes('Cotton Cash')) {
                                          displayName = 'CTY00 (Cash)';
                                        } else {
                                          // Extract contract info from commodity name
                                          const match = contract.commodity.match(/Cotton \(Cotton ([A-Z])(\d{2})\)/);
                                          if (match) {
                                            const monthCode = match[1];
                                            const year = match[2];
                                            
                                            // Convert month code to month name
                                            const monthNames = {
                                              'H': 'Mar',
                                              'K': 'May', 
                                              'N': 'Jul',
                                              'V': 'Oct',
                                              'Z': 'Dec'
                                            };
                                            
                                            const monthName = monthNames[monthCode] || monthCode;
                                            displayName = `CT${monthCode}${year} (${monthName} '${year})`;
                                          } else {
                                            displayName = contract.commodity;
                                          }
                                        }
                                        
                                        return (
                                          <div key={contractIndex} className="contract-row" style={{ 
                                            padding: '6px 0', 
                                            borderBottom: contractIndex < futuresContracts.length - 1 ? '1px solid #f0f0f0' : 'none',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center'
                                          }}>
                                            <div style={{ 
                                              fontSize: '14px', 
                                              fontWeight: '500',
                                              color: 'white',
                                              flex: '1'
                                            }}>
                                              {displayName}:
                                            </div>
                                            
                                            <div style={{ 
                                              fontSize: '14px',
                                              fontWeight: '600',
                                              color: 'white',
                                              marginLeft: '10px'
                                            }}>
                                              {contract.price} {contract.unit}
                                            </div>
                                            
                                            <div style={{ 
                                              marginLeft: '10px',
                                              minWidth: '50px',
                                              textAlign: 'right'
                                            }}>
                                              <span 
                                                className="change-value"
                                                style={{ 
                                                  color: getChangeColor(contract.change),
                                                  fontSize: '0.8rem',
                                                  padding: '0.25rem 0.5rem',
                                                  borderRadius: '12px'
                                                }}
                                              >
                                                <span className="change-icon" style={{ fontSize: '0.9rem' }}>{getChangeIcon(contract.change)}</span>
                                                {contract.change ? `${contract.change}${contract.change.toString().includes('%') ? '' : '%'}` : 'N/A'}
                                              </span>
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        ) : (
                          // Regular single commodity - styled like cotton
                          <div className="price-card expanded">
                            <div style={{ 
                              padding: '10px 0', 
                              borderBottom: '2px solid #ddd',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center'
                            }}>
                              <div style={{ 
                                fontSize: '16px', 
                                fontWeight: '600',
                                color: 'white',
                                flex: '1'
                              }}>
                                {(() => {
                                  // Format commodity name based on type
                                  if (item.commodity.includes('Wheat')) {
                                    return 'H2:';
                                  } else if (item.commodity.includes('Barley')) {
                                    return 'Feed:';
                                  } else if (item.commodity.includes('Beef')) {
                                    return 'Eastern Young Cattle Indicator:';
                                  } else {
                                    return `${item.commodity}:`;
                                  }
                                })()}
                              </div>
                              
                              <div style={{ 
                                fontSize: '16px',
                                fontWeight: '600',
                                color: 'white',
                                marginLeft: '10px'
                              }}>
                                {item.price} {item.unit}
                              </div>
                              
                              <div style={{ 
                                marginLeft: '10px',
                                minWidth: '60px',
                                textAlign: 'right'
                              }}>
                                <span 
                                  className="change-value"
                                  style={{ 
                                    color: getChangeColor(item.change),
                                    fontSize: '0.8rem',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: '12px'
                                  }}
                                >
                                  <span className="change-icon" style={{ fontSize: '0.9rem' }}>{getChangeIcon(item.change)}</span>
                                  {item.change ? `${item.change}${item.change.toString().includes('%') ? '' : '%'}` : 'N/A'}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}
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
