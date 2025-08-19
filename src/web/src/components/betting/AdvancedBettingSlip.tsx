import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Box,
  TextField,
  IconButton,
  Divider,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  Badge,
  Fab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Calculate as CalculateIcon,
  TrendingUp,
  AccountBalance,
  Security,
  PlayArrow,
  Stop,
  Assessment,
  ShoppingCart,
  Clear,
  ContentCopy,
  Star,
  StarBorder,
  Info
} from '@mui/icons-material';
import { useBettingRecommendations, useStage8Performance } from '../../hooks/useAPI';
import { BettingRecommendation } from '../../services/api';

interface BetSlipItem {
  id: string;
  horseName: string;
  raceName: string;
  raceTime: string;
  venue: string;
  odds: number;
  stake: number;
  betType: 'win' | 'place' | 'each-way';
  confidence: number;
  aiRecommended: boolean;
  bookmaker?: string;
  marketId?: string;
}

interface AccumulatorBet {
  id: string;
  name: string;
  selections: BetSlipItem[];
  totalOdds: number;
  totalStake: number;
  potentialReturn: number;
  type: 'accumulator' | 'treble' | 'yankee' | 'lucky-15';
}

interface BetCalculation {
  totalStake: number;
  potentialReturn: number;
  potentialProfit: number;
  roi: number;
}

const BET_TYPES = [
  { value: 'win', label: 'Win' },
  { value: 'place', label: 'Place' },
  { value: 'each-way', label: 'Each Way' }
];

const ACCUMULATOR_TYPES = [
  { value: 'accumulator', label: 'Accumulator', minSelections: 4 },
  { value: 'treble', label: 'Treble', minSelections: 3 },
  { value: 'yankee', label: 'Yankee', minSelections: 4 },
  { value: 'lucky-15', label: 'Lucky 15', minSelections: 4 }
];

