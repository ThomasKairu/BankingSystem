import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Button,
  Typography,
  Box,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import BudgetDialog from './BudgetDialog';
import { Budget } from '../../types/budget';
import { formatCurrency } from '../../utils/formatters';

interface BudgetListProps {
  budgets: Budget[];
}

const BudgetList: React.FC<BudgetListProps> = ({ budgets }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);

  const handleEdit = (budget: Budget) => {
    setSelectedBudget(budget);
    setOpenDialog(true);
  };

  const handleAdd = () => {
    setSelectedBudget(null);
    setOpenDialog(true);
  };

  const handleClose = () => {
    setOpenDialog(false);
    setSelectedBudget(null);
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Budgets</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAdd}
        >
          Add Budget
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Spent</TableCell>
              <TableCell>Remaining</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {budgets.map((budget) => (
              <TableRow key={budget.id}>
                <TableCell>{budget.name}</TableCell>
                <TableCell>{budget.category}</TableCell>
                <TableCell>{formatCurrency(budget.amount)}</TableCell>
                <TableCell>{budget.period}</TableCell>
                <TableCell>{formatCurrency(budget.spent || 0)}</TableCell>
                <TableCell>{formatCurrency(budget.remaining || 0)}</TableCell>
                <TableCell>
                  <IconButton onClick={() => handleEdit(budget)} size="small">
                    <EditIcon />
                  </IconButton>
                  <IconButton color="error" size="small">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <BudgetDialog
        open={openDialog}
        onClose={handleClose}
        budget={selectedBudget}
      />
    </>
  );
};

export default BudgetList;
