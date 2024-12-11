import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import { CloudDownload, EcoOutlined } from '@mui/icons-material';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export const SustainabilityReport: React.FC = () => {
  const { data: metrics, isLoading } = useQuery('sustainability-metrics', () =>
    api.get('/compliance/sustainability-metrics')
  );

  const { data: investments } = useQuery('green-investments', () =>
    api.get('/compliance/green-investments')
  );

  const { data: impact } = useQuery('environmental-impact', () =>
    api.get('/compliance/environmental-impact')
  );

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Sustainability Report</Typography>
        <Button
          variant="contained"
          startIcon={<CloudDownload />}
          color="primary"
        >
          Export Report
        </Button>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <EcoOutlined sx={{ fontSize: 40, color: 'success.main' }} />
            <Typography variant="h4" mt={1}>
              {metrics?.sustainabilityScore}%
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Overall Sustainability Score
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4">
              {metrics?.carbonFootprint.toFixed(2)}
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Carbon Footprint (tons CO2e)
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4">
              ${metrics?.greenInvestments.toLocaleString()}
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Green Investments
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Environmental Impact */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Environmental Impact Trends
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={impact?.trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="impact" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Green Investment Distribution */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Green Investment Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={investments?.distribution}
                  dataKey="value"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {investments?.distribution.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sustainability Initiatives
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Initiative</TableCell>
                    <TableCell>Impact</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {metrics?.initiatives.map((initiative: any) => (
                    <TableRow key={initiative.id}>
                      <TableCell>{initiative.name}</TableCell>
                      <TableCell>{initiative.impact}</TableCell>
                      <TableCell>
                        <Box
                          sx={{
                            backgroundColor:
                              initiative.status === 'Completed'
                                ? 'success.light'
                                : 'warning.light',
                            color:
                              initiative.status === 'Completed'
                                ? 'success.dark'
                                : 'warning.dark',
                            px: 1,
                            py: 0.5,
                            borderRadius: 1,
                            display: 'inline-block',
                          }}
                        >
                          {initiative.status}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
