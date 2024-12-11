import { api } from './api';

export const advisorService = {
  getComprehensiveInsights: async () => {
    const response = await api.get('/advisor/insights');
    return response.data;
  },

  getSpendingAnalysis: async () => {
    const response = await api.get('/advisor/spending-analysis');
    return response.data;
  },

  getBudgetRecommendations: async () => {
    const response = await api.get('/advisor/budget-recommendations');
    return response.data;
  },

  getInvestmentRecommendations: async () => {
    const response = await api.get('/advisor/investment-recommendations');
    return response.data;
  },

  getSavingsOpportunities: async () => {
    const response = await api.get('/advisor/savings-opportunities');
    return response.data;
  },

  getRiskAnalysis: async () => {
    const response = await api.get('/advisor/risk-analysis');
    return response.data;
  },

  getFinancialGoals: async () => {
    const response = await api.get('/advisor/financial-goals');
    return response.data;
  },
};
