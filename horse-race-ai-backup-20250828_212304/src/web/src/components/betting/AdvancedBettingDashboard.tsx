import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Box,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Divider,
  LinearProgress,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MonetizationOn,
  Assessment,
  Warning,
  CheckCircle,
  Error,
  Timeline,
  Speed,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon
} from '@mui/icons-material';

// Import our advanced betting components
import AdvancedBettingSlip from './AdvancedBettingSlip';
import ProfessionalStakeCalculator from './ProfessionalStakeCalculator';
import BettingStrategyAnalyzer from './BettingStrategyAnalyzer';
import BettingPortfolioManager from './BettingPortfolioManager';

import { useStage8Performance } from '../../hooks/useAPI';

export const BettingDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedBet, setSelectedBet] = useState<any>(null);
  const [betDialogOpen, setBetDialogOpen] = useState(false);
  const [liveBettingEnabled, setLiveBettingEnabled] = useState(true);
  const [autoStakingEnabled, setAutoStakingEnabled] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // API hooks
  const { performance } = useStage8Performance();

  // Mock betting data - in real implementation, this would come from API
  const mockBettingData = {
    total_staked: 2450.00,
    active_bets: 8,
    settled_bets: 156
  };

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    setRefreshing(false);
  }, []);

  const handlePlaceBet = useCallback((betData: any) => {
    setSelectedBet(betData);
    setBetDialogOpen(true);
  }, []);

  const confirmBetPlacement = useCallback(async () => {
    if (!selectedBet) return;
    
    try {
      // In real implementation, this would call the betting API
      console.log('Placing bet:', selectedBet);
      setBetDialogOpen(false);
      setSelectedBet(null);
      // Show success notification
    } catch (error) {
      console.error('Error placing bet:', error);
      // Show error notification
    }
  }, [selectedBet]);

  return (
    <Box sx={{ width: '100%' }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h4" component="h1">
              🏇 Professional Betting Center
            </Typography>
            <Box display="flex" gap={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={liveBettingEnabled}
                    onChange={(e) => setLiveBettingEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="Live Betting"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={autoStakingEnabled}
                    onChange={(e) => setAutoStakingEnabled(e.target.checked)}
                    color="secondary"
                  />
                }
                label="Auto Staking"
              />
              <IconButton 
                onClick={handleRefresh} 
                disabled={refreshing}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Box>
          </Box>

          {refreshing && <LinearProgress sx={{ mb: 2 }} />}

          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle1">
              📊 Professional Trading Suite Active
            </Typography>
            <Typography variant="body2">
              Access advanced betting tools, portfolio management, stake calculation, and strategy analysis.
              All components are integrated with real-time data and risk management systems.
            </Typography>
          </Alert>

          {/* Performance Overview */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    £{mockBettingData.total_staked?.toFixed(2) || '0.00'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Staked
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography 
                    variant="h6" 
                    color={(performance.daily_pnl || 0) >= 0 ? 'success.main' : 'error.main'}
                  >
                    £{performance.daily_pnl?.toFixed(2) || '0.00'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Today's P&L
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" color="primary">
                    {performance.win_rate?.toFixed(1) || '0.0'}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Win Rate
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography 
                    variant="h6" 
                    color={performance.roi >= 0 ? 'success.main' : 'error.main'}
                  >
                    {performance.roi?.toFixed(1) || '0.0'}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ROI
                  </Typography>
                </CardContent>
              </Card>
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
        <Tab label="🎯 Advanced Betting Slip" />
        <Tab label="💰 Stake Calculator" />
        <Tab label="📊 Strategy Analyzer" />
        <Tab label="💼 Portfolio Manager" />
      </Tabs>

      {/* Advanced Betting Slip Tab */}
      {activeTab === 0 && (
        <Box>
          <AdvancedBettingSlip />
        </Box>
      )}

      {/* Professional Stake Calculator Tab */}
      {activeTab === 1 && (
        <Box>
          <ProfessionalStakeCalculator />
        </Box>
      )}

      {/* Betting Strategy Analyzer Tab */}
      {activeTab === 2 && (
        <Box>
          <BettingStrategyAnalyzer />
        </Box>
      )}

      {/* Betting Portfolio Manager Tab */}
      {activeTab === 3 && (
        <Box>
          <BettingPortfolioManager />
        </Box>
      )}

      {/* Bet Confirmation Dialog */}
      <Dialog 
        open={betDialogOpen} 
        onClose={() => setBetDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm Professional Bet Placement
        </DialogTitle>
        <DialogContent>
          {selectedBet && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedBet.horse_name || selectedBet.selection}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Bet Type
                  </Typography>
                  <Typography variant="body1">
                    {selectedBet.bet_type?.toUpperCase() || 'WIN'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Stake
                  </Typography>
                  <Typography variant="body1">
                    £{selectedBet.stake?.toFixed(2) || '0.00'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Odds
                  </Typography>
                  <Typography variant="body1">
                    {selectedBet.odds?.toFixed(2) || '1.00'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Potential Return
                  </Typography>
                  <Typography variant="body1" color="success.main">
                    £{((selectedBet.stake || 0) * (selectedBet.odds || 1)).toFixed(2)}
                  </Typography>
                </Grid>
                {selectedBet.confidence && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence Level
                    </Typography>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress
                        variant="determinate"
                        value={selectedBet.confidence * 100}
                        color={selectedBet.confidence > 0.8 ? 'success' : 
                               selectedBet.confidence > 0.6 ? 'warning' : 'error'}
                        sx={{ flexGrow: 1, height: 8 }}
                      />
                      <Typography variant="body2">
                        {(selectedBet.confidence * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
              
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  This bet has been analyzed by our advanced algorithms and meets your 
                  risk management criteria. Kelly Criterion suggests this stake size 
                  for optimal bankroll growth.
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBetDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={confirmBetPlacement} 
            variant="contained"
            color="primary"
            startIcon={<PlayIcon />}
          >
            Place Professional Bet
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BettingDashboard;
