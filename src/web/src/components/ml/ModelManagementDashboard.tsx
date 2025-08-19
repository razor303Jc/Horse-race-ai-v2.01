import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Badge,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Slider,
  Divider
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  Settings,
  PlayArrow,
  Pause,
  Stop,
  Refresh,
  CloudDownload,
  CloudUpload,
  Assessment,
  CompareArrows,
  Memory,
  Speed,
  BugReport,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  ExpandMore,
  Visibility,
  VisibilityOff,
  Download,
  Upload,
  Delete,
  Edit,
  Add,
  Science,
  ModelTraining,
  Psychology,
  AutoAwesome,
  DataUsage,
  Timeline,
  ShowChart,
  PieChart,
  BarChart
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart
} from 'recharts';

// Enhanced interfaces for ML model management
interface MLModel {
  id: string;
  name: string;
  version: string;
  type: 'ensemble' | 'neural_network' | 'gradient_boosting' | 'linear' | 'svm' | 'random_forest';
  status: 'training' | 'active' | 'inactive' | 'testing' | 'deprecated' | 'error';
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  lastTrained: string;
  trainingDuration: number;
  dataSize: number;
  features: string[];
  hyperparameters: Record<string, any>;
  performance: ModelPerformance;
  tier: 'free' | 'premium' | 'professional';
  costPerPrediction: number;
  monthlyLimit: number;
  usage: ModelUsage;
  metadata: ModelMetadata;
}

interface ModelPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  roc_auc: number;
  sharpeRatio: number;
  winRate: number;
  profitability: number;
  drawdown: number;
  volatility: number;
  predictions: number;
  correctPredictions: number;
  trend: 'improving' | 'stable' | 'declining';
  lastUpdated: string;
}

interface ModelUsage {
  predictionsToday: number;
  predictionsThisMonth: number;
  remainingPredictions: number;
  costThisMonth: number;
  peakUsageHour: string;
  averageResponseTime: number;
  errorRate: number;
}

interface ModelMetadata {
  creator: string;
  description: string;
  tags: string[];
  category: string;
  targetMarkets: string[];
  updateFrequency: string;
  lastUpdate: string;
  changelog: string[];
  documentation: string;
  supportContact: string;
}

interface ABTest {
  id: string;
  name: string;
  modelA: string;
  modelB: string;
  status: 'running' | 'completed' | 'paused';
  trafficSplit: number;
  startDate: string;
  duration: number;
  metrics: {
    conversionsA: number;
    conversionsB: number;
    significanceLevel: number;
    winner: 'A' | 'B' | 'inconclusive';
  };
  results: ABTestResults;
}

interface ABTestResults {
  modelAPerformance: ModelPerformance;
  modelBPerformance: ModelPerformance;
  statisticalSignificance: number;
  confidenceInterval: [number, number];
  recommendation: string;
  insights: string[];
}

const ModelManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [models, setModels] = useState<MLModel[]>([]);
  const [abTests, setABTests] = useState<ABTest[]>([]);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState<'create' | 'edit' | 'test' | 'deploy'>('create');

  // Model marketplace and management states
  const [marketplaceFilter, setMarketplaceFilter] = useState('all');
  const [sortBy, setSortBy] = useState<'accuracy' | 'popularity' | 'price' | 'recent'>('accuracy');
  const [showOnlyOwned, setShowOnlyOwned] = useState(false);
  const [autoRetraining, setAutoRetraining] = useState(true);
  const [performanceAlerts, setPerformanceAlerts] = useState(true);

  // Load models and tests on component mount
  useEffect(() => {
    loadModels();
    loadABTests();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      // Simulate API call - replace with actual API
      const mockModels: MLModel[] = [
        {
          id: 'model-1',
          name: 'Premium Ensemble Predictor',
          version: '2.3.1',
          type: 'ensemble',
          status: 'active',
          accuracy: 0.847,
          precision: 0.823,
          recall: 0.891,
          f1Score: 0.856,
          lastTrained: '2025-08-19T10:30:00Z',
          trainingDuration: 3600,
          dataSize: 1250000,
          features: ['form', 'track_condition', 'jockey_stats', 'trainer_stats', 'weather', 'odds_movement'],
          hyperparameters: { max_depth: 10, n_estimators: 200, learning_rate: 0.1 },
          performance: {
            accuracy: 0.847,
            precision: 0.823,
            recall: 0.891,
            f1Score: 0.856,
            roc_auc: 0.912,
            sharpeRatio: 1.34,
            winRate: 0.67,
            profitability: 0.156,
            drawdown: 0.089,
            volatility: 0.234,
            predictions: 15420,
            correctPredictions: 13051,
            trend: 'improving',
            lastUpdated: '2025-08-19T15:45:00Z'
          },
          tier: 'premium',
          costPerPrediction: 0.05,
          monthlyLimit: 10000,
          usage: {
            predictionsToday: 234,
            predictionsThisMonth: 7856,
            remainingPredictions: 2144,
            costThisMonth: 392.80,
            peakUsageHour: '14:00',
            averageResponseTime: 145,
            errorRate: 0.002
          },
          metadata: {
            creator: 'AI Racing Labs',
            description: 'Advanced ensemble model combining multiple algorithms for superior prediction accuracy',
            tags: ['ensemble', 'premium', 'high-accuracy', 'all-weather'],
            category: 'Win Prediction',
            targetMarkets: ['UK', 'Ireland', 'Australia'],
            updateFrequency: 'Daily',
            lastUpdate: '2025-08-19T06:00:00Z',
            changelog: ['Improved weather factor integration', 'Enhanced jockey analysis'],
            documentation: 'https://docs.airacings.com/models/premium-ensemble',
            supportContact: 'support@airacings.com'
          }
        },
        {
          id: 'model-2',
          name: 'Neural Network Pro',
          version: '1.8.3',
          type: 'neural_network',
          status: 'training',
          accuracy: 0.792,
          precision: 0.768,
          recall: 0.834,
          f1Score: 0.8,
          lastTrained: '2025-08-19T08:15:00Z',
          trainingDuration: 7200,
          dataSize: 2100000,
          features: ['form', 'pace', 'breeding', 'track_bias', 'market_confidence', 'historical_performance'],
          hyperparameters: { layers: 5, neurons: [256, 128, 64, 32, 1], dropout: 0.3, learning_rate: 0.001 },
          performance: {
            accuracy: 0.792,
            precision: 0.768,
            recall: 0.834,
            f1Score: 0.8,
            roc_auc: 0.878,
            sharpeRatio: 1.12,
            winRate: 0.62,
            profitability: 0.134,
            drawdown: 0.112,
            volatility: 0.267,
            predictions: 8932,
            correctPredictions: 7074,
            trend: 'stable',
            lastUpdated: '2025-08-19T12:20:00Z'
          },
          tier: 'professional',
          costPerPrediction: 0.08,
          monthlyLimit: 5000,
          usage: {
            predictionsToday: 89,
            predictionsThisMonth: 3421,
            remainingPredictions: 1579,
            costThisMonth: 273.68,
            peakUsageHour: '16:00',
            averageResponseTime: 203,
            errorRate: 0.001
          },
          metadata: {
            creator: 'DeepRacing AI',
            description: 'Deep neural network with advanced feature engineering for complex pattern recognition',
            tags: ['neural-network', 'deep-learning', 'pattern-recognition'],
            category: 'Place Prediction',
            targetMarkets: ['UK', 'US', 'Japan'],
            updateFrequency: 'Weekly',
            lastUpdate: '2025-08-18T22:00:00Z',
            changelog: ['Added breeding factor analysis', 'Optimized network architecture'],
            documentation: 'https://docs.deepracing.ai/neural-pro',
            supportContact: 'support@deepracing.ai'
          }
        }
      ];

      setModels(mockModels);
      setError(null);
    } catch (err) {
      setError('Failed to load models');
      console.error('Error loading models:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadABTests = async () => {
    try {
      // Simulate API call for A/B tests
      const mockABTests: ABTest[] = [
        {
          id: 'test-1',
          name: 'Ensemble vs Neural Network',
          modelA: 'model-1',
          modelB: 'model-2',
          status: 'running',
          trafficSplit: 50,
          startDate: '2025-08-15T09:00:00Z',
          duration: 14,
          metrics: {
            conversionsA: 1247,
            conversionsB: 1189,
            significanceLevel: 0.89,
            winner: 'inconclusive'
          },
          results: {
            modelAPerformance: {
              accuracy: 0.847,
              precision: 0.823,
              recall: 0.891,
              f1Score: 0.856,
              roc_auc: 0.912,
              sharpeRatio: 1.34,
              winRate: 0.67,
              profitability: 0.156,
              drawdown: 0.089,
              volatility: 0.234,
              predictions: 2500,
              correctPredictions: 2118,
              trend: 'improving',
              lastUpdated: '2025-08-19T15:45:00Z'
            },
            modelBPerformance: {
              accuracy: 0.792,
              precision: 0.768,
              recall: 0.834,
              f1Score: 0.8,
              roc_auc: 0.878,
              sharpeRatio: 1.12,
              winRate: 0.62,
              profitability: 0.134,
              drawdown: 0.112,
              volatility: 0.267,
              predictions: 2500,
              correctPredictions: 1980,
              trend: 'stable',
              lastUpdated: '2025-08-19T15:45:00Z'
            },
            statisticalSignificance: 0.89,
            confidenceInterval: [0.02, 0.08],
            recommendation: 'Continue test for 3 more days to reach statistical significance',
            insights: [
              'Model A shows higher accuracy but Model B has lower response time',
              'Cost per prediction favors Model A for high-volume usage',
              'Model B performs better in volatile market conditions'
            ]
          }
        }
      ];

      setABTests(mockABTests);
    } catch (err) {
      console.error('Error loading A/B tests:', err);
    }
  };

  const handleModelToggle = useCallback((modelId: string, enabled: boolean) => {
    setModels(prev => prev.map(model => 
      model.id === modelId 
        ? { ...model, status: enabled ? 'active' : 'inactive' }
        : model
    ));
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'training': return 'info';
      case 'testing': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'professional': return '#1976d2';
      case 'premium': return '#9c27b0';
      default: return '#757575';
    }
  };

  const renderModelCard = (model: MLModel) => (
    <Card key={model.id} sx={{ mb: 2, border: `2px solid ${getTierColor(model.tier)}` }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {model.name}
              <Chip 
                label={model.tier} 
                size="small" 
                sx={{ 
                  backgroundColor: getTierColor(model.tier),
                  color: 'white',
                  textTransform: 'capitalize'
                }}
              />
              <Chip 
                label={model.status} 
                size="small" 
                color={getStatusColor(model.status) as any}
                icon={
                  model.status === 'active' ? <CheckCircle /> :
                  model.status === 'training' ? <ModelTraining /> :
                  model.status === 'error' ? <ErrorIcon /> : <Warning />
                }
              />
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Version {model.version} • {model.type} • Last trained {new Date(model.lastTrained).toLocaleDateString()}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {model.metadata.description}
            </Typography>
            <Box display="flex" gap={0.5} flexWrap="wrap">
              {model.metadata.tags.map(tag => (
                <Chip key={tag} label={tag} size="small" variant="outlined" />
              ))}
            </Box>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="flex-end" gap={1}>
            <FormControlLabel
              control={
                <Switch 
                  checked={model.status === 'active'}
                  onChange={(e) => handleModelToggle(model.id, e.target.checked)}
                  color="primary"
                />
              }
              label="Active"
            />
            <Box display="flex" gap={1}>
              <IconButton size="small" onClick={() => setSelectedModel(model)}>
                <Visibility />
              </IconButton>
              <IconButton size="small">
                <Edit />
              </IconButton>
              <IconButton size="small">
                <Assessment />
              </IconButton>
            </Box>
          </Box>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>Performance Metrics</Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Accuracy</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {(model.performance.accuracy * 100).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={model.performance.accuracy * 100} 
                sx={{ height: 6, borderRadius: 3 }}
              />
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Sharpe Ratio</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {model.performance.sharpeRatio.toFixed(2)}
                </Typography>
              </Box>
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Win Rate</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {(model.performance.winRate * 100).toFixed(1)}%
                </Typography>
              </Box>
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Profitability</Typography>
                <Typography 
                  variant="body2" 
                  fontWeight="bold"
                  color={model.performance.profitability > 0 ? 'success.main' : 'error.main'}
                >
                  {(model.performance.profitability * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>Usage & Costs</Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Today's Predictions</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {model.usage.predictionsToday.toLocaleString()}
                </Typography>
              </Box>
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Monthly Usage</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {model.usage.predictionsThisMonth.toLocaleString()} / {model.monthlyLimit.toLocaleString()}
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(model.usage.predictionsThisMonth / model.monthlyLimit) * 100}
                sx={{ height: 6, borderRadius: 3 }}
              />
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Cost This Month</Typography>
                <Typography variant="body2" fontWeight="bold">
                  ${model.usage.costThisMonth.toFixed(2)}
                </Typography>
              </Box>
              
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Avg Response Time</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {model.usage.averageResponseTime}ms
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderABTestCard = (test: ABTest) => (
    <Card key={test.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box>
            <Typography variant="h6" component="div" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {test.name}
              <Chip 
                label={test.status} 
                size="small" 
                color={test.status === 'running' ? 'primary' : test.status === 'completed' ? 'success' : 'default'}
              />
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Traffic Split: {test.trafficSplit}% / {100 - test.trafficSplit}% • 
              Started {new Date(test.startDate).toLocaleDateString()}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <IconButton size="small">
              <Pause />
            </IconButton>
            <IconButton size="small">
              <Stop />
            </IconButton>
            <IconButton size="small">
              <Assessment />
            </IconButton>
          </Box>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>Model A Performance</Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Accuracy</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {(test.results.modelAPerformance.accuracy * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Conversions</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {test.metrics.conversionsA.toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" gutterBottom>Model B Performance</Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Accuracy</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {(test.results.modelBPerformance.accuracy * 100).toFixed(1)}%
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Conversions</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {test.metrics.conversionsB.toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>Test Insights</Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Statistical Significance:</strong> {(test.results.statisticalSignificance * 100).toFixed(1)}%
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Recommendation:</strong> {test.results.recommendation}
          </Typography>
          <Box>
            {test.results.insights.map((insight, index) => (
              <Typography key={index} variant="body2" sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                • {insight}
              </Typography>
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const renderPerformanceChart = () => {
    const chartData = models.map(model => ({
      name: model.name.split(' ').slice(0, 2).join(' '),
      accuracy: model.performance.accuracy * 100,
      sharpe: model.performance.sharpeRatio,
      winRate: model.performance.winRate * 100,
      profitability: model.performance.profitability * 100
    }));

    return (
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="accuracy" fill="#8884d8" name="Accuracy %" />
          <Line type="monotone" dataKey="sharpe" stroke="#ff7300" name="Sharpe Ratio" />
          <Line type="monotone" dataKey="profitability" stroke="#00ff00" name="Profitability %" />
        </ComposedChart>
      </ResponsiveContainer>
    );
  };

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Science color="primary" />
        Advanced AI & ML Management
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Model Dashboard" icon={<Analytics />} />
          <Tab label="A/B Testing" icon={<CompareArrows />} />
          <Tab label="Model Marketplace" icon={<CloudDownload />} />
          <Tab label="Performance Analytics" icon={<ShowChart />} />
          <Tab label="Training & Deployment" icon={<ModelTraining />} />
        </Tabs>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Model Dashboard Tab */}
      {activeTab === 0 && (
        <Box>
          <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
            <Typography variant="h5" gutterBottom>
              Active Models ({models.filter(m => m.status === 'active').length})
            </Typography>
            <Box display="flex" gap={2}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={autoRetraining}
                    onChange={(e) => setAutoRetraining(e.target.checked)}
                  />
                }
                label="Auto Retraining"
              />
              <FormControlLabel
                control={
                  <Switch 
                    checked={performanceAlerts}
                    onChange={(e) => setPerformanceAlerts(e.target.checked)}
                  />
                }
                label="Performance Alerts"
              />
              <Button variant="contained" startIcon={<Add />}>
                Deploy New Model
              </Button>
            </Box>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              {models.map(renderModelCard)}
            </Grid>
          </Grid>
        </Box>
      )}

      {/* A/B Testing Tab */}
      {activeTab === 1 && (
        <Box>
          <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
            <Typography variant="h5" gutterBottom>
              A/B Tests ({abTests.filter(t => t.status === 'running').length} running)
            </Typography>
            <Button variant="contained" startIcon={<Add />}>
              Create A/B Test
            </Button>
          </Box>

          {abTests.map(renderABTestCard)}
        </Box>
      )}

      {/* Performance Analytics Tab */}
      {activeTab === 3 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Model Performance Comparison
          </Typography>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics Comparison
              </Typography>
              {renderPerformanceChart()}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Model Details Dialog */}
      <Dialog 
        open={Boolean(selectedModel)} 
        onClose={() => setSelectedModel(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {selectedModel?.name} - Detailed Analytics
        </DialogTitle>
        <DialogContent>
          {selectedModel && (
            <Box>
              {/* Detailed model analytics would go here */}
              <Typography variant="body1">
                Detailed model performance analytics, feature importance, 
                prediction history, and advanced configuration options.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedModel(null)}>Close</Button>
          <Button variant="contained">Export Report</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelManagementDashboard;
