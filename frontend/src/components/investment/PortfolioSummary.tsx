import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { Portfolio } from '../../types/investment';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface PortfolioSummaryProps {
  portfolios: Portfolio[];
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ portfolios }) => {
  const totalValue = portfolios.reduce((sum, portfolio) => {
    return (
      sum +
      portfolio.holdings.reduce((holdingSum, holding) => holdingSum + holding.market_value, 0)
    );
  }, 0);

  const totalGainLoss = portfolios.reduce((sum, portfolio) => {
    return (
      sum +
      portfolio.holdings.reduce((holdingSum, holding) => holdingSum + holding.gain_loss, 0)
    );
  }, 0);

  const gainLossPercentage = totalGainLoss / (totalValue - totalGainLoss);

  const bestPerforming = portfolios.reduce(
    (best, portfolio) => {
      const portfolioReturn = portfolio.holdings.reduce(
        (sum, holding) => sum + holding.gain_loss_percentage,
        0
      ) / portfolio.holdings.length;
      return portfolioReturn > best.return
        ? { name: portfolio.name, return: portfolioReturn }
        : best;
    },
    { name: '', return: -Infinity }
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Portfolio Value
            </Typography>
            <Typography variant="h4" component="div">
              {formatCurrency(totalValue)}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
              {totalGainLoss >= 0 ? (
                <TrendingUpIcon color="success" />
              ) : (
                <TrendingDownIcon color="error" />
              )}
              <Typography
                variant="body2"
                sx={{
                  color: totalGainLoss >= 0 ? 'success.main' : 'error.main',
                  ml: 1,
                }}
              >
                {formatPercentage(gainLossPercentage)} overall return
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Gain/Loss
            </Typography>
            <Typography
              variant="h4"
              component="div"
              sx={{ color: totalGainLoss >= 0 ? 'success.main' : 'error.main' }}
            >
              {formatCurrency(totalGainLoss)}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <LinearProgress
                variant="determinate"
                value={Math.min(Math.abs(gainLossPercentage * 100), 100)}
                color={totalGainLoss >= 0 ? 'success' : 'error'}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Number of Portfolios
            </Typography>
            <Typography variant="h4" component="div">
              {portfolios.length}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              {portfolios.reduce(
                (sum, portfolio) => sum + portfolio.holdings.length,
                0
              )}{' '}
              total holdings
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6} lg={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Best Performing Portfolio
            </Typography>
            <Typography variant="h6" component="div">
              {bestPerforming.name || 'N/A'}
            </Typography>
            {bestPerforming.return > -Infinity && (
              <Typography
                variant="body2"
                sx={{ color: 'success.main', mt: 1 }}
              >
                {formatPercentage(bestPerforming.return)} return
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default PortfolioSummary;
