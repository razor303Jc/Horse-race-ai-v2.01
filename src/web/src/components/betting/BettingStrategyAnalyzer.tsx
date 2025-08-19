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
  Rating,
  Tooltip,
  IconButton
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
  Psychology,
  MonetizationOn,
  BarChart,
  ShowChart,
  PieChart,
  Download,
  Refresh
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart as RechartsBarChart, Bar, PieChart as RechartsPieChart, Pie, Cell } from 'recharts';

interface StrategyPerformance {
  strategy_name: string;
  total_bets: number;
  win_rate: number;
  roi: number;
  profit_loss: number;
  avg_odds: number;
  max_drawdown: number;
  sharpe_ratio: number;
  kelly_criterion_score: number;
  confidence_level: number;
  risk_rating: 'Low' | 'Medium' | 'High';
  recommended: boolean;
  last_updated: string;
}

interface BettingPattern {
  pattern_type: string;
  frequency: number;
  success_rate: number;
  avg_return: number;
  risk_level: number;
  description: string;
  recommendations: string[];
}

interface MarketAnalysis {
  market_type: string;
  total_volume: number;
  average_odds: number;
  volatility: number;
  efficiency_score: number;
  opportunities: number;
  trend: 'bullish' | 'bearish' | 'neutral';
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const BettingStrategyAnalyzer: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [analysisTimeframe, setAnalysisTimeframe] = useState('30days');
  const [selectedStrategy, setSelectedStrategy] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  // Mock data - in real implementation, this would come from API
  const strategyPerformance: StrategyPerformance[] = [
    {
      strategy_name: 'Kelly Criterion Value Betting',
      total_bets: 245,
      win_rate: 34.7,
      roi: 12.8,
      profit_loss: 1280.50,
      avg_odds: 3.45,
      max_drawdown: 8.2,
      sharpe_ratio: 1.45,
      kelly_criterion_score: 0.85,
      confidence_level: 4.2,
      risk_rating: 'Medium',
      recommended: true,
      last_updated: '2024-01-15T10:30:00Z'
    },
    {
      strategy_name: 'Lay the Favourite',
      total_bets: 189,
      win_rate: 67.2,
      roi: 8.4,
      profit_loss: 840.25,
      avg_odds: 1.95,
      max_drawdown: 12.5,
      sharpe_ratio: 0.92,
      kelly_criterion_score: 0.62,
      confidence_level: 3.8,
      risk_rating: 'High',
      recommended: false,
      last_updated: '2024-01-15T10:30:00Z'
    },
    {
      strategy_name: 'Each-Way Arbing',
      total_bets: 156,
      win_rate: 78.8,
      roi: 6.2,
      profit_loss: 620.75,
      avg_odds: 2.15,
      max_drawdown: 3.1,
      sharpe_ratio: 2.18,
      kelly_criterion_score: 0.45,
      confidence_level: 4.5,
      risk_rating: 'Low',
      recommended: true,
      last_updated: '2024-01-15T10:30:00Z'
    },
    {
      strategy_name: 'Place Only Systems',
      total_bets: 298,
      win_rate: 52.3,
      roi: 15.6,
      profit_loss: 1560.90,
      avg_odds: 2.85,
      max_drawdown: 6.8,
      sharpe_ratio: 1.73,
      kelly_criterion_score: 0.78,
      confidence_level: 4.1,
      risk_rating: 'Medium',
      recommended: true,
      last_updated: '2024-01-15T10:30:00Z'
    }
  ];

