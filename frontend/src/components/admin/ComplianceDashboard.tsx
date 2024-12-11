import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import {
  Assessment,
  Security,
  Nature,
  Gavel,
  Warning,
} from '@mui/icons-material';

export const ComplianceDashboard: React.FC = () => {
  // Fetch compliance overview
  const { data: overview, isLoading: loadingOverview } = useQuery(
    'compliance-overview',
    () => api.get('/compliance/overview')
  );

  // Fetch recent compliance checks
  const { data: recentChecks } = useQuery('recent-checks', () =>
    api.get('/compliance/recent-checks')
  );

  // Fetch risk metrics
  const { data: riskMetrics } = useQuery('risk-metrics', () =>
    api.get('/compliance/risk-metrics')
  );

  const renderStatusChip = (status: string) => {
    const colors: { [key: string]: "success" | "error" | "warning" | "default" } = {
      passed: "success",
      failed: "error",
      pending: "warning",
      unknown: "default",
    };
    return <Chip label={status} color={colors[status.toLowerCase()]} size="small" />;
  };

  if (loadingOverview) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Compliance Dashboard
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Assessment sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                KYC Completion Rate
              </Typography>
              <Typography variant="h4">
                {overview?.kycCompletionRate}%
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Security sx={{ fontSize: 40, mr: 2, color: 'secondary.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                AML Alerts
              </Typography>
              <Typography variant="h4">{overview?.amlAlerts}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Nature sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Sustainability Score
              </Typography>
              <Typography variant="h4">
                {overview?.sustainabilityScore}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Gavel sx={{ fontSize: 40, mr: 2, color: 'error.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Regulatory Issues
              </Typography>
              <Typography variant="h4">
                {overview?.regulatoryIssues}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Risk Assessment */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Risk Assessment
        </Typography>
        <Grid container spacing={2}>
          {riskMetrics?.categories.map((category: any) => (
            <Grid item xs={12} md={4} key={category.name}>
              <Box>
                <Typography variant="subtitle2" color="textSecondary">
                  {category.name}
                </Typography>
                <Box display="flex" alignItems="center">
                  <Box
                    sx={{
                      width: '100%',
                      bgcolor: 'background.paper',
                      borderRadius: 1,
                      mr: 1,
                    }}
                  >
                    <Box
                      sx={{
                        width: `${category.score}%`,
                        height: 10,
                        bgcolor: category.score > 70 ? 'error.main' :
                                category.score > 40 ? 'warning.main' : 'success.main',
                        borderRadius: 1,
                      }}
                    />
                  </Box>
                  <Typography variant="body2">{category.score}%</Typography>
                </Box>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Recent Compliance Checks */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Compliance Checks
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Check Type</TableCell>
                <TableCell>Entity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentChecks?.map((check: any) => (
                <TableRow key={check.id}>
                  <TableCell>{check.type}</TableCell>
                  <TableCell>{check.entity}</TableCell>
                  <TableCell>{renderStatusChip(check.status)}</TableCell>
                  <TableCell>
                    {new Date(check.date).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Button size="small" variant="outlined">
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* High Risk Alerts */}
      {overview?.highRiskAlerts > 0 && (
        <Alert
          severity="error"
          sx={{ mt: 3 }}
          action={
            <Button color="inherit" size="small">
              View All
            </Button>
          }
        >
          {overview.highRiskAlerts} high-risk compliance alerts require immediate attention
        </Alert>
      )}
    </Box>
  );
};
