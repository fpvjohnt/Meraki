import React from 'react';

const CheckResults = ({ check }) => {
  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'green';
      case 'warning':
        return 'orange';
      case 'critical':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <div style={{
      border: '1px solid #ccc',
      borderRadius: '4px',
      padding: '16px',
      margin: '16px 0',
      backgroundColor: '#f9f9f9'
    }}>
      <h3 style={{ margin: '0 0 8px 0', color: getStatusColor(check.status) }}>
        Status: {check.status}
      </h3>
      <p style={{ fontSize: '14px', color: '#666', margin: '0 0 12px 0' }}>
        {new Date(check.timestamp).toLocaleString()}
      </p>
      <p style={{ margin: '0' }}>
        {check.message}
      </p>
    </div>
  );
};

export default CheckResults;