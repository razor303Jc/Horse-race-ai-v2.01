import {
    Assessment,
    AttachMoney,
    Dashboard as DashboardIcon,
    Psychology,
    Refresh,
    Speed,
    Sports,
    TrendingUp
} from '@mui/icons-material'
import {
    Alert,
    AppBar,
    Box,
    Card,
    CardContent,
    Chip,
    Container,
    Grid,
    IconButton,
    LinearProgress,
    Paper,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    Toolbar,
    Typography,
} from '@mui/material'
import axios from 'axios'
import { useEffect, useState } from 'react'
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts'
import { DailyRaces } from './DailyRaces'

interface SystemStatus {
  overall_status: string
  timestamp: string
  ml_models: string
  betting_integration: string
  contextual_ai: string
  notifications: string
  performance_tracker: string
}

interface DashboardData {
  ml_models: {
    ensemble_auc: number
    models_active: number
    status: string
    predictions_today: number
    features_per_horse: number
    training_records: number
    model_accuracy: {
      gradient_boost: number
      neural_network: number
      random_forest: number
      svm: number
    }
    feature_importance: Array<{
      name: string
      importance: number
    }>
  }
  betting_performance: {
    total_pnl: number
    win_rate: number
    roi: number
    trades_today: number
    weekly_performance: Array<{
      day: string
      pnl: number
    }>
    bet_types: {
      win: { count: number; success_rate: number; avg_odds: number }
      place: { count: number; success_rate: number; avg_odds: number }
      each_way: { count: number; success_rate: number; avg_odds: number }
    }
    risk_metrics: {
      max_drawdown: number
      sharpe_ratio: number
      kelly_criterion: number
    }
  }
  contextual_ai: {
    processing_threads: number
    last_insight: string
    confidence_level: number
    insights_generated: number
    sentiment_analysis: {
      market_sentiment: string
      social_buzz: string
      expert_consensus: number
    }
    recent_insights: Array<{
      timestamp: string
      insight: string
      confidence: number
      races_affected: string[]
    }>
  }
  live_predictions: Array<{
    horse: string
    race: string
    probability: number
    confidence: number
    value_rating: number
    status: string
    odds?: number
    suggested_stake?: number
    form_rating?: string
    jockey?: string
    trainer?: string
    result?: string
    profit?: number
  }>
  market_data: {
    active_races: number
    total_volume: number
    avg_odds_movement: number
    liquidity_index: number
    top_tracks: Array<{
      name: string
      races: number
      volume: number
    }>
  }
}

interface BettingOpportunities {
  opportunities: Array<{
    race: string
    horse: string
    bet_type: string
    bookmaker_odds: number
    fair_odds: number
    value_percentage: number
    confidence: number
    suggested_stake: number
    expected_value: number
  }>
  portfolio_stats: {
    total_opportunities: number
    avg_value: number
    recommended_total_stake: number
    potential_profit: number
  }
}

