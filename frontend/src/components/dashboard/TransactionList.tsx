import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Typography,
  Chip,
  Box,
  IconButton,
  Collapse,
  useTheme,
  CircularProgress,
} from '@mui/material';
import {
  ArrowUpward as SendIcon,
  ArrowDownward as ReceiveIcon,
  Payment as PaymentIcon,
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { TransactionDetails } from './TransactionDetails';

interface Transaction {
  id: string;
  type: string;
  amount: number;
  currency: string;
  status: string;
  description: string;
  created_at: string;
  metadata?: Record<string, any>;
  source_account?: string;
  destination_account?: string;
}

interface TransactionListProps {
  transactions: Transaction[];
  loading?: boolean;
}

export const TransactionList: React.FC<TransactionListProps> = ({
  transactions,
  loading,
}) => {
  const theme = useTheme();
  const [expandedId, setExpandedId] = React.useState<string | null>(null);

  const getTransactionIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'send':
        return <SendIcon color="error" />;
      case 'receive':
        return <ReceiveIcon color="success" />;
      default:
        return <PaymentIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return theme.palette.success.main;
      case 'pending':
        return theme.palette.warning.main;
      case 'failed':
        return theme.palette.error.main;
      default:
        return theme.palette.info.main;
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!transactions.length) {
    return (
      <Box textAlign="center" p={3}>
        <Typography color="textSecondary">
          No transactions found
        </Typography>
      </Box>
    );
  }

  return (
    <List>
      {transactions.map((transaction) => (
        <React.Fragment key={transaction.id}>
          <ListItem
            button
            onClick={() => setExpandedId(
              expandedId === transaction.id ? null : transaction.id
            )}
            sx={{
              borderRadius: 1,
              mb: 1,
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              },
            }}
          >
            <ListItemIcon>
              {getTransactionIcon(transaction.type)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="subtitle1">
                    {transaction.description}
                  </Typography>
                  <Chip
                    label={transaction.status}
                    size="small"
                    sx={{
                      backgroundColor: getStatusColor(transaction.status),
                      color: 'white',
                    }}
                  />
                </Box>
              }
              secondary={formatDate(transaction.created_at)}
            />
            <ListItemSecondaryAction>
              <Box display="flex" alignItems="center" gap={1}>
                <Typography
                  variant="subtitle1"
                  color={
                    transaction.type.toLowerCase() === 'receive'
                      ? 'success.main'
                      : 'error.main'
                  }
                >
                  {transaction.type.toLowerCase() === 'receive' ? '+' : '-'}
                  {formatCurrency(transaction.amount, transaction.currency)}
                </Typography>
                <IconButton
                  edge="end"
                  onClick={(e) => {
                    e.stopPropagation();
                    setExpandedId(
                      expandedId === transaction.id ? null : transaction.id
                    );
                  }}
                >
                  <ExpandMoreIcon
                    sx={{
                      transform: expandedId === transaction.id
                        ? 'rotate(180deg)'
                        : 'rotate(0deg)',
                      transition: 'transform 0.3s',
                    }}
                  />
                </IconButton>
              </Box>
            </ListItemSecondaryAction>
          </ListItem>
          <Collapse
            in={expandedId === transaction.id}
            timeout="auto"
            unmountOnExit
          >
            <TransactionDetails transaction={transaction} />
          </Collapse>
        </React.Fragment>
      ))}
    </List>
  );
};
