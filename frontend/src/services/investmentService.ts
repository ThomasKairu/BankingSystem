import { api } from './api';
import {
  Portfolio,
  PortfolioCreate,
  PortfolioUpdate,
  Transaction,
  TransactionCreate,
  Alert,
  AlertCreate,
  PortfolioSummary,
  PerformanceHistory,
} from '../types/investment';

export const fetchPortfolios = async (): Promise<Portfolio[]> => {
  const response = await api.get('/investments/portfolios');
  return response.data;
};

export const fetchPortfolio = async (id: number): Promise<Portfolio> => {
  const response = await api.get(`/investments/portfolios/${id}`);
  return response.data;
};

export const createPortfolio = async (
  portfolio: PortfolioCreate
): Promise<Portfolio> => {
  const response = await api.post('/investments/portfolios', portfolio);
  return response.data;
};

export const updatePortfolio = async (
  id: number,
  portfolio: PortfolioUpdate
): Promise<Portfolio> => {
  const response = await api.put(`/investments/portfolios/${id}`, portfolio);
  return response.data;
};

export const addTransaction = async (
  portfolioId: number,
  transaction: TransactionCreate
): Promise<Transaction> => {
  const response = await api.post(
    `/investments/portfolios/${portfolioId}/transactions`,
    transaction
  );
  return response.data;
};

export const updatePrices = async (portfolioId: number): Promise<void> => {
  await api.post(`/investments/portfolios/${portfolioId}/update-prices`);
};

export const fetchPortfolioSummary = async (
  portfolioId: number
): Promise<PortfolioSummary> => {
  const response = await api.get(`/investments/portfolios/${portfolioId}/summary`);
  return response.data;
};

export const fetchPortfolioPerformance = async (
  portfolioId: number,
  timeframe: string
): Promise<PerformanceHistory[]> => {
  const response = await api.get(
    `/investments/portfolios/${portfolioId}/performance`,
    {
      params: { timeframe },
    }
  );
  return response.data;
};

export const createAlert = async (
  portfolioId: number,
  alert: AlertCreate
): Promise<Alert> => {
  const response = await api.post(
    `/investments/portfolios/${portfolioId}/alerts`,
    alert
  );
  return response.data;
};
