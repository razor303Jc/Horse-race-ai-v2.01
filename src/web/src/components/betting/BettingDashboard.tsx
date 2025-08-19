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
import { useBettingRecommendations, useStage8Performance } from '../../hooks/useAPI';
import { BettingRecommendation } from '../../services/api';

interface PaperBet {
  bet_id: string;
  horse_name: string;
  stake: number;
  odds: number;
  status: string;
  pnl: number;
  timestamp: string;
}

export const BettingDashboard: React.FC = () => {
  // Use API hooks for real data
  const { 
    recommendations, 
    loading: recommendationsLoading, 
    error: recommendationsError,
    refetch: refetchRecommendations 
  } = useBettingRecommendations();
  
  const { 
    performance, 
    loading: performanceLoading, 
    error: performanceError,
    refetch: refetchPerformance 
  } = useStage8Performance();

  // Local state for UI controls and paper trading
  const [activeBets, setActiveBets] = useState<PaperBet[]>([]);
  const [bettingEnabled, setBettingEnabled] = useState(false);
  const [paperTradingMode, setPaperTradingMode] = useState(true);
  const [emergencyStop, setEmergencyStop] = useState(false);
  const [selectedBet, setSelectedBet] = useState<BettingRecommendation | null>(null);
  const [stakeAmount, setStakeAmount] = useState(5.0);
  const [loading, setLoading] = useState(false);

  const handlePlaceBet = async (recommendation: BettingRecommendation) => {
    if (!bettingEnabled || emergencyStop) {
      alert('Betting is currently disabled');
      return;
    }

    setLoading(true);
    try {
      // Simulate bet placement for paper trading
      const newBet: PaperBet = {
        bet_id: `bet_${Date.now()}`,
        horse_name: recommendation.horse_name,
        stake: stakeAmount,
        odds: recommendation.current_odds,
        status: 'placed',
        pnl: 0.0,
        timestamp: new Date().toISOString()
      };

      setActiveBets(prev => [...prev, newBet]);
      setSelectedBet(null);
      
    } catch (error) {
      console.error('Failed to place bet:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.75) return 'warning';
    return 'default';
  };

  const getValueColor = (value: number) => {
    if (value >= 0.1) return 'success';
    if (value >= 0.05) return 'warning';
    return 'error';
  };

  // Show loading state
  if (recommendationsLoading || performanceLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading betting dashboard...</Typography>
      </Box>
    );
  }

  // Show error state
  if (recommendationsError || performanceError) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading betting data: {recommendationsError || performanceError}
        <Button 
          onClick={() => {
            refetchRecommendations();
            refetchPerformance();
          }} 
          sx={{ ml: 2 }}
        >
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Emergency Controls */}
      <Card sx={{ mb: 3, backgroundColor: emergencyStop ? '#ffebee' : 'inherit' }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                <Security sx={{ mr: 1 }} />
                Betting Controls
              </Typography>
            </Grid>
            <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={bettingEnabled}
                    onChange={(e) => setBettingEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="Enable Betting"
              />
            </Grid>
            <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={paperTradingMode}
                    onChange={(e) => setPaperTradingMode(e.target.checked)}
                    color="secondary"
                  />
                }
                label="Paper Trading Mode"
              />
            </Grid>
            <Grid item>
              <Button
                variant={emergencyStop ? "contained" : "outlined"}
                color="error"
                startIcon={emergencyStop ? <PlayArrow /> : <Stop />}
                onClick={() => setEmergencyStop(!emergencyStop)}
              >
                {emergencyStop ? 'Resume' : 'Emergency Stop'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Account Balance
              </Typography>
              <Typography variant="h4" color="primary">
                £{performance.account_balance.toFixed(2)}
              </Typography>
              <Typography variant="body2" color={performance.daily_pnl >= 0 ? 'success.main' : 'error.main'}>
                Today: {performance.daily_pnl >= 0 ? '+' : ''}£{performance.daily_pnl.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Win Rate
              </Typography>
              <Typography variant="h4">
                {performance.win_rate.toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={performance.win_rate} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                ROI
              </Typography>
              <Typography variant="h4" color={performance.roi >= 0 ? 'success.main' : 'error.main'}>
                {performance.roi.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Active Bets
              </Typography>
              <Typography variant="h4">
                {performance.active_bets}
              </Typography>
              <Typography variant="body2">
                Total: {performance.total_bets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Betting Recommendations */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🔮 AI Betting Recommendations
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Horse</TableCell>
                  <TableCell>Confidence</TableCell>
                  <TableCell>Odds</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell>Recommended Stake</TableCell>
                  <TableCell>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recommendations.map((rec, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="bold">
                        {rec.horse_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {rec.race_time} • {rec.venue}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${(rec.confidence * 100).toFixed(0)}%`}
                        color={getConfidenceColor(rec.confidence)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{rec.current_odds.toFixed(1)}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${(rec.value * 100).toFixed(1)}%`}
                        color={getValueColor(rec.value)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>£{rec.stake_recommendation.toFixed(2)}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        disabled={!bettingEnabled || emergencyStop || loading}
                        onClick={() => setSelectedBet(rec)}
                        color="primary"
                      >
                        {rec.recommended_action}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {recommendations.length === 0 && (
            <Typography sx={{ textAlign: 'center', py: 3, color: 'text.secondary' }}>
              No betting recommendations available at this time
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Active Bets */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📊 Active Bets
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Bet ID</TableCell>
                  <TableCell>Horse</TableCell>
                  <TableCell>Stake</TableCell>
                  <TableCell>Odds</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>P&L</TableCell>
                  <TableCell>Time</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activeBets.map((bet) => (
                  <TableRow key={bet.bet_id}>
                    <TableCell>{bet.bet_id}</TableCell>
                    <TableCell>{bet.horse_name}</TableCell>
                    <TableCell>£{bet.stake.toFixed(2)}</TableCell>
                    <TableCell>{bet.odds.toFixed(1)}</TableCell>
                    <TableCell>
                      <Chip 
                        label={bet.status}
                        color={bet.status === 'won' ? 'success' : 
                               bet.status === 'lost' ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell 
                      sx={{ 
                        color: bet.pnl >= 0 ? 'success.main' : 'error.main',
                        fontWeight: 'bold'
                      }}
                    >
                      {bet.pnl >= 0 ? '+' : ''}£{bet.pnl.toFixed(2)}
                    </TableCell>
                    <TableCell>
                      {new Date(bet.timestamp).toLocaleTimeString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {activeBets.length === 0 && (
            <Typography sx={{ textAlign: 'center', py: 3, color: 'text.secondary' }}>
              No active bets
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Bet Placement Dialog */}
      <Dialog open={selectedBet !== null} onClose={() => setSelectedBet(null)}>
        <DialogTitle>Place Bet</DialogTitle>
        <DialogContent>
          {selectedBet && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6">{selectedBet.horse_name}</Typography>
              <Typography color="text.secondary" gutterBottom>
                Odds: {selectedBet.current_odds.toFixed(1)} | 
                Confidence: {(selectedBet.confidence * 100).toFixed(0)}%
              </Typography>
              
              <Typography gutterBottom sx={{ mt: 2 }}>
                Stake Amount: £{stakeAmount.toFixed(2)}
              </Typography>
              <Slider
                value={stakeAmount}
                onChange={(_, value) => setStakeAmount(value as number)}
                min={1}
                max={50}
                step={0.5}
                marks
                valueLabelDisplay="auto"
              />
              
              <Typography variant="body2" sx={{ mt: 2 }}>
                Potential Return: £{(stakeAmount * selectedBet.current_odds).toFixed(2)}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedBet(null)}>Cancel</Button>
          <Button 
            onClick={() => selectedBet && handlePlaceBet(selectedBet)}
            variant="contained"
            disabled={loading}
          >
            {paperTradingMode ? 'Paper Trade' : 'Place Bet'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
