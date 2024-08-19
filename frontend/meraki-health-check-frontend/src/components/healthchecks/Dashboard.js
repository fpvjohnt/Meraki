import React, { useState, useEffect } from 'react';
import SwitchChecks from './SwitchChecks';
import WirelessChecks from './WirelessChecks';

const Dashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        console.log('Fetching health check data...');
        const response = await fetch('/api/health-check');
        console.log('Response status:', response.status);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Received data:', data);
        setHealthData(data);
      } catch (err) {
        console.error('Error fetching health check data:', err);
        setError('Failed to fetch health check data');
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();
  }, []);

  if (loading) {
    return <div>Loading health check data...</div>;
  }

  if (error) {
    return (
      <div className="error-alert">
        <h2>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>Meraki Network Health Dashboard</h1>
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Switch Checks</h2>
          <SwitchChecks data={healthData?.switchChecks} />
        </div>
        <div className="dashboard-card">
          <h2>Wireless Checks</h2>
          <WirelessChecks data={healthData?.wirelessChecks} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;