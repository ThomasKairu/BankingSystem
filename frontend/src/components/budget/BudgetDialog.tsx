import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Budget, BudgetCategory, BudgetPeriod } from '../../types/budget';
import { createBudget, updateBudget } from '../../services/budgetService';

interface BudgetDialogProps {
  open: boolean;
  onClose: () => void;
  budget?: Budget | null;
}

const BudgetDialog: React.FC<BudgetDialogProps> = ({ open, onClose, budget }) => {
  const queryClient = useQueryClient();
  const isEdit = !!budget;

  const [formData, setFormData] = useState({
    name: '',
    category: BudgetCategory.OTHER,
    amount: '',
    period: BudgetPeriod.MONTHLY,
    startDate: new Date(),
    endDate: null as Date | null,
  });

  useEffect(() => {
    if (budget) {
      setFormData({
        name: budget.name,
        category: budget.category,
        amount: budget.amount.toString(),
        period: budget.period,
        startDate: new Date(budget.startDate),
        endDate: budget.endDate ? new Date(budget.endDate) : null,
      });
    }
  }, [budget]);

  const mutation = useMutation(
    (data: any) => (isEdit ? updateBudget(budget.id, data) : createBudget(data)),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['budgets']);
        onClose();
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      ...formData,
      amount: parseFloat(formData.amount),
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isEdit ? 'Edit Budget' : 'Create Budget'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                name="name"
                label="Budget Name"
                value={formData.name}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                name="category"
                select
                label="Category"
                value={formData.category}
                onChange={handleChange}
                fullWidth
                required
              >
                {Object.values(BudgetCategory).map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                name="period"
                select
                label="Period"
                value={formData.period}
                onChange={handleChange}
                fullWidth
                required
              >
                {Object.values(BudgetPeriod).map((period) => (
                  <MenuItem key={period} value={period}>
                    {period}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                name="amount"
                label="Amount"
                type="number"
                value={formData.amount}
                onChange={handleChange}
                fullWidth
                required
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <DatePicker
                label="Start Date"
                value={formData.startDate}
                onChange={(date) =>
                  setFormData({ ...formData, startDate: date || new Date() })
                }
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <DatePicker
                label="End Date (Optional)"
                value={formData.endDate}
                onChange={(date) =>
                  setFormData({ ...formData, endDate: date })
                }
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" color="primary">
            {isEdit ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default BudgetDialog;