export const AdvancedBettingSlip: React.FC = () => {
  // State management
  const [betSlip, setBetSlip] = useState<BetSlipItem[]>([]);
  const [accumulatorBets, setAccumulatorBets] = useState<AccumulatorBet[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [quickStakeAmount, setQuickStakeAmount] = useState(5);
  const [bettingEnabled, setBettingEnabled] = useState(false);
  const [paperTradingMode, setPaperTradingMode] = useState(true);
  const [autoCalculate, setAutoCalculate] = useState(true);
  const [showCalculator, setShowCalculator] = useState(false);
  const [stakeStrategy, setStakeStrategy] = useState<'fixed' | 'percentage' | 'kelly'>('fixed');
  const [bankrollPercentage, setBankrollPercentage] = useState(2);
  const [selectedMultiples, setSelectedMultiples] = useState<string[]>([]);

  // API hooks
  const { recommendations } = useBettingRecommendations();
  const { performance } = useStage8Performance();

  // Calculate total bet slip value
  const calculateBetSlip = useCallback((): BetCalculation => {
    const totalStake = betSlip.reduce((sum, bet) => sum + bet.stake, 0);
    const potentialReturn = betSlip.reduce((sum, bet) => sum + (bet.stake * bet.odds), 0);
    const potentialProfit = potentialReturn - totalStake;
    const roi = totalStake > 0 ? (potentialProfit / totalStake) * 100 : 0;

    return { totalStake, potentialReturn, potentialProfit, roi };
  }, [betSlip]);

  // Add bet to slip
  const addToBetSlip = useCallback((recommendation: BettingRecommendation) => {
    const newBet: BetSlipItem = {
      id: `bet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      horseName: recommendation.horse_name,
      raceName: `${recommendation.venue} ${recommendation.race_time}`,
      raceTime: recommendation.race_time,
      venue: recommendation.venue,
      odds: recommendation.current_odds,
      stake: recommendation.stake_recommendation,
      betType: 'win',
      confidence: recommendation.confidence,
      aiRecommended: true
    };

    setBetSlip(prev => [...prev, newBet]);
  }, []);

  // Remove bet from slip
  const removeBetFromSlip = useCallback((betId: string) => {
    setBetSlip(prev => prev.filter(bet => bet.id !== betId));
  }, []);

  // Update bet stake
  const updateBetStake = useCallback((betId: string, newStake: number) => {
    setBetSlip(prev => prev.map(bet => 
      bet.id === betId ? { ...bet, stake: Math.max(0.5, newStake) } : bet
    ));
  }, []);

  // Update bet type
  const updateBetType = useCallback((betId: string, newType: 'win' | 'place' | 'each-way') => {
    setBetSlip(prev => prev.map(bet => 
      bet.id === betId ? { ...bet, betType: newType } : bet
    ));
  }, []);

  // Apply quick stake to all bets
  const applyQuickStakeToAll = useCallback(() => {
    setBetSlip(prev => prev.map(bet => ({ ...bet, stake: quickStakeAmount })));
  }, [quickStakeAmount]);

  // Clear bet slip
  const clearBetSlip = useCallback(() => {
    setBetSlip([]);
    setAccumulatorBets([]);
  }, []);

  // Create accumulator bet
  const createAccumulator = useCallback(() => {
    if (betSlip.length < 2) return;

    const totalOdds = betSlip.reduce((product, bet) => product * bet.odds, 1);
    const totalStake = quickStakeAmount;
    const potentialReturn = totalStake * totalOdds;

    const newAccumulator: AccumulatorBet = {
      id: `acc_${Date.now()}`,
      name: `${betSlip.length}-fold Accumulator`,
      selections: [...betSlip],
      totalOdds,
      totalStake,
      potentialReturn,
      type: 'accumulator'
    };

    setAccumulatorBets(prev => [...prev, newAccumulator]);
  }, [betSlip, quickStakeAmount]);

  // Auto-calculate stakes based on strategy
  useEffect(() => {
    if (!autoCalculate || betSlip.length === 0) return;

    const accountBalance = performance.account_balance || 1000;

    setBetSlip(prev => prev.map(bet => {
      let newStake = bet.stake;

      switch (stakeStrategy) {
        case 'percentage':
          newStake = (accountBalance * bankrollPercentage) / 100;
          break;
        case 'kelly':
          // Kelly Criterion: f = (bp - q) / b
          // where f = fraction of bankroll, b = odds-1, p = probability, q = 1-p
          const probability = bet.confidence;
          const b = bet.odds - 1;
          const q = 1 - probability;
          const kellyFraction = Math.max(0, (b * probability - q) / b);
          newStake = Math.min(accountBalance * kellyFraction, accountBalance * 0.05); // Cap at 5%
          break;
        case 'fixed':
        default:
          newStake = quickStakeAmount;
          break;
      }

      return { ...bet, stake: Math.max(0.5, Math.min(newStake, 100)) };
    }));
  }, [stakeStrategy, bankrollPercentage, quickStakeAmount, autoCalculate, performance.account_balance]);

  const calculation = calculateBetSlip();

  // Render single bet row
  const renderBetRow = (bet: BetSlipItem, index: number) => (
    <Accordion key={bet.id} defaultExpanded={betSlip.length <= 3}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1" component="div">
              {bet.horseName}
              {bet.aiRecommended && (
                <Chip 
                  label="AI" 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1 }} 
                />
              )}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {bet.venue} • {bet.raceTime}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'right' }}>
            <Typography variant="body2">
              {bet.odds.toFixed(1)} @ £{bet.stake.toFixed(2)}
            </Typography>
            <Typography variant="caption" color="success.main">
              Returns: £{(bet.stake * bet.odds).toFixed(2)}
            </Typography>
          </Box>
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Bet Type</InputLabel>
              <Select
                value={bet.betType}
                label="Bet Type"
                onChange={(e) => updateBetType(bet.id, e.target.value as any)}
              >
                {BET_TYPES.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              size="small"
              label="Stake"
              type="number"
              value={bet.stake}
              onChange={(e) => updateBetStake(bet.id, parseFloat(e.target.value) || 0)}
              InputProps={{
                startAdornment: <InputAdornment position="start">£</InputAdornment>,
                inputProps: { min: 0.5, max: 100, step: 0.5 }
              }}
            />
          </Grid>
          <Grid item xs={12} sm={2}>
            <Typography variant="body2" color="text.secondary">
              Odds: {bet.odds.toFixed(1)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={2}>
            <IconButton
              color="error"
              onClick={() => removeBetFromSlip(bet.id)}
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          </Grid>
          
          {/* Confidence and additional info */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                label={`${(bet.confidence * 100).toFixed(0)}% Confidence`}
                size="small"
                color={bet.confidence >= 0.8 ? 'success' : bet.confidence >= 0.75 ? 'warning' : 'default'}
              />
              <Chip
                label={bet.betType.charAt(0).toUpperCase() + bet.betType.slice(1)}
                size="small"
                variant="outlined"
              />
              <Chip
                label={`Return: £${(bet.stake * bet.odds).toFixed(2)}`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Box>
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
            🎯 Advanced Betting Slip
          </Typography>
          <Badge badgeContent={betSlip.length} color="primary">
            <ShoppingCart />
          </Badge>
        </Box>

        {/* Betting Controls */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
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
            <Grid item xs={12} sm={6} md={3}>
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
            <Grid item xs={12} sm={6} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={autoCalculate}
                    onChange={(e) => setAutoCalculate(e.target.checked)}
                    color="info"
                  />
                }
                label="Auto Calculate"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                color="error"
                onClick={clearBetSlip}
                startIcon={<Clear />}
                disabled={betSlip.length === 0}
              >
                Clear All
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Stake Strategy Controls */}
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">⚙️ Stake Strategy & Calculator</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Staking Strategy</InputLabel>
                  <Select
                    value={stakeStrategy}
                    label="Staking Strategy"
                    onChange={(e) => setStakeStrategy(e.target.value as any)}
                  >
                    <MenuItem value="fixed">Fixed Amount</MenuItem>
                    <MenuItem value="percentage">Percentage of Bankroll</MenuItem>
                    <MenuItem value="kelly">Kelly Criterion</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              {stakeStrategy === 'fixed' && (
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Quick Stake Amount"
                    type="number"
                    value={quickStakeAmount}
                    onChange={(e) => setQuickStakeAmount(parseFloat(e.target.value) || 5)}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">£</InputAdornment>,
                      endAdornment: (
                        <InputAdornment position="end">
                          <Button
                            size="small"
                            onClick={applyQuickStakeToAll}
                            disabled={betSlip.length === 0}
                          >
                            Apply to All
                          </Button>
                        </InputAdornment>
                      )
                    }}
                  />
                </Grid>
              )}
              
              {stakeStrategy === 'percentage' && (
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography gutterBottom>
                      Bankroll Percentage: {bankrollPercentage}%
                    </Typography>
                    <Slider
                      value={bankrollPercentage}
                      onChange={(_, value) => setBankrollPercentage(value as number)}
                      min={0.5}
                      max={10}
                      step={0.5}
                      marks={[
                        { value: 1, label: '1%' },
                        { value: 2, label: '2%' },
                        { value: 5, label: '5%' },
                        { value: 10, label: '10%' }
                      ]}
                      valueLabelDisplay="auto"
                    />
                  </Box>
                </Grid>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Bet Slip Content */}
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
          <Tab label={`Single Bets (${betSlip.length})`} />
          <Tab label={`Multiples (${accumulatorBets.length})`} />
        </Tabs>

        {/* Single Bets Tab */}
        {activeTab === 0 && (
          <Box>
            {betSlip.length === 0 ? (
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="h6">Your bet slip is empty</Typography>
                <Typography>
                  Add bets from AI recommendations or browse race cards to get started.
                </Typography>
              </Alert>
            ) : (
              <Box>
                {betSlip.map((bet, index) => renderBetRow(bet, index))}
                
                {/* Bet Slip Summary */}
                <Card sx={{ mt: 2, backgroundColor: 'primary.50' }}>
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Total Stake
                        </Typography>
                        <Typography variant="h6">
                          £{calculation.totalStake.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Potential Return
                        </Typography>
                        <Typography variant="h6" color="success.main">
                          £{calculation.potentialReturn.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Potential Profit
                        </Typography>
                        <Typography 
                          variant="h6" 
                          color={calculation.potentialProfit >= 0 ? 'success.main' : 'error.main'}
                        >
                          £{calculation.potentialProfit.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={3}>
                        <Typography variant="body2" color="text.secondary">
                          Total ROI
                        </Typography>
                        <Typography 
                          variant="h6"
                          color={calculation.roi >= 0 ? 'success.main' : 'error.main'}
                        >
                          {calculation.roi.toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    disabled={!bettingEnabled || betSlip.length === 0}
                    startIcon={<PlayArrow />}
                    sx={{ flexGrow: 1 }}
                  >
                    {paperTradingMode ? 'Paper Trade All' : 'Place All Bets'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={createAccumulator}
                    disabled={betSlip.length < 2}
                    startIcon={<Add />}
                  >
                    Create Accumulator
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        )}

        {/* Multiples Tab */}
        {activeTab === 1 && (
          <Box>
            {accumulatorBets.length === 0 ? (
              <Alert severity="info">
                <Typography variant="h6">No multiple bets created</Typography>
                <Typography>
                  Add multiple selections to your bet slip and create accumulators, trebles, or system bets.
                </Typography>
              </Alert>
            ) : (
              accumulatorBets.map((acc) => (
                <Card key={acc.id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6">{acc.name}</Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {acc.selections.length} selections • Total odds: {acc.totalOdds.toFixed(2)}
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={4}>
                        <Typography variant="body2">Stake: £{acc.totalStake.toFixed(2)}</Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" color="success.main">
                          Potential Return: £{acc.potentialReturn.toFixed(2)}
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Button
                          variant="contained"
                          size="small"
                          disabled={!bettingEnabled}
                        >
                          Place Bet
                        </Button>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))
            )}
          </Box>
        )}

        {/* Add AI Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🤖 AI Recommendations
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Tap to add to your bet slip
              </Typography>
              
              <Grid container spacing={1}>
                {recommendations.slice(0, 6).map((rec, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => addToBetSlip(rec)}
                    >
                      <CardContent sx={{ p: 2 }}>
                        <Typography variant="subtitle2" noWrap>
                          {rec.horse_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {rec.venue} • {rec.current_odds.toFixed(1)}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                          <Chip
                            label={`${(rec.confidence * 100).toFixed(0)}%`}
                            size="small"
                            color={rec.confidence >= 0.8 ? 'success' : 'warning'}
                          />
                          <IconButton size="small" color="primary">
                            <AddIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
};

export default AdvancedBettingSlip;
