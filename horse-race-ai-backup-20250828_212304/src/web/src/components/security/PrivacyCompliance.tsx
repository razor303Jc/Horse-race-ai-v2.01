import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Divider,
  Grid,
  CircularProgress
} from '@mui/material';
import {
  Security,
  Shield,
  Lock,
  Visibility,
  VisibilityOff,
  Download,
  Delete,
  Settings,
  Info,
  Warning,
  CheckCircle,
  Error,
  Gavel,
  Description,
  CloudDownload,
  PersonOff,
  PolicyOutlined as Privacy,
  DataUsage,
  Cookie,
  LocationOn,
  CameraAlt,
  Mic,
  Contacts,
  Schedule,
  History,
  Assessment,
  Timeline,
  BarChart,
  Email,
  VideoLibrary as PersonalVideo,
  ExpandMore
} from '@mui/icons-material';

interface PrivacySetting {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  required: boolean;
  category: 'data' | 'marketing' | 'analytics' | 'functional';
}

interface DataRequest {
  id: string;
  type: 'export' | 'deletion' | 'correction';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  requestedAt: string;
  completedAt?: string;
  downloadUrl?: string;
}

interface ConsentRecord {
  id: string;
  type: string;
  granted: boolean;
  timestamp: string;
  version: string;
  ipAddress: string;
}

const PRIVACY_CATEGORIES = {
  functional: {
    name: 'Functional',
    description: 'Essential cookies and data processing required for the website to function properly',
    color: 'primary' as const
  },
  analytics: {
    name: 'Analytics',
    description: 'Help us understand how you use our website to improve your experience',
    color: 'info' as const
  },
  marketing: {
    name: 'Marketing',
    description: 'Used to show you relevant advertisements and track campaign effectiveness',
    color: 'warning' as const
  },
  data: {
    name: 'Data Processing',
    description: 'Additional data processing for enhanced features and personalization',
    color: 'secondary' as const
  }
};

