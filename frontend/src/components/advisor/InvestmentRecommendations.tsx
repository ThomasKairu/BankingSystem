import React from 'react';
import { Card, CardContent, Typography, Grid, Box, Chip, Divider } from '@mui/material';
import { PieChart } from '@mui/x-charts';

interface Recommendation {
  assetClass: string;
  currentAllocation: number;
  recommendedAllocation: number;
  reasoning: string;
  risk: 'low' | 'medium' | 'high';
}

interface InvestmentRecommendationsProps {
  recommendations: {
    summary: string;
    riskProfile: string;
    expectedReturn: number;
    items: Recommendation[];
  };
}

const InvestmentRecommendations: React.FC<InvestmentRecommendationsProps> = ({ recommendations }) => {
  const currentData = recommendations.items.map(item => ({
    value: item.currentAllocation,
    label: item.assetClass,
  }));

  const recommendedData = recommendations.items.map(item => ({
    value: item.recommendedAllocation,
    label: item.assetClass,
  }));

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Investment Recommendations
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          {recommendations.summary}
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Risk Profile: {recommendations.riskProfile}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Expected Annual Return: {recommendations.expectedReturn}%
          </Typography>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" align="center" gutterBottom>
              Current Allocation
            </Typography>
            <PieChart
              series={[{ data: currentData }]}
              height={200}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" align="center" gutterBottom>
              Recommended Allocation
            </Typography>
            <PieChart
              series={[{ data: recommendedData }]}
              height={200}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Typography variant="subtitle1" gutterBottom>
          Detailed Recommendations
        </Typography>

        {recommendations.items.map((item, index) => (
          <Box key={index} sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2">
                {item.assetClass}
              </Typography>
              <Chip
                label={item.risk}
                size="small"
                color={getRiskColor(item.risk)}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Current: {item.currentAllocation}% → Recommended: {item.recommendedAllocation}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {item.reasoning}
            </Typography>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

export default InvestmentRecommendations;
