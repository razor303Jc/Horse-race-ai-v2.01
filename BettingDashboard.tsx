import {
    PlayArrow,
    Stop
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControlLabel,
    Grid,
    LinearProgress,
    Slider,
    Switch,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

interface BettingRecommendation {
  horse_name: string;
  confidence: number;
  current_odds: number;
  value: number;
  stake_recommendation: number;
  recommended_action: string;
}

interface PaperBet {
  bet_id: string;
  horse_name: string;
  stake: number;
  odds: number;
  status: string;
  pnl: number;
  timestamp: string;
}

interface BettingPerformance {
  account_balance: number;
  daily_pnl: number;
  win_rate: number;
  roi: number;
  total_bets: number;
  active_bets: number;
}

export const BettingDashboard: React.FC = () => {
  const [recommendations, setRecommendations] = useState<BettingRecommendation[]>([]);
  const [activeBets, setActiveBets] = useState<PaperBet[]>([]);
  const [performance, setPerformance] = useState<BettingPerformance>({
    account_balance: 1000.0,
    daily_pnl: 0.0,
    win_rate: 0.0,
    roi: 0.0,
    total_bets: 0,
    active_bets: 0
  });
  const [bettingEnabled, setBettingEnabled] = useState(false);
  const [paperTradingMode, setPaperTradingMode] = useState(true);
  const [emergencyStop, setEmergencyStop] = useState(false);
  const [selectedBet, setSelectedBet] = useState<BettingRecommendation | null>(null);
  const [stakeAmount, setStakeAmount] = useState(5.0);
  const [loading, setLoading] = useState(false);

  // Fetch betting data
  useEffect(() => {
    fetchBettingData();
    const interval = setInterval(fetchBettingData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchBettingData = async () => {
    try {
      // Simulate API calls - replace with actual endpoints
      const mockRecommendations: BettingRecommendation[] = [
        {
          horse_name: "Thunder Strike",
          confidence: 0.85,
          current_odds: 3.5,
          value: 0.12,
          stake_recommendation: 8.5,
          recommended_action: "BACK"
        },
        {
          horse_name: "Lightning Bolt", 
          confidence: 0.78,
          current_odds: 4.2,
          value: 0.08,
          stake_recommendation: 6.2,
          recommended_action: "BACK"
        },
        {
          horse_name: "Storm Chaser",
          confidence: 0.72,
          current_odds: 5.1,
          value: 0.04,
          stake_recommendation: 4.1,
          recommended_action: "SKIP"
        }
      ];

      const mockActiveBets: PaperBet[] = [
        {
          bet_id: "bet_001",
          horse_name: "Thunder Strike",
          stake: 8.5,
          odds: 3.5,
          status: "active",
          pnl: 0.0,
          timestamp: new Date().toISOString()
        }
      ];

      setRecommendations(mockRecommendations.filter(r => r.recommended_action !== "SKIP"));
      setActiveBets(mockActiveBets);
      
      // Update performance from Stage 8 data
      const stage8Data = await fetch('/api/stage8/performance').catch(() => null);
      if (stage8Data) {
        const perfData = await stage8Data.json();
        setPerformance(perfData);
      }
      
    } catch (error) {
      console.error('Failed to fetch betting data:', error);
    }
  };

  const handlePlaceBet = async (recommendation: BettingRecommendation) => {
    if (!bettingEnabled || emergencyStop) {
      alert('Betting is currently disabled');
      return;
    }

    setLoading(true);
    try {
      // Simulate bet placement
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
      
      // Update balance
      setPerformance(prev => ({
        ...prev,
        account_balance: prev.account_balance - stakeAmount,
        total_bets: prev.total_bets + 1,
        active_bets: prev.active_bets + 1
      }));

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
    return 'default';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        💰 Betting Dashboard
      </Typography>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <FormControlLabel
                control={
                  <Switch
                    checked={bettingEnabled}
                    onChange={(e) => setBettingEnabled(e.target.checked)}
                    color="primary"
                  />
                }
                label="Betting Enabled"
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
                label="Paper Trading"
              />
            </Grid>
            <Grid item>
              <Button
                variant={emergencyStop ? "contained" : "outlined"}
                color="error"
                startIcon={<Stop />}
                onClick={() => setEmergencyStop(!emergencyStop)}
              >
                Emergency Stop
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Performance Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Account Balance
              </Typography>
              <Typography variant="h4" color={performance.daily_pnl >= 0 ? 'success.main' : 'error.main'}>
                £{performance.account_balance.toFixed(2)}
              </Typography>
              <Typography variant="body2">
                Daily P&L: £{performance.daily_pnl.toFixed(2)}
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
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={`${(rec.confidence * 100).toFixed(1)}%`}
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
                        color="primary"
                        size="small"
                        startIcon={<PlayArrow />}
                        onClick={() => setSelectedBet(rec)}
                        disabled={!bettingEnabled || emergencyStop || loading}
                      >
                        {rec.recommended_action}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
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
                        color={bet.status === 'won' ? 'success' : bet.status === 'lost' ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography color={bet.pnl >= 0 ? 'success.main' : 'error.main'}>
                        £{bet.pnl.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {new Date(bet.timestamp).toLocaleTimeString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Bet Placement Dialog */}
      <Dialog open={selectedBet !== null} onClose={() => setSelectedBet(null)}>
        <DialogTitle>Place Bet: {selectedBet?.horse_name}</DialogTitle>
        <DialogContent>
          {selectedBet && (
            <Box sx={{ pt: 2 }}>
              <Typography gutterBottom>
                Confidence: {(selectedBet.confidence * 100).toFixed(1)}%
              </Typography>
              <Typography gutterBottom>
                Odds: {selectedBet.current_odds.toFixed(1)}
              </Typography>
              <Typography gutterBottom>
                Value: {(selectedBet.value * 100).toFixed(1)}%
              </Typography>
              <Typography gutterBottom>
                Recommended: £{selectedBet.stake_recommendation.toFixed(2)}
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Typography gutterBottom>
                  Stake Amount: £{stakeAmount.toFixed(2)}
                </Typography>
                <Slider
                  value={stakeAmount}
                  onChange={(_, value) => setStakeAmount(value as number)}
                  min={1}
                  max={20}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              {paperTradingMode && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Paper Trading Mode - No real money will be wagered
                </Alert>
              )}
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
            {loading ? 'Placing...' : 'Place Bet'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