  const bettingPatterns: BettingPattern[] = [
    {
      pattern_type: 'Favorite Bias',
      frequency: 68,
      success_rate: 45.2,
      avg_return: -2.1,
      risk_level: 3,
      description: 'Tendency to bet on heavily favored horses',
      recommendations: [
        'Look for value in outsiders with strong form',
        'Consider each-way betting on longer odds',
        'Analyze favorite strike rates by distance'
      ]
    },
    {
      pattern_type: 'Distance Specialization',
      frequency: 134,
      success_rate: 58.7,
      avg_return: 8.4,
      risk_level: 2,
      description: 'Consistent success in specific distance ranges',
      recommendations: [
        'Focus on 6f-1m sprint races',
        'Avoid 2m+ staying races',
        'Increase stakes on specialized distances'
      ]
    },
    {
      pattern_type: 'Going Dependency',
      frequency: 89,
      success_rate: 62.1,
      avg_return: 11.2,
      risk_level: 1,
      description: 'Strong performance correlation with track conditions',
      recommendations: [
        'Heavy/Soft ground specialist backing',
        'Weather-based staking adjustments',
        'Track condition value identification'
      ]
    }
  ];

  const marketAnalysis: MarketAnalysis[] = [
    {
      market_type: 'Win Markets',
      total_volume: 2450000,
      average_odds: 4.25,
      volatility: 18.5,
      efficiency_score: 87.2,
      opportunities: 23,
      trend: 'neutral'
    },
    {
      market_type: 'Place Markets',
      total_volume: 1890000,
      average_odds: 2.15,
      volatility: 12.3,
      efficiency_score: 92.1,
      opportunities: 15,
      trend: 'bullish'
    },
    {
      market_type: 'Each-Way',
      total_volume: 1560000,
      average_odds: 3.45,
      volatility: 15.7,
      efficiency_score: 85.6,
      opportunities: 31,
      trend: 'bullish'
    }
  ];

  // Chart data preparation
  const performanceChartData = useMemo(() => {
    return strategyPerformance.map(strategy => ({
      name: strategy.strategy_name.split(' ')[0],
      ROI: strategy.roi,
      WinRate: strategy.win_rate,
      ProfitLoss: strategy.profit_loss / 100 // Scale for display
    }));
  }, [strategyPerformance]);

  const pieChartData = useMemo(() => {
    return strategyPerformance.map(strategy => ({
      name: strategy.strategy_name.split(' ')[0],
      value: strategy.total_bets,
      profit: strategy.profit_loss
    }));
  }, [strategyPerformance]);

  const getRiskColor = (risk: string): 'success' | 'warning' | 'error' => {
    switch (risk) {
      case 'Low': return 'success';
      case 'Medium': return 'warning';
      case 'High': return 'error';
      default: return 'warning';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'bullish': return <TrendingUp color="success" />;
      case 'bearish': return <TrendingDown color="error" />;
      default: return <Timeline color="action" />;
    }
  };

