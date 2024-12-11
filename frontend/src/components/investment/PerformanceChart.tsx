import React, { useState } from 'react';
import {
  Box,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  useTheme,
} from '@mui/material';
import { LineChart } from '@mui/x-charts/LineChart';
import { useQuery } from '@tanstack/react-query';
import { Portfolio } from '../../types/investment';
import { fetchPortfolioPerformance } from '../../services/investmentService';
import { formatCurrency } from '../../utils/formatters';

interface PerformanceChartProps {
  portfolios: Portfolio[];
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ portfolios }) => {
  const theme = useTheme();
  const [timeframe, setTimeframe] = useState('1Y');
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | 'all'>(
    'all'
  );

  const { data: performanceData } = useQuery(
    ['portfolioPerformance', selectedPortfolio, timeframe],
    () =>
      selectedPortfolio === 'all'
        ? Promise.all(
            portfolios.map((p) =>
              fetchPortfolioPerformance(p.id, timeframe)
            )
          )
        : fetchPortfolioPerformance(selectedPortfolio, timeframe)
  );

  const handleTimeframeChange = (
    event: React.MouseEvent<HTMLElement>,
    newTimeframe: string
  ) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
    }
  };

  const handlePortfolioChange = (
    event: React.MouseEvent<HTMLElement>,
    newPortfolio: number | 'all'
  ) => {
    if (newPortfolio !== null) {
      setSelectedPortfolio(newPortfolio);
    }
  };

  if (!performanceData) {
    return <div>Loading...</div>;
  }

  const chartData = Array.isArray(performanceData)
    ? performanceData.reduce(
        (acc, portfolioData, index) => {
          const portfolio = portfolios[index];
          return {
            dates: acc.dates.concat(
              portfolioData.map((d) => new Date(d.date))
            ),
            values: acc.values.concat(
              portfolioData.map((d) => d.total_value)
            ),
            portfolioNames: acc.portfolioNames.concat(
              Array(portfolioData.length).fill(portfolio.name)
            ),
          };
        },
        { dates: [], values: [], portfolioNames: [] }
      )
    : {
        dates: performanceData.map((d) => new Date(d.date)),
        values: performanceData.map((d) => d.total_value),
        portfolioNames: Array(performanceData.length).fill(
          portfolios.find((p) => p.id === selectedPortfolio)?.name
        ),
      };

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}
      >
        <Typography variant="h6">Portfolio Performance</Typography>
        <Box>
          <ToggleButtonGroup
            size="small"
            value={timeframe}
            exclusive
            onChange={handleTimeframeChange}
            sx={{ mr: 2 }}
          >
            <ToggleButton value="1M">1M</ToggleButton>
            <ToggleButton value="3M">3M</ToggleButton>
            <ToggleButton value="6M">6M</ToggleButton>
            <ToggleButton value="1Y">1Y</ToggleButton>
          </ToggleButtonGroup>

          <ToggleButtonGroup
            size="small"
            value={selectedPortfolio}
            exclusive
            onChange={handlePortfolioChange}
          >
            <ToggleButton value="all">All</ToggleButton>
            {portfolios.map((portfolio) => (
              <ToggleButton key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>
      </Box>

      <Box sx={{ height: 400 }}>
        <LineChart
          xAxis={[
            {
              data: chartData.dates,
              scaleType: 'time',
              valueFormatter: (date: Date) =>
                date.toLocaleDateString(),
            },
          ]}
          yAxis={[
            {
              valueFormatter: (value: number) =>
                formatCurrency(value),
            },
          ]}
          series={[
            {
              data: chartData.values,
              valueFormatter: (value: number) =>
                formatCurrency(value),
              area: true,
            },
          ]}
          height={400}
        />
      </Box>
    </Box>
  );
};

export default PerformanceChart;
