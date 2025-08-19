import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tab,
  Tabs,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  LinearProgress,
  Alert,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Divider
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Science,
  CloudUpload,
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  Assessment,
  CompareArrows,
  Store,
  Timeline,
  Memory,
  Speed,
  ExpandMore,
  Visibility,
  Edit,
  Delete,
  GetApp,
  Publish,
  BugReport,
  CheckCircle,
  Error,
  Warning,
  Info
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface MLModel {
  id: string;
  name: string;
  version: string;
  model_type: string;
  algorithm: string;
  framework: string;
  tier: 'free' | 'premium' | 'professional';
  is_active: boolean;
  is_public: boolean;
  performance_metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    profit_loss: number;
    sharpe_ratio: number;
  };
  created_at: string;
  updated_at: string;
}

interface ABExperiment {
  id: string;
  name: string;
  description: string;
  model_a_id: string;
  model_b_id: string;
  traffic_split: number;
  status: 'draft' | 'running' | 'completed' | 'cancelled';
  target_metric: string;
  statistical_significance: boolean;
  results: any;
  start_date: string;
  end_date?: string;
}

interface TrainingJob {
  id: string;
  name: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  training_metrics: any;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`ml-tabpanel-${index}`}
      aria-labelledby={`ml-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const MLModelManagementDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [models, setModels] = useState<MLModel[]>([]);
  const [experiments, setExperiments] = useState<ABExperiment[]>([]);
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [experimentDialogOpen, setExperimentDialogOpen] = useState(false);

  // Mock data for development
  useEffect(() => {
    const mockModels: MLModel[] = [
      {
        id: '1',
        name: 'Win Predictor Pro',
        version: '2.1.0',
        model_type: 'classification',
        algorithm: 'random_forest',
        framework: 'sklearn',
        tier: 'professional',
        is_active: true,
        is_public: true,
        performance_metrics: {
          accuracy: 0.847,
          precision: 0.823,
          recall: 0.856,
          f1_score: 0.839,
          roc_auc: 0.912,
          profit_loss: 12543.50,
          sharpe_ratio: 1.86
        },
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-03-20T14:22:00Z'
      },
      {
        id: '2',
        name: 'Place Predictor Elite',
        version: '1.8.3',
        model_type: 'classification',
        algorithm: 'xgboost',
        framework: 'xgboost',
        tier: 'premium',
        is_active: true,
        is_public: false,
        performance_metrics: {
          accuracy: 0.792,
          precision: 0.788,
          recall: 0.801,
          f1_score: 0.794,
          roc_auc: 0.876,
          profit_loss: 8921.25,
          sharpe_ratio: 1.43
        },
        created_at: '2024-02-01T09:15:00Z',
        updated_at: '2024-03-18T11:45:00Z'
      },
      {
        id: '3',
        name: 'Track Specialist',
        version: '3.0.1',
        model_type: 'ensemble',
        algorithm: 'ensemble',
        framework: 'sklearn',
        tier: 'free',
        is_active: false,
        is_public: true,
        performance_metrics: {
          accuracy: 0.756,
          precision: 0.741,
          recall: 0.769,
          f1_score: 0.755,
          roc_auc: 0.834,
          profit_loss: 5247.80,
          sharpe_ratio: 1.12
        },
        created_at: '2024-01-08T16:20:00Z',
        updated_at: '2024-03-15T13:30:00Z'
      }
    ];

    const mockExperiments: ABExperiment[] = [
      {
        id: '1',
        name: 'Win Predictor vs XGBoost',
        description: 'Testing new Random Forest model against existing XGBoost',
        model_a_id: '1',
        model_b_id: '2',
        traffic_split: 0.5,
        status: 'running',
        target_metric: 'profit_loss',
        statistical_significance: false,
        results: {
          model_a_performance: { profit: 2341.20, accuracy: 0.847 },
          model_b_performance: { profit: 1876.50, accuracy: 0.812 }
        },
        start_date: '2024-03-15T00:00:00Z'
      },
      {
        id: '2',
        name: 'Feature Engineering Test',
        description: 'Testing new feature pipeline effectiveness',
        model_a_id: '2',
        model_b_id: '3',
        traffic_split: 0.3,
        status: 'completed',
        target_metric: 'accuracy',
        statistical_significance: true,
        results: {
          model_a_performance: { profit: 3124.75, accuracy: 0.892 },
          model_b_performance: { profit: 2654.30, accuracy: 0.834 },
          winner: 'model_a'
        },
        start_date: '2024-02-20T00:00:00Z',
        end_date: '2024-03-10T00:00:00Z'
      }
    ];

    const mockTrainingJobs: TrainingJob[] = [
      {
        id: '1',
        name: 'Win Predictor v2.2 Training',
        status: 'running',
        progress_percentage: 67,
        started_at: '2024-03-20T08:30:00Z',
        training_metrics: {
          current_epoch: 134,
          total_epochs: 200,
          train_loss: 0.234,
          val_loss: 0.287,
          train_accuracy: 0.891,
          val_accuracy: 0.843
        }
      },
      {
        id: '2',
        name: 'Place Predictor Retraining',
        status: 'completed',
        progress_percentage: 100,
        started_at: '2024-03-19T14:15:00Z',
        completed_at: '2024-03-20T02:45:00Z',
        training_metrics: {
          final_train_accuracy: 0.912,
          final_val_accuracy: 0.876,
          training_time: '12h 30m'
        }
      },
      {
        id: '3',
        name: 'Neural Network Experiment',
        status: 'failed',
        progress_percentage: 23,
        started_at: '2024-03-18T20:00:00Z',
        error_message: 'GPU memory exceeded during batch processing',
        training_metrics: null
      }
    ];

    setModels(mockModels);
    setExperiments(mockExperiments);
    setTrainingJobs(mockTrainingJobs);
    setLoading(false);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'cancelled': return 'default';
      case 'draft': return 'warning';
      default: return 'default';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'professional': return 'secondary';
      case 'premium': return 'primary';
      case 'free': return 'default';
      default: return 'default';
    }
  };

  const renderModelOverview = () => (
    <Grid container spacing={3}>
      {/* Summary Cards */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Psychology color="primary" />
              <Box>
                <Typography variant="h4">{models.length}</Typography>
                <Typography variant="body2" color="textSecondary">
                  Total Models
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <PlayArrow color="success" />
              <Box>
                <Typography variant="h4">
                  {models.filter(m => m.is_active).length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Models
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <TrendingUp color="warning" />
              <Box>
                <Typography variant="h4">
                  {experiments.filter(e => e.status === 'running').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active A/B Tests
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Memory color="info" />
              <Box>
                <Typography variant="h4">
                  {trainingJobs.filter(j => j.status === 'running').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Training Jobs
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Models Table */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Model Registry</Typography>
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => setModelDialogOpen(true)}
              >
                Upload Model
              </Button>
            </Box>
            
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Model Name</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Algorithm</TableCell>
                    <TableCell>Tier</TableCell>
                    <TableCell>Accuracy</TableCell>
                    <TableCell>Profit/Loss</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {models.map((model) => (
                    <TableRow key={model.id}>
                      <TableCell>
                        <Typography variant="subtitle2">{model.name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {model.framework}
                        </Typography>
                      </TableCell>
                      <TableCell>{model.version}</TableCell>
                      <TableCell>
                        <Chip 
                          label={model.algorithm} 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={model.tier} 
                          size="small" 
                          color={getTierColor(model.tier) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {(model.performance_metrics.accuracy * 100).toFixed(1)}%
                      </TableCell>
                      <TableCell>
                        <Typography 
                          color={model.performance_metrics.profit_loss > 0 ? 'success.main' : 'error.main'}
                        >
                          ${model.performance_metrics.profit_loss.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={model.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={model.is_active ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedModel(model);
                                setModelDialogOpen(true);
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Deploy">
                            <IconButton size="small">
                              <Publish />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Settings">
                            <IconButton size="small">
                              <Settings />
                            </IconButton>
                          </Tooltip>
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
    </Grid>
  );

  const renderABTesting = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">A/B Testing Experiments</Typography>
              <Button
                variant="contained"
                startIcon={<Science />}
                onClick={() => setExperimentDialogOpen(true)}
              >
                Create Experiment
              </Button>
            </Box>

            {experiments.map((experiment) => (
              <Accordion key={experiment.id}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                      {experiment.name}
                    </Typography>
                    <Chip 
                      label={experiment.status}
                      size="small"
                      color={getStatusColor(experiment.status) as any}
                    />
                    {experiment.statistical_significance && (
                      <Chip 
                        label="Significant"
                        size="small"
                        color="success"
                        icon={<CheckCircle />}
                      />
                    )}
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Description
                      </Typography>
                      <Typography variant="body1" paragraph>
                        {experiment.description}
                      </Typography>
                      
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Configuration
                      </Typography>
                      <Typography variant="body2">
                        Traffic Split: {(experiment.traffic_split * 100).toFixed(0)}% / {(100 - experiment.traffic_split * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2">
                        Target Metric: {experiment.target_metric}
                      </Typography>
                      <Typography variant="body2">
                        Start Date: {new Date(experiment.start_date).toLocaleDateString()}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      {experiment.results && (
                        <Box>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Results
                          </Typography>
                          <Box display="flex" gap={2}>
                            <Card variant="outlined" sx={{ p: 2, flex: 1 }}>
                              <Typography variant="caption" color="textSecondary">
                                Model A
                              </Typography>
                              <Typography variant="h6">
                                ${experiment.results.model_a_performance?.profit?.toLocaleString() || 'N/A'}
                              </Typography>
                              <Typography variant="body2">
                                {((experiment.results.model_a_performance?.accuracy || 0) * 100).toFixed(1)}% accuracy
                              </Typography>
                            </Card>
                            <Card variant="outlined" sx={{ p: 2, flex: 1 }}>
                              <Typography variant="caption" color="textSecondary">
                                Model B
                              </Typography>
                              <Typography variant="h6">
                                ${experiment.results.model_b_performance?.profit?.toLocaleString() || 'N/A'}
                              </Typography>
                              <Typography variant="body2">
                                {((experiment.results.model_b_performance?.accuracy || 0) * 100).toFixed(1)}% accuracy
                              </Typography>
                            </Card>
                          </Box>
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTrainingJobs = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Training Jobs</Typography>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
              >
                Start Training
              </Button>
            </Box>

            {trainingJobs.map((job) => (
              <Card key={job.id} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="subtitle1">{job.name}</Typography>
                    <Chip 
                      label={job.status}
                      size="small"
                      color={getStatusColor(job.status) as any}
                    />
                  </Box>

                  {job.status === 'running' && (
                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2">Progress</Typography>
                        <Typography variant="body2">{job.progress_percentage}%</Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={job.progress_percentage}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}

                  {job.training_metrics && (
                    <Grid container spacing={2}>
                      {job.status === 'running' && (
                        <>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="textSecondary">
                              Epoch
                            </Typography>
                            <Typography variant="body2">
                              {job.training_metrics.current_epoch}/{job.training_metrics.total_epochs}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="textSecondary">
                              Train Loss
                            </Typography>
                            <Typography variant="body2">
                              {job.training_metrics.train_loss?.toFixed(4)}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="textSecondary">
                              Val Accuracy
                            </Typography>
                            <Typography variant="body2">
                              {(job.training_metrics.val_accuracy * 100).toFixed(1)}%
                            </Typography>
                          </Grid>
                        </>
                      )}
                      
                      {job.status === 'completed' && (
                        <>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="textSecondary">
                              Final Accuracy
                            </Typography>
                            <Typography variant="body2">
                              {(job.training_metrics.final_val_accuracy * 100).toFixed(1)}%
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="caption" color="textSecondary">
                              Training Time
                            </Typography>
                            <Typography variant="body2">
                              {job.training_metrics.training_time}
                            </Typography>
                          </Grid>
                        </>
                      )}
                    </Grid>
                  )}

                  {job.error_message && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {job.error_message}
                    </Alert>
                  )}
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderMarketplace = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            🚀 <strong>Premium Model Marketplace</strong> - Access professional-grade models with enhanced accuracy guarantees
          </Typography>
        </Alert>
      </Grid>
      
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Available Models
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Browse and purchase professional-grade ML models from verified vendors
            </Typography>
            
            <Box textAlign="center" py={4}>
              <Store sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                Marketplace Coming Soon
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Professional model vendors and marketplace features will be available in the next release
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Box textAlign="center">
          <Psychology sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Loading ML Management Dashboard
          </Typography>
          <LinearProgress sx={{ width: 200 }} />
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            ML Model Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage models, run A/B tests, and monitor training jobs
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button variant="outlined" startIcon={<Refresh />}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<Assessment />}>
            View Analytics
          </Button>
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <Psychology />
                Model Registry
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <CompareArrows />
                A/B Testing
                <Badge badgeContent={experiments.filter(e => e.status === 'running').length} color="primary" />
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <Memory />
                Training Jobs
                <Badge badgeContent={trainingJobs.filter(j => j.status === 'running').length} color="warning" />
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center" gap={1}>
                <Store />
                Marketplace
              </Box>
            }
          />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {renderModelOverview()}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        {renderABTesting()}
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        {renderTrainingJobs()}
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        {renderMarketplace()}
      </TabPanel>
    </Box>
  );
};

export default MLModelManagementDashboard;
