import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Chip,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  CircularProgress,
  Divider,
  Tab,
  Tabs,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Analytics,
  Assessment,
  MonetizationOn,
  SportsCricket,
  TableChart,
  BarChart,
  PieChart,
  Timeline,
  Refresh,
  FilterList,
  Download,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ScatterChart,
  Scatter
} from 'recharts';

interface PerformanceData {
  summary: {
    total_predictions: number;
    correct_predictions: number;
    accuracy_rate: number;
    win_rate: number;
    place_rate: number;
    total_stakes: number;
    total_returns: number;
    total_profit_loss: number;
    roi_percentage: number;
    avg_starting_price: number;
    latest_running_roi: number;
    period_start: string;
    period_end: string;
  };
  confidence_breakdown: {
    [key: string]: {
      total_bets: number;
      successful_bets: number;
      accuracy_rate: number;
      profit_loss: number;
      avg_roi: number;
      total_stakes: number;
    };
  };
  daily_performance: Array<{
    date: string;
    bets: number;
    wins: number;
    profit: number;
    roi: number;
    accuracy: number;
  }>;
  best_performers: Array<{
    horse_name: string;
    race_result: string;
    profit_loss: number;
    roi_percentage: number;
    starting_price: number;
    confidence_level: string;
    date: string;
  }>;
  worst_performers: Array<{
    horse_name: string;
    race_result: string;
    profit_loss: number;
    roi_percentage: number;
    starting_price: number;
    confidence_level: string;
    date: string;
  }>;
}

interface SelectionData {
  race_id: string;
  horse_name: string;
  selection_date: string;
  ai_probability: number;
  confidence_level: string;
  recommended_stake: number;
  value_rating: number;
  starting_price: number;
  market_rank: number;
  finishing_position: number;
  race_result: string;
  profit_loss: number;
  roi_percentage: number;
  created_at: string;
}

