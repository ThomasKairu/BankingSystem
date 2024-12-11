import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { PieChart } from '@mui/x-charts/PieChart';
import { Budget, BudgetCategory } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';

interface CategorySpendingProps {
  budgets: Budget[];
}

const CategorySpending: React.FC<CategorySpendingProps> = ({ budgets }) => {
  const categoryData = Object.values(BudgetCategory).map((category) => {
    const categoryBudgets = budgets.filter(
      (budget) => budget.category === category
    );
    const totalAmount = categoryBudgets.reduce(
      (sum, budget) => sum + budget.amount,
      0
    );
    const totalSpent = categoryBudgets.reduce(
      (sum, budget) => sum + (budget.spent || 0),
      0
    );
    return {
      category,
      amount: totalAmount,
      spent: totalSpent,
      percentage: totalAmount > 0 ? (totalSpent / totalAmount) * 100 : 0,
    };
  });

  const pieData = categoryData
    .filter((data) => data.spent > 0)
    .map((data) => ({
      id: data.category,
      value: data.spent,
      label: data.category,
    }));

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Category Spending
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <PieChart
              series={[
                {
                  data: pieData,
                  highlightScope: { faded: 'global', highlighted: 'item' },
                  faded: { innerRadius: 30, additionalRadius: -30 },
                },
              ]}
              height={300}
            />
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            {categoryData.map((data) => (
              <Card key={data.category} sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        mb: 1,
                      }}
                    >
                      <Typography variant="subtitle1">{data.category}</Typography>
                      <Typography variant="subtitle1">
                        {formatCurrency(data.spent)} /{' '}
                        {formatCurrency(data.amount)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(data.percentage, 100)}
                      color={data.percentage > 90 ? 'error' : 'primary'}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        mt: 0.5,
                      }}
                    >
                      <Typography variant="body2" color="textSecondary">
                        {data.percentage.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CategorySpending;
