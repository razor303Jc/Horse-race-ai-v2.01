import React, { useState, useMemo, useCallback, useEffect } from 'react';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  Avatar
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Assessment,
  Timeline,
  MonetizationOn,
  Warning,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  AccountBalance,
  PieChart,
  BarChart,
  Notifications,
  Settings,
  History,
  Download,
  Upload
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface BettingPortfolio {
  id: string;
  name: string;
  description: string;
  total_stakes: number;
  current_value: number;
  unrealized_pnl: number;
  realized_pnl: number;
  active_bets: number;
  win_rate: number;
  roi: number;
  max_drawdown: number;
  sharpe_ratio: number;
  created_date: string;
  last_activity: string;
  status: 'active' | 'paused' | 'archived';
  risk_level: 'conservative' | 'moderate' | 'aggressive';
  auto_staking: boolean;
  max_daily_stake: number;
  strategies: string[];
}

interface ActivePosition {
  id: string;
  portfolio_id: string;
  race_id: string;
  horse_name: string;
  bet_type: 'win' | 'place' | 'each_way' | 'lay';
  stake: number;
  odds: number;
  potential_return: number;
  current_odds: number;
  unrealized_pnl: number;
  confidence: number;
  time_to_race: string;
  market_status: 'open' | 'suspended' | 'closed';
  hedging_opportunities: number;
}

interface PortfolioAlert {
  id: string;
  portfolio_id: string;
  type: 'risk' | 'opportunity' | 'performance' | 'system';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  action_required: boolean;
  created_at: string;
  acknowledged: boolean;
}

