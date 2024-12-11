import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { LineChart } from '@mui/x-charts';
import { CategoryBreakdown } from './CategoryBreakdown';

interface SpendingData {
  monthlyTrends: {
    month: string;
    amount: number;
  }[];
  categoryBreakdown: {
    category: string;
    amount: number;
    percentage: number;
  }[];
  insights: string[];
}

interface SpendingAnalysisProps {
  data: SpendingData;
}

const SpendingAnalysis: React.FC<SpendingAnalysisProps> = ({ data }) => {
  const chartData = {
    xAxis: [{
      data: data.monthlyTrends.map(trend => trend.month),
      scaleType: 'band',
    }],
    series: [{
      data: data.monthlyTrends.map(trend => trend.amount),
      area: true,
    }],
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Spending Analysis
        </Typography>

        <Box sx={{ height: 300, mb: 4 }}>
          <LineChart
            xAxis={chartData.xAxis}
            series={chartData.series}
            height={300}
          />
        </Box>

        <CategoryBreakdown categories={data.categoryBreakdown} />

        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Key Insights
          </Typography>
          {data.insights.map((insight, index) => (
            <Typography key={index} variant="body2" color="text.secondary" paragraph>
              {insight}
            </Typography>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
};

export default SpendingAnalysis;
