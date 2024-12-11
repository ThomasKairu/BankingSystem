import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  loading?: boolean;
  error?: boolean;
}> = ({ title, value, loading, error }) => (
  <Paper
    sx={{
      p: 2,
      display: 'flex',
      flexDirection: 'column',
      height: 140,
    }}
  >
    <Typography component="h2" variant="h6" color="primary" gutterBottom>
      {title}
    </Typography>
    {loading ? (
      <Box display="flex" justifyContent="center" alignItems="center" flex={1}>
        <CircularProgress />
      </Box>
    ) : error ? (
      <Alert severity="error">Error loading data</Alert>
    ) : (
      <Typography component="p" variant="h4">
        {value}
      </Typography>
    )}
  </Paper>
);

export const AdminDashboard: React.FC = () => {
  const { data: systemStats, isLoading: loadingSystem } = useQuery(
    'systemStats',
    () => api.get('/admin/stats/system')
  );

  const { data: userStats, isLoading: loadingUsers } = useQuery(
    'userStats',
    () => api.get('/admin/stats/users')
  );

  const { data: transactionStats, isLoading: loadingTransactions } = useQuery(
    'transactionStats',
    () => api.get('/admin/stats/transactions')
  );

  const { data: securityStats, isLoading: loadingSecurity } = useQuery(
    'securityStats',
    () => api.get('/admin/stats/security')
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={3}>
        {/* System Stats */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Active Users"
            value={systemStats?.active_users ?? 0}
            loading={loadingSystem}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Requests/min"
            value={systemStats?.requests_per_minute?.toFixed(2) ?? 0}
            loading={loadingSystem}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Error Rate"
            value={`${(systemStats?.error_rate * 100)?.toFixed(2)}%` ?? '0%'}
            loading={loadingSystem}
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard
            title="Avg Response Time"
            value={`${systemStats?.average_response_time?.toFixed(2)}ms` ?? '0ms'}
            loading={loadingSystem}
          />
        </Grid>

        {/* User Stats */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 240,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              User Statistics
            </Typography>
            {loadingUsers ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                flex={1}
              >
                <CircularProgress />
              </Box>
            ) : (
              <ResponsiveContainer>
                <LineChart
                  data={[
                    {
                      name: 'Total Users',
                      value: userStats?.total_users ?? 0,
                    },
                    {
                      name: 'Active Users',
                      value: userStats?.active_users ?? 0,
                    },
                    {
                      name: 'Verified Users',
                      value: userStats?.verified_users ?? 0,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#8884d8"
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Transaction Stats */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 240,
            }}
          >
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Transaction Statistics
            </Typography>
            {loadingTransactions ? (
              <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                flex={1}
              >
                <CircularProgress />
              </Box>
            ) : (
              <ResponsiveContainer>
                <LineChart
                  data={[
                    {
                      name: 'Total',
                      value: transactionStats?.total_transactions ?? 0,
                    },
                    {
                      name: 'Successful',
                      value: transactionStats?.successful_transactions ?? 0,
                    },
                    {
                      name: 'Failed',
                      value: transactionStats?.failed_transactions ?? 0,
                    },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#82ca9d"
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Paper>
        </Grid>

        {/* Security Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography component="h2" variant="h6" color="primary" gutterBottom>
              Security Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={3}>
                <StatCard
                  title="Blocked IPs"
                  value={securityStats?.blocked_ips ?? 0}
                  loading={loadingSecurity}
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <StatCard
                  title="Rate Limited"
                  value={securityStats?.rate_limited_requests ?? 0}
                  loading={loadingSecurity}
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <StatCard
                  title="Suspicious Activities"
                  value={securityStats?.suspicious_activities ?? 0}
                  loading={loadingSecurity}
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <StatCard
                  title="Failed Logins"
                  value={securityStats?.failed_login_attempts ?? 0}
                  loading={loadingSecurity}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
