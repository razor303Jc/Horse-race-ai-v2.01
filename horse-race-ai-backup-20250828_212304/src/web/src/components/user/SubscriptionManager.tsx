import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Tabs,
  Tab,
  Button,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel,
  Divider,
  Avatar,
  IconButton,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Star,
  WorkspacePremium,
  Person,
  Payment,
  Receipt,
  History,
  CreditCard,
  Security,
  AutorenewOutlined,
  Download,
  Upgrade,
  VerifiedUser,
  Speed,
  Analytics,
  Api,
  Support,
  Notifications,
  Cloud,
  Shield,
  TrendingUp,
  MonetizationOn,
  Assessment,
  Timeline,
  BarChart,
  ShowChart
} from '@mui/icons-material';

interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  billing_period: 'monthly' | 'yearly';
  description: string;
  features: string[];
  limits: {
    bets_per_day?: number;
    api_calls_per_day?: number;
    data_retention_days?: number;
    portfolios?: number;
    strategies?: number;
  };
  popular: boolean;
  recommended: boolean;
}

interface BillingHistory {
  id: string;
  date: string;
  description: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  invoice_url?: string;
}

interface UsageMetrics {
  current_period_start: string;
  current_period_end: string;
  bets_placed: number;
  api_calls_made: number;
  data_usage_gb: number;
  active_portfolios: number;
  active_strategies: number;
}

interface PaymentMethod {
  id: string;
  type: 'card' | 'paypal' | 'bank_transfer';
  last_four?: string;
  brand?: string;
  expiry_month?: number;
  expiry_year?: number;
  is_default: boolean;
  email?: string; // for PayPal
}