function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [bettingOpportunities, setBettingOpportunities] = useState<BettingOpportunities | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [currentTab, setCurrentTab] = useState(0)

  const fetchData = async () => {
    try {
      const [statusResponse, dashboardResponse, bettingResponse] = await Promise.all([
        axios.get('/api/system_status'),
        axios.get('/api/dashboard_data'),
        axios.get('/api/betting_opportunities')
      ])
      
      setSystemStatus(statusResponse.data)
      setDashboardData(dashboardResponse.data)
      setBettingOpportunities(bettingResponse.data)
      setLastUpdate(new Date())
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch data:', error)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Update every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'operational':
      case 'excellent':
      case 'connected':
      case 'active':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'info'
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(value)
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography variant="h6" align="center" sx={{ mt: 2, color: 'white' }}>
          Loading Advanced Horse Racing AI Dashboard...
        </Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
      <AppBar position="static" sx={{ background: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <DashboardIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🐎 Horse Racing AI v2.0 - Advanced Analytics Dashboard
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            Last Update: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <IconButton color="inherit" onClick={fetchData}>
            <Refresh />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, pb: 4 }}>
        {/* System Status Overview */}
        <Paper sx={{ p: 3, mb: 4, background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
          <Typography variant="h5" gutterBottom sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
            <Speed /> System Status Overview
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`Overall: ${systemStatus?.overall_status || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.overall_status || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`ML Models: ${systemStatus?.ml_models || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.ml_models || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`Betting: ${systemStatus?.betting_integration || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.betting_integration || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`AI: ${systemStatus?.contextual_ai || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.contextual_ai || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`Notifications: ${systemStatus?.notifications || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.notifications || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Chip
                label={`Performance: ${systemStatus?.performance_tracker || 'UNKNOWN'}`}
                color={getStatusColor(systemStatus?.performance_tracker || '')}
                variant="outlined"
                sx={{ width: '100%' }}
              />
            </Grid>
          </Grid>
        </Paper>

        {/* Navigation Tabs */}
        <Paper sx={{ mb: 3, background: 'rgba(255, 255, 255, 0.05)' }}>
          <Tabs 
            value={currentTab} 
            onChange={(_, newValue) => setCurrentTab(newValue)}
            variant="fullWidth"
            sx={{ '& .MuiTab-root': { color: 'white' } }}
          >
            <Tab icon={<Assessment />} label="Overview" />
            <Tab icon={<TrendingUp />} label="ML Analytics" />
            <Tab icon={<AttachMoney />} label="Betting Performance" />
            <Tab icon={<Sports />} label="Live Predictions" />
            <Tab icon={<Psychology />} label="AI Insights" />
            <Tab icon={<DashboardIcon />} label="Daily Races" />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        {currentTab === 0 && (
          <Grid container spacing={3}>
            {/* Key Metrics Cards */}
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <TrendingUp /> Today's P&L
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {formatCurrency(dashboardData?.betting_performance.total_pnl || 0)}
                  </Typography>
                  <Typography variant="body2">
                    {dashboardData?.betting_performance.trades_today || 0} trades
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Assessment /> Win Rate
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {dashboardData?.betting_performance.win_rate || 0}%
                  </Typography>
                  <Typography variant="body2">
                    ROI: {dashboardData?.betting_performance.roi || 0}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Psychology /> ML Accuracy
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {dashboardData?.ml_models.ensemble_auc || 0}%
                  </Typography>
                  <Typography variant="body2">
                    {dashboardData?.ml_models.predictions_today || 0} predictions today
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Speed /> Active Races
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {dashboardData?.market_data.active_races || 0}
                  </Typography>
                  <Typography variant="body2">
                    {formatCurrency(dashboardData?.market_data.total_volume || 0)} volume
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Weekly Performance Chart */}
            <Grid item xs={12} md={8}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Weekly Performance Trend</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={dashboardData?.betting_performance.weekly_performance || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'P&L']} />
                    <Area type="monotone" dataKey="pnl" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>
            </Grid>

            {/* Bet Types Distribution */}
            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Bet Types Success Rate</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dashboardData?.betting_performance.bet_types ? [
                    { name: 'Win', rate: dashboardData.betting_performance.bet_types.win.success_rate },
                    { name: 'Place', rate: dashboardData.betting_performance.bet_types.place.success_rate },
                    { name: 'Each Way', rate: dashboardData.betting_performance.bet_types.each_way.success_rate },
                  ] : []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value}%`, 'Success Rate']} />
                    <Bar dataKey="rate" fill="#00C49F" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Grid>
          </Grid>
        )}

        {currentTab === 1 && (
          <Grid container spacing={3}>
            {/* ML Model Performance */}
            <Grid item xs={12} md={6}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Model Accuracy Comparison</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dashboardData?.ml_models.model_accuracy ? [
                    { name: 'Gradient Boost', accuracy: dashboardData.ml_models.model_accuracy.gradient_boost },
                    { name: 'Neural Network', accuracy: dashboardData.ml_models.model_accuracy.neural_network },
                    { name: 'Random Forest', accuracy: dashboardData.ml_models.model_accuracy.random_forest },
                    { name: 'SVM', accuracy: dashboardData.ml_models.model_accuracy.svm },
                  ] : []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
                    <Bar dataKey="accuracy" fill="#0088FE" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Grid>

            {/* Feature Importance */}
            <Grid item xs={12} md={6}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Feature Importance</Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={dashboardData?.ml_models.feature_importance || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, importance }) => `${name}: ${(importance * 100).toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="importance"
                    >
                      {dashboardData?.ml_models.feature_importance?.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Grid>

            {/* ML Stats */}
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>ML Model Statistics</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2">Active Models</Typography>
                    <Typography variant="h5">{dashboardData?.ml_models.models_active || 0}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2">Training Records</Typography>
                    <Typography variant="h5">{dashboardData?.ml_models.training_records?.toLocaleString() || 0}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2">Features per Horse</Typography>
                    <Typography variant="h5">{dashboardData?.ml_models.features_per_horse || 0}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="body2">Predictions Today</Typography>
                    <Typography variant="h5">{dashboardData?.ml_models.predictions_today || 0}</Typography>
                  </Grid>
                </Grid>
              </Card>
            </Grid>
          </Grid>
        )}

        {currentTab === 2 && (
          <Grid container spacing={3}>
            {/* Betting Opportunities */}
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>High-Value Betting Opportunities</Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: 'white' }}>Race</TableCell>
                        <TableCell sx={{ color: 'white' }}>Horse</TableCell>
                        <TableCell sx={{ color: 'white' }}>Bet Type</TableCell>
                        <TableCell sx={{ color: 'white' }}>Value %</TableCell>
                        <TableCell sx={{ color: 'white' }}>Confidence</TableCell>
                        <TableCell sx={{ color: 'white' }}>Suggested Stake</TableCell>
                        <TableCell sx={{ color: 'white' }}>Expected Value</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bettingOpportunities?.opportunities.map((opp, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ color: 'white' }}>{opp.race}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{opp.horse}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{opp.bet_type}</TableCell>
                          <TableCell sx={{ color: 'white' }}>
                            <Chip 
                              label={`${opp.value_percentage.toFixed(1)}%`}
                              color={opp.value_percentage > 25 ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell sx={{ color: 'white' }}>{opp.confidence}%</TableCell>
                          <TableCell sx={{ color: 'white' }}>{formatCurrency(opp.suggested_stake)}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{formatCurrency(opp.expected_value)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Card>
            </Grid>

            {/* Portfolio Stats */}
            <Grid item xs={12} md={6}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Portfolio Statistics</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2">Total Opportunities</Typography>
                    <Typography variant="h5">{bettingOpportunities?.portfolio_stats.total_opportunities || 0}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Average Value</Typography>
                    <Typography variant="h5">{bettingOpportunities?.portfolio_stats.avg_value.toFixed(1) || 0}%</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Recommended Stake</Typography>
                    <Typography variant="h5">{formatCurrency(bettingOpportunities?.portfolio_stats.recommended_total_stake || 0)}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2">Potential Profit</Typography>
                    <Typography variant="h5">{formatCurrency(bettingOpportunities?.portfolio_stats.potential_profit || 0)}</Typography>
                  </Grid>
                </Grid>
              </Card>
            </Grid>

            {/* Risk Metrics */}
            <Grid item xs={12} md={6}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Risk Metrics</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="body2">Max Drawdown</Typography>
                    <Typography variant="h6" color="error">{formatCurrency(dashboardData?.betting_performance.risk_metrics.max_drawdown || 0)}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">Sharpe Ratio</Typography>
                    <Typography variant="h6" color="success">{dashboardData?.betting_performance.risk_metrics.sharpe_ratio || 0}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="body2">Kelly Criterion</Typography>
                    <Typography variant="h6" color="info">{dashboardData?.betting_performance.risk_metrics.kelly_criterion || 0}</Typography>
                  </Grid>
                </Grid>
              </Card>
            </Grid>
          </Grid>
        )}

        {currentTab === 3 && (
          <Grid container spacing={3}>
            {/* Live Predictions Table */}
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Live Race Predictions</Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ color: 'white' }}>Horse</TableCell>
                        <TableCell sx={{ color: 'white' }}>Race</TableCell>
                        <TableCell sx={{ color: 'white' }}>Probability</TableCell>
                        <TableCell sx={{ color: 'white' }}>Confidence</TableCell>
                        <TableCell sx={{ color: 'white' }}>Value Rating</TableCell>
                        <TableCell sx={{ color: 'white' }}>Odds</TableCell>
                        <TableCell sx={{ color: 'white' }}>Jockey</TableCell>
                        <TableCell sx={{ color: 'white' }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData?.live_predictions.map((prediction, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ color: 'white' }}>{prediction.horse}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{prediction.race}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{prediction.probability.toFixed(1)}%</TableCell>
                          <TableCell sx={{ color: 'white' }}>{prediction.confidence}%</TableCell>
                          <TableCell sx={{ color: 'white' }}>
                            <Chip 
                              label={prediction.value_rating.toFixed(1)}
                              color={prediction.value_rating > 8 ? 'success' : prediction.value_rating > 6 ? 'warning' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell sx={{ color: 'white' }}>{prediction.odds?.toFixed(1) || 'N/A'}</TableCell>
                          <TableCell sx={{ color: 'white' }}>{prediction.jockey || 'N/A'}</TableCell>
                          <TableCell sx={{ color: 'white' }}>
                            <Chip 
                              label={prediction.status}
                              color={prediction.status === 'ACTIVE' ? 'success' : prediction.status === 'COMPLETED' ? 'info' : 'default'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Card>
            </Grid>
          </Grid>
        )}

        {currentTab === 4 && (
          <Grid container spacing={3}>
            {/* AI Insights Overview */}
            <Grid item xs={12} md={8}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Recent AI Insights</Typography>
                {dashboardData?.contextual_ai.recent_insights?.map((insight, index) => (
                  <Alert 
                    key={index}
                    severity="info" 
                    sx={{ mb: 2, backgroundColor: 'rgba(33, 150, 243, 0.1)' }}
                  >
                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                      {insight.insight}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Confidence: {insight.confidence}% | Races: {insight.races_affected.join(', ')}
                    </Typography>
                    <Typography variant="caption">
                      {new Date(insight.timestamp).toLocaleString()}
                    </Typography>
                  </Alert>
                ))}
              </Card>
            </Grid>

            {/* AI Statistics */}
            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>AI Performance</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="body2">Processing Threads</Typography>
                    <Typography variant="h5">{dashboardData?.contextual_ai.processing_threads || 0}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2">Confidence Level</Typography>
                    <Typography variant="h5">{dashboardData?.contextual_ai.confidence_level || 0}%</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2">Insights Generated</Typography>
                    <Typography variant="h5">{dashboardData?.contextual_ai.insights_generated || 0}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2">Expert Consensus</Typography>
                    <Typography variant="h5">{dashboardData?.contextual_ai.sentiment_analysis?.expert_consensus || 0}%</Typography>
                  </Grid>
                </Grid>
              </Card>
            </Grid>

            {/* Latest Insight */}
            <Grid item xs={12}>
              <Card sx={{ background: 'rgba(255, 255, 255, 0.05)', color: 'white', p: 2 }}>
                <Typography variant="h6" gutterBottom>Latest AI Insight</Typography>
                <Alert severity="success" sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)' }}>
                  <Typography variant="body1">
                    {dashboardData?.contextual_ai.last_insight || 'No recent insights available'}
                  </Typography>
                </Alert>
              </Card>
            </Grid>
          </Grid>
        )}

        {currentTab === 5 && (
          <DailyRaces />
        )}
      </Container>
    </Box>
  )
}

export default App
