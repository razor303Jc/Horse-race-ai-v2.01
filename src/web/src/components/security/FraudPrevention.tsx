import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Paper,
  Grid,
  IconButton,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress
} from '@mui/material';
import {
  Security,
  Warning,
  Block,
  Visibility,
  ExpandMore,
  ExpandLess,
  MonetizationOn,
  AccountBalance,
  CreditCard,
  TrendingUp,
  Person,
  LocationOn,
  Schedule,
  Flag
} from '@mui/icons-material';

interface FraudAlert {
  id: string;
  type: 'unusual_betting' | 'suspicious_login' | 'large_deposit' | 'rapid_withdrawals' | 'pattern_anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  timestamp: string;
  userId: string;
  username: string;
  resolved: boolean;
  resolvedBy?: string;
  resolvedAt?: string;
  details: Record<string, any>;
}

interface RiskMetrics {
  riskScore: number;
  accountAge: number;
  totalDeposits: number;
  totalWithdrawals: number;
  avgBetSize: number;
  winRate: number;
  suspiciousActivity: number;
  verificationLevel: 'basic' | 'enhanced' | 'verified';
}

interface FraudPattern {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  sensitivity: number;
  detections: number;
  falsePositives: number;
  accuracy: number;
}

const FRAUD_TYPES = {
  unusual_betting: {
    name: 'Unusual Betting Pattern',
    icon: MonetizationOn,
    color: 'warning' as const
  },
  suspicious_login: {
    name: 'Suspicious Login',
    icon: Security,
    color: 'error' as const
  },
  large_deposit: {
    name: 'Large Deposit',
    icon: AccountBalance,
    color: 'info' as const
  },
  rapid_withdrawals: {
    name: 'Rapid Withdrawals',
    icon: CreditCard,
    color: 'warning' as const
  },
  pattern_anomaly: {
    name: 'Pattern Anomaly',
    icon: TrendingUp,
    color: 'secondary' as const
  }
};

const SEVERITY_COLORS = {
  low: 'info' as const,
  medium: 'warning' as const,
  high: 'error' as const,
  critical: 'error' as const
};

