import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Typography,
  Box,
  Collapse,
  Chip,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { Portfolio } from '../../types/investment';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

interface PortfolioListProps {
  portfolios: Portfolio[];
}

const PortfolioRow: React.FC<{ portfolio: Portfolio }> = ({ portfolio }) => {
  const [open, setOpen] = useState(false);

  const totalValue = portfolio.holdings.reduce(
    (sum, holding) => sum + holding.market_value,
    0
  );

  const totalGainLoss = portfolio.holdings.reduce(
    (sum, holding) => sum + holding.gain_loss,
    0
  );

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{portfolio.name}</TableCell>
        <TableCell align="right">{formatCurrency(totalValue)}</TableCell>
        <TableCell
          align="right"
          sx={{
            color: totalGainLoss >= 0 ? 'success.main' : 'error.main',
          }}
        >
          {formatCurrency(totalGainLoss)}
          <br />
          <Typography variant="caption">
            ({formatPercentage(totalGainLoss / (totalValue - totalGainLoss))})
          </Typography>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Holdings
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Price</TableCell>
                    <TableCell align="right">Market Value</TableCell>
                    <TableCell align="right">Gain/Loss</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolio.holdings.map((holding) => (
                    <TableRow key={holding.id}>
                      <TableCell>{holding.symbol}</TableCell>
                      <TableCell>
                        <Chip
                          label={holding.asset_type}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell align="right">{holding.quantity}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(holding.current_price || holding.average_price)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(holding.market_value)}
                      </TableCell>
                      <TableCell
                        align="right"
                        sx={{
                          color: holding.gain_loss >= 0 ? 'success.main' : 'error.main',
                        }}
                      >
                        {formatCurrency(holding.gain_loss)}
                        <br />
                        <Typography variant="caption">
                          ({formatPercentage(holding.gain_loss_percentage)})
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

const PortfolioList: React.FC<PortfolioListProps> = ({ portfolios }) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Your Portfolios
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Portfolio Name</TableCell>
              <TableCell align="right">Total Value</TableCell>
              <TableCell align="right">Total Gain/Loss</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {portfolios.map((portfolio) => (
              <PortfolioRow key={portfolio.id} portfolio={portfolio} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PortfolioList;
