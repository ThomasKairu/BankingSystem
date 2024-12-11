import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
} from '@mui/material';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import RemoveCircleIcon from '@mui/icons-material/RemoveCircle';
import { Portfolio, TransactionType } from '../../types/investment';
import { formatCurrency } from '../../utils/formatters';

interface RecentTransactionsProps {
  portfolios: Portfolio[];
}

const RecentTransactions: React.FC<RecentTransactionsProps> = ({ portfolios }) => {
  // Get all transactions from all portfolios
  const allTransactions = portfolios.flatMap((portfolio) =>
    portfolio.transactions.map((transaction) => ({
      ...transaction,
      portfolioName: portfolio.name,
    }))
  );

  // Sort by date descending
  allTransactions.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  // Take only the 10 most recent transactions
  const recentTransactions = allTransactions.slice(0, 10);

  const getTransactionIcon = (type: TransactionType) => {
    switch (type) {
      case TransactionType.BUY:
        return <AddCircleIcon color="success" />;
      case TransactionType.SELL:
        return <RemoveCircleIcon color="error" />;
      default:
        return null;
    }
  };

  const getTransactionColor = (type: TransactionType) => {
    switch (type) {
      case TransactionType.BUY:
        return 'success';
      case TransactionType.SELL:
        return 'error';
      case TransactionType.DIVIDEND:
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Recent Transactions
      </Typography>

      <List>
        {recentTransactions.map((transaction, index) => (
          <React.Fragment key={transaction.id}>
            <ListItem>
              <ListItemIcon>{getTransactionIcon(transaction.transaction_type)}</ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body1" sx={{ mr: 1 }}>
                      {transaction.symbol}
                    </Typography>
                    <Chip
                      label={transaction.transaction_type}
                      size="small"
                      color={getTransactionColor(transaction.transaction_type)}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <>
                    <Typography variant="body2" color="textSecondary">
                      {transaction.portfolioName}
                    </Typography>
                    <Typography variant="body2">
                      {transaction.quantity} shares @ {formatCurrency(transaction.price)}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {new Date(transaction.date).toLocaleDateString()}
                    </Typography>
                  </>
                }
              />
              <Box sx={{ textAlign: 'right' }}>
                <Typography
                  variant="body2"
                  color={
                    transaction.transaction_type === TransactionType.BUY
                      ? 'error.main'
                      : 'success.main'
                  }
                >
                  {transaction.transaction_type === TransactionType.BUY ? '-' : '+'}
                  {formatCurrency(transaction.total_amount)}
                </Typography>
                {transaction.fees > 0 && (
                  <Typography variant="caption" color="textSecondary">
                    Fees: {formatCurrency(transaction.fees)}
                  </Typography>
                )}
              </Box>
            </ListItem>
            {index < recentTransactions.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

export default RecentTransactions;
