import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { useQuery, useMutation } from 'react-query';
import { api } from '../../services/api';
import { Download as DownloadIcon } from '@mui/icons-material';

interface ReportFilters {
  startDate: Date;
  endDate: Date;
  reportType: string;
  userId?: string;
}

export const Reports: React.FC = () => {
  const [filters, setFilters] = React.useState<ReportFilters>({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    endDate: new Date(),
    reportType: 'transactions_summary',
  });

  const { data: report, isLoading } = useQuery(
    ['report', filters],
    () => {
      const params = new URLSearchParams({
        start_date: filters.startDate.toISOString(),
        end_date: filters.endDate.toISOString(),
        report_type: filters.reportType.split('_')[0],
        ...(filters.userId && { user_id: filters.userId }),
      });

      return api.get(`/reports/${filters.reportType.split('_')[0]}?${params}`);
    }
  );

  const { data: metrics } = useQuery(
    ['metrics', filters],
    () => {
      const params = new URLSearchParams({
        start_date: filters.startDate.toISOString(),
        end_date: filters.endDate.toISOString(),
        report_type: filters.reportType.split('_')[0],
      });

      return api.get(`/reports/metrics?${params}`);
    }
  );

  const exportReport = useMutation(
    () => {
      const params = new URLSearchParams({
        start_date: filters.startDate.toISOString(),
        end_date: filters.endDate.toISOString(),
        report_type: filters.reportType,
        ...(filters.userId && { user_id: filters.userId }),
      });

      return api.get(`/reports/export?${params}`, {
        responseType: 'blob',
      });
    },
    {
      onSuccess: (data) => {
        const url = window.URL.createObjectURL(new Blob([data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute(
          'download',
          `${filters.reportType}_${filters.startDate.toISOString().split('T')[0]}_${
            filters.endDate.toISOString().split('T')[0]
          }.csv`
        );
        document.body.appendChild(link);
        link.click();
        link.remove();
      },
    }
  );

  const renderChart = () => {
    if (!report) return null;

    if (filters.reportType.startsWith('transactions')) {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={Object.entries(report.type_distribution || {})}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="0" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="1" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      );
    }

    if (filters.reportType === 'user_activity') {
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={Object.entries(metrics?.daily_active_users || {})}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="0" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="1" stroke="#82ca9d" />
          </LineChart>
        </ResponsiveContainer>
      );
    }

    return null;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Report Type</InputLabel>
              <Select
                value={filters.reportType}
                onChange={(e) =>
                  setFilters({ ...filters, reportType: e.target.value as string })
                }
              >
                <MenuItem value="transactions_summary">
                  Transactions Summary
                </MenuItem>
                <MenuItem value="transactions_detailed">
                  Transactions Detailed
                </MenuItem>
                <MenuItem value="user_activity">User Activity</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <DatePicker
              label="Start Date"
              value={filters.startDate}
              onChange={(date) =>
                setFilters({ ...filters, startDate: date || new Date() })
              }
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <DatePicker
              label="End Date"
              value={filters.endDate}
              onChange={(date) =>
                setFilters({ ...filters, endDate: date || new Date() })
              }
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="User ID (Optional)"
              value={filters.userId || ''}
              onChange={(e) =>
                setFilters({ ...filters, userId: e.target.value })
              }
            />
          </Grid>
        </Grid>
      </Paper>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={3}>
          <CircularProgress />
        </Box>
      ) : report ? (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Report Results</Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportReport.mutate()}
                >
                  Export CSV
                </Button>
              </Box>
              {renderChart()}
            </Paper>
          </Grid>

          {filters.reportType === 'transactions_summary' && (
            <>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Total Transactions
                  </Typography>
                  <Typography variant="h4">
                    {report.total_transactions}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Success Rate
                  </Typography>
                  <Typography variant="h4">
                    {(report.success_rate * 100).toFixed(1)}%
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Total Amount
                  </Typography>
                  <Typography variant="h4">
                    ${report.total_amount.toFixed(2)}
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Average Amount
                  </Typography>
                  <Typography variant="h4">
                    ${report.average_amount.toFixed(2)}
                  </Typography>
                </Paper>
              </Grid>
            </>
          )}

          {filters.reportType === 'user_activity' && (
            <>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    New Users
                  </Typography>
                  <Typography variant="h4">{report.new_users}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Active Users
                  </Typography>
                  <Typography variant="h4">{report.active_users}</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Security Events
                  </Typography>
                  <Typography variant="h4">
                    {report.security_events.length}
                  </Typography>
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      ) : (
        <Alert severity="info">Select report parameters to generate a report</Alert>
      )}
    </Box>
  );
};
