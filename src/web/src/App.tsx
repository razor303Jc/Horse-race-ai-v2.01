import {
    AttachMoney,
    Dashboard as DashboardIcon,
    Psychology,
    Refresh,
    Speed,
    Timeline,
    TrendingUp,
} from '@mui/icons-material'
import {
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
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Toolbar,
    Typography,
} from '@mui/material'
import axios from 'axios'
import { useEffect, useState } from 'react'

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
  }
  betting_integration: {
    status: string
    live_markets: number
    profit_loss: number
    strategies_available: number
  }
  contextual_ai: {
    status: string
    factors_active: number
    enhancement_score: number
  }
  real_time_performance: {
    prediction_speed: string
    live_feeds: string
    auto_download: string
  }
}

interface RecentPrediction {
  horse: string
  race: string
  probability: number
  confidence: number
  status: string
  value_rating?: number
}

function App() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [recentPredictions, setRecentPredictions] = useState<RecentPrediction[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const fetchData = async () => {
    try {
      const statusResponse = await axios.get('/api/system_status')
      setSystemStatus(statusResponse.data)
      
      // Fetch real dashboard data from API
      const dashboardResponse = await axios.get('/api/dashboard_data')
      setDashboardData(dashboardResponse.data)
      setRecentPredictions(dashboardResponse.data.recent_predictions || [])
      
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

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography variant="h6" align="center" sx={{ mt: 2, color: 'white' }}>
          Loading Horse Racing AI Dashboard...
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
            🐎 Horse Racing AI v2.0 Dashboard
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

        {/* Main Dashboard Cards */}
        <Grid container spacing={4}>
          {/* ML Models Card */}
          <Grid item xs={12} md={6} lg={4}>
            <Card className="dashboard-card" sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Psychology /> ML Models
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography className="metric-value">{dashboardData?.ml_models.ensemble_auc}%</Typography>
                  <Typography className="metric-label">Ensemble AUC</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography className="metric-value" sx={{ fontSize: '1.5rem' }}>
                      {dashboardData?.ml_models.models_active}
                    </Typography>
                    <Typography className="metric-label">Active Models</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography className="metric-value" sx={{ fontSize: '1.5rem' }}>
                      {dashboardData?.ml_models.predictions_today}
                    </Typography>
                    <Typography className="metric-label">Predictions Today</Typography>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={dashboardData?.ml_models.status || 'Unknown'}
                    color={getStatusColor(dashboardData?.ml_models.status || '')}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Betting Integration Card */}
          <Grid item xs={12} md={6} lg={4}>
            <Card className="dashboard-card" sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AttachMoney /> Betting Integration
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography className="metric-value">£{dashboardData?.betting_integration.profit_loss}</Typography>
                  <Typography className="metric-label">P&L Today</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography className="metric-value" sx={{ fontSize: '1.5rem' }}>
                      {dashboardData?.betting_integration.live_markets}
                    </Typography>
                    <Typography className="metric-label">Live Markets</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography className="metric-value" sx={{ fontSize: '1.5rem' }}>
                      {dashboardData?.betting_integration.strategies_available}
                    </Typography>
                    <Typography className="metric-label">Strategies</Typography>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={dashboardData?.betting_integration.status || 'Unknown'}
                    color={getStatusColor(dashboardData?.betting_integration.status || '')}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Contextual AI Card */}
          <Grid item xs={12} md={6} lg={4}>
            <Card className="dashboard-card" sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUp /> Contextual AI
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography className="metric-value">{(dashboardData?.contextual_ai.enhancement_score! * 100).toFixed(1)}%</Typography>
                  <Typography className="metric-label">Enhancement Score</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography className="metric-value" sx={{ fontSize: '1.5rem' }}>
                      {dashboardData?.contextual_ai.factors_active}
                    </Typography>
                    <Typography className="metric-label">Active Factors</Typography>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2 }}>
                  <Chip
                    label={dashboardData?.contextual_ai.status || 'Unknown'}
                    color={getStatusColor(dashboardData?.contextual_ai.status || '')}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Predictions Table */}
        <Paper sx={{ mt: 4, background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
              <Timeline /> Recent Predictions
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Horse</TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Race</TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Probability</TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Confidence</TableCell>
                    <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentPredictions.map((prediction, index) => (
                    <TableRow key={index}>
                      <TableCell sx={{ color: 'white' }}>{prediction.horse}</TableCell>
                      <TableCell sx={{ color: 'white' }}>{prediction.race}</TableCell>
                      <TableCell sx={{ color: 'white' }}>{prediction.probability}%</TableCell>
                      <TableCell sx={{ color: 'white' }}>{prediction.confidence}%</TableCell>
                      <TableCell>
                        <Chip
                          label={prediction.status}
                          color={prediction.status === 'ACTIVE' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}

export default App
