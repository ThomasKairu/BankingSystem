import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Grid } from '@mui/material';
import { Warning, Security, Timeline } from '@mui/icons-material';

interface RiskFactor {
  category: string;
  level: 'low' | 'medium' | 'high';
  description: string;
  mitigation: string;
}

interface RiskAnalysisProps {
  analysis: {
    overallRisk: 'low' | 'medium' | 'high';
    summary: string;
    factors: RiskFactor[];
    trends: {
      period: string;
      riskScore: number;
    }[];
  };
}

const RiskAnalysis: React.FC<RiskAnalysisProps> = ({ analysis }) => {
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
          Risk Analysis
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Security sx={{ mr: 1 }} />
          <Typography variant="subtitle1">
            Overall Risk Level:
          </Typography>
          <Chip
            label={analysis.overallRisk.toUpperCase()}
            color={getRiskColor(analysis.overallRisk)}
            size="small"
            sx={{ ml: 1 }}
          />
        </Box>

        <Typography variant="body1" color="text.secondary" paragraph>
          {analysis.summary}
        </Typography>

        <Typography variant="subtitle1" gutterBottom>
          Risk Factors
        </Typography>

        <Grid container spacing={2}>
          {analysis.factors.map((factor, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ 
                p: 2, 
                border: 1, 
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: factor.level === 'high' ? 'error.light' : 'background.paper'
              }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2">
                    {factor.category}
                  </Typography>
                  <Chip
                    label={factor.level}
                    size="small"
                    color={getRiskColor(factor.level)}
                    icon={<Warning />}
                  />
                </Box>
                <Typography variant="body2" paragraph>
                  {factor.description}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Mitigation:</strong> {factor.mitigation}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Timeline sx={{ mr: 1 }} />
            Risk Score Trend
          </Typography>
          {/* Add a line chart here for risk score trends */}
        </Box>
      </CardContent>
    </Card>
  );
};

export default RiskAnalysis;