export const SubscriptionManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [currentSubscription, setCurrentSubscription] = useState('premium');
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false);
  const [selectedTier, setSelectedTier] = useState<SubscriptionTier | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  const [autoRenew, setAutoRenew] = useState(true);

  const subscriptionTiers: SubscriptionTier[] = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      billing_period: 'monthly',
      description: 'Basic access to essential racing data and predictions',
      features: [
        'Basic race cards and results',
        'Simple win/place predictions',
        'Limited historical data (30 days)',
        'Community forum access',
        'Email support'
      ],
      limits: {
        bets_per_day: 5,
        api_calls_per_day: 100,
        data_retention_days: 30,
        portfolios: 1,
        strategies: 2
      },
      popular: false,
      recommended: false
    },
    {
      id: 'premium',
      name: 'Premium',
      price: 29,
      billing_period: 'monthly',
      description: 'Advanced analytics and betting tools for serious punters',
      features: [
        'Advanced AI predictions and analytics',
        'Professional betting slip with Kelly Criterion',
        'Portfolio management and risk analysis',
        'Real-time odds tracking and alerts',
        'Extended historical data (2 years)',
        'Strategy backtesting and optimization',
        'Priority email support',
        'Mobile app access',
        'Export capabilities (CSV/Excel)'
      ],
      limits: {
        bets_per_day: 100,
        api_calls_per_day: 2500,
        data_retention_days: 730,
        portfolios: 5,
        strategies: 10
      },
      popular: true,
      recommended: true
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 99,
      billing_period: 'monthly',
      description: 'Complete professional trading suite with API access',
      features: [
        'Everything in Premium',
        'Full API access with webhooks',
        'Advanced machine learning models',
        'Custom strategy development tools',
        'Arbitrage opportunity detection',
        'White-label solutions available',
        'Dedicated account manager',
        '24/7 priority support',
        'Custom integrations',
        'Advanced risk management tools',
        'Institutional-grade analytics',
        'Real-time market data feeds'
      ],
      limits: {
        bets_per_day: -1, // unlimited
        api_calls_per_day: 25000,
        data_retention_days: -1, // unlimited
        portfolios: -1, // unlimited
        strategies: -1 // unlimited
      },
      popular: false,
      recommended: false
    }
  ];

  const [billingHistory] = useState<BillingHistory[]>([
    {
      id: 'inv_001',
      date: '2024-01-01',
      description: 'Premium Subscription - January 2024',
      amount: 29.00,
      status: 'paid',
      invoice_url: '/invoices/inv_001.pdf'
    },
    {
      id: 'inv_002',
      date: '2023-12-01',
      description: 'Premium Subscription - December 2023',
      amount: 29.00,
      status: 'paid',
      invoice_url: '/invoices/inv_002.pdf'
    },
    {
      id: 'inv_003',
      date: '2023-11-01',
      description: 'Premium Subscription - November 2023',
      amount: 29.00,
      status: 'paid',
      invoice_url: '/invoices/inv_003.pdf'
    }
  ]);

  const [usageMetrics] = useState<UsageMetrics>({
    current_period_start: '2024-01-01',
    current_period_end: '2024-01-31',
    bets_placed: 47,
    api_calls_made: 1250,
    data_usage_gb: 2.3,
    active_portfolios: 3,
    active_strategies: 7
  });

  const [paymentMethods] = useState<PaymentMethod[]>([
    {
      id: 'pm_001',
      type: 'card',
      last_four: '4242',
      brand: 'Visa',
      expiry_month: 12,
      expiry_year: 2026,
      is_default: true
    },
    {
      id: 'pm_002',
      type: 'paypal',
      email: 'user@example.com',
      is_default: false
    }
  ]);

  const currentTier = subscriptionTiers.find(tier => tier.id === currentSubscription);
  const premiumTier = subscriptionTiers.find(tier => tier.id === 'premium');
  const professionalTier = subscriptionTiers.find(tier => tier.id === 'professional');

  const handleUpgrade = useCallback((tier: SubscriptionTier) => {
    setSelectedTier(tier);
    setUpgradeDialogOpen(true);
  }, []);

  const confirmUpgrade = useCallback(() => {
    if (!selectedTier) return;
    setPaymentDialogOpen(true);
    setUpgradeDialogOpen(false);
  }, [selectedTier]);

  const processPayment = useCallback(() => {
    // Here you would integrate with Stripe/PayPal
    console.log('Processing payment for:', selectedTier);
    setPaymentDialogOpen(false);
    setSelectedTier(null);
    // Update subscription status
  }, [selectedTier]);

  const getStatusColor = (status: string): 'success' | 'warning' | 'error' => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'failed': return 'error';
      default: return 'warning';
    }
  };

  const getUsagePercentage = (used: number, limit: number): number => {
    if (limit === -1) return 0; // unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number): 'success' | 'warning' | 'error' => {
    if (percentage >= 90) return 'error';
    if (percentage >= 70) return 'warning';
    return 'success';
  };

  const yearlyDiscount = 0.2; // 20% discount for yearly billing

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              💳 Subscription Management
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
              <Chip
                icon={currentTier?.id === 'professional' ? <WorkspacePremium /> : 
                      currentTier?.id === 'premium' ? <Star /> : <Person />}
                label={`${currentTier?.name.toUpperCase()} PLAN`}
                color={currentTier?.id === 'professional' ? 'secondary' : 
                       currentTier?.id === 'premium' ? 'primary' : 'default'}
                variant="filled"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={autoRenew}
                    onChange={(e) => setAutoRenew(e.target.checked)}
                    color="primary"
                  />
                }
                label="Auto-renew"
              />
            </Box>
          </Box>

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">
              💡 Current Plan: {currentTier?.name}
            </Typography>
            <Typography variant="body2">
              Your subscription renews on {new Date(usageMetrics.current_period_end).toLocaleDateString()}.
              {currentTier?.id === 'free' && ' Upgrade to unlock advanced features and unlimited access!'}
            </Typography>
          </Alert>
        </CardContent>
      </Card>

      <Tabs 
        value={activeTab} 
        onChange={(_, newValue) => setActiveTab(newValue)} 
        sx={{ mb: 3 }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab label="📊 Current Plan" />
        <Tab label="⬆️ Upgrade Options" />
        <Tab label="💳 Billing History" />
        <Tab label="📈 Usage Metrics" />
        <Tab label="💰 Payment Methods" />
      </Tabs>

      {/* Current Plan Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Plan Details
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h4" color="primary" gutterBottom>
                    {currentTier?.name}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    £{currentTier?.price}/{currentTier?.billing_period === 'monthly' ? 'month' : 'year'}
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {currentTier?.description}
                  </Typography>
                </Box>

                <Typography variant="h6" gutterBottom>
                  Included Features
                </Typography>
                <List>
                  {currentTier?.features.map((feature, index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary={feature} />
                    </ListItem>
                  ))}
                </List>

                {currentTier?.id !== 'professional' && (
                  <Button
                    variant="contained"
                    startIcon={<Upgrade />}
                    onClick={() => handleUpgrade(currentTier?.id === 'free' ? premiumTier! : professionalTier!)}
                    sx={{ mt: 2 }}
                  >
                    Upgrade Plan
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Usage
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Bets This Month
                  </Typography>
                  <Typography variant="h6">
                    {usageMetrics.bets_placed}
                    {currentTier?.limits.bets_per_day !== -1 && 
                     ` / ${currentTier?.limits.bets_per_day! * 31}`}
                  </Typography>
                  {currentTier?.limits.bets_per_day !== -1 && (
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage(usageMetrics.bets_placed, currentTier?.limits.bets_per_day! * 31)}
                      color={getUsageColor(getUsagePercentage(usageMetrics.bets_placed, currentTier?.limits.bets_per_day! * 31))}
                      sx={{ mt: 1 }}
                    />
                  )}
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    API Calls This Month
                  </Typography>
                  <Typography variant="h6">
                    {usageMetrics.api_calls_made.toLocaleString()}
                    {currentTier?.limits.api_calls_per_day !== -1 && 
                     ` / ${(currentTier?.limits.api_calls_per_day! * 31).toLocaleString()}`}
                  </Typography>
                  {currentTier?.limits.api_calls_per_day !== -1 && (
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage(usageMetrics.api_calls_made, currentTier?.limits.api_calls_per_day! * 31)}
                      color={getUsageColor(getUsagePercentage(usageMetrics.api_calls_made, currentTier?.limits.api_calls_per_day! * 31))}
                      sx={{ mt: 1 }}
                    />
                  )}
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Active Portfolios
                  </Typography>
                  <Typography variant="h6">
                    {usageMetrics.active_portfolios}
                    {currentTier?.limits.portfolios !== -1 && 
                     ` / ${currentTier?.limits.portfolios}`}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Active Strategies
                  </Typography>
                  <Typography variant="h6">
                    {usageMetrics.active_strategies}
                    {currentTier?.limits.strategies !== -1 && 
                     ` / ${currentTier?.limits.strategies}`}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Upgrade Options Tab */}
      {activeTab === 1 && (
        <Box>
          <Box display="flex" justifyContent="center" sx={{ mb: 3 }}>
            <FormControl>
              <InputLabel>Billing Period</InputLabel>
              <Select
                value={billingPeriod}
                label="Billing Period"
                onChange={(e) => setBillingPeriod(e.target.value as 'monthly' | 'yearly')}
              >
                <MenuItem value="monthly">Monthly</MenuItem>
                <MenuItem value="yearly">Yearly (20% off)</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Grid container spacing={3}>
            {subscriptionTiers.map((tier) => (
              <Grid item xs={12} md={4} key={tier.id}>
                <Card 
                  variant={tier.popular ? 'elevation' : 'outlined'}
                  sx={{
                    height: '100%',
                    border: tier.popular ? '2px solid' : undefined,
                    borderColor: tier.popular ? 'primary.main' : undefined,
                    position: 'relative'
                  }}
                >
                  {tier.popular && (
                    <Chip
                      label="MOST POPULAR"
                      color="primary"
                      size="small"
                      sx={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        zIndex: 1
                      }}
                    />
                  )}
                  
                  <CardContent sx={{ textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <Box sx={{ mb: 2 }}>
                      {tier.id === 'professional' ? (
                        <WorkspacePremium sx={{ fontSize: 48, color: 'secondary.main' }} />
                      ) : tier.id === 'premium' ? (
                        <Star sx={{ fontSize: 48, color: 'primary.main' }} />
                      ) : (
                        <Person sx={{ fontSize: 48, color: 'text.secondary' }} />
                      )}
                    </Box>
                    
                    <Typography variant="h5" gutterBottom>
                      {tier.name}
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="h3" component="div">
                        £{billingPeriod === 'yearly' && tier.price > 0 ? 
                          Math.round(tier.price * 12 * (1 - yearlyDiscount)) : 
                          tier.price}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {tier.price === 0 ? 'Forever free' : 
                         billingPeriod === 'yearly' ? '/year' : '/month'}
                      </Typography>
                      {billingPeriod === 'yearly' && tier.price > 0 && (
                        <Typography variant="caption" color="success.main">
                          Save £{Math.round(tier.price * 12 * yearlyDiscount)} annually
                        </Typography>
                      )}
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {tier.description}
                    </Typography>
                    
                    <Box sx={{ flexGrow: 1, textAlign: 'left' }}>
                      <List dense>
                        {tier.features.slice(0, 5).map((feature, index) => (
                          <ListItem key={index} disablePadding>
                            <ListItemIcon>
                              <CheckCircle color="success" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={feature}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                        {tier.features.length > 5 && (
                          <ListItem disablePadding>
                            <ListItemText 
                              primary={`+ ${tier.features.length - 5} more features`}
                              primaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                            />
                          </ListItem>
                        )}
                      </List>
                    </Box>
                    
                    <Button
                      fullWidth
                      variant={tier.popular ? 'contained' : 'outlined'}
                      color={tier.id === 'professional' ? 'secondary' : 'primary'}
                      disabled={tier.id === currentSubscription}
                      onClick={() => handleUpgrade(tier)}
                      sx={{ mt: 2 }}
                    >
                      {tier.id === currentSubscription ? 'Current Plan' : 
                       tier.id === 'free' ? 'Downgrade' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Billing History Tab */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Billing History
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="center">Status</TableCell>
                    <TableCell align="center">Invoice</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {billingHistory.map((bill) => (
                    <TableRow key={bill.id}>
                      <TableCell>
                        {new Date(bill.date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{bill.description}</TableCell>
                      <TableCell align="right">£{bill.amount.toFixed(2)}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={bill.status.toUpperCase()}
                          color={getStatusColor(bill.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="center">
                        {bill.invoice_url && (
                          <IconButton size="small" href={bill.invoice_url} download>
                            <Download />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Usage Metrics Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Usage Overview
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Period: {new Date(usageMetrics.current_period_start).toLocaleDateString()} - {new Date(usageMetrics.current_period_end).toLocaleDateString()}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Bets Placed
                    </Typography>
                    <Typography variant="h5">
                      {usageMetrics.bets_placed}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      API Calls
                    </Typography>
                    <Typography variant="h5">
                      {usageMetrics.api_calls_made.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Data Usage
                    </Typography>
                    <Typography variant="h5">
                      {usageMetrics.data_usage_gb} GB
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Portfolios
                    </Typography>
                    <Typography variant="h5">
                      {usageMetrics.active_portfolios}
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
                  Plan Limits
                </Typography>
                
                {currentTier?.limits.bets_per_day !== -1 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Daily Bet Limit
                    </Typography>
                    <Typography variant="h6">
                      {currentTier?.limits.bets_per_day} bets/day
                    </Typography>
                  </Box>
                )}
                
                {currentTier?.limits.api_calls_per_day !== -1 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Daily API Limit
                    </Typography>
                    <Typography variant="h6">
                      {currentTier?.limits.api_calls_per_day?.toLocaleString()} calls/day
                    </Typography>
                  </Box>
                )}
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Portfolio Limit
                  </Typography>
                  <Typography variant="h6">
                    {currentTier?.limits.portfolios === -1 ? 'Unlimited' : currentTier?.limits.portfolios}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Strategy Limit
                  </Typography>
                  <Typography variant="h6">
                    {currentTier?.limits.strategies === -1 ? 'Unlimited' : currentTier?.limits.strategies}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Payment Methods Tab */}
      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">
                Payment Methods
              </Typography>
              <Button variant="outlined" startIcon={<Payment />}>
                Add Payment Method
              </Button>
            </Box>
            
            <List>
              {paymentMethods.map((method, index) => (
                <Box key={method.id}>
                  <ListItem>
                    <ListItemIcon>
                      <Avatar sx={{ bgcolor: method.is_default ? 'primary.main' : 'grey.300' }}>
                        {method.type === 'card' ? <CreditCard /> : <Payment />}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        method.type === 'card' 
                          ? `${method.brand} ending in ${method.last_four}`
                          : `PayPal (${method.email})`
                      }
                      secondary={
                        method.type === 'card'
                          ? `Expires ${method.expiry_month}/${method.expiry_year}`
                          : 'PayPal account'
                      }
                    />
                    <Box>
                      {method.is_default && (
                        <Chip
                          label="Default"
                          color="primary"
                          size="small"
                          sx={{ mr: 1 }}
                        />
                      )}
                      <IconButton size="small">
                        <Security />
                      </IconButton>
                    </Box>
                  </ListItem>
                  {index < paymentMethods.length - 1 && <Divider />}
                </Box>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Upgrade Confirmation Dialog */}
      <Dialog open={upgradeDialogOpen} onClose={() => setUpgradeDialogOpen(false)}>
        <DialogTitle>
          Upgrade to {selectedTier?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTier && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                You're upgrading from {currentTier?.name} to {selectedTier.name}
              </Alert>
              
              <Typography variant="h6" gutterBottom>
                £{billingPeriod === 'yearly' && selectedTier.price > 0 ? 
                  Math.round(selectedTier.price * 12 * (1 - yearlyDiscount)) : 
                  selectedTier.price}
                /{billingPeriod === 'yearly' ? 'year' : 'month'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" paragraph>
                Your plan will be upgraded immediately and you'll be charged the prorated amount for the remaining billing period.
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom>
                New features you'll get:
              </Typography>
              <List dense>
                {selectedTier.features.slice(0, 5).map((feature, index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon>
                      <CheckCircle color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={feature}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={confirmUpgrade} variant="contained">
            Confirm Upgrade
          </Button>
        </DialogActions>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={paymentDialogOpen} onClose={() => setPaymentDialogOpen(false)}>
        <DialogTitle>
          Complete Payment
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            You'll be redirected to our secure payment processor to complete your subscription upgrade.
          </Alert>
          
          <Typography variant="body2">
            Amount: £{selectedTier?.price || 0} /{billingPeriod === 'yearly' ? 'year' : 'month'}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={processPayment} variant="contained" startIcon={<Payment />}>
            Proceed to Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SubscriptionManager;
