import React from 'react';
import { Card, CardContent, Typography, Box, Chip, LinearProgress } from '@mui/material';
import { Savings, TrendingUp } from '@mui/icons-material';

interface Opportunity {
  category: string;
  potentialSavings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  impact: number;
  description: string;
  steps: string[];
}

interface SavingsOpportunitiesProps {
  opportunities: {
    totalPotentialSavings: number;
    items: Opportunity[];
  };
}

const SavingsOpportunities: React.FC<SavingsOpportunitiesProps> = ({ opportunities }) => {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Savings Opportunities
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Savings color="primary" sx={{ mr: 1 }} />
          <Typography variant="h5" color="primary">
            ${opportunities.totalPotentialSavings.toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            potential annual savings
          </Typography>
        </Box>

        {opportunities.items.map((opportunity, index) => (
          <Box key={index} sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle1">
                {opportunity.category}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  label={`$${opportunity.potentialSavings.toLocaleString()}`}
                  size="small"
                  icon={<TrendingUp />}
                  color="primary"
                />
                <Chip
                  label={opportunity.difficulty}
                  size="small"
                  color={getDifficultyColor(opportunity.difficulty)}
                />
              </Box>
            </Box>

            <Typography variant="body2" color="text.secondary" paragraph>
              {opportunity.description}
            </Typography>

            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">Impact</Typography>
                <Typography variant="body2" color="text.secondary">
                  {opportunity.impact}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={opportunity.impact}
                sx={{
                  height: 6,
                  borderRadius: 3,
                }}
              />
            </Box>

            <Typography variant="subtitle2" gutterBottom>
              Steps to Implement:
            </Typography>
            {opportunity.steps.map((step, stepIndex) => (
              <Typography key={stepIndex} variant="body2" color="text.secondary" sx={{ ml: 2 }}>
                • {step}
              </Typography>
            ))}
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

export default SavingsOpportunities;
