import React from 'react';
import {
  Paper,
  Grid,
  Button,
  Typography,
  Box,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Send as SendIcon,
  AccountBalance as AccountIcon,
  Receipt as BillIcon,
  CreditCard as CardIcon,
  History as HistoryIcon,
  Description as StatementIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface QuickAction {
  icon: React.ReactNode;
  label: string;
  path: string;
  color: string;
}

export const QuickActions: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();

  const quickActions: QuickAction[] = [
    {
      icon: <SendIcon />,
      label: 'Send Money',
      path: '/transfer',
      color: theme.palette.primary.main,
    },
    {
      icon: <AccountIcon />,
      label: 'Add Account',
      path: '/accounts/new',
      color: theme.palette.secondary.main,
    },
    {
      icon: <BillIcon />,
      label: 'Pay Bills',
      path: '/bills',
      color: theme.palette.error.main,
    },
    {
      icon: <CardIcon />,
      label: 'Cards',
      path: '/cards',
      color: theme.palette.warning.main,
    },
    {
      icon: <HistoryIcon />,
      label: 'History',
      path: '/transactions',
      color: theme.palette.info.main,
    },
    {
      icon: <StatementIcon />,
      label: 'Statements',
      path: '/statements',
      color: theme.palette.success.main,
    },
  ];

  return (
    <Paper
      sx={{
        p: 2,
        mb: 3,
        background: theme.palette.background.paper,
      }}
    >
      <Typography variant="h6" gutterBottom>
        Quick Actions
      </Typography>
      <Grid container spacing={2}>
        {quickActions.map((action) => (
          <Grid item xs={6} sm={4} md={2} key={action.label}>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate(action.path)}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                padding: 2,
                height: '100%',
                borderColor: action.color,
                color: action.color,
                '&:hover': {
                  borderColor: action.color,
                  backgroundColor: `${action.color}10`,
                },
                transition: 'all 0.3s ease-in-out',
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  backgroundColor: `${action.color}20`,
                  color: action.color,
                  marginBottom: 1,
                }}
              >
                {action.icon}
              </Box>
              <Typography
                variant="body2"
                sx={{
                  textAlign: 'center',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {action.label}
              </Typography>
            </Button>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};