export const BettingPortfolioManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>('all');
  const [portfolioDialogOpen, setPortfolioDialogOpen] = useState(false);
  const [editingPortfolio, setEditingPortfolio] = useState<BettingPortfolio | null>(null);
  const [alertsDialogOpen, setAlertsDialogOpen] = useState(false);

  // Portfolio creation/edit form state
  const [portfolioForm, setPortfolioForm] = useState({
    name: '',
    description: '',
    risk_level: 'moderate' as const,
    max_daily_stake: 100,
    auto_staking: false,
    strategies: [] as string[]
  });

  // Mock data - in real implementation, this would come from API
  const portfolios: BettingPortfolio[] = [
    {
      id: 'portfolio_1',
      name: 'Conservative Growth',
      description: 'Low-risk portfolio focusing on each-way and place betting',
      total_stakes: 5240.50,
      current_value: 5687.25,
      unrealized_pnl: 284.50,
      realized_pnl: 162.25,
      active_bets: 12,
      win_rate: 67.8,
      roi: 8.5,
      max_drawdown: 3.2,
      sharpe_ratio: 1.85,
      created_date: '2024-01-01',
      last_activity: '2024-01-15T10:30:00Z',
      status: 'active',
      risk_level: 'conservative',
      auto_staking: true,
      max_daily_stake: 150,
      strategies: ['Each-Way Arbing', 'Place Only Systems']
    },
    {
      id: 'portfolio_2',
      name: 'Value Hunter',
      description: 'Medium-risk value betting with Kelly Criterion staking',
      total_stakes: 8950.75,
      current_value: 10245.50,
      unrealized_pnl: 567.25,
      realized_pnl: 727.50,
      active_bets: 18,
      win_rate: 42.3,
      roi: 14.5,
      max_drawdown: 12.8,
      sharpe_ratio: 1.35,
      created_date: '2023-12-15',
      last_activity: '2024-01-15T11:15:00Z',
      status: 'active',
      risk_level: 'moderate',
      auto_staking: true,
      max_daily_stake: 300,
      strategies: ['Kelly Criterion Value Betting', 'Distance Specialization']
    },
    {
      id: 'portfolio_3',
      name: 'High Stakes Pro',
      description: 'Aggressive portfolio for experienced traders',
      total_stakes: 15680.00,
      current_value: 14950.25,
      unrealized_pnl: -125.75,
      realized_pnl: -604.00,
      active_bets: 8,
      win_rate: 38.9,
      roi: -4.7,
      max_drawdown: 22.5,
      sharpe_ratio: 0.45,
      created_date: '2023-11-01',
      last_activity: '2024-01-15T09:45:00Z',
      status: 'paused',
      risk_level: 'aggressive',
      auto_staking: false,
      max_daily_stake: 500,
      strategies: ['Lay the Favourite', 'Arbitrage Opportunities']
    }
  ];

  const activePositions: ActivePosition[] = [
    {
      id: 'pos_1',
      portfolio_id: 'portfolio_1',
      race_id: 'race_001',
      horse_name: 'Thunder Bay',
      bet_type: 'each_way',
      stake: 25.00,
      odds: 4.5,
      potential_return: 112.50,
      current_odds: 4.2,
      unrealized_pnl: -7.50,
      confidence: 0.72,
      time_to_race: '2h 15m',
      market_status: 'open',
      hedging_opportunities: 2
    },
    {
      id: 'pos_2',
      portfolio_id: 'portfolio_2',
      race_id: 'race_002',
      horse_name: 'Lightning Strike',
      bet_type: 'win',
      stake: 50.00,
      odds: 3.25,
      potential_return: 162.50,
      current_odds: 2.8,
      unrealized_pnl: -16.25,
      confidence: 0.68,
      time_to_race: '45m',
      market_status: 'open',
      hedging_opportunities: 1
    },
    {
      id: 'pos_3',
      portfolio_id: 'portfolio_1',
      race_id: 'race_003',
      horse_name: 'Royal Ascent',
      bet_type: 'place',
      stake: 30.00,
      odds: 2.1,
      potential_return: 63.00,
      current_odds: 1.95,
      unrealized_pnl: -4.50,
      confidence: 0.85,
      time_to_race: '1h 30m',
      market_status: 'open',
      hedging_opportunities: 0
    }
  ];

  const portfolioAlerts: PortfolioAlert[] = [
    {
      id: 'alert_1',
      portfolio_id: 'portfolio_3',
      type: 'risk',
      severity: 'high',
      title: 'High Drawdown Alert',
      message: 'Portfolio has exceeded 20% drawdown threshold. Consider reducing position sizes.',
      action_required: true,
      created_at: '2024-01-15T10:00:00Z',
      acknowledged: false
    },
    {
      id: 'alert_2',
      portfolio_id: 'portfolio_2',
      type: 'opportunity',
      severity: 'medium',
      title: 'Arbitrage Opportunity',
      message: 'New arbitrage opportunity detected in Race 004 with 3.2% guaranteed profit.',
      action_required: false,
      created_at: '2024-01-15T10:30:00Z',
      acknowledged: false
    },
    {
      id: 'alert_3',
      portfolio_id: 'portfolio_1',
      type: 'performance',
      severity: 'low',
      title: 'Performance Milestone',
      message: 'Portfolio has achieved 10% ROI target for the month.',
      action_required: false,
      created_at: '2024-01-15T09:15:00Z',
      acknowledged: true
    }
  ];

  // Filter portfolios based on selection
  const filteredPortfolios = useMemo(() => {
    if (selectedPortfolio === 'all') return portfolios;
    return portfolios.filter(p => p.id === selectedPortfolio);
  }, [selectedPortfolio, portfolios]);

  // Calculate aggregate metrics
  const aggregateMetrics = useMemo(() => {
    const totalValue = portfolios.reduce((sum, p) => sum + p.current_value, 0);
    const totalStakes = portfolios.reduce((sum, p) => sum + p.total_stakes, 0);
    const totalUnrealizedPnL = portfolios.reduce((sum, p) => sum + p.unrealized_pnl, 0);
    const totalRealizedPnL = portfolios.reduce((sum, p) => sum + p.realized_pnl, 0);
    const totalActiveBets = portfolios.reduce((sum, p) => sum + p.active_bets, 0);
    const avgROI = portfolios.reduce((sum, p) => sum + p.roi, 0) / portfolios.length;

    return {
      totalValue,
      totalStakes,
      totalUnrealizedPnL,
      totalRealizedPnL,
      totalActiveBets,
      avgROI,
      totalPnL: totalUnrealizedPnL + totalRealizedPnL
    };
  }, [portfolios]);

  // Portfolio performance chart data
  const performanceData = useMemo(() => {
    // Mock historical data
    return Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      value: aggregateMetrics.totalValue + (Math.random() - 0.5) * 1000 * (i / 30),
      pnl: aggregateMetrics.totalPnL + (Math.random() - 0.5) * 500 * (i / 30)
    }));
  }, [aggregateMetrics]);

  const unacknowledgedAlerts = useMemo(() => {
    return portfolioAlerts.filter(alert => !alert.acknowledged);
  }, [portfolioAlerts]);

  const getRiskColor = (risk: string): 'success' | 'warning' | 'error' => {
    switch (risk) {
      case 'conservative': return 'success';
      case 'moderate': return 'warning';
      case 'aggressive': return 'error';
      default: return 'warning';
    }
  };

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'archived': return 'error';
      default: return 'warning';
    }
  };

  const getSeverityColor = (severity: string): 'success' | 'warning' | 'error' => {
    switch (severity) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': case 'critical': return 'error';
      default: return 'warning';
    }
  };

  const handleCreatePortfolio = useCallback(() => {
    setEditingPortfolio(null);
    setPortfolioForm({
      name: '',
      description: '',
      risk_level: 'moderate',
      max_daily_stake: 100,
      auto_staking: false,
      strategies: []
    });
    setPortfolioDialogOpen(true);
  }, []);

  const handleEditPortfolio = useCallback((portfolio: BettingPortfolio) => {
    setEditingPortfolio(portfolio);
    setPortfolioForm({
      name: portfolio.name,
      description: portfolio.description,
      risk_level: portfolio.risk_level,
      max_daily_stake: portfolio.max_daily_stake,
      auto_staking: portfolio.auto_staking,
      strategies: portfolio.strategies
    });
    setPortfolioDialogOpen(true);
  }, []);

  const handleSavePortfolio = useCallback(() => {
    // Here you would save the portfolio to the API
    console.log('Saving portfolio:', portfolioForm);
    setPortfolioDialogOpen(false);
  }, [portfolioForm]);

  const acknowledgeAlert = useCallback((alertId: string) => {
    // Here you would acknowledge the alert via API
    console.log('Acknowledging alert:', alertId);
  }, []);

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" component="h2">
            💼 Betting Portfolio Manager
          </Typography>
          <Box>
            <IconButton onClick={() => setAlertsDialogOpen(true)}>
              <Badge badgeContent={unacknowledgedAlerts.length} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            <Button
              startIcon={<AddIcon />}
              onClick={handleCreatePortfolio}
              variant="contained"
              size="small"
              sx={{ ml: 1 }}
            >
              New Portfolio
            </Button>
          </Box>
        </Box>

        {/* Overview Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="h6" color="primary">
                  £{aggregateMetrics.totalValue.toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Portfolio Value
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography 
                  variant="h6" 
                  color={aggregateMetrics.totalPnL >= 0 ? 'success.main' : 'error.main'}
                >
                  £{aggregateMetrics.totalPnL.toFixed(2)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total P&L
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography 
                  variant="h6" 
                  color={aggregateMetrics.avgROI >= 0 ? 'success.main' : 'error.main'}
                >
                  {aggregateMetrics.avgROI.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Average ROI
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="h6" color="primary">
                  {aggregateMetrics.totalActiveBets}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Active Positions
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="h6" color="primary">
                  {portfolios.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Active Portfolios
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card variant="outlined">
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Typography 
                  variant="h6" 
                  color={unacknowledgedAlerts.length > 0 ? 'error.main' : 'success.main'}
                >
                  {unacknowledgedAlerts.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Pending Alerts
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
          <Tab label="Portfolio Overview" />
          <Tab label="Active Positions" />
          <Tab label="Performance Analytics" />
          <Tab label="Risk Management" />
        </Tabs>

        {/* Portfolio Overview Tab */}
        {activeTab === 0 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Portfolio Performance Summary
                    </Typography>
                    
                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Portfolio</TableCell>
                            <TableCell align="right">Value</TableCell>
                            <TableCell align="right">P&L</TableCell>
                            <TableCell align="right">ROI</TableCell>
                            <TableCell align="right">Active Bets</TableCell>
                            <TableCell align="right">Win Rate</TableCell>
                            <TableCell align="center">Risk</TableCell>
                            <TableCell align="center">Status</TableCell>
                            <TableCell align="center">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {portfolios.map((portfolio) => (
                            <TableRow key={portfolio.id}>
                              <TableCell>
                                <Box>
                                  <Typography variant="subtitle2">
                                    {portfolio.name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {portfolio.description}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell align="right">
                                £{portfolio.current_value.toFixed(2)}
                              </TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={(portfolio.unrealized_pnl + portfolio.realized_pnl) >= 0 ? 'success.main' : 'error.main'}
                                  fontWeight="bold"
                                >
                                  £{(portfolio.unrealized_pnl + portfolio.realized_pnl).toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={portfolio.roi >= 0 ? 'success.main' : 'error.main'}
                                  fontWeight="bold"
                                >
                                  {portfolio.roi.toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">{portfolio.active_bets}</TableCell>
                              <TableCell align="right">{portfolio.win_rate.toFixed(1)}%</TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={portfolio.risk_level}
                                  color={getRiskColor(portfolio.risk_level)}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Chip
                                  label={portfolio.status}
                                  color={getStatusColor(portfolio.status)}
                                  size="small"
                                  icon={portfolio.status === 'active' ? <PlayIcon /> : 
                                        portfolio.status === 'paused' ? <PauseIcon /> : <StopIcon />}
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Tooltip title="Edit Portfolio">
                                  <IconButton 
                                    size="small" 
                                    onClick={() => handleEditPortfolio(portfolio)}
                                  >
                                    <EditIcon />
                                  </IconButton>
                                </Tooltip>
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
          </Box>
        )}

        {/* Active Positions Tab */}
        {activeTab === 1 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🎯 Active Betting Positions
                    </Typography>
                    
                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Position</TableCell>
                            <TableCell align="right">Stake</TableCell>
                            <TableCell align="right">Odds</TableCell>
                            <TableCell align="right">Current</TableCell>
                            <TableCell align="right">P&L</TableCell>
                            <TableCell align="right">Confidence</TableCell>
                            <TableCell align="center">Time</TableCell>
                            <TableCell align="center">Hedge</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {activePositions.map((position) => (
                            <TableRow key={position.id}>
                              <TableCell>
                                <Box>
                                  <Typography variant="subtitle2">
                                    {position.horse_name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {position.bet_type.toUpperCase()} • {position.race_id}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell align="right">£{position.stake.toFixed(2)}</TableCell>
                              <TableCell align="right">{position.odds.toFixed(2)}</TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={position.current_odds > position.odds ? 'success.main' : 'error.main'}
                                >
                                  {position.current_odds.toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={position.unrealized_pnl >= 0 ? 'success.main' : 'error.main'}
                                  fontWeight="bold"
                                >
                                  £{position.unrealized_pnl.toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <LinearProgress
                                  variant="determinate"
                                  value={position.confidence * 100}
                                  color={position.confidence > 0.8 ? 'success' : 
                                         position.confidence > 0.6 ? 'warning' : 'error'}
                                  sx={{ width: 60 }}
                                />
                              </TableCell>
                              <TableCell align="center">
                                <Typography variant="body2">
                                  {position.time_to_race}
                                </Typography>
                              </TableCell>
                              <TableCell align="center">
                                {position.hedging_opportunities > 0 ? (
                                  <Badge badgeContent={position.hedging_opportunities} color="success">
                                    <MonetizationOn color="success" />
                                  </Badge>
                                ) : (
                                  <MonetizationOn color="disabled" />
                                )}
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
          </Box>
        )}

        {/* Performance Analytics Tab */}
        {activeTab === 2 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📈 Portfolio Performance Trends
                    </Typography>
                    <ResponsiveContainer width="100%" height={400}>
                      <AreaChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <RechartsTooltip />
                        <Area 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#8884d8" 
                          fill="#8884d8" 
                          fillOpacity={0.6}
                          name="Portfolio Value"
                        />
                        <Area 
                          type="monotone" 
                          dataKey="pnl" 
                          stroke="#82ca9d" 
                          fill="#82ca9d" 
                          fillOpacity={0.6}
                          name="P&L"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Risk Management Tab */}
        {activeTab === 3 && (
          <Box>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="h6">⚠️ Portfolio Risk Overview</Typography>
              <Typography>
                Monitor risk metrics and receive alerts for potential issues across all portfolios.
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              {portfolios.map((portfolio) => (
                <Grid item xs={12} md={6} key={portfolio.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                          {portfolio.name}
                        </Typography>
                        <Chip
                          label={portfolio.risk_level}
                          color={getRiskColor(portfolio.risk_level)}
                          size="small"
                        />
                      </Box>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Max Drawdown
                          </Typography>
                          <Typography variant="h6">
                            {portfolio.max_drawdown.toFixed(1)}%
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Sharpe Ratio
                          </Typography>
                          <Typography variant="h6">
                            {portfolio.sharpe_ratio.toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Daily Limit
                          </Typography>
                          <Typography variant="h6">
                            £{portfolio.max_daily_stake}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Auto Staking
                          </Typography>
                          <Typography variant="h6">
                            {portfolio.auto_staking ? '✅' : '❌'}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </CardContent>

      {/* Portfolio Creation/Edit Dialog */}
      <Dialog 
        open={portfolioDialogOpen} 
        onClose={() => setPortfolioDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingPortfolio ? 'Edit Portfolio' : 'Create New Portfolio'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Portfolio Name"
                value={portfolioForm.name}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, name: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={portfolioForm.description}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  value={portfolioForm.risk_level}
                  label="Risk Level"
                  onChange={(e) => setPortfolioForm(prev => ({ ...prev, risk_level: e.target.value as any }))}
                >
                  <MenuItem value="conservative">Conservative</MenuItem>
                  <MenuItem value="moderate">Moderate</MenuItem>
                  <MenuItem value="aggressive">Aggressive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Max Daily Stake"
                type="number"
                value={portfolioForm.max_daily_stake}
                onChange={(e) => setPortfolioForm(prev => ({ ...prev, max_daily_stake: parseFloat(e.target.value) || 0 }))}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={portfolioForm.auto_staking}
                    onChange={(e) => setPortfolioForm(prev => ({ ...prev, auto_staking: e.target.checked }))}
                  />
                }
                label="Enable Automatic Staking"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPortfolioDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSavePortfolio} variant="contained">
            {editingPortfolio ? 'Update' : 'Create'} Portfolio
          </Button>
        </DialogActions>
      </Dialog>

      {/* Alerts Dialog */}
      <Dialog 
        open={alertsDialogOpen} 
        onClose={() => setAlertsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Portfolio Alerts & Notifications
        </DialogTitle>
        <DialogContent>
          <List>
            {portfolioAlerts.map((alert) => (
              <Box key={alert.id}>
                <ListItem>
                  <ListItemIcon>
                    <Avatar 
                      sx={{ 
                        bgcolor: getSeverityColor(alert.severity) === 'error' ? 'error.main' :
                                getSeverityColor(alert.severity) === 'warning' ? 'warning.main' : 'success.main',
                        width: 32, 
                        height: 32 
                      }}
                    >
                      {alert.type === 'risk' ? <Warning /> :
                       alert.type === 'opportunity' ? <TrendingUp /> :
                       alert.type === 'performance' ? <Assessment /> : <Settings />}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="subtitle1">{alert.title}</Typography>
                        <Chip
                          label={alert.severity}
                          color={getSeverityColor(alert.severity)}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {alert.message}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(alert.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                  />
                  {!alert.acknowledged && (
                    <Button
                      size="small"
                      onClick={() => acknowledgeAlert(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  )}
                </ListItem>
                <Divider />
              </Box>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default BettingPortfolioManager;
