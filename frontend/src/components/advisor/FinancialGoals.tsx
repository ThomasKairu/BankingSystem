import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Chip, Grid } from '@mui/material';
import { Flag, CheckCircle, Schedule } from '@mui/icons-material';

interface Goal {
  name: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  progress: number;
  status: 'on_track' | 'at_risk' | 'behind';
  nextSteps: string[];
}

interface FinancialGoalsProps {
  goals: {
    summary: string;
    items: Goal[];
  };
}

const FinancialGoals: React.FC<FinancialGoalsProps> = ({ goals }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'success';
      case 'at_risk':
        return 'warning';
      case 'behind':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    return status.replace('_', ' ').toUpperCase();
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Flag sx={{ mr: 1 }} />
          Financial Goals
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          {goals.summary}
        </Typography>

        <Grid container spacing={3}>
          {goals.items.map((goal, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ 
                p: 2, 
                border: 1, 
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: 'background.paper'
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    {goal.name}
                  </Typography>
                  <Chip
                    label={getStatusLabel(goal.status)}
                    color={getStatusColor(goal.status)}
                    size="small"
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">
                      Progress: ${goal.currentAmount.toLocaleString()} of ${goal.targetAmount.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {goal.progress}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={goal.progress}
                    color={getStatusColor(goal.status) as "success" | "warning" | "error"}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                    }}
                  />
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Schedule sx={{ mr: 1, fontSize: 'small', color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    Target Date: {goal.deadline}
                  </Typography>
                </Box>

                <Typography variant="subtitle2" gutterBottom>
                  Next Steps:
                </Typography>
                {goal.nextSteps.map((step, stepIndex) => (
                  <Box key={stepIndex} sx={{ display: 'flex', alignItems: 'center', ml: 1, mb: 0.5 }}>
                    <CheckCircle sx={{ mr: 1, fontSize: 'small', color: 'success.main' }} />
                    <Typography variant="body2">
                      {step}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default FinancialGoals;
