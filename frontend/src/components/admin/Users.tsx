import React from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Button,
  Typography,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Block as BlockIcon,
  CheckCircle as UnblockIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  role: string;
}

interface EditUserDialogProps {
  open: boolean;
  onClose: () => void;
  user: User | null;
}

const EditUserDialog: React.FC<EditUserDialogProps> = ({ open, onClose, user }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = React.useState({
    email: '',
    role: '',
    is_verified: false,
  });

  React.useEffect(() => {
    if (user) {
      setFormData({
        email: user.email,
        role: user.role,
        is_verified: user.is_verified,
      });
    }
  }, [user]);

  const updateUser = useMutation(
    (data: any) => api.put(`/admin/users/${user?.id}`, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
        onClose();
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateUser.mutate(formData);
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Edit User</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email"
            type="email"
            fullWidth
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
          />
          <TextField
            margin="dense"
            label="Role"
            fullWidth
            value={formData.role}
            onChange={(e) =>
              setFormData({ ...formData, role: e.target.value })
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" color="primary">
            Save
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export const Users: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = React.useState<User | null>(null);
  const [editDialogOpen, setEditDialogOpen] = React.useState(false);

  const { data: users, isLoading, error } = useQuery('users', () =>
    api.get('/admin/users')
  );

  const blockUser = useMutation(
    (userId: number) => api.post(`/admin/users/${userId}/block`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
      },
    }
  );

  const unblockUser = useMutation(
    (userId: number) => api.post(`/admin/users/${userId}/unblock`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
      },
    }
  );

  const handleEditClick = (user: User) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading users</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Verified</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users?.map((user: User) => (
              <TableRow key={user.id}>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>
                  {user.is_active ? (
                    <Typography color="primary">Active</Typography>
                  ) : (
                    <Typography color="error">Blocked</Typography>
                  )}
                </TableCell>
                <TableCell>
                  {user.is_verified ? (
                    <Typography color="primary">Yes</Typography>
                  ) : (
                    <Typography color="error">No</Typography>
                  )}
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => handleEditClick(user)}
                    color="primary"
                  >
                    <EditIcon />
                  </IconButton>
                  {user.is_active ? (
                    <IconButton
                      onClick={() => blockUser.mutate(user.id)}
                      color="error"
                    >
                      <BlockIcon />
                    </IconButton>
                  ) : (
                    <IconButton
                      onClick={() => unblockUser.mutate(user.id)}
                      color="success"
                    >
                      <UnblockIcon />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <EditUserDialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        user={selectedUser}
      />
    </Box>
  );
};
