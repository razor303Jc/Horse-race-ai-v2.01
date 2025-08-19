import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Switch,
  FormControlLabel,
  Paper,
  Divider
} from '@mui/material';
import {
  Security,
  Smartphone,
  QrCode,
  Key,
  Delete,
  Add,
  CheckCircle,
  Warning,
  Info,
  Backup,
  Download
} from '@mui/icons-material';
import { QRCodeSVG } from 'qrcode.react';

interface BackupCode {
  code: string;
  used: boolean;
  usedAt?: string;
}

interface AuthDevice {
  id: string;
  name: string;
  type: 'authenticator' | 'sms' | 'email';
  enabled: boolean;
  lastUsed?: string;
  createdAt: string;
}

interface TwoFactorSetup {
  secret: string;
  qrCodeUrl: string;
  backupCodes: string[];
  manualEntryKey: string;
}

export const TwoFactorAuth: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [setupData, setSetupData] = useState<TwoFactorSetup | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEnabled, setIsEnabled] = useState(false);
  const [devices, setDevices] = useState<AuthDevice[]>([]);
  const [backupCodes, setBackupCodes] = useState<BackupCode[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const [showAddDevice, setShowAddDevice] = useState(false);

  const steps = [
    'Setup Authenticator',
    'Verify Code',
    'Save Backup Codes',
    'Complete Setup'
  ];

  useEffect(() => {
    loadTwoFactorStatus();
  }, []);

  const loadTwoFactorStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/auth/2fa/status', {
        credentials: 'include'
      });
      const data = await response.json();
      
      if (response.ok) {
        setIsEnabled(data.enabled);
        setDevices(data.devices || []);
        setBackupCodes(data.backupCodes || []);
      }
    } catch (err) {
      setError('Failed to load 2FA status');
    } finally {
      setLoading(false);
    }
  };

  const initiateTwoFactorSetup = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/auth/2fa/setup', {
        method: 'POST',
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSetupData(data);
        setCurrentStep(1);
      } else {
        setError(data.message || 'Failed to initiate 2FA setup');
      }
    } catch (err) {
      setError('Network error during 2FA setup');
    } finally {
      setLoading(false);
    }
  };

  const verifyTwoFactorCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/auth/2fa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          code: verificationCode,
          secret: setupData?.secret
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setCurrentStep(2);
        setBackupCodes(data.backupCodes?.map((code: string) => ({
          code,
          used: false
        })) || []);
        setSuccess('2FA code verified successfully!');
      } else {
        setError(data.message || 'Invalid verification code');
      }
    } catch (err) {
      setError('Network error during verification');
    } finally {
      setLoading(false);
    }
  };

  const completeTwoFactorSetup = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/auth/2fa/complete', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        setIsEnabled(true);
        setCurrentStep(3);
        setSuccess('Two-factor authentication enabled successfully!');
        await loadTwoFactorStatus();
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to complete 2FA setup');
      }
    } catch (err) {
      setError('Network error during setup completion');
    } finally {
      setLoading(false);
    }
  };

  const disableTwoFactor = async () => {
    if (!window.confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/auth/2fa/disable', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        setIsEnabled(false);
        setDevices([]);
        setBackupCodes([]);
        setCurrentStep(0);
        setSetupData(null);
        setSuccess('Two-factor authentication disabled');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to disable 2FA');
      }
    } catch (err) {
      setError('Network error while disabling 2FA');
    } finally {
      setLoading(false);
    }
  };

  const generateNewBackupCodes = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/auth/2fa/backup-codes/regenerate', {
        method: 'POST',
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setBackupCodes(data.backupCodes?.map((code: string) => ({
          code,
          used: false
        })) || []);
        setSuccess('New backup codes generated');
        setShowBackupCodes(true);
      } else {
        setError(data.message || 'Failed to generate backup codes');
      }
    } catch (err) {
      setError('Network error while generating backup codes');
    } finally {
      setLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const codesText = backupCodes.map(bc => bc.code).join('\n');
    const blob = new Blob([`Horse Racing AI - Backup Codes\n\n${codesText}\n\nKeep these codes safe and secure!`], {
      type: 'text/plain'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'horse-racing-ai-backup-codes.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const removeDevice = async (deviceId: string) => {
    if (!window.confirm('Are you sure you want to remove this device?')) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`/api/auth/2fa/devices/${deviceId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (response.ok) {
        await loadTwoFactorStatus();
        setSuccess('Device removed successfully');
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to remove device');
      }
    } catch (err) {
      setError('Network error while removing device');
    } finally {
      setLoading(false);
    }
  };

  const renderSetupStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Scan QR Code
            </Typography>
            <Typography color="textSecondary" paragraph>
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </Typography>
            
            {setupData && (
              <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
                <Paper elevation={2} sx={{ p: 2, display: 'inline-block' }}>
                  <QRCodeSVG value={setupData.qrCodeUrl} size={200} />
                </Paper>
                
                <Box textAlign="center">
                  <Typography variant="subtitle2" gutterBottom>
                    Manual Entry Key:
                  </Typography>
                  <Typography 
                    variant="body2" 
                    fontFamily="monospace"
                    sx={{ 
                      backgroundColor: 'grey.100', 
                      p: 1, 
                      borderRadius: 1,
                      wordBreak: 'break-all'
                    }}
                  >
                    {setupData.manualEntryKey}
                  </Typography>
                </Box>
                
                <TextField
                  label="Verification Code"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="123456"
                  fullWidth
                  inputProps={{ 
                    maxLength: 6,
                    style: { textAlign: 'center', fontSize: '1.5rem' }
                  }}
                />
                
                <Button
                  variant="contained"
                  onClick={verifyTwoFactorCode}
                  disabled={loading || verificationCode.length !== 6}
                  startIcon={loading ? <CircularProgress size={20} /> : <CheckCircle />}
                  fullWidth
                >
                  {loading ? 'Verifying...' : 'Verify Code'}
                </Button>
              </Box>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Save Backup Codes
            </Typography>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
              </Typography>
            </Alert>
            
            <Paper sx={{ p: 2, mb: 3, backgroundColor: 'grey.50' }}>
              <Box display="grid" gridTemplateColumns="1fr 1fr" gap={1}>
                {backupCodes.map((backup, index) => (
                  <Typography 
                    key={index}
                    variant="body2" 
                    fontFamily="monospace"
                    sx={{ p: 1, backgroundColor: 'white', borderRadius: 1 }}
                  >
                    {backup.code}
                  </Typography>
                ))}
              </Box>
            </Paper>
            
            <Box display="flex" gap={2} mb={3}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={downloadBackupCodes}
                fullWidth
              >
                Download Codes
              </Button>
            </Box>
            
            <Button
              variant="contained"
              onClick={completeTwoFactorSetup}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <Security />}
              fullWidth
            >
              {loading ? 'Completing Setup...' : 'Complete Setup'}
            </Button>
          </Box>
        );

      case 3:
        return (
          <Box textAlign="center">
            <CheckCircle color="success" sx={{ fontSize: 80, mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Two-Factor Authentication Enabled!
            </Typography>
            <Typography color="textSecondary" paragraph>
              Your account is now protected with two-factor authentication.
            </Typography>
            <Button
              variant="contained"
              onClick={() => setCurrentStep(0)}
              sx={{ mt: 2 }}
            >
              Manage 2FA Settings
            </Button>
          </Box>
        );

      default:
        return null;
    }
  };

  if (loading && !setupData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Two-Factor Authentication
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

      {!isEnabled && currentStep === 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Security color="primary" />
              <Typography variant="h6">
                Enable Two-Factor Authentication
              </Typography>
            </Box>
            
            <Typography color="textSecondary" paragraph>
              Add an extra layer of security to your account. You'll need your authenticator app to sign in.
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText primary="Protects against unauthorized access" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText primary="Works with popular authenticator apps" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" />
                </ListItemIcon>
                <ListItemText primary="Backup codes for account recovery" />
              </ListItem>
            </List>
            
            <Button
              variant="contained"
              onClick={initiateTwoFactorSetup}
              disabled={loading}
              startIcon={<Security />}
              sx={{ mt: 2 }}
            >
              Enable 2FA
            </Button>
          </CardContent>
        </Card>
      )}

      {currentStep > 0 && currentStep < 3 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stepper activeStep={currentStep - 1} sx={{ mb: 4 }}>
              {steps.slice(0, 3).map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            {renderSetupStep()}
          </CardContent>
        </Card>
      )}

      {isEnabled && currentStep === 0 && (
        <>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between" mb={2}>
                <Box display="flex" alignItems="center" gap={2}>
                  <CheckCircle color="success" />
                  <Typography variant="h6">
                    Two-Factor Authentication Enabled
                  </Typography>
                </Box>
                <Chip label="Active" color="success" variant="outlined" />
              </Box>
              
              <Typography color="textSecondary" paragraph>
                Your account is protected with two-factor authentication.
              </Typography>
              
              <Box display="flex" gap={2} flexWrap="wrap">
                <Button
                  variant="outlined"
                  startIcon={<Backup />}
                  onClick={() => setShowBackupCodes(true)}
                >
                  View Backup Codes
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => setShowAddDevice(true)}
                >
                  Add Device
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Security />}
                  onClick={disableTwoFactor}
                >
                  Disable 2FA
                </Button>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Authenticated Devices
              </Typography>
              
              {devices.length === 0 ? (
                <Typography color="textSecondary">
                  No devices configured
                </Typography>
              ) : (
                <List>
                  {devices.map((device) => (
                    <ListItem key={device.id}>
                      <ListItemIcon>
                        <Smartphone />
                      </ListItemIcon>
                      <ListItemText
                        primary={device.name}
                        secondary={`${device.type} • Last used: ${device.lastUsed || 'Never'}`}
                      />
                      <FormControlLabel
                        control={<Switch checked={device.enabled} />}
                        label=""
                      />
                      <IconButton
                        color="error"
                        onClick={() => removeDevice(device.id)}
                      >
                        <Delete />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </>
      )}

      <Dialog open={showBackupCodes} onClose={() => setShowBackupCodes(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Backup Codes</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Each backup code can only be used once. Generate new codes if you've used most of them.
          </Alert>
          
          <Paper sx={{ p: 2, backgroundColor: 'grey.50' }}>
            <Box display="grid" gridTemplateColumns="1fr 1fr" gap={1}>
              {backupCodes.map((backup, index) => (
                <Box key={index} display="flex" alignItems="center">
                  <Typography 
                    variant="body2" 
                    fontFamily="monospace"
                    sx={{ 
                      p: 1, 
                      backgroundColor: backup.used ? 'grey.200' : 'white', 
                      borderRadius: 1,
                      textDecoration: backup.used ? 'line-through' : 'none',
                      flex: 1
                    }}
                  >
                    {backup.code}
                  </Typography>
                  {backup.used && <Chip label="Used" size="small" sx={{ ml: 1 }} />}
                </Box>
              ))}
            </Box>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={downloadBackupCodes} startIcon={<Download />}>
            Download
          </Button>
          <Button onClick={generateNewBackupCodes} variant="outlined">
            Generate New Codes
          </Button>
          <Button onClick={() => setShowBackupCodes(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TwoFactorAuth;