export const PrivacyCompliance: React.FC = () => {
  const [settings, setSettings] = useState<PrivacySetting[]>([]);
  const [dataRequests, setDataRequests] = useState<DataRequest[]>([]);
  const [consentHistory, setConsentHistory] = useState<ConsentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showDataRequest, setShowDataRequest] = useState(false);
  const [requestType, setRequestType] = useState<'export' | 'deletion' | 'correction'>('export');
  const [requestReason, setRequestReason] = useState('');
  const [showConsentHistory, setShowConsentHistory] = useState(false);

  useEffect(() => {
    loadPrivacyData();
  }, []);

  const loadPrivacyData = async () => {
    try {
      setLoading(true);
      const [settingsRes, requestsRes, consentRes] = await Promise.all([
        fetch('/api/privacy/settings', { credentials: 'include' }),
        fetch('/api/privacy/data-requests', { credentials: 'include' }),
        fetch('/api/privacy/consent-history', { credentials: 'include' })
      ]);

      if (settingsRes.ok) {
        const settingsData = await settingsRes.json();
        setSettings(settingsData.settings || []);
      }

      if (requestsRes.ok) {
        const requestsData = await requestsRes.json();
        setDataRequests(requestsData.requests || []);
      }

      if (consentRes.ok) {
        const consentData = await consentRes.json();
        setConsentHistory(consentData.consents || []);
      }
    } catch (err) {
      setError('Failed to load privacy data');
    } finally {
      setLoading(false);
    }
  };

  const updatePrivacySetting = async (settingId: string, enabled: boolean) => {
    try {
      const response = await fetch(`/api/privacy/settings/${settingId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ enabled })
      });

      if (response.ok) {
        setSettings(prev => prev.map(setting => 
          setting.id === settingId ? { ...setting, enabled } : setting
        ));
        setSuccess('Privacy setting updated successfully');
        
        // Record consent
        await recordConsent(settingId, enabled);
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to update privacy setting');
      }
    } catch (err) {
      setError('Network error while updating privacy setting');
    }
  };

  const recordConsent = async (settingId: string, granted: boolean) => {
    try {
      await fetch('/api/privacy/consent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          type: settingId,
          granted,
          version: '1.0'
        })
      });
    } catch (err) {
      console.error('Failed to record consent:', err);
    }
  };

  const submitDataRequest = async () => {
    if (!requestReason.trim()) {
      setError('Please provide a reason for your request');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('/api/privacy/data-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          type: requestType,
          reason: requestReason
        })
      });

      if (response.ok) {
        const data = await response.json();
        setDataRequests(prev => [data.request, ...prev]);
        setShowDataRequest(false);
        setRequestReason('');
        setSuccess(`${requestType} request submitted successfully`);
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to submit data request');
      }
    } catch (err) {
      setError('Network error while submitting request');
    } finally {
      setLoading(false);
    }
  };

  const downloadData = async (requestId: string) => {
    try {
      const response = await fetch(`/api/privacy/data-export/${requestId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `horse-racing-ai-data-export-${requestId}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        setError('Failed to download data export');
      }
    } catch (err) {
      setError('Network error while downloading data');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <CircularProgress size={20} />;
      case 'failed':
        return <Warning color="error" />;
      default:
        return <Info color="info" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'functional':
        return <Security />;
      case 'analytics':
        return <DataUsage />;
      case 'marketing':
        return <Email />;
      case 'data':
        return <PersonalVideo />;
      default:
        return <Privacy />;
    }
  };

  const groupedSettings = settings.reduce((acc, setting) => {
    if (!acc[setting.category]) {
      acc[setting.category] = [];
    }
    acc[setting.category].push(setting);
    return acc;
  }, {} as Record<string, PrivacySetting[]>);

  if (loading && settings.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Privacy & GDPR Compliance
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

      {/* Privacy Settings by Category */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Privacy Settings
          </Typography>
          
          <Typography color="textSecondary" paragraph>
            Manage how your data is used and processed. You can change these settings at any time.
          </Typography>

          {Object.entries(groupedSettings).map(([category, categorySettings]) => (
            <Accordion key={category} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box display="flex" alignItems="center" gap={2}>
                  {getCategoryIcon(category)}
                  <Box>
                    <Typography variant="subtitle1">
                      {PRIVACY_CATEGORIES[category as keyof typeof PRIVACY_CATEGORIES]?.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {PRIVACY_CATEGORIES[category as keyof typeof PRIVACY_CATEGORIES]?.description}
                    </Typography>
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {categorySettings.map((setting) => (
                    <ListItem key={setting.id}>
                      <ListItemIcon>
                        <Chip
                          size="small"
                          label={setting.required ? 'Required' : 'Optional'}
                          color={setting.required ? 'primary' : 'default'}
                          variant={setting.required ? 'filled' : 'outlined'}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={setting.name}
                        secondary={setting.description}
                      />
                      <ListItemSecondaryAction>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={setting.enabled}
                              disabled={setting.required}
                              onChange={(e) => updatePrivacySetting(setting.id, e.target.checked)}
                            />
                          }
                          label=""
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Data Rights */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Your Data Rights
              </Typography>
              
              <Typography color="textSecondary" paragraph>
                Under GDPR, you have several rights regarding your personal data.
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Download />
                  </ListItemIcon>
                  <ListItemText
                    primary="Right to Data Portability"
                    secondary="Export your data in a machine-readable format"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Delete />
                  </ListItemIcon>
                  <ListItemText
                    primary="Right to Erasure"
                    secondary="Request deletion of your personal data"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Warning />
                  </ListItemIcon>
                  <ListItemText
                    primary="Right to Rectification"
                    secondary="Request correction of inaccurate data"
                  />
                </ListItem>
              </List>
              
              <Button
                variant="contained"
                onClick={() => setShowDataRequest(true)}
                sx={{ mt: 2 }}
                fullWidth
              >
                Make Data Request
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Consent History
              </Typography>
              
              <Typography color="textSecondary" paragraph>
                View your privacy consent history and decisions.
              </Typography>
              
              <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
                <Typography variant="body2" color="textSecondary">
                  Total consents recorded: {consentHistory.length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Last updated: {consentHistory[0]?.timestamp ? new Date(consentHistory[0].timestamp).toLocaleDateString() : 'Never'}
                </Typography>
              </Paper>
              
              <Button
                variant="outlined"
                onClick={() => setShowConsentHistory(true)}
                sx={{ mt: 2 }}
                fullWidth
              >
                View Full History
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Requests */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Requests
          </Typography>
          
          {dataRequests.length === 0 ? (
            <Typography color="textSecondary">
              No data requests submitted yet.
            </Typography>
          ) : (
            <List>
              {dataRequests.map((request) => (
                <ListItem key={request.id}>
                  <ListItemIcon>
                    {getStatusIcon(request.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={`${request.type.charAt(0).toUpperCase() + request.type.slice(1)} Request`}
                    secondary={`Submitted: ${new Date(request.requestedAt).toLocaleDateString()} • Status: ${request.status}`}
                  />
                  <ListItemSecondaryAction>
                    {request.status === 'completed' && request.downloadUrl && (
                      <Button
                        size="small"
                        startIcon={<Download />}
                        onClick={() => downloadData(request.id)}
                      >
                        Download
                      </Button>
                    )}
                    <Chip
                      label={request.status}
                      size="small"
                      color={request.status === 'completed' ? 'success' : 
                             request.status === 'failed' ? 'error' : 'default'}
                      sx={{ ml: 1 }}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Data Request Dialog */}
      <Dialog open={showDataRequest} onClose={() => setShowDataRequest(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Data Request</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              select
              label="Request Type"
              value={requestType}
              onChange={(e) => setRequestType(e.target.value as any)}
              fullWidth
              sx={{ mb: 3 }}
            >
              <MenuItem value="export">Data Export</MenuItem>
              <MenuItem value="deletion">Data Deletion</MenuItem>
              <MenuItem value="correction">Data Correction</MenuItem>
            </TextField>
            
            <TextField
              label="Reason for Request"
              value={requestReason}
              onChange={(e) => setRequestReason(e.target.value)}
              multiline
              rows={4}
              fullWidth
              placeholder="Please provide a reason for your request..."
            />
            
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                {requestType === 'export' && 'Your data will be exported in JSON format and available for download.'}
                {requestType === 'deletion' && 'This will permanently delete your personal data. This action cannot be undone.'}
                {requestType === 'correction' && 'Please describe what data needs to be corrected and provide the correct information.'}
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDataRequest(false)}>
            Cancel
          </Button>
          <Button
            onClick={submitDataRequest}
            variant="contained"
            disabled={loading || !requestReason.trim()}
          >
            {loading ? 'Submitting...' : 'Submit Request'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Consent History Dialog */}
      <Dialog open={showConsentHistory} onClose={() => setShowConsentHistory(false)} maxWidth="md" fullWidth>
        <DialogTitle>Consent History</DialogTitle>
        <DialogContent>
          <List>
            {consentHistory.map((consent) => (
              <ListItem key={consent.id}>
                <ListItemIcon>
                  {consent.granted ? <CheckCircle color="success" /> : <Warning color="error" />}
                </ListItemIcon>
                <ListItemText
                  primary={consent.type}
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary">
                        {consent.granted ? 'Granted' : 'Denied'} on {new Date(consent.timestamp).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Version: {consent.version} • IP: {consent.ipAddress}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConsentHistory(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PrivacyCompliance;
