// src/components/NavBar.js
import React from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import { Link, useHistory } from 'react-router-dom';

function NavBar() {
  const history = useHistory();

  const handleLogout = () => {
    localStorage.removeItem('token');
    history.push('/login');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" style={{ flexGrow: 1 }}>
          Meraki Health Check
        </Typography>
        <Button color="inherit" component={Link} to="/">Dashboard</Button>
        <Button color="inherit" component={Link} to="/manage-thresholds">Manage Thresholds</Button>
        <Button color="inherit" onClick={handleLogout}>Logout</Button>
      </Toolbar>
    </AppBar>
  );
}

export default NavBar;