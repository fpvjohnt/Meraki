import React, { useEffect, useState } from 'react';
import CheckResult from './CheckResults'; // Updated import statement

const WirelessChecks = () => {
  const [wirelessData, setWirelessData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWirelessData = async () => {
      try {
        const response = await fetch('/api/health-checks/wireless');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setWirelessData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchWirelessData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Wireless Checks</h2>
      {wirelessData.map((check, index) => (
        <CheckResult key={index} check={check} />
      ))}
    </div>
  );
};

export default WirelessChecks;