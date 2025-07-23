import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [prices, setPrices] = useState([]);

  useEffect(() => {
    axios.get('/api/prices')
      .then(res => {
        console.log("Data received:", res.data);
        setPrices(res.data);
      })
      .catch(err => {
        console.error("Failed to fetch prices:", err);
      });
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Commodity Prices</h1>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Commodity</th>
            <th>Price</th>
            <th>Change (%)</th>
            <th>Unit</th>
            <th>Accessed</th>
          </tr>
        </thead>
        <tbody>
          {prices.length === 0 ? (
            <tr><td colSpan="5">Loading or no data</td></tr>
          ) : (
            prices.map((item, index) => (
              <tr key={index}>
                <td>{item.commodity}</td>
                <td>{item.price}</td>
                <td>{item.change}</td>
                <td>{item.unit}</td>
                <td>{new Date(item.timestamp).toLocaleString()}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