  const refreshAnalysis = useCallback(async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsLoading(false);
  }, []);

  const exportReport = useCallback(() => {
    // Generate and download strategy analysis report
    const reportData = {
      timestamp: new Date().toISOString(),
      timeframe: analysisTimeframe,
      strategies: strategyPerformance,
      patterns: bettingPatterns,
      markets: marketAnalysis
    };
    
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `betting-strategy-analysis-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [analysisTimeframe, strategyPerformance, bettingPatterns, marketAnalysis]);

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5" component="h2">
            📊 Advanced Strategy Analytics
          </Typography>
          <Box>
            <IconButton onClick={refreshAnalysis} disabled={isLoading}>
              <Refresh />
            </IconButton>
            <Button
              startIcon={<Download />}
              onClick={exportReport}
              variant="outlined"
              size="small"
            >
              Export Report
            </Button>
          </Box>
        </Box>

        {isLoading && <LinearProgress sx={{ mb: 2 }} />}
        
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Analysis Timeframe</InputLabel>
              <Select
                value={analysisTimeframe}
                label="Analysis Timeframe"
                onChange={(e) => setAnalysisTimeframe(e.target.value)}
              >
                <MenuItem value="7days">Last 7 Days</MenuItem>
                <MenuItem value="30days">Last 30 Days</MenuItem>
                <MenuItem value="90days">Last 90 Days</MenuItem>
                <MenuItem value="1year">Last Year</MenuItem>
                <MenuItem value="all">All Time</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Strategy Filter</InputLabel>
              <Select
                value={selectedStrategy}
                label="Strategy Filter"
                onChange={(e) => setSelectedStrategy(e.target.value)}
              >
                <MenuItem value="all">All Strategies</MenuItem>
                <MenuItem value="recommended">Recommended Only</MenuItem>
                <MenuItem value="profitable">Profitable Only</MenuItem>
                <MenuItem value="high-volume">High Volume</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
          <Tab label="Strategy Performance" />
          <Tab label="Betting Patterns" />
          <Tab label="Market Analysis" />
          <Tab label="Risk Assessment" />
        </Tabs>

        {/* Strategy Performance Tab */}
        {activeTab === 0 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📈 Strategy Performance Overview
                    </Typography>
                    
                    <TableContainer component={Paper} variant="outlined">
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Strategy</TableCell>
                            <TableCell align="right">Bets</TableCell>
                            <TableCell align="right">Win Rate</TableCell>
                            <TableCell align="right">ROI</TableCell>
                            <TableCell align="right">P&L</TableCell>
                            <TableCell align="right">Risk</TableCell>
                            <TableCell align="right">Rating</TableCell>
                            <TableCell align="center">Status</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {strategyPerformance.map((strategy, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                <Box>
                                  <Typography variant="subtitle2">
                                    {strategy.strategy_name}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    Avg Odds: {strategy.avg_odds.toFixed(2)}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell align="right">{strategy.total_bets}</TableCell>
                              <TableCell align="right">{strategy.win_rate.toFixed(1)}%</TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={strategy.roi >= 0 ? 'success.main' : 'error.main'}
                                  fontWeight="bold"
                                >
                                  {strategy.roi.toFixed(1)}%
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Typography 
                                  color={strategy.profit_loss >= 0 ? 'success.main' : 'error.main'}
                                  fontWeight="bold"
                                >
                                  £{strategy.profit_loss.toFixed(2)}
                                </Typography>
                              </TableCell>
                              <TableCell align="right">
                                <Chip
                                  label={strategy.risk_rating}
                                  color={getRiskColor(strategy.risk_rating)}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell align="right">
                                <Rating
                                  value={strategy.confidence_level}
                                  max={5}
                                  size="small"
                                  readOnly
                                />
                              </TableCell>
                              <TableCell align="center">
                                {strategy.recommended ? (
                                  <CheckCircle color="success" />
                                ) : (
                                  <Warning color="warning" />
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
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Performance Comparison
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsBarChart data={performanceChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <RechartsTooltip />
                        <Bar dataKey="ROI" fill="#8884d8" name="ROI %" />
                        <Bar dataKey="WinRate" fill="#82ca9d" name="Win Rate %" />
                      </RechartsBarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🥧 Betting Volume Distribution
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <RechartsPieChart>
                        <Pie
                          dataKey="value"
                          data={pieChartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => `${entry.name}: ${entry.value}`}
                          outerRadius={80}
                          fill="#8884d8"
                        >
                          {pieChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Betting Patterns Tab */}
        {activeTab === 1 && (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="h6">🧠 Behavioral Pattern Analysis</Typography>
              <Typography>
                Identify and optimize your betting behavior patterns for improved performance.
              </Typography>
            </Alert>
            
            {bettingPatterns.map((pattern, index) => (
              <Accordion key={index} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Grid container alignItems="center" spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="h6">{pattern.pattern_type}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={2}>
                      <Typography variant="body2" color="text.secondary">
                        Frequency: {pattern.frequency}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={2}>
                      <Typography variant="body2" color="text.secondary">
                        Success: {pattern.success_rate.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={2}>
                      <Typography 
                        variant="body2"
                        color={pattern.avg_return >= 0 ? 'success.main' : 'error.main'}
                      >
                        Return: {pattern.avg_return.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} sm={2}>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2" sx={{ mr: 1 }}>Risk:</Typography>
                        <Box display="flex">
                          {[...Array(5)].map((_, i) => (
                            <Box
                              key={i}
                              sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                backgroundColor: i < pattern.risk_level ? 
                                  (pattern.risk_level <= 2 ? 'success.main' : 
                                   pattern.risk_level <= 3 ? 'warning.main' : 'error.main') : 
                                  'grey.300',
                                mr: 0.5
                              }}
                            />
                          ))}
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Pattern Description
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {pattern.description}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        Optimization Recommendations
                      </Typography>
                      <List dense>
                        {pattern.recommendations.map((rec, recIndex) => (
                          <ListItem key={recIndex} disablePadding>
                            <ListItemIcon>
                              <CheckCircle color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={rec}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}

        {/* Market Analysis Tab */}
        {activeTab === 2 && (
          <Box>
            <Grid container spacing={3}>
              {marketAnalysis.map((market, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">
                          {market.market_type}
                        </Typography>
                        {getTrendIcon(market.trend)}
                      </Box>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Volume
                          </Typography>
                          <Typography variant="h6">
                            £{(market.total_volume / 1000000).toFixed(1)}M
                          </Typography>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Avg Odds
                          </Typography>
                          <Typography variant="h6">
                            {market.average_odds.toFixed(2)}
                          </Typography>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Volatility
                          </Typography>
                          <Typography variant="h6">
                            {market.volatility.toFixed(1)}%
                          </Typography>
                        </Grid>
                        
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Efficiency
                          </Typography>
                          <Typography variant="h6">
                            {market.efficiency_score.toFixed(1)}%
                          </Typography>
                        </Grid>
                        
                        <Grid item xs={12}>
                          <Divider sx={{ my: 1 }} />
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="body2" color="text.secondary">
                              Opportunities
                            </Typography>
                            <Chip
                              label={market.opportunities}
                              color={market.opportunities > 20 ? 'success' : 
                                     market.opportunities > 10 ? 'warning' : 'error'}
                              size="small"
                            />
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Risk Assessment Tab */}
        {activeTab === 3 && (
          <Box>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="h6">⚠️ Risk Management Overview</Typography>
              <Typography>
                Monitor and manage your betting risks across all strategies and markets.
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Risk Metrics Summary
                    </Typography>
                    
                    {strategyPerformance.map((strategy, index) => (
                      <Box key={index} sx={{ mb: 3 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="subtitle2">
                            {strategy.strategy_name}
                          </Typography>
                          <Chip
                            label={strategy.risk_rating}
                            color={getRiskColor(strategy.risk_rating)}
                            size="small"
                          />
                        </Box>
                        
                        <Grid container spacing={2}>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">
                              Max Drawdown
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {strategy.max_drawdown.toFixed(1)}%
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">
                              Sharpe Ratio
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {strategy.sharpe_ratio.toFixed(2)}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">
                              Kelly Score
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {strategy.kelly_criterion_score.toFixed(2)}
                            </Typography>
                          </Grid>
                        </Grid>
                        
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="text.secondary">
                            Risk-Adjusted Performance
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={strategy.sharpe_ratio * 20} // Scale for display
                            color={strategy.sharpe_ratio > 1 ? 'success' : 
                                   strategy.sharpe_ratio > 0.5 ? 'warning' : 'error'}
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                        
                        {index < strategyPerformance.length - 1 && <Divider sx={{ mt: 2 }} />}
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🎯 Risk Recommendations
                    </Typography>
                    
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <Warning color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Reduce Exposure to Lay Betting"
                          secondary="High drawdown risk detected in laying strategies"
                        />
                      </ListItem>
                      
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircle color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Increase Each-Way Allocation"
                          secondary="Low risk, consistent returns with good Sharpe ratio"
                        />
                      </ListItem>
                      
                      <ListItem>
                        <ListItemIcon>
                          <Info color="info" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Monitor Kelly Criterion Adherence"
                          secondary="Some strategies exceeding optimal stake sizes"
                        />
                      </ListItem>
                      
                      <ListItem>
                        <ListItemIcon>
                          <TrendingUp color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Diversify Across Time Frames"
                          secondary="Consider adding longer-term position strategies"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default BettingStrategyAnalyzer;
