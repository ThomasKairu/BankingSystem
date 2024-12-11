import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const TransactionHistory = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Transaction History
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography>No transactions to display</Typography>
      </Paper>
    </Box>
  );
};

export default TransactionHistory;
