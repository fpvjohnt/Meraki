import React, { useEffect, useState } from 'react';
import CheckResults from './CheckResults';

const SwitchChecks = () => {
  const [switchData, setSwitchData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSwitchData = async () => {
      try {
        const response = await fetch('/api/health-checks/switches');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSwitchData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSwitchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Switch Checks</h2>
      {switchData.map((check, index) => (
        <CheckResults key={index} check={check} />
      ))}
    </div>
  );
};

export default SwitchChecks;