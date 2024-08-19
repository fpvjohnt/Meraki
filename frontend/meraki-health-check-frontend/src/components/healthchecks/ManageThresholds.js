// src/components/ManageThresholds.js
import React, { useState, useEffect } from 'react';
import { Container, Typography, TextField, Button, Grid, Paper } from '@mui/material';
import axios from 'axios';

function ManageThresholds() {
  const [thresholds, setThresholds] = useState({});

  useEffect(() => {
    fetchThresholds();
  }, []);

  const fetchThresholds = async () => {
    try {
      const response = await axios.get('/api/thresholds', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setThresholds(response.data);
    } catch (error) {
      console.error('Error fetching thresholds:', error);
    }
  };

  const handleThresholdChange = (name, value) => {
    setThresholds(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/thresholds', thresholds, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      alert('Thresholds updated successfully');
    } catch (error) {
      console.error('Error updating thresholds:', error);
      alert('Error updating thresholds');
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>Manage Thresholds</Typography>
      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {Object.entries(thresholds).map(([name, value]) => (
              <Grid item xs={12} sm={6} key={name}>
                <TextField
                  fullWidth
                  label={name}
                  type="number"
                  value={value}
                  onChange={(e) => handleThresholdChange(name, e.target.value)}
                />
              </Grid>
            ))}
          </Grid>
          <Button type="submit" variant="contained" color="primary" sx={{ mt: 3 }}>
            Update Thresholds
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export default ManageThresholds;