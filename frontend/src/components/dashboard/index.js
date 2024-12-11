import React from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Paper,
  useTheme
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import SecurityIcon from '@mui/icons-material/Security';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import SpeedIcon from '@mui/icons-material/Speed';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import logo from '../../assets/images/logo.png';

// Temporarily comment out UserDashboard until we fix the auth
const Dashboard = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  // const isAuthenticated = false;

  // if (isAuthenticated) {
  //   return <UserDashboard />;
  // }

  const features = [
    {
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      title: 'Advanced Security',
      description: 'Bank with confidence using our state-of-the-art security systems'
    },
    {
      icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />,
      title: 'Smart Banking',
      description: 'Experience intelligent financial management with real-time insights'
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40 }} />,
      title: 'Fast Transactions',
      description: 'Instant transfers and quick transaction processing across Africa'
    },
    {
      icon: <VerifiedUserIcon sx={{ fontSize: 40 }} />,
      title: 'Compliance First',
      description: 'Full regulatory compliance and ethical African banking practices'
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: theme.palette.primary.main,
          color: 'white',
          py: 8,
          mb: 6
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography 
                variant="h2" 
                component="h1" 
                gutterBottom
                sx={{ 
                  fontWeight: 'bold',
                  letterSpacing: '0.5px'
                }}
              >
                Welcome to Mavuno Bank
              </Typography>
              <Typography variant="h5" paragraph>
                Your Trusted Partner in African Banking Excellence
              </Typography>
              <Typography variant="subtitle1" paragraph>
                Experience secure, efficient, and ethical banking solutions tailored for Africa's digital age
              </Typography>
              <Box sx={{ mt: 4 }}>
                <Button
                  variant="contained"
                  color="secondary"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{ mr: 2 }}
                >
                  Open Account
                </Button>
                <Button
                  variant="outlined"
                  color="inherit"
                  size="large"
                  onClick={() => navigate('/login')}
                >
                  Login
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  height: '100%'
                }}
              >
                <img
                  src={logo}
                  alt="Mavuno Bank"
                  style={{
                    maxWidth: '80%',
                    height: 'auto',
                    filter: 'drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.2))'
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg">
        <Typography variant="h3" align="center" gutterBottom>
          Why Choose Mavuno Bank
        </Typography>
        <Grid container spacing={4} sx={{ mt: 2 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper
                sx={{
                  p: 3,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center'
                }}
                elevation={2}
              >
                <Box sx={{ color: theme.palette.primary.main, mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography color="text.secondary">
                  {feature.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Call to Action */}
        <Box sx={{ textAlign: 'center', mt: 8, mb: 6 }}>
          <Typography variant="h4" gutterBottom>
            Ready to Experience Modern African Banking?
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" paragraph>
            Join thousands of satisfied customers who trust Mavuno Bank for their financial needs
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/register')}
            sx={{ mt: 2 }}
          >
            Open Your Account Today
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default Dashboard;