const AISelectionsResults: React.FC = () => {
  // State management
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [selectionData, setSelectionData] = useState<SelectionData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [chartType, setChartType] = useState('line');
  const [daysPeriod, setDaysPeriod] = useState(30);
  const [viewMode, setViewMode] = useState('overview');
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalSelections, setTotalSelections] = useState(0);
  
  // Filter state
  const [confidenceFilter, setConfidenceFilter] = useState('all');
  const [resultFilter, setResultFilter] = useState('all');
  const [profitFilter, setProfitFilter] = useState('all');

  // Fetch data
  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/ai_selections/performance?days_back=${daysPeriod}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setPerformanceData(result.data);
      } else {
        setError(result.message || 'Failed to fetch performance data');
      }
    } catch (err) {
      setError('Error fetching performance data');
      console.error('Performance data error:', err);
    }
  };

  const fetchSelectionData = async () => {
    try {
      const offset = page * rowsPerPage;
      const response = await fetch(`/api/ai_selections/recent?limit=${rowsPerPage}&offset=${offset}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setSelectionData(result.data.selections);
        setTotalSelections(result.data.total_count || result.data.count);
      } else {
        setError(result.message || 'Failed to fetch selection data');
      }
    } catch (err) {
      setError('Error fetching selection data');
      console.error('Selection data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformanceData();
  }, [daysPeriod]);

  useEffect(() => {
    fetchSelectionData();
  }, [page, rowsPerPage]);

  // Handle pagination
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Filter selections based on filters
  const filteredSelections = selectionData.filter(selection => {
    if (confidenceFilter !== 'all' && selection.confidence_level !== confidenceFilter) return false;
    if (resultFilter !== 'all' && selection.race_result !== resultFilter) return false;
    if (profitFilter === 'profitable' && selection.profit_loss <= 0) return false;
    if (profitFilter === 'losing' && selection.profit_loss >= 0) return false;
    return true;
  });

  // Chart color schemes
  const chartColors = {
    primary: '#667eea',
    secondary: '#43e97b',
    profit: '#4caf50',
    loss: '#f44336',
    warning: '#ff9800',
    info: '#2196f3',
    gradient: ['#667eea', '#764ba2', '#43e97b', '#f093fb']
  };

  // Performance summary cards
  const renderSummaryCards = () => {
    if (!performanceData?.summary) return null;

    const { summary } = performanceData;
    
    const cards = [
      {
        title: 'Total Predictions',
        value: summary.total_predictions,
        icon: <Analytics />,
        color: chartColors.primary,
        format: 'number'
      },
      {
        title: 'Accuracy Rate',
        value: summary.accuracy_rate,
        icon: <Assessment />,
        color: summary.accuracy_rate > 25 ? chartColors.profit : chartColors.loss,
        format: 'percentage'
      },
      {
        title: 'Total P&L',
        value: summary.total_profit_loss,
        icon: <MonetizationOn />,
        color: summary.total_profit_loss > 0 ? chartColors.profit : chartColors.loss,
        format: 'currency'
      },
      {
        title: 'ROI',
        value: summary.roi_percentage,
        icon: <TrendingUp />,
        color: summary.roi_percentage > 0 ? chartColors.profit : chartColors.loss,
        format: 'percentage'
      },
      {
        title: 'Win Rate',
        value: summary.win_rate,
        icon: <SportsCricket />,
        color: summary.win_rate > 20 ? chartColors.profit : chartColors.warning,
        format: 'percentage'
      },
      {
        title: 'Avg Odds',
        value: summary.avg_starting_price,
        icon: <Timeline />,
        color: chartColors.info,
        format: 'decimal'
      }
    ];

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={index}>
            <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${card.color}20, ${card.color}10)` }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      {card.title}
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color={card.color}>
                      {formatValue(card.value, card.format)}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  // Format values based on type
  const formatValue = (value: number, format: string) => {
    switch (format) {
      case 'currency':
        return `£${value.toFixed(2)}`;
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'decimal':
        return value.toFixed(2);
      default:
        return value.toString();
    }
  };

  // Render daily performance chart
  const renderDailyPerformanceChart = () => {
    if (!performanceData?.daily_performance) return null;

    const data = performanceData.daily_performance.map(day => ({
      ...day,
      date: new Date(day.date).toLocaleDateString('en-GB', { 
        month: 'short', 
        day: 'numeric' 
      })
    }));

    const ChartComponent = chartType === 'line' ? LineChart : 
                          chartType === 'bar' ? RechartsBarChart : AreaChart;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Daily Performance Trend</Typography>
            <ToggleButtonGroup
              value={chartType}
              exclusive
              onChange={(e, newType) => newType && setChartType(newType)}
              size="small"
            >
              <ToggleButton value="line">
                <Timeline />
              </ToggleButton>
              <ToggleButton value="bar">
                <BarChart />
              </ToggleButton>
              <ToggleButton value="area">
                <Analytics />
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>
          
          <ResponsiveContainer width="100%" height={400}>
            {chartType === 'line' && (
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="profit" orientation="left" />
                <YAxis yAxisId="accuracy" orientation="right" />
                <RechartsTooltip />
                <Legend />
                <Line 
                  yAxisId="profit"
                  type="monotone" 
                  dataKey="profit" 
                  stroke={chartColors.primary} 
                  strokeWidth={3}
                  name="Daily Profit (£)"
                />
                <Line 
                  yAxisId="accuracy"
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke={chartColors.secondary} 
                  strokeWidth={2}
                  name="Accuracy (%)"
                />
              </LineChart>
            )}
            {chartType === 'bar' && (
              <RechartsBarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="profit" fill={chartColors.primary} name="Daily Profit (£)" />
                <Bar dataKey="bets" fill={chartColors.secondary} name="Daily Bets" />
              </RechartsBarChart>
            )}
            {chartType === 'area' && (
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="profit" 
                  stackId="1"
                  stroke={chartColors.primary} 
                  fill={chartColors.primary}
                  fillOpacity={0.6}
                  name="Profit (£)"
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  // Render confidence level breakdown
  const renderConfidenceBreakdown = () => {
    if (!performanceData?.confidence_breakdown) return null;

    const data = Object.entries(performanceData.confidence_breakdown).map(([level, stats]) => ({
      confidence_level: level,
      ...stats,
      success_rate: stats.accuracy_rate
    }));

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Confidence Level Performance</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="confidence_level" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="success_rate" fill={chartColors.primary} name="Success Rate (%)" />
                  <Bar dataKey="avg_roi" fill={chartColors.secondary} name="Avg ROI (%)" />
                </RechartsBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Profit Distribution by Confidence</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill={chartColors.primary}
                    dataKey="profit_loss"
                    label={({ confidence_level, profit_loss }) => 
                      `${confidence_level}: £${profit_loss.toFixed(0)}`
                    }
                  >
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={chartColors.gradient[index % chartColors.gradient.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  // Render selections table with pagination
  const renderSelectionsTable = () => {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Recent AI Selections</Typography>
            <Box display="flex" gap={2}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Confidence</InputLabel>
                <Select
                  value={confidenceFilter}
                  label="Confidence"
                  onChange={(e) => setConfidenceFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="High">High</MenuItem>
                  <MenuItem value="Medium">Medium</MenuItem>
                  <MenuItem value="Low">Low</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Result</InputLabel>
                <Select
                  value={resultFilter}
                  label="Result"
                  onChange={(e) => setResultFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="WIN">Win</MenuItem>
                  <MenuItem value="PLACE">Place</MenuItem>
                  <MenuItem value="LOSE">Lose</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>P&L</InputLabel>
                <Select
                  value={profitFilter}
                  label="P&L"
                  onChange={(e) => setProfitFilter(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="profitable">Profitable</MenuItem>
                  <MenuItem value="losing">Losing</MenuItem>
                </Select>
              </FormControl>
              
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  fetchSelectionData();
                  fetchPerformanceData();
                }}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Horse Name</TableCell>
                  <TableCell>AI Probability</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Starting Price</TableCell>
                  <TableCell>Result</TableCell>
                  <TableCell>Position</TableCell>
                  <TableCell>Stake</TableCell>
                  <TableCell>P&L</TableCell>
                  <TableCell>ROI</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={10} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : filteredSelections.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={10} align="center">
                      No selections found matching your filters
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredSelections.map((selection, index) => (
                    <TableRow key={index} hover>
                      <TableCell>
                        {new Date(selection.selection_date).toLocaleDateString('en-GB')}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          {selection.horse_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="primary">
                          {selection.ai_probability.toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={selection.confidence_level}
                          size="small"
                          color={
                            selection.confidence_level === 'High' ? 'success' :
                            selection.confidence_level === 'Medium' ? 'warning' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell>{selection.starting_price.toFixed(2)}</TableCell>
                      <TableCell>
                        <Chip
                          label={selection.race_result}
                          size="small"
                          color={
                            selection.race_result === 'WIN' ? 'success' :
                            selection.race_result === 'PLACE' ? 'info' : 'error'
                          }
                        />
                      </TableCell>
                      <TableCell>{selection.finishing_position || '-'}</TableCell>
                      <TableCell>£{selection.recommended_stake.toFixed(2)}</TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          color={selection.profit_loss >= 0 ? 'success.main' : 'error.main'}
                          fontWeight="medium"
                        >
                          £{selection.profit_loss.toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          color={selection.roi_percentage >= 0 ? 'success.main' : 'error.main'}
                          fontWeight="medium"
                        >
                          {selection.roi_percentage.toFixed(1)}%
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={totalSelections}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </CardContent>
      </Card>
    );
  };

  // Render top performers tables
  const renderPerformers = () => {
    if (!performanceData?.best_performers && !performanceData?.worst_performers) return null;

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="success.main">
                🏆 Best Performers
              </Typography>
              <TableContainer sx={{ maxHeight: 300 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Horse</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>P&L</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceData.best_performers.slice(0, 10).map((performer, index) => (
                      <TableRow key={index}>
                        <TableCell>{performer.horse_name}</TableCell>
                        <TableCell>
                          <Chip label={performer.race_result} size="small" color="success" />
                        </TableCell>
                        <TableCell>
                          <Typography color="success.main" fontWeight="medium">
                            £{performer.profit_loss.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {new Date(performer.date).toLocaleDateString('en-GB')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error.main">
                📉 Worst Performers
              </Typography>
              <TableContainer sx={{ maxHeight: 300 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Horse</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>P&L</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {performanceData.worst_performers.slice(0, 10).map((performer, index) => (
                      <TableRow key={index}>
                        <TableCell>{performer.horse_name}</TableCell>
                        <TableCell>
                          <Chip label={performer.race_result} size="small" color="error" />
                        </TableCell>
                        <TableCell>
                          <Typography color="error.main" fontWeight="medium">
                            £{performer.profit_loss.toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {new Date(performer.date).toLocaleDateString('en-GB')}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          🤖 AI Selections Performance Dashboard
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small">
            <InputLabel>Period</InputLabel>
            <Select
              value={daysPeriod}
              label="Period"
              onChange={(e) => setDaysPeriod(e.target.value as number)}
            >
              <MenuItem value={7}>Last 7 days</MenuItem>
              <MenuItem value={14}>Last 14 days</MenuItem>
              <MenuItem value={30}>Last 30 days</MenuItem>
              <MenuItem value={60}>Last 60 days</MenuItem>
              <MenuItem value={90}>Last 90 days</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => {
              // Export functionality would go here
              console.log('Export data...');
            }}
          >
            Export
          </Button>
        </Box>
      </Box>

      {loading && !performanceData ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress size={60} />
        </Box>
      ) : (
        <>
          {/* Summary Cards */}
          {renderSummaryCards()}

          {/* Tabs for different views */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab icon={<Analytics />} label="Overview" />
              <Tab icon={<Timeline />} label="Performance Trends" />
              <Tab icon={<TableChart />} label="Detailed Results" />
              <Tab icon={<Assessment />} label="Analysis" />
            </Tabs>
          </Box>

          {/* Tab Content */}
          {tabValue === 0 && (
            <>
              {renderDailyPerformanceChart()}
              {renderConfidenceBreakdown()}
              {renderPerformers()}
            </>
          )}

          {tabValue === 1 && (
            <>
              {renderDailyPerformanceChart()}
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>ROI Trend</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={performanceData?.daily_performance || []}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Line 
                            type="monotone" 
                            dataKey="roi" 
                            stroke={chartColors.primary} 
                            strokeWidth={3}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Accuracy Trend</Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={performanceData?.daily_performance || []}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Area 
                            type="monotone" 
                            dataKey="accuracy" 
                            stroke={chartColors.secondary} 
                            fill={chartColors.secondary}
                            fillOpacity={0.6}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </>
          )}

          {tabValue === 2 && renderSelectionsTable()}

          {tabValue === 3 && (
            <>
              {renderConfidenceBreakdown()}
              {renderPerformers()}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Performance Insights</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="textSecondary">
                        Best Confidence Level
                      </Typography>
                      <Typography variant="h6" color="success.main">
                        {performanceData?.confidence_breakdown && 
                         Object.entries(performanceData.confidence_breakdown)
                           .sort(([,a], [,b]) => b.avg_roi - a.avg_roi)[0]?.[0] || 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="textSecondary">
                        Most Profitable Day
                      </Typography>
                      <Typography variant="h6" color="success.main">
                        {performanceData?.daily_performance &&
                         [...performanceData.daily_performance]
                           .sort((a, b) => b.profit - a.profit)[0]?.date.split('T')[0] || 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="textSecondary">
                        Avg Profit per Bet
                      </Typography>
                      <Typography variant="h6" color={performanceData?.summary.total_profit_loss && performanceData.summary.total_profit_loss > 0 ? 'success.main' : 'error.main'}>
                        £{performanceData?.summary && performanceData.summary.total_predictions > 0
                          ? (performanceData.summary.total_profit_loss / performanceData.summary.total_predictions).toFixed(2)
                          : '0.00'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}
    </Container>
  );
};

export default AISelectionsResults;
