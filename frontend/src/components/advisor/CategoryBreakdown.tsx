import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';

interface Category {
  category: string;
  amount: number;
  percentage: number;
}

interface CategoryBreakdownProps {
  categories: Category[];
}

export const CategoryBreakdown: React.FC<CategoryBreakdownProps> = ({ categories }) => {
  return (
    <Box>
      <Typography variant="subtitle1" gutterBottom>
        Spending by Category
      </Typography>
      {categories.map((category, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">
              {category.category}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ${category.amount.toLocaleString()} ({category.percentage}%)
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={category.percentage}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
              },
            }}
          />
        </Box>
      ))}
    </Box>
  );
};
