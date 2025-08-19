import React, { useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Tabs,
  Tab,
  Switch,
  FormControl,
  FormControlLabel,
  FormGroup,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Slider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  RadioGroup,
  Radio,
  FormLabel,
  Checkbox,
  Paper,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge
} from '@mui/material';
import {
  Notifications,
  Security,
  Monitor,
  Language,
  Storage,
  Api,
  Tune,
  ExpandMore,
  Save,
  RestoreFromTrash,
  Info,
  Warning,
  CheckCircle,
  Error,
  Email,
  Sms,
  Phone,
  Computer,
  PhoneIphone,
  DarkMode,
  LightMode,
  AutoMode,
  Speed,
  VolumeUp,
  VolumeOff,
  Visibility,
  VisibilityOff,
  Download,
  CloudSync,
  Lock,
  Shield,
  Key,
  AccountCircle,
  Timeline,
  Assessment,
  TrendingUp,
  MonetizationOn,
  EmojiEvents,
  Camera,
  Mic,
  LocationOn,
  Bluetooth,
  Wifi,
  PersonalVideo
} from '@mui/icons-material';

interface NotificationSettings {
  email: {
    enabled: boolean;
    bet_confirmations: boolean;
    result_updates: boolean;
    balance_alerts: boolean;
    promotional: boolean;
    weekly_reports: boolean;
    security_alerts: boolean;
  };
  push: {
    enabled: boolean;
    race_starts: boolean;
    odds_changes: boolean;
    live_results: boolean;
    portfolio_alerts: boolean;
    system_maintenance: boolean;
  };
  sms: {
    enabled: boolean;
    large_wins: boolean;
    account_security: boolean;
    payment_confirmations: boolean;
  };
}

interface DisplaySettings {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  currency: string;
  odds_format: 'decimal' | 'fractional' | 'american';
  date_format: 'DD/MM/YYYY' | 'MM/DD/YYYY' | 'YYYY-MM-DD';
  time_format: '12h' | '24h';
  compact_mode: boolean;
  animations: boolean;
  sound_effects: boolean;
  high_contrast: boolean;
}

interface PrivacySettings {
  profile_visibility: 'public' | 'friends' | 'private';
  show_betting_activity: boolean;
  show_statistics: boolean;
  allow_friend_requests: boolean;
  data_collection: boolean;
  analytics_tracking: boolean;
  personalized_ads: boolean;
  location_services: boolean;
  camera_access: boolean;
  microphone_access: boolean;
  contacts_access: boolean;
}

interface APISettings {
  api_key_enabled: boolean;
  webhook_url: string;
  rate_limit: number;
  allowed_origins: string[];
  ip_whitelist: string[];
  api_version: string;
  debug_mode: boolean;
}

interface AutomationSettings {
  auto_bet_enabled: boolean;
  auto_bet_amount: number;
  auto_bet_conditions: string[];
  stop_loss_enabled: boolean;
  stop_loss_amount: number;
  profit_target_enabled: boolean;
  profit_target_amount: number;
  email_reports_enabled: boolean;
  report_frequency: 'daily' | 'weekly' | 'monthly';
  backup_frequency: 'daily' | 'weekly' | 'monthly' | 'never';
}

