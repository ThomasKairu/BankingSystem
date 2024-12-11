import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Box,
  Chip,
  Menu,
  MenuItem,
  useTheme,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  AccountBalance as AccountIcon,
  CreditCard as CreditCardIcon,
  Savings as SavingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface AccountCardProps {
  account: {
    id: string;
    type: string;
    name: string;
    balance: number;
    currency: string;
    status: string;
    last_transaction?: string;
  };
}

export const AccountCard: React.FC<AccountCardProps> = ({ account }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const theme = useTheme();
  const navigate = useNavigate();

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getAccountIcon = () => {
    switch (account.type.toLowerCase()) {
      case 'savings':
        return <SavingsIcon />;
      case 'credit':
        return <CreditCardIcon />;
      default:
        return <AccountIcon />;
    }
  };

  const getStatusColor = () => {
    switch (account.status.toLowerCase()) {
      case 'active':
        return theme.palette.success.main;
      case 'inactive':
        return theme.palette.error.main;
      default:
        return theme.palette.warning.main;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: account.currency,
    }).format(amount);
  };

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        '&:hover': {
          boxShadow: theme.shadows[4],
          transform: 'translateY(-2px)',
          transition: 'all 0.3s ease-in-out',
        },
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {getAccountIcon()}
            <Typography variant="h6" component="div">
              {account.name}
            </Typography>
          </Box>
          <Box>
            <Chip
              label={account.status}
              size="small"
              sx={{
                backgroundColor: getStatusColor(),
                color: 'white',
                mr: 1,
              }}
            />
            <IconButton
              size="small"
              onClick={handleMenuClick}
              aria-label="account menu"
            >
              <MoreIcon />
            </IconButton>
          </Box>
        </Box>

        <Typography variant="h4" component="div" gutterBottom>
          {formatCurrency(account.balance)}
        </Typography>

        <Typography color="textSecondary" variant="body2">
          Account Type: {account.type}
        </Typography>
        {account.last_transaction && (
          <Typography color="textSecondary" variant="body2">
            Last Transaction: {new Date(account.last_transaction).toLocaleDateString()}
          </Typography>
        )}
      </CardContent>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/accounts/${account.id}`);
          handleMenuClose();
        }}>
          View Details
        </MenuItem>
        <MenuItem onClick={() => {
          navigate(`/accounts/${account.id}/transactions`);
          handleMenuClose();
        }}>
          View Transactions
        </MenuItem>
        <MenuItem onClick={() => {
          navigate(`/transfer?from=${account.id}`);
          handleMenuClose();
        }}>
          Make Transfer
        </MenuItem>
        <MenuItem onClick={() => {
          navigate(`/accounts/${account.id}/statements`);
          handleMenuClose();
        }}>
          View Statements
        </MenuItem>
      </Menu>
    </Card>
  );
};
