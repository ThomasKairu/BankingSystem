import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { PieChart } from '@mui/x-charts/PieChart';
import { Portfolio, AssetType } from '../../types/investment';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface AssetAllocationProps {
  portfolios: Portfolio[];
}

const AssetAllocation: React.FC<AssetAllocationProps> = ({ portfolios }) => {
  const theme = useTheme();

  // Calculate total allocation by asset type
  const allocation = portfolios.reduce((acc, portfolio) => {
    portfolio.holdings.forEach((holding) => {
      if (!acc[holding.asset_type]) {
        acc[holding.asset_type] = 0;
      }
      acc[holding.asset_type] += holding.market_value;
    });
    return acc;
  }, {} as Record<AssetType, number>);

  const totalValue = Object.values(allocation).reduce((sum, value) => sum + value, 0);

  // Convert to percentage and format for pie chart
  const pieData = Object.entries(allocation).map(([type, value]) => ({
    id: type,
    value: value,
    label: type,
    percentage: (value / totalValue) * 100,
  }));

  // Sort by value descending
  pieData.sort((a, b) => b.value - a.value);

  const colors = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.error.main,
    theme.palette.warning.main,
    theme.palette.info.main,
    // Add more colors as needed
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Asset Allocation
      </Typography>

      <Box sx={{ height: 300, display: 'flex' }}>
        <PieChart
          series={[
            {
              data: pieData,
              highlightScope: { faded: 'global', highlighted: 'item' },
              faded: { innerRadius: 30, additionalRadius: -30 },
              valueFormatter: (value: number) => formatCurrency(value),
            },
          ]}
          height={300}
          colors={colors}
        />
      </Box>

      <Box sx={{ mt: 2 }}>
        {pieData.map((item, index) => (
          <Box
            key={item.id}
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 1,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: colors[index % colors.length],
                  mr: 1,
                }}
              />
              <Typography variant="body2">{item.label}</Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="body2">
                {formatCurrency(item.value)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                {formatPercentage(item.percentage)}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default AssetAllocation;