export const UserSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetCategory, setResetCategory] = useState<string>('');

  const [notifications, setNotifications] = useState<NotificationSettings>({
    email: {
      enabled: true,
      bet_confirmations: true,
      result_updates: true,
      balance_alerts: true,
      promotional: false,
      weekly_reports: true,
      security_alerts: true
    },
    push: {
      enabled: true,
      race_starts: true,
      odds_changes: false,
      live_results: true,
      portfolio_alerts: true,
      system_maintenance: true
    },
    sms: {
      enabled: false,
      large_wins: false,
      account_security: true,
      payment_confirmations: false
    }
  });

  const [display, setDisplay] = useState<DisplaySettings>({
    theme: 'auto',
    language: 'en',
    timezone: 'Europe/London',
    currency: 'GBP',
    odds_format: 'decimal',
    date_format: 'DD/MM/YYYY',
    time_format: '24h',
    compact_mode: false,
    animations: true,
    sound_effects: true,
    high_contrast: false
  });

  const [privacy, setPrivacy] = useState<PrivacySettings>({
    profile_visibility: 'private',
    show_betting_activity: false,
    show_statistics: true,
    allow_friend_requests: true,
    data_collection: true,
    analytics_tracking: true,
    personalized_ads: false,
    location_services: false,
    camera_access: false,
    microphone_access: false,
    contacts_access: false
  });

  const [apiSettings, setApiSettings] = useState<APISettings>({
    api_key_enabled: false,
    webhook_url: '',
    rate_limit: 1000,
    allowed_origins: [],
    ip_whitelist: [],
    api_version: 'v1',
    debug_mode: false
  });

  const [automation, setAutomation] = useState<AutomationSettings>({
    auto_bet_enabled: false,
    auto_bet_amount: 10,
    auto_bet_conditions: [],
    stop_loss_enabled: false,
    stop_loss_amount: 100,
    profit_target_enabled: false,
    profit_target_amount: 500,
    email_reports_enabled: true,
    report_frequency: 'weekly',
    backup_frequency: 'weekly'
  });

  const handleSave = useCallback(() => {
    // Here you would save all settings to the backend
    console.log('Saving settings:', {
      notifications,
      display,
      privacy,
      apiSettings,
      automation
    });
    setUnsavedChanges(false);
  }, [notifications, display, privacy, apiSettings, automation]);

  const handleReset = useCallback((category: string) => {
    setResetCategory(category);
    setResetDialogOpen(true);
  }, []);

  const confirmReset = useCallback(() => {
    switch (resetCategory) {
      case 'notifications':
        setNotifications({
          email: {
            enabled: true,
            bet_confirmations: true,
            result_updates: true,
            balance_alerts: true,
            promotional: false,
            weekly_reports: true,
            security_alerts: true
          },
          push: {
            enabled: true,
            race_starts: true,
            odds_changes: false,
            live_results: true,
            portfolio_alerts: true,
            system_maintenance: true
          },
          sms: {
            enabled: false,
            large_wins: false,
            account_security: true,
            payment_confirmations: false
          }
        });
        break;
      case 'display':
        setDisplay({
          theme: 'auto',
          language: 'en',
          timezone: 'Europe/London',
          currency: 'GBP',
          odds_format: 'decimal',
          date_format: 'DD/MM/YYYY',
          time_format: '24h',
          compact_mode: false,
          animations: true,
          sound_effects: true,
          high_contrast: false
        });
        break;
      // Add other reset cases...
    }
    setResetDialogOpen(false);
    setUnsavedChanges(true);
  }, [resetCategory]);

  const updateNotificationSetting = useCallback((category: keyof NotificationSettings, key: string, value: boolean) => {
    setNotifications(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
    setUnsavedChanges(true);
  }, []);

  const updateDisplaySetting = useCallback((key: keyof DisplaySettings, value: any) => {
    setDisplay(prev => ({
      ...prev,
      [key]: value
    }));
    setUnsavedChanges(true);
  }, []);

  const updatePrivacySetting = useCallback((key: keyof PrivacySettings, value: any) => {
    setPrivacy(prev => ({
      ...prev,
      [key]: value
    }));
    setUnsavedChanges(true);
  }, []);

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              ⚙️ User Settings
            </Typography>
            <Box display="flex" gap={2}>
              {unsavedChanges && (
                <Badge color="warning" variant="dot">
                  <Button variant="contained" onClick={handleSave} startIcon={<Save />}>
                    Save Changes
                  </Button>
                </Badge>
              )}
            </Box>
          </Box>

          {unsavedChanges && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              You have unsaved changes. Don't forget to save your settings!
            </Alert>
          )}
        </CardContent>
      </Card>

      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)} 
        sx={{ mb: 3 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="🔔 Notifications" />
        <Tab label="🎨 Display" />
        <Tab label="🔒 Privacy" />
        <Tab label="🔧 Automation" />
        <Tab label="🔌 API" />
        <Tab label="📱 Device" />
      </Tabs>

      {/* Notifications Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography variant="h6">
                    Notification Preferences
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleReset('notifications')}
                    startIcon={<RestoreFromTrash />}
                  >
                    Reset to Defaults
                  </Button>
                </Box>

                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Email />
                      <Typography variant="h6">Email Notifications</Typography>
                      <Switch
                        checked={notifications.email.enabled}
                        onChange={(e) => updateNotificationSetting('email', 'enabled', e.target.checked)}
                        size="small"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <FormGroup>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.bet_confirmations}
                            onChange={(e) => updateNotificationSetting('email', 'bet_confirmations', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Bet confirmations and receipts"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.result_updates}
                            onChange={(e) => updateNotificationSetting('email', 'result_updates', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Race results and winnings"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.balance_alerts}
                            onChange={(e) => updateNotificationSetting('email', 'balance_alerts', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Account balance alerts"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.weekly_reports}
                            onChange={(e) => updateNotificationSetting('email', 'weekly_reports', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Weekly performance reports"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.security_alerts}
                            onChange={(e) => updateNotificationSetting('email', 'security_alerts', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Security and login alerts"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.email.promotional}
                            onChange={(e) => updateNotificationSetting('email', 'promotional', e.target.checked)}
                            disabled={!notifications.email.enabled}
                          />
                        }
                        label="Promotional offers and updates"
                      />
                    </FormGroup>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Notifications />
                      <Typography variant="h6">Push Notifications</Typography>
                      <Switch
                        checked={notifications.push.enabled}
                        onChange={(e) => updateNotificationSetting('push', 'enabled', e.target.checked)}
                        size="small"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <FormGroup>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.push.race_starts}
                            onChange={(e) => updateNotificationSetting('push', 'race_starts', e.target.checked)}
                            disabled={!notifications.push.enabled}
                          />
                        }
                        label="Race starting soon"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.push.odds_changes}
                            onChange={(e) => updateNotificationSetting('push', 'odds_changes', e.target.checked)}
                            disabled={!notifications.push.enabled}
                          />
                        }
                        label="Significant odds changes"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.push.live_results}
                            onChange={(e) => updateNotificationSetting('push', 'live_results', e.target.checked)}
                            disabled={!notifications.push.enabled}
                          />
                        }
                        label="Live race results"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.push.portfolio_alerts}
                            onChange={(e) => updateNotificationSetting('push', 'portfolio_alerts', e.target.checked)}
                            disabled={!notifications.push.enabled}
                          />
                        }
                        label="Portfolio performance alerts"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.push.system_maintenance}
                            onChange={(e) => updateNotificationSetting('push', 'system_maintenance', e.target.checked)}
                            disabled={!notifications.push.enabled}
                          />
                        }
                        label="System maintenance notifications"
                      />
                    </FormGroup>
                  </AccordionDetails>
                </Accordion>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Sms />
                      <Typography variant="h6">SMS Notifications</Typography>
                      <Switch
                        checked={notifications.sms.enabled}
                        onChange={(e) => updateNotificationSetting('sms', 'enabled', e.target.checked)}
                        size="small"
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      SMS notifications may incur additional charges from your mobile provider.
                    </Alert>
                    <FormGroup>
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.sms.large_wins}
                            onChange={(e) => updateNotificationSetting('sms', 'large_wins', e.target.checked)}
                            disabled={!notifications.sms.enabled}
                          />
                        }
                        label="Large wins (£100+)"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.sms.account_security}
                            onChange={(e) => updateNotificationSetting('sms', 'account_security', e.target.checked)}
                            disabled={!notifications.sms.enabled}
                          />
                        }
                        label="Account security alerts"
                      />
                      <FormControlLabel
                        control={
                          <Checkbox
                            checked={notifications.sms.payment_confirmations}
                            onChange={(e) => updateNotificationSetting('sms', 'payment_confirmations', e.target.checked)}
                            disabled={!notifications.sms.enabled}
                          />
                        }
                        label="Payment confirmations"
                      />
                    </FormGroup>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Display Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🎨 Appearance
                </Typography>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <FormLabel component="legend">Theme</FormLabel>
                  <RadioGroup
                    value={display.theme}
                    onChange={(e) => updateDisplaySetting('theme', e.target.value)}
                    row
                  >
                    <FormControlLabel value="light" control={<Radio />} label={<Box display="flex" alignItems="center" gap={1}><LightMode fontSize="small" />Light</Box>} />
                    <FormControlLabel value="dark" control={<Radio />} label={<Box display="flex" alignItems="center" gap={1}><DarkMode fontSize="small" />Dark</Box>} />
                    <FormControlLabel value="auto" control={<Radio />} label={<Box display="flex" alignItems="center" gap={1}><AutoMode fontSize="small" />Auto</Box>} />
                  </RadioGroup>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={display.compact_mode}
                      onChange={(e) => updateDisplaySetting('compact_mode', e.target.checked)}
                    />
                  }
                  label="Compact mode"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={display.animations}
                      onChange={(e) => updateDisplaySetting('animations', e.target.checked)}
                    />
                  }
                  label="Enable animations"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={display.sound_effects}
                      onChange={(e) => updateDisplaySetting('sound_effects', e.target.checked)}
                    />
                  }
                  label="Sound effects"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={display.high_contrast}
                      onChange={(e) => updateDisplaySetting('high_contrast', e.target.checked)}
                    />
                  }
                  label="High contrast mode"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🌍 Localization
                </Typography>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Language</InputLabel>
                  <Select
                    value={display.language}
                    label="Language"
                    onChange={(e) => updateDisplaySetting('language', e.target.value)}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Español</MenuItem>
                    <MenuItem value="fr">Français</MenuItem>
                    <MenuItem value="de">Deutsch</MenuItem>
                    <MenuItem value="it">Italiano</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Timezone</InputLabel>
                  <Select
                    value={display.timezone}
                    label="Timezone"
                    onChange={(e) => updateDisplaySetting('timezone', e.target.value)}
                  >
                    <MenuItem value="Europe/London">London (GMT)</MenuItem>
                    <MenuItem value="Europe/Paris">Paris (CET)</MenuItem>
                    <MenuItem value="America/New_York">New York (EST)</MenuItem>
                    <MenuItem value="America/Los_Angeles">Los Angeles (PST)</MenuItem>
                    <MenuItem value="Asia/Tokyo">Tokyo (JST)</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={display.currency}
                    label="Currency"
                    onChange={(e) => updateDisplaySetting('currency', e.target.value)}
                  >
                    <MenuItem value="GBP">British Pound (£)</MenuItem>
                    <MenuItem value="EUR">Euro (€)</MenuItem>
                    <MenuItem value="USD">US Dollar ($)</MenuItem>
                    <MenuItem value="CAD">Canadian Dollar (C$)</MenuItem>
                    <MenuItem value="AUD">Australian Dollar (A$)</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Odds Format</InputLabel>
                  <Select
                    value={display.odds_format}
                    label="Odds Format"
                    onChange={(e) => updateDisplaySetting('odds_format', e.target.value)}
                  >
                    <MenuItem value="decimal">Decimal (1.50)</MenuItem>
                    <MenuItem value="fractional">Fractional (1/2)</MenuItem>
                    <MenuItem value="american">American (+150)</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Date Format</InputLabel>
                  <Select
                    value={display.date_format}
                    label="Date Format"
                    onChange={(e) => updateDisplaySetting('date_format', e.target.value)}
                  >
                    <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                    <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                    <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Time Format</InputLabel>
                  <Select
                    value={display.time_format}
                    label="Time Format"
                    onChange={(e) => updateDisplaySetting('time_format', e.target.value)}
                  >
                    <MenuItem value="12h">12-hour (2:30 PM)</MenuItem>
                    <MenuItem value="24h">24-hour (14:30)</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Privacy Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  👥 Profile Privacy
                </Typography>
                
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <FormLabel component="legend">Profile Visibility</FormLabel>
                  <RadioGroup
                    value={privacy.profile_visibility}
                    onChange={(e) => updatePrivacySetting('profile_visibility', e.target.value)}
                  >
                    <FormControlLabel value="public" control={<Radio />} label="Public - Anyone can see your profile" />
                    <FormControlLabel value="friends" control={<Radio />} label="Friends only - Only your friends can see your profile" />
                    <FormControlLabel value="private" control={<Radio />} label="Private - Only you can see your profile" />
                  </RadioGroup>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.show_betting_activity}
                      onChange={(e) => updatePrivacySetting('show_betting_activity', e.target.checked)}
                    />
                  }
                  label="Show betting activity to friends"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.show_statistics}
                      onChange={(e) => updatePrivacySetting('show_statistics', e.target.checked)}
                    />
                  }
                  label="Show performance statistics"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.allow_friend_requests}
                      onChange={(e) => updatePrivacySetting('allow_friend_requests', e.target.checked)}
                    />
                  }
                  label="Allow friend requests"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📊 Data & Analytics
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.data_collection}
                      onChange={(e) => updatePrivacySetting('data_collection', e.target.checked)}
                    />
                  }
                  label="Allow data collection for service improvement"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.analytics_tracking}
                      onChange={(e) => updatePrivacySetting('analytics_tracking', e.target.checked)}
                    />
                  }
                  label="Analytics tracking"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.personalized_ads}
                      onChange={(e) => updatePrivacySetting('personalized_ads', e.target.checked)}
                    />
                  }
                  label="Personalized advertisements"
                  sx={{ mb: 2, display: 'block' }}
                />

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>
                  📱 Device Permissions
                </Typography>

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.location_services}
                      onChange={(e) => updatePrivacySetting('location_services', e.target.checked)}
                    />
                  }
                  label="Location services"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.camera_access}
                      onChange={(e) => updatePrivacySetting('camera_access', e.target.checked)}
                    />
                  }
                  label="Camera access"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.microphone_access}
                      onChange={(e) => updatePrivacySetting('microphone_access', e.target.checked)}
                    />
                  }
                  label="Microphone access"
                  sx={{ mb: 2, display: 'block' }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={privacy.contacts_access}
                      onChange={(e) => updatePrivacySetting('contacts_access', e.target.checked)}
                    />
                  }
                  label="Contacts access"
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Automation Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                ⚠️ Automated Betting Warning
              </Typography>
              Automated betting features should be used with extreme caution. Always set appropriate limits and monitor your account regularly.
            </Alert>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🤖 Auto-Betting
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={automation.auto_bet_enabled}
                      onChange={(e) => setAutomation(prev => ({ ...prev, auto_bet_enabled: e.target.checked }))}
                    />
                  }
                  label="Enable auto-betting"
                  sx={{ mb: 2, display: 'block' }}
                />

                {automation.auto_bet_enabled && (
                  <Box>
                    <Typography variant="body2" gutterBottom>
                      Default Auto-Bet Amount: £{automation.auto_bet_amount}
                    </Typography>
                    <Slider
                      value={automation.auto_bet_amount}
                      onChange={(_, value) => setAutomation(prev => ({ ...prev, auto_bet_amount: value as number }))}
                      min={1}
                      max={100}
                      valueLabelDisplay="auto"
                      sx={{ mb: 2 }}
                    />

                    <Typography variant="body2" gutterBottom>
                      Auto-bet conditions:
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                      {automation.auto_bet_conditions.map((condition, index) => (
                        <Chip key={index} label={condition} size="small" />
                      ))}
                      {automation.auto_bet_conditions.length === 0 && (
                        <Typography variant="caption" color="text.secondary">
                          No conditions set
                        </Typography>
                      )}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  ⚡ Risk Management
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={automation.stop_loss_enabled}
                      onChange={(e) => setAutomation(prev => ({ ...prev, stop_loss_enabled: e.target.checked }))}
                    />
                  }
                  label="Stop-loss protection"
                  sx={{ mb: 2, display: 'block' }}
                />

                {automation.stop_loss_enabled && (
                  <Box mb={2}>
                    <Typography variant="body2" gutterBottom>
                      Stop-loss amount: £{automation.stop_loss_amount}
                    </Typography>
                    <Slider
                      value={automation.stop_loss_amount}
                      onChange={(_, value) => setAutomation(prev => ({ ...prev, stop_loss_amount: value as number }))}
                      min={10}
                      max={1000}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                )}

                <FormControlLabel
                  control={
                    <Switch
                      checked={automation.profit_target_enabled}
                      onChange={(e) => setAutomation(prev => ({ ...prev, profit_target_enabled: e.target.checked }))}
                    />
                  }
                  label="Profit target"
                  sx={{ mb: 2, display: 'block' }}
                />

                {automation.profit_target_enabled && (
                  <Box>
                    <Typography variant="body2" gutterBottom>
                      Profit target: £{automation.profit_target_amount}
                    </Typography>
                    <Slider
                      value={automation.profit_target_amount}
                      onChange={(_, value) => setAutomation(prev => ({ ...prev, profit_target_amount: value as number }))}
                      min={50}
                      max={2000}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📧 Reports & Backups
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={automation.email_reports_enabled}
                          onChange={(e) => setAutomation(prev => ({ ...prev, email_reports_enabled: e.target.checked }))}
                        />
                      }
                      label="Email reports"
                      sx={{ mb: 2, display: 'block' }}
                    />
                    
                    {automation.email_reports_enabled && (
                      <FormControl fullWidth>
                        <InputLabel>Report Frequency</InputLabel>
                        <Select
                          value={automation.report_frequency}
                          label="Report Frequency"
                          onChange={(e) => setAutomation(prev => ({ ...prev, report_frequency: e.target.value as any }))}
                        >
                          <MenuItem value="daily">Daily</MenuItem>
                          <MenuItem value="weekly">Weekly</MenuItem>
                          <MenuItem value="monthly">Monthly</MenuItem>
                        </Select>
                      </FormControl>
                    )}
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <Typography variant="body2" gutterBottom>
                      Data Backup Frequency
                    </Typography>
                    <FormControl fullWidth>
                      <InputLabel>Backup Frequency</InputLabel>
                      <Select
                        value={automation.backup_frequency}
                        label="Backup Frequency"
                        onChange={(e) => setAutomation(prev => ({ ...prev, backup_frequency: e.target.value as any }))}
                      >
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="weekly">Weekly</MenuItem>
                        <MenuItem value="monthly">Monthly</MenuItem>
                        <MenuItem value="never">Never</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Reset Confirmation Dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)}>
        <DialogTitle>
          Reset {resetCategory} Settings
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to reset all {resetCategory} settings to their default values? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={confirmReset} color="warning" variant="contained">
            Reset Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserSettings;
