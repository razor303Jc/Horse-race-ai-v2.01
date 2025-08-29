import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Slider,
  RadioGroup,
  Radio,
  FormLabel,
  Checkbox
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  TrendingUp,
  TrendingDown,
  Analytics,
  Assessment,
  Timeline,
  Warning,
  CheckCircle,
  Error,
  Info,
  Speed,
  MonetizationOn,
  BarChart,
  ShowChart,
  PieChart,
  Download,
  Refresh,
  FilterList,
  DateRange,
  Calculate,
  Compare,
  Insights,
  Psychology,
  EmojiEvents,
  Star,
  LocalAtm,
  AccountBalance,
  TrendingFlat
} from '@mui/icons-material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer, 
  BarChart as RechartsBarChart, 
  Bar, 
  PieChart as RechartsPieChart, 
  Pie, 
  Cell,
  Area,
  AreaChart,
  ComposedChart,
  Scatter,
  ScatterChart,
  RadialBarChart,
  RadialBar,
  Legend
} from 'recharts';

// Interfaces for analytics data
interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  previous_value: number;
  change: number;
  change_percentage: number;
  trend: 'up' | 'down' | 'stable';
  category: 'profitability' | 'accuracy' | 'risk' | 'volume';
}

interface BettingAnalytics {
  total_bets: number;
  total_stake: number;
  total_returns: number;
  net_profit: number;
  roi_percentage: number;
  win_rate: number;
  place_rate: number;
  avg_odds: number;
  sharpe_ratio: number;
  max_drawdown: number;
  profit_factor: number;
  kelly_efficiency: number;
}

interface HistoricalPerformance {
  date: string;
  cumulative_profit: number;
  daily_profit: number;
  running_balance: number;
  bets_count: number;
  win_rate: number;
  roi: number;
  drawdown: number;
}

interface TrackAnalysis {
  track_name: string;
  races_count: number;
  bets_count: number;
  win_rate: number;
  roi: number;
  profit: number;
  avg_odds: number;
  confidence: number;
}

interface JockeyTrainerAnalysis {
  name: string;
  type: 'jockey' | 'trainer';
  bets_count: number;
  win_rate: number;
  place_rate: number;
  roi: number;
  profit: number;
  avg_odds: number;
  races_count: number;
}

interface MarketEfficiencyData {
  market_type: string;
  total_volume: number;
  avg_margin: number;
  liquidity_score: number;
  price_accuracy: number;
  arbitrage_opportunities: number;
  efficiency_rating: number;
}

