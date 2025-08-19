import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Psychology,
  Speed,
  TrendingUp,
  Science,
  Star,
  CheckCircle,
  Warning,
  CloudDownload,
  Timeline
} from '@mui/icons-material';
import { mlAPIService } from '../../services/mlAPIService';

interface LivePrediction {
  horse_id: string;
  horse_name: string;
  current_position: number;
  win_probability: number;
  place_probability: number;
  model_confidence: number;
  predicted_finish_time: number;
  model_used: string;
}

interface LivePredictionData {
  race_id: string;
  last_updated: string;
  predictions: LivePrediction[];
  market_analysis: {
    efficiency_score: number;
    arbitrage_opportunities: Array<{
      type: string;
      expected_profit: number;
      confidence: number;
    }>;
  };
}

const AdvancedMLFeatures: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [livePredictions, setLivePredictions] = useState<LivePredictionData | null>(null);
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock data for demonstration
  const mlSystemStatus = {
    active_models: 6,
    total_predictions_today: 2840,
    average_accuracy: 0.847,
    system_health: 'excellent',
    live_races: 3,
    premium_features_available: true
  };

  const quickStats = [
    {
      title: 'Active Models',
      value: mlSystemStatus.active_models,
      icon: <Psychology color="primary" />,
      trend: '+2 this week',
      color: 'primary'
    },
    {
      title: 'Predictions Today',
      value: mlSystemStatus.total_predictions_today.toLocaleString(),
      icon: <Speed color="secondary" />,
      trend: '+15% vs yesterday',
      color: 'secondary'
    },
    {
      title: 'Avg Accuracy',
      value: `${(mlSystemStatus.average_accuracy * 100).toFixed(1)}%`,
      icon: <TrendingUp color="success" />,
      trend: '+2.3% this month',
      color: 'success'
    },
    {
      title: 'Live Races',
      value: mlSystemStatus.live_races,
      icon: <Timeline color="warning" />,
      trend: 'Real-time updates',
      color: 'warning'
    }
  ];

  const premiumFeatures = [
    {
      name: 'Professional Win Predictor Pro',
      description: 'Enhanced accuracy with track-specific optimizations',
      accuracy: '89.2%',
      roi: '+24.7%',
      tier: 'professional',
      price: '$0.50/prediction',
      features: ['Weather optimization', 'Live updates', 'Track expertise']
    },
    {
      name: 'Premium Market Analyzer',
      description: 'Advanced market movement and arbitrage detection',
      accuracy: '82.1%',
      roi: '+18.3%',
      tier: 'premium',
      price: '$0.25/prediction',
      features: ['Market efficiency', 'Arbitrage alerts', 'Real-time analysis']
    },
    {
      name: 'Elite Ensemble Model',
      description: 'Cutting-edge neural network ensemble',
      accuracy: '91.8%',
      roi: '+31.2%',
      tier: 'professional',
      price: '$0.75/prediction',
      features: ['Neural networks', 'Deep learning', 'Multi-factor analysis']
    }
  ];

  const recentABTests = [
    {
      name: 'Enhanced vs Standard Win Predictor',
      status: 'completed',
      winner: 'Enhanced Model',
      improvement: '+8.3%',
      confidence: '95%'
    },
    {
      name: 'Neural Network vs Random Forest',
      status: 'running',
      winner: 'TBD',
      improvement: '+2.1%',
      confidence: '85%'
    }
  ];

  useEffect(() => {
    if (autoUpdate) {
      const interval = setInterval(() => {
        // Simulate live predictions update
        const mockLivePredictions: LivePredictionData = {
          race_id: 'race_001',
          last_updated: new Date().toISOString(),
          predictions: Array.from({ length: 8 }, (_, i) => ({
            horse_id: `horse_${i + 1}`,
            horse_name: `Thunder ${i + 1}`,
            current_position: i + 1,
            win_probability: Math.random() * 0.3 + 0.1,
            place_probability: Math.random() * 0.4 + 0.2,
            model_confidence: Math.random() * 0.2 + 0.8,
            predicted_finish_time: 120 + Math.random() * 30,
            model_used: 'Enhanced Ensemble v2.1'
          })),
          market_analysis: {
            efficiency_score: Math.random() * 0.2 + 0.8,
            arbitrage_opportunities: [
              {
                type: 'Win/Place Arbitrage',
                expected_profit: Math.random() * 5 + 2,
                confidence: Math.random() * 0.2 + 0.8
              }
            ]
          }
        };
        setLivePredictions(mockLivePredictions);
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [autoUpdate]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'professional': return 'secondary';
      case 'premium': return 'primary';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
          🤖 Advanced AI & ML Features
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Next-generation machine learning pipeline with live predictions and premium models
        </Typography>
      </Box>

      {/* System Status Alert */}
      <Alert 
        severity="success" 
        sx={{ mb: 3 }}
        icon={<CheckCircle />}
      >
        <Typography variant="body1">
          <strong>All Systems Operational</strong> - Advanced ML features are running optimally. 
          {mlSystemStatus.live_races} races with live predictions active.
        </Typography>
      </Alert>

      {/* Quick Stats Cards */}
      <Grid container spacing={3} mb={4}>
        {quickStats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                background: `linear-gradient(135deg, ${
                  stat.color === 'primary' ? '#1976d2' : 
                  stat.color === 'secondary' ? '#dc004e' :
                  stat.color === 'success' ? '#2e7d32' : '#ed6c02'
                }15, transparent)`,
                border: `1px solid ${
                  stat.color === 'primary' ? '#1976d2' : 
                  stat.color === 'secondary' ? '#dc004e' :
                  stat.color === 'success' ? '#2e7d32' : '#ed6c02'
                }30`
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold">
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.trend}
                    </Typography>
                  </Box>
                  <Box>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Live Predictions" icon={<Timeline />} />
          <Tab label="Premium Models" icon={<Star />} />
          <Tab label="A/B Testing" icon={<Science />} />
          <Tab label="Model Performance" icon={<TrendingUp />} />
        </Tabs>

        <Box p={3}>
          {/* Live Predictions Tab */}
          {activeTab === 0 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5" gutterBottom>
                  🔴 Live Race Predictions
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoUpdate}
                      onChange={(e) => setAutoUpdate(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Auto-update"
                />
              </Box>

              {livePredictions ? (
                <Grid container spacing={3}>
                  <Grid item xs={12} lg={8}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Race Predictions - Live Updates
                        </Typography>
                        <Typography variant="body2" color="text.secondary" mb={2}>
                          Last updated: {new Date(livePredictions.last_updated).toLocaleTimeString()}
                        </Typography>
                        
                        <List>
                          {livePredictions.predictions.map((pred, index) => (
                            <React.Fragment key={pred.horse_id}>
                              <ListItem>
                                <ListItemIcon>
                                  <Chip 
                                    label={pred.current_position} 
                                    size="small" 
                                    color={pred.current_position <= 3 ? 'success' : 'default'}
                                  />
                                </ListItemIcon>
                                <ListItemText
                                  primary={pred.horse_name}
                                  secondary={
                                    <Box>
                                      <Typography variant="body2">
                                        Win: {(pred.win_probability * 100).toFixed(1)}% | 
                                        Place: {(pred.place_probability * 100).toFixed(1)}%
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        Model confidence: {(pred.model_confidence * 100).toFixed(1)}%
                                      </Typography>
                                    </Box>
                                  }
                                />
                                <Box textAlign="right">
                                  <Chip 
                                    label={`${(pred.win_probability * 100).toFixed(1)}%`}
                                    color={pred.win_probability > 0.25 ? 'success' : 'default'}
                                    size="small"
                                  />
                                </Box>
                              </ListItem>
                              {index < livePredictions.predictions.length - 1 && <Divider />}
                            </React.Fragment>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} lg={4}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Market Analysis
                        </Typography>
                        <Box mb={2}>
                          <Typography variant="body2" gutterBottom>
                            Market Efficiency Score
                          </Typography>
                          <Typography variant="h4" color="success.main">
                            {(livePredictions.market_analysis.efficiency_score * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                        
                        <Divider sx={{ my: 2 }} />
                        
                        <Typography variant="body2" gutterBottom>
                          Arbitrage Opportunities
                        </Typography>
                        {livePredictions.market_analysis.arbitrage_opportunities.map((opp, index) => (
                          <Alert severity="info" sx={{ mt: 1 }} key={index}>
                            <Typography variant="body2">
                              <strong>{opp.type}</strong><br />
                              Expected profit: +{opp.expected_profit.toFixed(1)}%<br />
                              Confidence: {(opp.confidence * 100).toFixed(0)}%
                            </Typography>
                          </Alert>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              ) : (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
                  <CircularProgress />
                </Box>
              )}
            </Box>
          )}

          {/* Premium Models Tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                🌟 Premium Model Marketplace
              </Typography>
              <Typography variant="body1" color="text.secondary" mb={3}>
                Access professional-grade models with enhanced accuracy guarantees and specialized features.
              </Typography>

              <Grid container spacing={3}>
                {premiumFeatures.map((model, index) => (
                  <Grid item xs={12} md={6} lg={4} key={index}>
                    <Card sx={{ height: '100%' }}>
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                          <Star color="primary" />
                          <Typography variant="h6">
                            {model.name}
                          </Typography>
                          <Chip 
                            label={model.tier.toUpperCase()} 
                            color={getTierColor(model.tier)}
                            size="small"
                          />
                        </Box>

                        <Typography color="text.secondary" gutterBottom>
                          {model.description}
                        </Typography>

                        <Box mt={2} mb={2}>
                          <Typography variant="body2" gutterBottom>
                            <strong>Accuracy:</strong> {model.accuracy}
                          </Typography>
                          <Typography variant="body2" gutterBottom>
                            <strong>ROI:</strong> {model.roi}
                          </Typography>
                          <Typography variant="body2" gutterBottom>
                            <strong>Cost:</strong> {model.price}
                          </Typography>
                        </Box>

                        <Typography variant="body2" gutterBottom>
                          <strong>Features:</strong>
                        </Typography>
                        <Box mb={2}>
                          {model.features.map((feature, idx) => (
                            <Chip 
                              key={idx}
                              label={feature} 
                              size="small" 
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                        </Box>

                        <Button 
                          variant="contained" 
                          startIcon={<CloudDownload />}
                          fullWidth
                          disabled={model.tier === 'professional'}
                        >
                          {model.tier === 'professional' ? 'Upgrade Required' : 'Access Model'}
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* A/B Testing Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                🧪 A/B Testing & Model Comparison
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Recent A/B Tests
                      </Typography>
                      
                      <List>
                        {recentABTests.map((test, index) => (
                          <React.Fragment key={index}>
                            <ListItem>
                              <ListItemIcon>
                                {test.status === 'completed' ? (
                                  <CheckCircle color="success" />
                                ) : (
                                  <Warning color="warning" />
                                )}
                              </ListItemIcon>
                              <ListItemText
                                primary={test.name}
                                secondary={
                                  <Box>
                                    <Typography variant="body2">
                                      Status: {test.status} | Winner: {test.winner}
                                    </Typography>
                                    <Typography variant="body2">
                                      Improvement: {test.improvement} | Confidence: {test.confidence}
                                    </Typography>
                                  </Box>
                                }
                              />
                              <Chip 
                                label={test.status}
                                color={test.status === 'completed' ? 'success' : 'warning'}
                                size="small"
                              />
                            </ListItem>
                            {index < recentABTests.length - 1 && <Divider />}
                          </React.Fragment>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Model Performance Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                📈 Model Performance Analytics
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                Detailed performance analytics and monitoring dashboard will load here with real-time model metrics.
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Performance Summary
                      </Typography>
                      <Typography variant="body2">
                        Real-time performance tracking, accuracy trends, and ROI analysis across all active models.
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Model Optimization
                      </Typography>
                      <Typography variant="body2">
                        Automated hyperparameter tuning and performance optimization recommendations.
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default AdvancedMLFeatures;
