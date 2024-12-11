import React from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { TrendingUp, Insights, NotificationsActive } from '@mui/icons-material';

interface InsightsCardProps {
  insights: {
    summary: string;
    keyFindings: string[];
    alerts: string[];
  };
}

const InsightsCard: React.FC<InsightsCardProps> = ({ insights }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Financial Insights Overview
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          {insights.summary}
        </Typography>

        <Typography variant="subtitle1" gutterBottom>
          Key Findings
        </Typography>
        <List>
          {insights.keyFindings.map((finding, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <Insights color="primary" />
              </ListItemIcon>
              <ListItemText primary={finding} />
            </ListItem>
          ))}
        </List>

        <Typography variant="subtitle1" gutterBottom>
          Important Alerts
        </Typography>
        <List>
          {insights.alerts.map((alert, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <NotificationsActive color="error" />
              </ListItemIcon>
              <ListItemText primary={alert} />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default InsightsCard;