export const FraudPrevention: React.FC = () => {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [patterns, setPatterns] = useState<FraudPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<FraudAlert | null>(null);
  const [expandedAlert, setExpandedAlert] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [showResolved, setShowResolved] = useState(false);

  useEffect(() => {
    loadFraudData();
  }, []);

  const loadFraudData = async () => {
    try {
      setLoading(true);
      const [alertsRes, patternsRes] = await Promise.all([
        fetch('/api/fraud/alerts', { credentials: 'include' }),
        fetch('/api/fraud/patterns', { credentials: 'include' })
      ]);

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }

      if (patternsRes.ok) {
        const patternsData = await patternsRes.json();
        setPatterns(patternsData.patterns || []);
      }
    } catch (err) {
      setError('Failed to load fraud prevention data');
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId: string, resolution: string) => {
    try {
      const response = await fetch(`/api/fraud/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ resolution })
      });

      if (response.ok) {
        setAlerts(prev => prev.map(alert => 
          alert.id === alertId 
            ? { ...alert, resolved: true, resolvedAt: new Date().toISOString() }
            : alert
        ));
        setSelectedAlert(null);
        setSuccess('Alert resolved successfully');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to resolve alert');
      }
    } catch (err) {
      setError('Network error while resolving alert');
    }
  };

  const updatePattern = async (patternId: string, updates: Partial<FraudPattern>) => {
    try {
      const response = await fetch(`/api/fraud/patterns/${patternId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        setPatterns(prev => prev.map(pattern => 
          pattern.id === patternId ? { ...pattern, ...updates } : pattern
        ));
        setSuccess('Fraud pattern updated successfully');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to update pattern');
      }
    } catch (err) {
      setError('Network error while updating pattern');
    }
  };

  const getUserRiskMetrics = async (userId: string): Promise<RiskMetrics | null> => {
    try {
      const response = await fetch(`/api/fraud/risk-metrics/${userId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        return data.metrics;
      }
    } catch (err) {
      console.error('Failed to load risk metrics:', err);
    }
    return null;
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false;
    if (filterType !== 'all' && alert.type !== filterType) return false;
    if (!showResolved && alert.resolved) return false;
    return true;
  });

  const getSeverityProgress = (severity: string) => {
    switch (severity) {
      case 'low': return 25;
      case 'medium': return 50;
      case 'high': return 75;
      case 'critical': return 100;
      default: return 0;
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'error';
    if (score >= 60) return 'warning';
    if (score >= 40) return 'info';
    return 'success';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Fraud Prevention
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Warning color="error" />
                <Box>
                  <Typography variant="h4">
                    {alerts.filter(a => !a.resolved).length}
                  </Typography>
                  <Typography color="textSecondary">
                    Active Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Security color="primary" />
                <Box>
                  <Typography variant="h4">
                    {patterns.filter(p => p.enabled).length}
                  </Typography>
                  <Typography color="textSecondary">
                    Active Patterns
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Block color="warning" />
                <Box>
                  <Typography variant="h4">
                    {alerts.filter(a => a.severity === 'critical').length}
                  </Typography>
                  <Typography color="textSecondary">
                    Critical Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <TrendingUp color="success" />
                <Box>
                  <Typography variant="h4">
                    {Math.round(patterns.reduce((sum, p) => sum + p.accuracy, 0) / patterns.length)}%
                  </Typography>
                  <Typography color="textSecondary">
                    Avg Accuracy
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Fraud Alerts
          </Typography>
          
          <Box display="flex" gap={2} mb={3} flexWrap="wrap">
            <TextField
              select
              label="Severity"
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              size="small"
              sx={{ minWidth: 120 }}
            >
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </TextField>

            <TextField
              select
              label="Type"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              size="small"
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="all">All Types</MenuItem>
              {Object.entries(FRAUD_TYPES).map(([key, type]) => (
                <MenuItem key={key} value={key}>{type.name}</MenuItem>
              ))}
            </TextField>

            <Button
              variant={showResolved ? "contained" : "outlined"}
              onClick={() => setShowResolved(!showResolved)}
              size="small"
            >
              {showResolved ? 'Hide' : 'Show'} Resolved
            </Button>
          </Box>

          {/* Alerts List */}
          {filteredAlerts.length === 0 ? (
            <Typography color="textSecondary">
              No alerts match the current filters.
            </Typography>
          ) : (
            <List>
              {filteredAlerts.map((alert) => {
                const fraudType = FRAUD_TYPES[alert.type];
                const IconComponent = fraudType.icon;
                
                return (
                  <Paper key={alert.id} sx={{ mb: 1 }}>
                    <ListItem
                      button
                      onClick={() => setExpandedAlert(
                        expandedAlert === alert.id ? null : alert.id
                      )}
                    >
                      <ListItemIcon>
                        <IconComponent color={fraudType.color} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={2}>
                            <Typography variant="subtitle1">
                              {fraudType.name}
                            </Typography>
                            <Chip
                              label={alert.severity}
                              size="small"
                              color={SEVERITY_COLORS[alert.severity]}
                            />
                            {alert.resolved && (
                              <Chip label="Resolved" size="small" color="success" variant="outlined" />
                            )}
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {alert.description}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              User: {alert.username} • {new Date(alert.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                      <IconButton size="small">
                        {expandedAlert === alert.id ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    </ListItem>
                    
                    <Collapse in={expandedAlert === alert.id}>
                      <Box sx={{ p: 2, pt: 0 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Alert Details
                        </Typography>
                        
                        <Grid container spacing={2} sx={{ mb: 2 }}>
                          <Grid item xs={12} sm={6}>
                            <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                              <Typography variant="body2" color="textSecondary" gutterBottom>
                                Risk Level
                              </Typography>
                              <Box display="flex" alignItems="center" gap={1}>
                                <LinearProgress
                                  variant="determinate"
                                  value={getSeverityProgress(alert.severity)}
                                  color={SEVERITY_COLORS[alert.severity]}
                                  sx={{ flex: 1, height: 8, borderRadius: 4 }}
                                />
                                <Typography variant="body2" fontWeight="bold">
                                  {alert.severity.toUpperCase()}
                                </Typography>
                              </Box>
                            </Paper>
                          </Grid>
                          
                          <Grid item xs={12} sm={6}>
                            <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                              <Typography variant="body2" color="textSecondary" gutterBottom>
                                Detection Time
                              </Typography>
                              <Typography variant="body2">
                                {new Date(alert.timestamp).toLocaleString()}
                              </Typography>
                            </Paper>
                          </Grid>
                        </Grid>

                        {/* Alert-specific details */}
                        {alert.details && Object.keys(alert.details).length > 0 && (
                          <TableContainer component={Paper} sx={{ mb: 2 }}>
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Property</TableCell>
                                  <TableCell>Value</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {Object.entries(alert.details).map(([key, value]) => (
                                  <TableRow key={key}>
                                    <TableCell>{key.replace(/_/g, ' ').toUpperCase()}</TableCell>
                                    <TableCell>{String(value)}</TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        )}

                        {!alert.resolved && (
                          <Box display="flex" gap={2}>
                            <Button
                              variant="contained"
                              color="primary"
                              onClick={() => setSelectedAlert(alert)}
                            >
                              Investigate
                            </Button>
                            <Button
                              variant="outlined"
                              onClick={() => resolveAlert(alert.id, 'false_positive')}
                            >
                              Mark as False Positive
                            </Button>
                          </Box>
                        )}
                      </Box>
                    </Collapse>
                  </Paper>
                );
              })}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Fraud Detection Patterns */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detection Patterns
          </Typography>
          
          <Typography color="textSecondary" paragraph>
            Configure fraud detection patterns and their sensitivity levels.
          </Typography>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pattern</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Sensitivity</TableCell>
                  <TableCell>Detections</TableCell>
                  <TableCell>Accuracy</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {patterns.map((pattern) => (
                  <TableRow key={pattern.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">{pattern.name}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {pattern.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={pattern.enabled ? 'Active' : 'Disabled'}
                        color={pattern.enabled ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <LinearProgress
                        variant="determinate"
                        value={pattern.sensitivity}
                        sx={{ width: 100 }}
                      />
                      <Typography variant="body2" color="textSecondary">
                        {pattern.sensitivity}%
                      </Typography>
                    </TableCell>
                    <TableCell>{pattern.detections}</TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        color={pattern.accuracy >= 90 ? 'success.main' : 
                               pattern.accuracy >= 70 ? 'warning.main' : 'error.main'}
                      >
                        {pattern.accuracy}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => updatePattern(pattern.id, { enabled: !pattern.enabled })}
                      >
                        {pattern.enabled ? 'Disable' : 'Enable'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Alert Investigation Dialog */}
      <Dialog open={!!selectedAlert} onClose={() => setSelectedAlert(null)} maxWidth="md" fullWidth>
        {selectedAlert && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center" gap={2}>
                <Warning color="error" />
                Investigate Fraud Alert
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ pt: 1 }}>
                <Typography variant="h6" gutterBottom>
                  {FRAUD_TYPES[selectedAlert.type].name}
                </Typography>
                
                <Typography color="textSecondary" paragraph>
                  {selectedAlert.description}
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        User Information
                      </Typography>
                      <Typography variant="body2">Username: {selectedAlert.username}</Typography>
                      <Typography variant="body2">User ID: {selectedAlert.userId}</Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Alert Information
                      </Typography>
                      <Typography variant="body2">
                        Severity: {selectedAlert.severity.toUpperCase()}
                      </Typography>
                      <Typography variant="body2">
                        Detected: {new Date(selectedAlert.timestamp).toLocaleString()}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedAlert(null)}>
                Close
              </Button>
              <Button
                variant="outlined"
                onClick={() => resolveAlert(selectedAlert.id, 'false_positive')}
              >
                False Positive
              </Button>
              <Button
                variant="contained"
                color="error"
                onClick={() => resolveAlert(selectedAlert.id, 'confirmed_fraud')}
              >
                Confirm Fraud
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default FraudPrevention;
