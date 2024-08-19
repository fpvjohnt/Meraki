// src/components/OrganizationDetails.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Container, Typography, Paper, Grid } from '@mui/material';

function OrganizationDetails() {
  const [orgDetails, setOrgDetails] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchOrgDetails = async () => {
      try {
        const response = await axios.get(`/api/organization/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        setOrgDetails(response.data);
      } catch (error) {
        console.error('Error fetching organization details:', error);
      }
    };

    fetchOrgDetails();
  }, [id]);

  if (!orgDetails) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        {orgDetails.name} Details
      </Typography>
      <Grid container spacing={3}>
        {Object.entries(orgDetails.health_checks).map(([checkName, checkResult]) => (
          <Grid item xs={12} md={6} key={checkName}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">{checkName}</Typography>
              <Typography color={checkResult.is_ok ? 'success.main' : 'error.main'}>
                Status: {checkResult.is_ok ? 'OK' : 'Issue Detected'}
              </Typography>
              {checkResult.details && (
                <Typography variant="body2">
                  Details: {JSON.stringify(checkResult.details)}
                </Typography>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default OrganizationDetails;