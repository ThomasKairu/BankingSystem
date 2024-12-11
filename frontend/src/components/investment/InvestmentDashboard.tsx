import React from 'react';
import { Box, Grid, Typography, Paper, Button } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import PortfolioList from './PortfolioList';
import PortfolioSummary from './PortfolioSummary';
import PerformanceChart from './PerformanceChart';
import AssetAllocation from './AssetAllocation';
import RecentTransactions from './RecentTransactions';
import { fetchPortfolios } from '../../services/investmentService';

const InvestmentDashboard: React.FC = () => {
  const { data: portfolios, isLoading } = useQuery(['portfolios'], fetchPortfolios);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Portfolio Summary */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h5">Investment Portfolio</Typography>
              <Button variant="contained" color="primary">
                Create Portfolio
              </Button>
            </Box>
            <PortfolioSummary portfolios={portfolios || []} />
          </Paper>
        </Grid>

        {/* Performance Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <PerformanceChart portfolios={portfolios || []} />
          </Paper>
        </Grid>

        {/* Asset Allocation */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <AssetAllocation portfolios={portfolios || []} />
          </Paper>
        </Grid>

        {/* Portfolio List */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <PortfolioList portfolios={portfolios || []} />
          </Paper>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <RecentTransactions portfolios={portfolios || []} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default InvestmentDashboard;
