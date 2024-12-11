import React from 'react';
import {
  Box,
  Typography,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  useTheme,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface SpendingData {
  category: string;
  amount: number;
  percentage: number;
}

interface SpendingChartProps {
  data: {
    daily: SpendingData[];
    weekly: SpendingData[];
    monthly: SpendingData[];
  };
}

export const SpendingChart: React.FC<SpendingChartProps> = ({ data }) => {
  const theme = useTheme();
  const [timeframe, setTimeframe] = React.useState<'daily' | 'weekly' | 'monthly'>(
    'monthly'
  );

  const handleTimeframeChange = (event: SelectChangeEvent) => {
    setTimeframe(event.target.value as 'daily' | 'weekly' | 'monthly');
  };

  const COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.error.main,
    theme.palette.warning.main,
    theme.palette.info.main,
    theme.palette.success.main,
  ];

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: any[];
  }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          sx={{
            backgroundColor: 'background.paper',
            p: 1.5,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
          }}
        >
          <Typography variant="subtitle2">{data.category}</Typography>
          <Typography variant="body2" color="textSecondary">
            Amount: {formatCurrency(data.amount)}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Percentage: {data.percentage.toFixed(1)}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Typography variant="subtitle1">Spending by Category</Typography>
        <FormControl size="small">
          <Select value={timeframe} onChange={handleTimeframeChange}>
            <MenuItem value="daily">Daily</MenuItem>
            <MenuItem value="weekly">Weekly</MenuItem>
            <MenuItem value="monthly">Monthly</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Box height={300}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data[timeframe]}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="amount"
            >
              {data[timeframe].map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>

      <Box mt={2}>
        {data[timeframe].map((item, index) => (
          <Box
            key={item.category}
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={1}
          >
            <Box display="flex" alignItems="center" gap={1}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: COLORS[index % COLORS.length],
                }}
              />
              <Typography variant="body2">{item.category}</Typography>
            </Box>
            <Typography variant="body2" color="textSecondary">
              {formatCurrency(item.amount)}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};