export const AdvancedAnalyticsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState({ start: '2024-01-01', end: '2024-01-31' });
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [selectedTracks, setSelectedTracks] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['all']);
  const [comparisonMode, setComparisonMode] = useState(false);

  // Mock data - in real implementation, this would come from API
  const [performanceMetrics] = useState<PerformanceMetric[]>([
    {
      id: 'roi',
      name: 'Return on Investment',
      value: 15.6,
      previous_value: 12.3,
      change: 3.3,
      change_percentage: 26.8,
      trend: 'up',
      category: 'profitability'
    },
    {
      id: 'win_rate',
      name: 'Win Rate',
      value: 32.4,
      previous_value: 28.7,
      change: 3.7,
      change_percentage: 12.9,
      trend: 'up',
      category: 'accuracy'
    },
    {
      id: 'sharpe_ratio',
      name: 'Sharpe Ratio',
      value: 1.85,
      previous_value: 1.42,
      change: 0.43,
      change_percentage: 30.3,
      trend: 'up',
      category: 'risk'
    },
    {
      id: 'max_drawdown',
      name: 'Max Drawdown',
      value: -8.2,
      previous_value: -12.5,
      change: 4.3,
      change_percentage: -34.4,
      trend: 'up',
      category: 'risk'
    },
    {
      id: 'total_profit',
      name: 'Total Profit',
      value: 2847.50,
      previous_value: 2145.30,
      change: 702.20,
      change_percentage: 32.7,
      trend: 'up',
      category: 'profitability'
    },
    {
      id: 'avg_stake',
      name: 'Average Stake',
      value: 45.60,
      previous_value: 52.80,
      change: -7.20,
      change_percentage: -13.6,
      trend: 'down',
      category: 'volume'
    }
  ]);

  const [bettingAnalytics] = useState<BettingAnalytics>({
    total_bets: 287,
    total_stake: 13089.50,
    total_returns: 15937.00,
    net_profit: 2847.50,
    roi_percentage: 21.8,
    win_rate: 32.4,
    place_rate: 58.9,
    avg_odds: 3.95,
    sharpe_ratio: 1.85,
    max_drawdown: -8.2,
    profit_factor: 1.78,
    kelly_efficiency: 0.73
  });

  const [historicalData] = useState<HistoricalPerformance[]>([
    { date: '2024-01-01', cumulative_profit: 0, daily_profit: 0, running_balance: 5000, bets_count: 0, win_rate: 0, roi: 0, drawdown: 0 },
    { date: '2024-01-07', cumulative_profit: 156.30, daily_profit: 156.30, running_balance: 5156.30, bets_count: 12, win_rate: 33.3, roi: 3.1, drawdown: 0 },
    { date: '2024-01-14', cumulative_profit: 423.60, daily_profit: 267.30, running_balance: 5423.60, bets_count: 28, win_rate: 35.7, roi: 8.5, drawdown: 0 },
    { date: '2024-01-21', cumulative_profit: 298.40, daily_profit: -125.20, running_balance: 5298.40, bets_count: 45, win_rate: 31.1, roi: 6.0, drawdown: -2.3 },
    { date: '2024-01-28', cumulative_profit: 847.50, daily_profit: 549.10, running_balance: 5847.50, bets_count: 67, win_rate: 34.3, roi: 16.9, drawdown: 0 }
  ]);

  const [trackAnalysis] = useState<TrackAnalysis[]>([
    { track_name: 'Ascot', races_count: 24, bets_count: 45, win_rate: 38.9, roi: 24.7, profit: 456.80, avg_odds: 3.2, confidence: 0.89 },
    { track_name: 'Cheltenham', races_count: 18, bets_count: 32, win_rate: 34.4, roi: 19.3, profit: 298.50, avg_odds: 4.1, confidence: 0.85 },
    { track_name: 'Newmarket', races_count: 21, bets_count: 39, win_rate: 30.8, roi: 15.6, profit: 234.70, avg_odds: 3.8, confidence: 0.82 },
    { track_name: 'York', races_count: 15, bets_count: 28, win_rate: 42.9, roi: 31.2, profit: 387.20, avg_odds: 2.9, confidence: 0.91 },
    { track_name: 'Kempton', races_count: 12, bets_count: 22, win_rate: 27.3, roi: 8.4, profit: 98.30, avg_odds: 4.5, confidence: 0.76 }
  ]);

  const [jockeyTrainerData] = useState<JockeyTrainerAnalysis[]>([
    { name: 'Frankie Dettori', type: 'jockey', bets_count: 28, win_rate: 42.9, place_rate: 67.9, roi: 28.4, profit: 456.70, avg_odds: 3.1, races_count: 15 },
    { name: 'Ryan Moore', type: 'jockey', bets_count: 24, win_rate: 37.5, place_rate: 62.5, roi: 22.1, profit: 298.40, avg_odds: 3.4, races_count: 18 },
    { name: 'William Haggas', type: 'trainer', bets_count: 31, win_rate: 35.5, place_rate: 58.1, roi: 19.7, profit: 387.90, avg_odds: 3.6, races_count: 22 },
    { name: 'Aidan O\'Brien', type: 'trainer', bets_count: 26, win_rate: 38.5, place_rate: 65.4, roi: 25.8, profit: 423.60, avg_odds: 3.2, races_count: 19 }
  ]);

  const [marketEfficiency] = useState<MarketEfficiencyData[]>([
    { market_type: 'Win', total_volume: 1250000, avg_margin: 1.18, liquidity_score: 0.92, price_accuracy: 0.87, arbitrage_opportunities: 3, efficiency_rating: 0.89 },
    { market_type: 'Place', total_volume: 890000, avg_margin: 1.25, liquidity_score: 0.88, price_accuracy: 0.84, arbitrage_opportunities: 7, efficiency_rating: 0.85 },
    { market_type: 'Each-Way', total_volume: 620000, avg_margin: 1.32, liquidity_score: 0.81, price_accuracy: 0.79, arbitrage_opportunities: 12, efficiency_rating: 0.78 },
    { market_type: 'Forecast', total_volume: 340000, avg_margin: 1.45, liquidity_score: 0.73, price_accuracy: 0.71, arbitrage_opportunities: 18, efficiency_rating: 0.69 }
  ]);

  const getMetricIcon = (category: string) => {
    switch (category) {
      case 'profitability': return <MonetizationOn />;
      case 'accuracy': return <Analytics />;
      case 'risk': return <Assessment />;
      case 'volume': return <BarChart />;
      default: return <Timeline />;
    }
  };

  const getMetricColor = (trend: string): 'success' | 'error' | 'warning' => {
    return trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'warning';
  };

  const exportData = useCallback((format: 'csv' | 'excel' | 'pdf') => {
    console.log(`Exporting data as ${format}`);
    // Implementation would generate and download file
  }, []);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'];

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              📊 Advanced Analytics Dashboard
            </Typography>
            <Box display="flex" gap={2}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => setFilterDialogOpen(true)}
              >
                Filters
              </Button>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => exportData('csv')}
              >
                Export
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => window.location.reload()}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">
              📈 Performance Overview: {dateRange.start} to {dateRange.end}
            </Typography>
            <Typography variant="body2">
              Analyzing {bettingAnalytics.total_bets} bets across {trackAnalysis.length} tracks with £{bettingAnalytics.total_stake.toLocaleString()} total stake.
            </Typography>
          </Alert>
        </CardContent>
      </Card>

      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)} 
        sx={{ mb: 3 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="📊 Overview" />
        <Tab label="📈 Performance Trends" />
        <Tab label="🏇 Track Analysis" />
        <Tab label="👨‍🦳 Jockey/Trainer" />
        <Tab label="📉 Market Efficiency" />
        <Tab label="🧮 Risk Analysis" />
        <Tab label="📋 Reports" />
      </Tabs>

      {/* Overview Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Key Performance Metrics */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Key Performance Indicators
            </Typography>
            <Grid container spacing={2}>
              {performanceMetrics.map((metric) => (
                <Grid item xs={12} sm={6} md={4} lg={2} key={metric.id}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Box display="flex" justifyContent="center" mb={1}>
                        {getMetricIcon(metric.category)}
                      </Box>
                      <Typography variant="h5" color="primary">
                        {metric.id === 'total_profit' ? `£${metric.value.toFixed(2)}` :
                         metric.id.includes('rate') || metric.id === 'roi' ? `${metric.value}%` :
                         metric.value.toFixed(metric.id === 'sharpe_ratio' ? 2 : 1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {metric.name}
                      </Typography>
                      <Chip
                        icon={metric.trend === 'up' ? <TrendingUp /> : 
                              metric.trend === 'down' ? <TrendingDown /> : <TrendingFlat />}
                        label={`${metric.change >= 0 ? '+' : ''}${metric.change_percentage.toFixed(1)}%`}
                        color={getMetricColor(metric.trend)}
                        size="small"
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>

          {/* Detailed Analytics Summary */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Betting Analytics Summary
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Total Bets
                    </Typography>
                    <Typography variant="h6">
                      {bettingAnalytics.total_bets}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Total Stake
                    </Typography>
                    <Typography variant="h6">
                      £{bettingAnalytics.total_stake.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Total Returns
                    </Typography>
                    <Typography variant="h6">
                      £{bettingAnalytics.total_returns.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Net Profit
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      £{bettingAnalytics.net_profit.toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Win Rate
                    </Typography>
                    <Typography variant="h6">
                      {bettingAnalytics.win_rate}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Place Rate
                    </Typography>
                    <Typography variant="h6">
                      {bettingAnalytics.place_rate}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Average Odds
                    </Typography>
                    <Typography variant="h6">
                      {bettingAnalytics.avg_odds.toFixed(2)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Profit Factor
                    </Typography>
                    <Typography variant="h6">
                      {bettingAnalytics.profit_factor.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Insights */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📝 Quick Insights
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <TrendingUp color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Strong Performance"
                      secondary="ROI up 26.8% vs last period"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Star color="primary" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Best Track: York"
                      secondary="42.9% win rate, 31.2% ROI"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <EmojiEvents color="warning" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Top Jockey: Frankie Dettori"
                      secondary="42.9% win rate across 15 races"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Assessment color="info" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Risk Management"
                      secondary="Sharpe ratio improved to 1.85"
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Performance Trends Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cumulative Profit & Performance Trends
                </Typography>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={historicalData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip />
                      <Legend />
                      <Area
                        yAxisId="left"
                        type="monotone"
                        dataKey="cumulative_profit"
                        fill="#8884d8"
                        stroke="#8884d8"
                        name="Cumulative Profit (£)"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="win_rate"
                        stroke="#82ca9d"
                        name="Win Rate (%)"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="roi"
                        stroke="#ffc658"
                        name="ROI (%)"
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Daily Performance Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsBarChart data={historicalData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="daily_profit" fill="#8884d8" name="Daily Profit (£)" />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk-Return Analysis
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart data={historicalData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="roi" name="ROI %" />
                      <YAxis dataKey="drawdown" name="Drawdown %" />
                      <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                      <Scatter name="Risk-Return" data={historicalData} fill="#8884d8" />
                    </ScatterChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Track Analysis Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Track Performance Analysis
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Track</TableCell>
                        <TableCell align="right">Races</TableCell>
                        <TableCell align="right">Bets</TableCell>
                        <TableCell align="right">Win Rate</TableCell>
                        <TableCell align="right">ROI</TableCell>
                        <TableCell align="right">Profit</TableCell>
                        <TableCell align="right">Avg Odds</TableCell>
                        <TableCell align="right">Confidence</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trackAnalysis
                        .sort((a, b) => b.roi - a.roi)
                        .map((track) => (
                        <TableRow key={track.track_name}>
                          <TableCell component="th" scope="row">
                            <Box display="flex" alignItems="center" gap={1}>
                              {track.roi > 20 ? <TrendingUp color="success" /> : 
                               track.roi > 10 ? <TrendingFlat color="warning" /> : 
                               <TrendingDown color="error" />}
                              {track.track_name}
                            </Box>
                          </TableCell>
                          <TableCell align="right">{track.races_count}</TableCell>
                          <TableCell align="right">{track.bets_count}</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${track.win_rate}%`}
                              color={track.win_rate > 35 ? 'success' : track.win_rate > 25 ? 'warning' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography color={track.roi > 15 ? 'success.main' : track.roi > 5 ? 'warning.main' : 'error.main'}>
                              {track.roi}%
                            </Typography>
                          </TableCell>
                          <TableCell align="right">£{track.profit.toFixed(2)}</TableCell>
                          <TableCell align="right">{track.avg_odds.toFixed(2)}</TableCell>
                          <TableCell align="right">
                            <Box display="flex" alignItems="center" gap={1}>
                              <LinearProgress
                                variant="determinate"
                                value={track.confidence * 100}
                                sx={{ width: 60, height: 8 }}
                                color={track.confidence > 0.85 ? 'success' : track.confidence > 0.75 ? 'warning' : 'error'}
                              />
                              <Typography variant="caption">
                                {(track.confidence * 100).toFixed(0)}%
                              </Typography>
                            </Box>
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
                <Typography variant="h6" gutterBottom>
                  Track ROI Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsBarChart data={trackAnalysis}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="track_name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="roi" fill="#8884d8" name="ROI %" />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Track Profitability Breakdown
                </Typography>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={trackAnalysis}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry: any) => `${entry.track_name}: £${entry.profit.toFixed(0)}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="profit"
                      >
                        {trackAnalysis.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filter Dialog */}
      <Dialog open={filterDialogOpen} onClose={() => setFilterDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Analytics Filters
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Date Range
              </Typography>
              <Box display="flex" gap={2}>
                <TextField
                  label="Start Date"
                  type="date"
                  value={dateRange.start}
                  onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                />
                <TextField
                  label="End Date"
                  type="date"
                  value={dateRange.end}
                  onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tracks</InputLabel>
                <Select
                  multiple
                  value={selectedTracks}
                  onChange={(e) => setSelectedTracks(e.target.value as string[])}
                  renderValue={(selected) => selected.join(', ')}
                >
                  {trackAnalysis.map((track) => (
                    <MenuItem key={track.track_name} value={track.track_name}>
                      <Checkbox checked={selectedTracks.indexOf(track.track_name) > -1} />
                      <ListItemText primary={track.track_name} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={comparisonMode}
                    onChange={(e) => setComparisonMode(e.target.checked)}
                  />
                }
                label="Enable comparison mode"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFilterDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => setFilterDialogOpen(false)} variant="contained">
            Apply Filters
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;
