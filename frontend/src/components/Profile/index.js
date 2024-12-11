import React from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';

const Profile = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Profile
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Personal Information</Typography>
            <Typography>Name: John Doe</Typography>
            <Typography>Email: john@example.com</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Account Settings</Typography>
            <Typography>Account Type: Personal</Typography>
            <Typography>Member Since: January 1, 2024</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;
