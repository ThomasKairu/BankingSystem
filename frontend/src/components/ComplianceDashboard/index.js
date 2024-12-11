import React from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';

const ComplianceDashboard = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Compliance Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">KYC Status</Typography>
            <Typography color="success.main">Verified</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Recent Compliance Alerts</Typography>
            <Typography>No alerts to display</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComplianceDashboard;
