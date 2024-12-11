import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { useQuery } from 'react-query';
import { advisorService } from '../../services/advisorService';
import InsightsCard from './InsightsCard';
import SpendingAnalysis from './SpendingAnalysis';
import BudgetRecommendations from './BudgetRecommendations';
import InvestmentRecommendations from './InvestmentRecommendations';
import SavingsOpportunities from './SavingsOpportunities';
import RiskAnalysis from './RiskAnalysis';
import FinancialGoals from './FinancialGoals';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorAlert from '../common/ErrorAlert';

const AdvisorDashboard: React.FC = () => {
  const { data: insights, isLoading: insightsLoading, error: insightsError } = 
    useQuery('insights', advisorService.getComprehensiveInsights);

  const { data: spendingAnalysis, isLoading: spendingLoading, error: spendingError } = 
    useQuery('spending', advisorService.getSpendingAnalysis);

  const { data: budgetRecommendations, isLoading: budgetLoading, error: budgetError } = 
    useQuery('budget', advisorService.getBudgetRecommendations);

  const { data: investmentRecommendations, isLoading: investmentLoading, error: investmentError } = 
    useQuery('investment', advisorService.getInvestmentRecommendations);

  const { data: savingsOpportunities, isLoading: savingsLoading, error: savingsError } = 
    useQuery('savings', advisorService.getSavingsOpportunities);

  const { data: riskAnalysis, isLoading: riskLoading, error: riskError } = 
    useQuery('risk', advisorService.getRiskAnalysis);

  const { data: financialGoals, isLoading: goalsLoading, error: goalsError } = 
    useQuery('goals', advisorService.getFinancialGoals);

  if (insightsLoading || spendingLoading || budgetLoading || investmentLoading || 
      savingsLoading || riskLoading || goalsLoading) {
    return <LoadingSpinner />;
  }

  if (insightsError || spendingError || budgetError || investmentError || 
      savingsError || riskError || goalsError) {
    return <ErrorAlert message="Failed to load advisor data" />;
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Financial Advisor Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={3}>
            <InsightsCard insights={insights} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <SpendingAnalysis data={spendingAnalysis} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <BudgetRecommendations recommendations={budgetRecommendations} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <InvestmentRecommendations recommendations={investmentRecommendations} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <SavingsOpportunities opportunities={savingsOpportunities} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <RiskAnalysis analysis={riskAnalysis} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3}>
            <FinancialGoals goals={financialGoals} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvisorDashboard;
