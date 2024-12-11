import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { Budget } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';

interface BudgetSummaryProps {
  budgets: Budget[];
}

const BudgetSummary: React.FC<BudgetSummaryProps> = ({ budgets }) => {
  const totalBudget = budgets.reduce((sum, budget) => sum + budget.amount, 0);
  const totalSpent = budgets.reduce((sum, budget) => sum + (budget.spent || 0), 0);
  const totalRemaining = totalBudget - totalSpent;
  const spentPercentage = (totalSpent / totalBudget) * 100;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Budget Summary
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Total Budget
              </Typography>
              <Typography variant="h4" color="primary">
                {formatCurrency(totalBudget)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Spent
              </Typography>
              <Typography
                variant="h5"
                color={spentPercentage > 90 ? 'error' : 'textPrimary'}
              >
                {formatCurrency(totalSpent)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Remaining
              </Typography>
              <Typography
                variant="h5"
                color={totalRemaining < 0 ? 'error' : 'success'}
              >
                {formatCurrency(totalRemaining)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">
                {spentPercentage.toFixed(1)}% spent
              </Typography>
              <Typography variant="body2">
                {(100 - spentPercentage).toFixed(1)}% remaining
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(spentPercentage, 100)}
              color={spentPercentage > 90 ? 'error' : 'primary'}
              sx={{ height: 10, borderRadius: 5 }}
            />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BudgetSummary;
