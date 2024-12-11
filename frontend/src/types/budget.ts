export enum BudgetCategory {
  HOUSING = 'housing',
  TRANSPORTATION = 'transportation',
  FOOD = 'food',
  UTILITIES = 'utilities',
  HEALTHCARE = 'healthcare',
  ENTERTAINMENT = 'entertainment',
  SHOPPING = 'shopping',
  SAVINGS = 'savings',
  DEBT = 'debt',
  OTHER = 'other',
}

export enum BudgetPeriod {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

export enum AlertType {
  THRESHOLD = 'threshold',
  OVERSPENT = 'overspent',
  APPROACHING_LIMIT = 'approaching_limit',
  RECURRING_DUE = 'recurring_due',
}

export enum AlertStatus {
  ACTIVE = 'active',
  DISMISSED = 'dismissed',
  RESOLVED = 'resolved',
}

export interface Budget {
  id: number;
  userId: number;
  name: string;
  category: BudgetCategory;
  amount: number;
  period: BudgetPeriod;
  startDate: string;
  endDate?: string;
  spent?: number;
  remaining?: number;
  createdAt: string;
  updatedAt: string;
}

export interface BudgetCreate {
  name: string;
  category: BudgetCategory;
  amount: number;
  period: BudgetPeriod;
  startDate: string;
  endDate?: string;
}

export interface BudgetUpdate {
  name?: string;
  category?: BudgetCategory;
  amount?: number;
  period?: BudgetPeriod;
  endDate?: string;
}

export interface BudgetExpense {
  id: number;
  budgetId: number;
  transactionId?: number;
  amount: number;
  description?: string;
  date: string;
  createdAt: string;
}

export interface BudgetExpenseCreate {
  transactionId?: number;
  amount: number;
  description?: string;
  date?: string;
}

export interface BudgetAlert {
  id: number;
  budgetId: number;
  type: AlertType;
  status: AlertStatus;
  message: string;
  thresholdPercentage?: number;
  createdAt: string;
  updatedAt: string;
}

export interface CategorySpending {
  totalSpent: number;
  budgetAmount: number;
}
