import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemIcon, ListItemText, Box, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, Warning } from '@mui/icons-material';

interface Recommendation {
  category: string;
  currentSpending: number;
  recommendedBudget: number;
  impact: string;
  priority: 'high' | 'medium' | 'low';
}

interface BudgetRecommendationsProps {
  recommendations: {
    overview: string;
    items: Recommendation[];
  };
}

const BudgetRecommendations: React.FC<BudgetRecommendationsProps> = ({ recommendations }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
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

  const getChangeIcon = (current: number, recommended: number) => {
    return current > recommended ? (
      <TrendingDown color="error" />
    ) : (
      <TrendingUp color="success" />
    );
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Budget Recommendations
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          {recommendations.overview}
        </Typography>

        <List>
          {recommendations.items.map((item, index) => (
            <ListItem key={index} alignItems="flex-start">
              <ListItemIcon>
                {getChangeIcon(item.currentSpending, item.recommendedBudget)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">
                      {item.category}
                    </Typography>
                    <Chip
                      label={item.priority}
                      size="small"
                      color={getPriorityColor(item.priority)}
                    />
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2" component="span">
                      Current: ${item.currentSpending.toLocaleString()} →{' '}
                      Recommended: ${item.recommendedBudget.toLocaleString()}
                    </Typography>
                    <br />
                    <Typography variant="body2" color="text.secondary">
                      Impact: {item.impact}
                    </Typography>
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default BudgetRecommendations;
