import { api } from './api';
import { Budget, BudgetCreate, BudgetUpdate, BudgetExpenseCreate, BudgetAlert } from '../types/budget';

export const fetchBudgets = async (): Promise<Budget[]> => {
  const response = await api.get('/budgets');
  return response.data;
};

export const fetchBudget = async (id: number): Promise<Budget> => {
  const response = await api.get(`/budgets/${id}`);
  return response.data;
};

export const createBudget = async (budget: BudgetCreate): Promise<Budget> => {
  const response = await api.post('/budgets', budget);
  return response.data;
};

export const updateBudget = async (
  id: number,
  budget: BudgetUpdate
): Promise<Budget> => {
  const response = await api.put(`/budgets/${id}`, budget);
  return response.data;
};

export const deleteBudget = async (id: number): Promise<void> => {
  await api.delete(`/budgets/${id}`);
};

export const addBudgetExpense = async (
  budgetId: number,
  expense: BudgetExpenseCreate
): Promise<void> => {
  await api.post(`/budgets/${budgetId}/expenses`, expense);
};

export const fetchBudgetSummary = async (budgetId: number) => {
  const response = await api.get(`/budgets/${budgetId}/summary`);
  return response.data;
};

export const fetchCategorySpending = async (
  startDate: string,
  endDate: string
) => {
  const response = await api.get('/budgets/spending/categories', {
    params: { start_date: startDate, end_date: endDate },
  });
  return response.data;
};

export const fetchBudgetAlerts = async (): Promise<BudgetAlert[]> => {
  const response = await api.get('/budgets/alerts');
  return response.data;
};

export const dismissBudgetAlert = async (alertId: number): Promise<void> => {
  await api.post(`/budgets/alerts/${alertId}/dismiss`);
};
