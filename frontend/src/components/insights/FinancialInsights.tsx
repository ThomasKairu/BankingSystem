import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Collapse,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import { InsightCard } from './InsightCard';
import { SavingsRecommendations } from './SavingsRecommendations';
import { SpendingAnalysis } from './SpendingAnalysis';

export const FinancialInsights: React.FC = () => {
  const theme = useTheme();
  const [expandedInsight, setExpandedInsight] = React.useState<string | null>(null);

  const { data: summary, isLoading, error } = useQuery(
    'financial-summary',
    () => api.get('/insights/summary')
  );

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      default:
        return theme.palette.info.main;
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'spending_trend':
        return summary?.insights.find(i => i.type === type)?.trend_percentage > 0 
          ? <TrendingUpIcon color="error" />
          : <TrendingDownIcon color="success" />;
      case 'unusual_spending':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading insights</Alert>;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Financial Insights
      </Typography>

      {/* Overview Section */}
      <Paper sx={{ p: 3, mb: 3, background: theme.palette.background.default }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Spending Overview
            </Typography>
            <Typography color="textSecondary">
              {summary?.spending_overview}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Savings Overview
            </Typography>
            <Typography color="textSecondary">
              {summary?.savings_overview}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Key Insights */}
      <Typography variant="h6" gutterBottom>
        Key Insights
      </Typography>
      <Grid container spacing={3} mb={3}>
        {summary?.insights
          .filter(insight => insight.priority === 'high')
          .map((insight, index) => (
            <Grid item xs={12} md={4} key={index}>
              <InsightCard
                insight={insight}
                expanded={expandedInsight === `${insight.type}-${index}`}
                onExpand={() =>
                  setExpandedInsight(
                    expandedInsight === `${insight.type}-${index}`
                      ? null
                      : `${insight.type}-${index}`
                  )
                }
              />
            </Grid>
          ))}
      </Grid>

      {/* Detailed Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <SpendingAnalysis
            insights={summary?.insights.filter(i => i.category === 'spending')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <SavingsRecommendations
            recommendations={summary?.insights.filter(i => i.category === 'savings')}
          />
        </Grid>
      </Grid>

      {/* All Insights */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        All Insights
      </Typography>
      <Grid container spacing={2}>
        {summary?.insights.map((insight, index) => (
          <Grid item xs={12} key={index}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                '&:hover': {
                  boxShadow: theme.shadows[4],
                },
              }}
            >
              <Box display="flex" alignItems="center" gap={2}>
                {getInsightIcon(insight.type)}
                <Box flex={1}>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <Typography variant="subtitle1">
                      {insight.message}
                    </Typography>
                    <Chip
                      label={insight.priority}
                      size="small"
                      sx={{
                        backgroundColor: getPriorityColor(insight.priority),
                        color: 'white',
                      }}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Category: {insight.category}
                  </Typography>
                </Box>
                <IconButton
                  onClick={() =>
                    setExpandedInsight(
                      expandedInsight === `${insight.type}-${index}`
                        ? null
                        : `${insight.type}-${index}`
                    )
                  }
                  sx={{
                    transform: expandedInsight === `${insight.type}-${index}`
                      ? 'rotate(180deg)'
                      : 'rotate(0deg)',
                    transition: 'transform 0.3s',
                  }}
                >
                  <ExpandMoreIcon />
                </IconButton>
              </Box>
              <Collapse
                in={expandedInsight === `${insight.type}-${index}`}
                timeout="auto"
                unmountOnExit
              >
                <Box mt={2}>
                  {insight.type === 'spending_trend' && (
                    <Typography>
                      Change: {insight.trend_percentage.toFixed(1)}%
                    </Typography>
                  )}
                  {insight.type === 'unusual_spending' && (
                    <Typography>
                      Unusual transactions: {insight.transactions.length}
                    </Typography>
                  )}
                  {/* Add more type-specific details here */}
                </Box>
              </Collapse>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
