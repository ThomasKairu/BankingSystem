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
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { useQuery, useMutation } from 'react-query';
import { api } from '../../services/api';
import { Block, CheckCircle, Warning } from '@mui/icons-material';

export const EthicalCompliance: React.FC = () => {
  const [selectedTransaction, setSelectedTransaction] = React.useState<any>(null);

  // Fetch ethical compliance data
  const { data: ethicalData, isLoading } = useQuery('ethical-compliance', () =>
    api.get('/compliance/ethical-overview')
  );

  // Fetch restricted industries
  const { data: restrictedIndustries } = useQuery('restricted-industries', () =>
    api.get('/compliance/restricted-industries')
  );

  // Fetch recent ethical reviews
  const { data: recentReviews } = useQuery('ethical-reviews', () =>
    api.get('/compliance/ethical-reviews')
  );

  // Mutation for updating ethical compliance status
  const updateCompliance = useMutation(
    (data: any) =>
      api.post(`/compliance/ethical-review/${data.id}`, data),
    {
      onSuccess: () => {
        setSelectedTransaction(null);
      },
    }
  );

  const handleReviewSubmit = (decision: 'approve' | 'reject') => {
    if (selectedTransaction) {
      updateCompliance.mutate({
        id: selectedTransaction.id,
        decision,
        notes: selectedTransaction.notes,
      });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Ethical Compliance
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <CheckCircle sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Compliance Rate
              </Typography>
              <Typography variant="h4">
                {ethicalData?.complianceRate}%
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Warning sx={{ fontSize: 40, mr: 2, color: 'warning.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Pending Reviews
              </Typography>
              <Typography variant="h4">
                {ethicalData?.pendingReviews}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Block sx={{ fontSize: 40, mr: 2, color: 'error.main' }} />
            <Box>
              <Typography variant="subtitle2" color="textSecondary">
                Restricted Transactions
              </Typography>
              <Typography variant="h4">
                {ethicalData?.restrictedTransactions}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Restricted Industries */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Restricted Industries
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Industry</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Restrictions</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {restrictedIndustries?.map((industry: any) => (
                <TableRow key={industry.id}>
                  <TableCell>{industry.name}</TableCell>
                  <TableCell>
                    <Box
                      sx={{
                        backgroundColor:
                          industry.riskLevel === 'High'
                            ? 'error.light'
                            : industry.riskLevel === 'Medium'
                            ? 'warning.light'
                            : 'success.light',
                        color:
                          industry.riskLevel === 'High'
                            ? 'error.dark'
                            : industry.riskLevel === 'Medium'
                            ? 'warning.dark'
                            : 'success.dark',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        display: 'inline-block',
                      }}
                    >
                      {industry.riskLevel}
                    </Box>
                  </TableCell>
                  <TableCell>{industry.restrictions}</TableCell>
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

      {/* Recent Reviews */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Ethical Reviews
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Transaction ID</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentReviews?.map((review: any) => (
                <TableRow key={review.id}>
                  <TableCell>{review.transactionId}</TableCell>
                  <TableCell>{review.type}</TableCell>
                  <TableCell>${review.amount.toLocaleString()}</TableCell>
                  <TableCell>
                    <Box
                      sx={{
                        backgroundColor:
                          review.status === 'Approved'
                            ? 'success.light'
                            : review.status === 'Rejected'
                            ? 'error.light'
                            : 'warning.light',
                        color:
                          review.status === 'Approved'
                            ? 'success.dark'
                            : review.status === 'Rejected'
                            ? 'error.dark'
                            : 'warning.dark',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        display: 'inline-block',
                      }}
                    >
                      {review.status}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => setSelectedTransaction(review)}
                    >
                      Review
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Review Dialog */}
      <Dialog
        open={!!selectedTransaction}
        onClose={() => setSelectedTransaction(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Review Transaction</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Transaction Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Transaction ID
                </Typography>
                <Typography variant="body1">
                  {selectedTransaction?.transactionId}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">
                  Amount
                </Typography>
                <Typography variant="body1">
                  ${selectedTransaction?.amount.toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
            <TextField
              fullWidth
              multiline
              rows={4}
              margin="normal"
              label="Review Notes"
              value={selectedTransaction?.notes || ''}
              onChange={(e) =>
                setSelectedTransaction({
                  ...selectedTransaction,
                  notes: e.target.value,
                })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTransaction(null)}>Cancel</Button>
          <Button
            onClick={() => handleReviewSubmit('reject')}
            color="error"
            variant="contained"
          >
            Reject
          </Button>
          <Button
            onClick={() => handleReviewSubmit('approve')}
            color="success"
            variant="contained"
          >
            Approve
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
