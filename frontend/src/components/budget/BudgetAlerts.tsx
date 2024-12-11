import React from 'react';
import {
  Box,
  Typography,
  Alert,
  AlertTitle,
  IconButton,
  Stack,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { BudgetAlert, AlertType } from '../../types/budget';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { dismissBudgetAlert } from '../../services/budgetService';

interface BudgetAlertsProps {
  alerts: BudgetAlert[];
}

const BudgetAlerts: React.FC<BudgetAlertsProps> = ({ alerts }) => {
  const queryClient = useQueryClient();

  const dismissMutation = useMutation(dismissBudgetAlert, {
    onSuccess: () => {
      queryClient.invalidateQueries(['budgetAlerts']);
    },
  });

  const handleDismiss = (alertId: number) => {
    dismissMutation.mutate(alertId);
  };

  const getSeverity = (type: AlertType) => {
    switch (type) {
      case AlertType.OVERSPENT:
        return 'error';
      case AlertType.APPROACHING_LIMIT:
        return 'warning';
      case AlertType.RECURRING_DUE:
        return 'info';
      default:
        return 'info';
    }
  };

  if (alerts.length === 0) {
    return null;
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Budget Alerts
      </Typography>

      <Stack spacing={2}>
        {alerts.map((alert) => (
          <Alert
            key={alert.id}
            severity={getSeverity(alert.type)}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => handleDismiss(alert.id)}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            <AlertTitle>{alert.type}</AlertTitle>
            {alert.message}
          </Alert>
        ))}
      </Stack>
    </Box>
  );
};

export default BudgetAlerts;
