import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Tabs,
  Tab,
  Avatar,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Person,
  Settings,
  Notifications,
  Security,
  Payment,
  Analytics,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Lock,
  Email,
  Phone,
  LocationOn,
  Star,
  TrendingUp,
  MonetizationOn,
  Shield,
  Verified,
  WorkspacePremium,
  EmojiEvents,
  Timeline,
  CreditCard,
  Download,
  Upload,
  Share,
  Group,
  NotificationsActive
} from '@mui/icons-material';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  location: string;
  avatar: string;
  memberSince: string;
  lastLogin: string;
  subscription: 'free' | 'premium' | 'professional';
  verified: boolean;
  twoFactorEnabled: boolean;
  emailNotifications: boolean;
  smsNotifications: boolean;
  pushNotifications: boolean;
}

interface UserStats {
  totalBets: number;
  winRate: number;
  totalProfit: number;
  roi: number;
  avgStake: number;
  bestStreak: number;
  totalDeposits: number;
  currentBalance: number;
  rank: number;
  achievementPoints: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  earned: boolean;
  earnedDate?: string;
  progress: number;
  maxProgress: number;
}

interface NotificationPreference {
  type: string;
  label: string;
  description: string;
  email: boolean;
  sms: boolean;
  push: boolean;
}

export const UserManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [editing, setEditing] = useState(false);
  const [profileData, setProfileData] = useState<UserProfile>({
    id: '1',
    username: 'racing_pro_2024',
    email: 'user@example.com',
    firstName: 'John',
    lastName: 'Smith',
    phone: '+44 7700 123456',
    location: 'London, UK',
    avatar: '',
    memberSince: '2023-06-15',
    lastLogin: '2024-01-15T10:30:00Z',
    subscription: 'premium',
    verified: true,
    twoFactorEnabled: true,
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true
  });

  const [userStats] = useState<UserStats>({
    totalBets: 1247,
    winRate: 34.7,
    totalProfit: 2850.75,
    roi: 12.8,
    avgStake: 25.50,
    bestStreak: 8,
    totalDeposits: 15000,
    currentBalance: 3425.80,
    rank: 156,
    achievementPoints: 4275
  });

  const [achievements] = useState<Achievement[]>([
    {
      id: '1',
      title: 'First Win',
      description: 'Place your first winning bet',
      icon: '🏆',
      earned: true,
      earnedDate: '2023-06-20',
      progress: 1,
      maxProgress: 1
    },
    {
      id: '2',
      title: 'Profit Master',
      description: 'Achieve £1000 total profit',
      icon: '💰',
      earned: true,
      earnedDate: '2023-09-15',
      progress: 2850,
      maxProgress: 1000
    },
    {
      id: '3',
      title: 'Winning Streak',
      description: 'Win 5 bets in a row',
      icon: '🔥',
      earned: true,
      earnedDate: '2023-11-02',
      progress: 8,
      maxProgress: 5
    },
    {
      id: '4',
      title: 'Value Hunter',
      description: 'Find 100 value bets',
      icon: '🎯',
      earned: false,
      progress: 73,
      maxProgress: 100
    },
    {
      id: '5',
      title: 'High Roller',
      description: 'Place a bet over £500',
      icon: '💎',
      earned: false,
      progress: 350,
      maxProgress: 500
    }
  ]);

  const [notificationPreferences] = useState<NotificationPreference[]>([
    {
      type: 'race_results',
      label: 'Race Results',
      description: 'Get notified when your bet results are available',
      email: true,
      sms: false,
      push: true
    },
    {
      type: 'value_opportunities',
      label: 'Value Betting Alerts',
      description: 'Receive alerts for high-value betting opportunities',
      email: true,
      sms: true,
      push: true
    },
    {
      type: 'account_security',
      label: 'Security Alerts',
      description: 'Important security notifications and login alerts',
      email: true,
      sms: true,
      push: true
    },
    {
      type: 'promotions',
      label: 'Promotions & Offers',
      description: 'Special offers and promotional content',
      email: false,
      sms: false,
      push: false
    },
    {
      type: 'portfolio_updates',
      label: 'Portfolio Updates',
      description: 'Daily portfolio performance summaries',
      email: true,
      sms: false,
      push: true
    }
  ]);

  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [subscriptionDialogOpen, setSubscriptionDialogOpen] = useState(false);

  const handleSaveProfile = useCallback(() => {
    // Here you would save the profile via API
    console.log('Saving profile:', profileData);
    setEditing(false);
  }, [profileData]);

  const handleCancelEdit = useCallback(() => {
    // Reset changes
    setEditing(false);
  }, []);

  const getSubscriptionColor = (subscription: string): 'default' | 'primary' | 'secondary' => {
    switch (subscription) {
      case 'professional': return 'secondary';
      case 'premium': return 'primary';
      default: return 'default';
    }
  };

  const getSubscriptionIcon = (subscription: string) => {
    switch (subscription) {
      case 'professional': return <WorkspacePremium />;
      case 'premium': return <Star />;
      default: return <Person />;
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              👤 User Management Dashboard
            </Typography>
            <Box display="flex" gap={2}>
              <Chip
                icon={getSubscriptionIcon(profileData.subscription)}
                label={profileData.subscription.toUpperCase()}
                color={getSubscriptionColor(profileData.subscription)}
                variant="filled"
              />
              {profileData.verified && (
                <Chip
                  icon={<Verified />}
                  label="Verified"
                  color="success"
                  size="small"
                />
              )}
            </Box>
          </Box>

          {/* Profile Header */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <Box display="flex" flexDirection="column" alignItems="center">
                <Avatar
                  sx={{ width: 120, height: 120, mb: 2 }}
                  src={profileData.avatar}
                >
                  {profileData.firstName[0]}{profileData.lastName[0]}
                </Avatar>
                <Typography variant="h5" gutterBottom>
                  {profileData.firstName} {profileData.lastName}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  @{profileData.username}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Member since {new Date(profileData.memberSince).toLocaleDateString()}
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      {userStats.totalBets}
                    </Typography>
                    <Typography variant="caption">Total Bets</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="success.main">
                      {userStats.winRate}%
                    </Typography>
                    <Typography variant="caption">Win Rate</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="success.main">
                      £{userStats.totalProfit.toFixed(2)}
                    </Typography>
                    <Typography variant="caption">Total Profit</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6" color="primary">
                      #{userStats.rank}
                    </Typography>
                    <Typography variant="caption">Global Rank</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)} 
        sx={{ mb: 3 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="👤 Profile" />
        <Tab label="🔔 Notifications" />
        <Tab label="🔒 Security" />
        <Tab label="📊 Analytics" />
        <Tab label="🏆 Achievements" />
        <Tab label="💳 Subscription" />
      </Tabs>

      {/* Profile Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">Personal Information</Typography>
              <Box>
                {editing ? (
                  <>
                    <Button
                      startIcon={<SaveIcon />}
                      onClick={handleSaveProfile}
                      variant="contained"
                      sx={{ mr: 1 }}
                    >
                      Save
                    </Button>
                    <Button
                      startIcon={<CancelIcon />}
                      onClick={handleCancelEdit}
                      variant="outlined"
                    >
                      Cancel
                    </Button>
                  </>
                ) : (
                  <Button
                    startIcon={<EditIcon />}
                    onClick={() => setEditing(true)}
                    variant="outlined"
                  >
                    Edit Profile
                  </Button>
                )}
              </Box>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  value={profileData.firstName}
                  onChange={(e) => setProfileData(prev => ({ ...prev, firstName: e.target.value }))}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  value={profileData.lastName}
                  onChange={(e) => setProfileData(prev => ({ ...prev, lastName: e.target.value }))}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Username"
                  value={profileData.username}
                  onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                  disabled={!editing}
                  InputProps={{
                    endAdornment: profileData.verified && <Verified color="success" />
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={profileData.phone}
                  onChange={(e) => setProfileData(prev => ({ ...prev, phone: e.target.value }))}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  value={profileData.location}
                  onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                  disabled={!editing}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Notifications Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Notification Preferences
            </Typography>
            
            <List>
              {notificationPreferences.map((pref, index) => (
                <Box key={pref.type}>
                  <ListItem>
                    <ListItemIcon>
                      <NotificationsActive />
                    </ListItemIcon>
                    <ListItemText
                      primary={pref.label}
                      secondary={pref.description}
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" gap={1}>
                        <Tooltip title="Email">
                          <Switch checked={pref.email} size="small" />
                        </Tooltip>
                        <Tooltip title="SMS">
                          <Switch checked={pref.sms} size="small" />
                        </Tooltip>
                        <Tooltip title="Push">
                          <Switch checked={pref.push} size="small" />
                        </Tooltip>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < notificationPreferences.length - 1 && <Divider />}
                </Box>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Security Tab */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Security Settings
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <Lock />
                </ListItemIcon>
                <ListItemText
                  primary="Change Password"
                  secondary="Update your account password"
                />
                <ListItemSecondaryAction>
                  <Button 
                    variant="outlined" 
                    size="small"
                    onClick={() => setPasswordDialogOpen(true)}
                  >
                    Change
                  </Button>
                </ListItemSecondaryAction>
              </ListItem>
              
              <Divider />
              
              <ListItem>
                <ListItemIcon>
                  <Shield />
                </ListItemIcon>
                <ListItemText
                  primary="Two-Factor Authentication"
                  secondary="Add an extra layer of security to your account"
                />
                <ListItemSecondaryAction>
                  <Switch 
                    checked={profileData.twoFactorEnabled}
                    onChange={(e) => setProfileData(prev => ({ ...prev, twoFactorEnabled: e.target.checked }))}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              
              <Divider />
              
              <ListItem>
                <ListItemIcon>
                  <Email />
                </ListItemIcon>
                <ListItemText
                  primary="Email Verification"
                  secondary="Verify your email address"
                />
                <ListItemSecondaryAction>
                  {profileData.verified ? (
                    <Chip icon={<Verified />} label="Verified" color="success" size="small" />
                  ) : (
                    <Button variant="outlined" size="small">Verify</Button>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      )}

      {/* Analytics Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Betting Performance
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      ROI
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      {userStats.roi}%
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Avg Stake
                    </Typography>
                    <Typography variant="h6">
                      £{userStats.avgStake}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Best Streak
                    </Typography>
                    <Typography variant="h6">
                      {userStats.bestStreak} wins
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Current Balance
                    </Typography>
                    <Typography variant="h6" color="primary">
                      £{userStats.currentBalance}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Account Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Total Deposits
                    </Typography>
                    <Typography variant="h6">
                      £{userStats.totalDeposits.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Achievement Points
                    </Typography>
                    <Typography variant="h6" color="secondary.main">
                      {userStats.achievementPoints.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Global Rank
                    </Typography>
                    <Typography variant="h6">
                      #{userStats.rank}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Last Login
                    </Typography>
                    <Typography variant="body2">
                      {new Date(profileData.lastLogin).toLocaleDateString()}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Achievements Tab */}
      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Achievements & Badges
            </Typography>
            
            <Grid container spacing={2}>
              {achievements.map((achievement) => (
                <Grid item xs={12} sm={6} md={4} key={achievement.id}>
                  <Card variant={achievement.earned ? 'elevation' : 'outlined'} sx={{ 
                    opacity: achievement.earned ? 1 : 0.6,
                    border: achievement.earned ? '2px solid gold' : undefined
                  }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="h3" sx={{ mb: 1 }}>
                        {achievement.icon}
                      </Typography>
                      <Typography variant="h6" gutterBottom>
                        {achievement.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {achievement.description}
                      </Typography>
                      
                      {achievement.earned ? (
                        <Chip
                          icon={<EmojiEvents />}
                          label={`Earned ${new Date(achievement.earnedDate!).toLocaleDateString()}`}
                          color="success"
                          size="small"
                        />
                      ) : (
                        <Box>
                          <LinearProgress
                            variant="determinate"
                            value={(achievement.progress / achievement.maxProgress) * 100}
                            sx={{ mb: 1, height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="caption">
                            {achievement.progress} / {achievement.maxProgress}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Subscription Tab */}
      {activeTab === 5 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Subscription Management
            </Typography>
            
            <Alert severity="info" sx={{ mb: 3 }}>
              You are currently on the <strong>{profileData.subscription.toUpperCase()}</strong> plan.
              {profileData.subscription === 'free' && ' Upgrade to access advanced features!'}
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Person sx={{ fontSize: 48, mb: 2, color: 'text.secondary' }} />
                    <Typography variant="h6" gutterBottom>Free</Typography>
                    <Typography variant="h4" gutterBottom>£0</Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Basic features and limited access
                    </Typography>
                    <Button disabled={profileData.subscription === 'free'} variant="outlined" fullWidth>
                      Current Plan
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant={profileData.subscription === 'premium' ? 'elevation' : 'outlined'} sx={{
                  border: profileData.subscription === 'premium' ? '2px solid' : undefined,
                  borderColor: 'primary.main'
                }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Star sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
                    <Typography variant="h6" gutterBottom>Premium</Typography>
                    <Typography variant="h4" gutterBottom>£29<Typography component="span" variant="body2">/mo</Typography></Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Advanced analytics and unlimited betting
                    </Typography>
                    <Button 
                      disabled={profileData.subscription === 'premium'} 
                      variant={profileData.subscription === 'premium' ? 'contained' : 'outlined'}
                      fullWidth
                      onClick={() => setSubscriptionDialogOpen(true)}
                    >
                      {profileData.subscription === 'premium' ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Card variant={profileData.subscription === 'professional' ? 'elevation' : 'outlined'} sx={{
                  border: profileData.subscription === 'professional' ? '2px solid' : undefined,
                  borderColor: 'secondary.main'
                }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <WorkspacePremium sx={{ fontSize: 48, mb: 2, color: 'secondary.main' }} />
                    <Typography variant="h6" gutterBottom>Professional</Typography>
                    <Typography variant="h4" gutterBottom>£99<Typography component="span" variant="body2">/mo</Typography></Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Full suite with API access and priority support
                    </Typography>
                    <Button 
                      disabled={profileData.subscription === 'professional'} 
                      variant={profileData.subscription === 'professional' ? 'contained' : 'outlined'}
                      color="secondary"
                      fullWidth
                      onClick={() => setSubscriptionDialogOpen(true)}
                    >
                      {profileData.subscription === 'professional' ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Password Change Dialog */}
      <Dialog open={passwordDialogOpen} onClose={() => setPasswordDialogOpen(false)}>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Current Password"
                type="password"
                autoComplete="current-password"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="New Password"
                type="password"
                autoComplete="new-password"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Confirm New Password"
                type="password"
                autoComplete="new-password"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialogOpen(false)}>Cancel</Button>
          <Button variant="contained">Update Password</Button>
        </DialogActions>
      </Dialog>

      {/* Subscription Dialog */}
      <Dialog open={subscriptionDialogOpen} onClose={() => setSubscriptionDialogOpen(false)}>
        <DialogTitle>Upgrade Subscription</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Upgrading will give you immediate access to advanced features and analytics.
          </Alert>
          <Typography variant="body2">
            Your subscription will be automatically renewed monthly. You can cancel at any time.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubscriptionDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<CreditCard />}>
            Proceed to Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagementDashboard;
