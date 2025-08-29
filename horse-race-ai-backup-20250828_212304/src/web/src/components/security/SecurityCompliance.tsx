import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Grid,
  Button,
  Alert
} from '@mui/material';
import {
  Security,
  Shield,
  Lock,
  VpnKey,
  Fingerprint,
  PhonelinkLock,
  VerifiedUser,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  Download,
  Upload,
  PolicyOutlined as Privacy,
  Gavel,
  Assessment,
  Timeline,
  BarChart,
  TrendingUp,
  TrendingDown,
  Speed,
  Storage,
  Cloud,
  DeviceHub,
  NetworkCheck,
  BugReport,
  NotificationsActive
} from '@mui/icons-material';
import TwoFactorAuth from './TwoFactorAuth';
import PrivacyCompliance from './PrivacyCompliance';
import FraudPrevention from './FraudPrevention';

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
      id={`security-tabpanel-${index}`}
      aria-labelledby={`security-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `security-tab-${index}`,
    'aria-controls': `security-tabpanel-${index}`,
  };
}

export const SecurityCompliance: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [securityStatus, setSecurityStatus] = useState({
    twoFactorEnabled: false,
    privacyCompliant: false,
    fraudProtectionActive: false
  });

  useEffect(() => {
    loadSecurityStatus();
  }, []);

  const loadSecurityStatus = async () => {
    try {
      const response = await fetch('/api/security/status', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setSecurityStatus(data);
      }
    } catch (err) {
      console.error('Failed to load security status:', err);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security & Compliance
      </Typography>

      <Typography color="textSecondary" paragraph>
        Manage security settings, privacy compliance, and fraud prevention for your Horse Racing AI platform.
      </Typography>

      {/* Security Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Security color={securityStatus.twoFactorEnabled ? 'success' : 'error'} />
                <Typography variant="h6">
                  Two-Factor Authentication
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" paragraph>
                {securityStatus.twoFactorEnabled 
                  ? 'Your account is protected with 2FA'
                  : 'Enable 2FA to secure your account'
                }
              </Typography>
              <Button
                variant={securityStatus.twoFactorEnabled ? 'outlined' : 'contained'}
                onClick={() => setCurrentTab(0)}
                size="small"
              >
                {securityStatus.twoFactorEnabled ? 'Manage 2FA' : 'Enable 2FA'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Privacy color={securityStatus.privacyCompliant ? 'success' : 'warning'} />
                <Typography variant="h6">
                  Privacy & GDPR
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" paragraph>
                {securityStatus.privacyCompliant 
                  ? 'GDPR compliant data processing'
                  : 'Review privacy settings'
                }
              </Typography>
              <Button
                variant="outlined"
                onClick={() => setCurrentTab(1)}
                size="small"
              >
                Privacy Settings
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <Shield color={securityStatus.fraudProtectionActive ? 'success' : 'error'} />
                <Typography variant="h6">
                  Fraud Prevention
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" paragraph>
                {securityStatus.fraudProtectionActive 
                  ? 'Active fraud monitoring enabled'
                  : 'Configure fraud protection'
                }
              </Typography>
              <Button
                variant="outlined"
                onClick={() => setCurrentTab(2)}
                size="small"
              >
                Fraud Settings
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Security Alert */}
      {(!securityStatus.twoFactorEnabled || !securityStatus.fraudProtectionActive) && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            Your security settings need attention. Consider enabling two-factor authentication and fraud prevention for optimal security.
          </Typography>
        </Alert>
      )}

      {/* Security Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange} 
            aria-label="security compliance tabs"
            variant="fullWidth"
          >
            <Tab 
              label="Two-Factor Authentication" 
              icon={<Security />} 
              iconPosition="start"
              {...a11yProps(0)} 
            />
            <Tab 
              label="Privacy & GDPR" 
              icon={<Privacy />} 
              iconPosition="start"
              {...a11yProps(1)} 
            />
            <Tab 
              label="Fraud Prevention" 
              icon={<Shield />} 
              iconPosition="start"
              {...a11yProps(2)} 
            />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <TwoFactorAuth />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <PrivacyCompliance />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <FraudPrevention />
        </TabPanel>
      </Card>
    </Box>
  );
};

export default SecurityCompliance;
