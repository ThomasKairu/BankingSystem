import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  AccountBalance as AccountIcon,
  Payment as PaymentIcon,
  TrendingUp as InvestmentIcon,
  Notifications as NotificationIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import * as apiService from '../../services/api';
import AccountCard from './AccountCard';
import TransactionList from './TransactionList';
import QuickActions from './QuickActions';
import NotificationCenter from './NotificationCenter';
import SpendingChart from './SpendingChart';

const UserDashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const { data: accountData, isLoading: isLoadingAccount, error: accountError } = useQuery(
    'accountDetails',
    apiService.fetchAccountDetails
  );

  const { data: transactionsData, isLoading: isLoadingTransactions } = useQuery(
    'transactions',
    apiService.fetchTransactions
  );

  const { data: notificationsData, isLoading: isLoadingNotifications } = useQuery(
    'notifications',
    apiService.fetchNotifications
  );

  const { data: spendingData, isLoading: isLoadingSpending } = useQuery(
    'spending',
    apiService.fetchSpendingData
  );

  if (isLoadingAccount || isLoadingTransactions || isLoadingNotifications || isLoadingSpending) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (accountError) {
    return (
      <Alert severity="error">
        Error loading dashboard data. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Account Overview */}
        <Grid item xs={12} md={6}>
          <AccountCard accountData={accountData} />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <QuickActions />
        </Grid>

        {/* Transaction List */}
        <Grid item xs={12} md={8}>
          <TransactionList transactions={transactionsData} />
        </Grid>

        {/* Notifications */}
        <Grid item xs={12} md={4}>
          <NotificationCenter notifications={notificationsData} />
        </Grid>

        {/* Spending Chart */}
        <Grid item xs={12}>
          <SpendingChart data={spendingData} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserDashboard;
