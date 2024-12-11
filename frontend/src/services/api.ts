// Mock API service for development
export const fetchAccountDetails = async () => {
  return {
    accountNumber: '1234567890',
    accountType: 'Savings',
    balance: 25000.00,
    currency: 'KES'
  };
};

export const fetchTransactions = async () => {
  return [
    {
      id: 1,
      date: '2024-03-05',
      description: 'Salary Deposit',
      amount: 45000.00,
      type: 'credit'
    },
    {
      id: 2,
      date: '2024-03-04',
      description: 'Utility Bill Payment',
      amount: -2500.00,
      type: 'debit'
    },
    {
      id: 3,
      date: '2024-03-03',
      description: 'Shopping Mall',
      amount: -3500.00,
      type: 'debit'
    }
  ];
};

export const fetchNotifications = async () => {
  return [
    {
      id: 1,
      type: 'info',
      message: 'Your account statement is ready',
      date: '2024-03-05'
    },
    {
      id: 2,
      type: 'success',
      message: 'Successful fund transfer',
      date: '2024-03-04'
    }
  ];
};

export const fetchSpendingData = async () => {
  return [
    { category: 'Bills', amount: 15000 },
    { category: 'Shopping', amount: 8000 },
    { category: 'Transport', amount: 5000 },
    { category: 'Entertainment', amount: 3000 },
    { category: 'Others', amount: 2000 }
  ];
};
