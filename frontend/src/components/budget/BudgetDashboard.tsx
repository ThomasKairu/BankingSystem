import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, Paper, useTheme } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import BudgetList from './BudgetList';
import BudgetSummary from './BudgetSummary';
import BudgetAlerts from './BudgetAlerts';
import CategorySpending from './CategorySpending';
import { fetchBudgets, fetchBudgetAlerts } from '../../services/budgetService';

const BudgetDashboard: React.FC = () => {
  const theme = useTheme();

  const { data: budgets, isLoading: budgetsLoading } = useQuery(
    ['budgets'],
    fetchBudgets
  );

  const { data: alerts, isLoading: alertsLoading } = useQuery(
    ['budgetAlerts'],
    fetchBudgetAlerts
  );

  if (budgetsLoading || alertsLoading) {
    return <div>Loading...</div>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Budget Alerts */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <BudgetAlerts alerts={alerts || []} />
          </Paper>
        </Grid>

        {/* Budget Summary */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <BudgetSummary budgets={budgets || []} />
          </Paper>
        </Grid>

        {/* Category Spending */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <CategorySpending budgets={budgets || []} />
          </Paper>
        </Grid>

        {/* Budget List */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <BudgetList budgets={budgets || []} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BudgetDashboard;
