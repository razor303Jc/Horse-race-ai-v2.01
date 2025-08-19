import React, { useState, useCallback, useMemo } from 'react';
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
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Calculate as CalculateIcon,
  TrendingUp,
  Assessment,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import { useStage8Performance } from '../../hooks/useAPI';

interface StakeCalculation {
  recommended_stake: number;
  kelly_fraction: number;
  risk_percentage: number;
  expected_value: number;
  potential_return: number;
  potential_profit: number;
  roi_percentage: number;
  confidence_adjusted_stake: number;
}

interface ArbitrageOpportunity {
  bookmaker1: string;
  odds1: number;
  bookmaker2: string;
  odds2: number;
  stake1: number;
  stake2: number;
  guaranteed_profit: number;
  profit_percentage: number;
}

const BETTING_SYSTEMS = [
  { value: 'kelly', label: 'Kelly Criterion', description: 'Optimal stake based on edge and bankroll' },
  { value: 'fixed', label: 'Fixed Amount', description: 'Consistent stake amount per bet' },
  { value: 'percentage', label: 'Percentage Staking', description: 'Fixed percentage of bankroll' },
  { value: 'fibonacci', label: 'Fibonacci', description: 'Progressive staking system' },
  { value: 'martingale', label: 'Martingale', description: 'Double stake after loss (high risk)' },
  { value: 'proportional', label: 'Proportional', description: 'Stake proportional to confidence' }
];

export const ProfessionalStakeCalculator: React.FC = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [bettingSystem, setBettingSystem] = useState('kelly');
  const [bankroll, setBankroll] = useState(1000);
  const [odds, setOdds] = useState(2.5);
  const [confidence, setConfidence] = useState(0.65);
  const [maxRiskPercentage, setMaxRiskPercentage] = useState(5);
  const [fixedAmount, setFixedAmount] = useState(10);
  const [percentageStake, setPercentageStake] = useState(2);
  
  // Arbitrage calculator states
  const [arbOdds1, setArbOdds1] = useState(2.1);
  const [arbOdds2, setArbOdds2] = useState(2.0);
  const [arbTotalStake, setArbTotalStake] = useState(100);
  
  // Advanced settings
  const [includeCommission, setIncludeCommission] = useState(false);
  const [commission, setCommission] = useState(5);
  const [riskTolerance, setRiskTolerance] = useState('moderate');

  // API hooks
  const { performance } = useStage8Performance();

  // Update bankroll from performance data
  React.useEffect(() => {
    if (performance.account_balance > 0) {
      setBankroll(performance.account_balance);
    }
  }, [performance.account_balance]);

  // Kelly Criterion calculation
  const calculateKelly = useCallback((oddsValue: number, probabilityWin: number): number => {
    const b = oddsValue - 1; // Net odds (profit per unit staked)
    const p = probabilityWin; // Probability of winning
    const q = 1 - p; // Probability of losing
    
    // Kelly formula: f = (bp - q) / b
    const kellyFraction = (b * p - q) / b;
    
    // Return 0 if negative (no edge)
    return Math.max(0, kellyFraction);
  }, []);

  // Calculate stake based on selected system
  const calculateStake = useCallback((): StakeCalculation => {
    const probabilityWin = confidence;
    const impliedProbability = 1 / odds;
    const edge = probabilityWin - impliedProbability;
    
    let recommended_stake = 0;
    let kelly_fraction = 0;
    
    switch (bettingSystem) {
      case 'kelly':
        kelly_fraction = calculateKelly(odds, probabilityWin);
        recommended_stake = bankroll * kelly_fraction;
        break;
        
      case 'fixed':
        recommended_stake = fixedAmount;
        kelly_fraction = recommended_stake / bankroll;
        break;
        
      case 'percentage':
        recommended_stake = bankroll * (percentageStake / 100);
        kelly_fraction = percentageStake / 100;
        break;
        
      case 'proportional':
        // Stake proportional to confidence level
        const baseStake = bankroll * 0.02; // 2% base
        const confidenceMultiplier = (confidence - 0.5) * 2; // Scale 0.5-1 to 0-1
        recommended_stake = baseStake * (1 + confidenceMultiplier);
        kelly_fraction = recommended_stake / bankroll;
        break;
        
      case 'fibonacci':
        // Simplified fibonacci (would need bet history for full implementation)
        recommended_stake = bankroll * 0.02;
        kelly_fraction = 0.02;
        break;
        
      case 'martingale':
        // Simplified martingale (would need previous bet result)
        recommended_stake = bankroll * 0.05;
        kelly_fraction = 0.05;
        break;
        
      default:
        recommended_stake = fixedAmount;
        kelly_fraction = recommended_stake / bankroll;
    }
    
    // Apply risk management caps
    const maxStake = bankroll * (maxRiskPercentage / 100);
    recommended_stake = Math.min(recommended_stake, maxStake);
    
    // Apply risk tolerance adjustments
    const riskMultiplier = riskTolerance === 'conservative' ? 0.5 : 
                          riskTolerance === 'aggressive' ? 1.5 : 1.0;
    recommended_stake *= riskMultiplier;
    
    // Ensure minimum stake
    recommended_stake = Math.max(0.5, recommended_stake);
    
    const risk_percentage = (recommended_stake / bankroll) * 100;
    const potential_return = recommended_stake * odds;
    const net_return = includeCommission ? 
      potential_return * (1 - commission / 100) : potential_return;
    const potential_profit = net_return - recommended_stake;
    const roi_percentage = (potential_profit / recommended_stake) * 100;
    const expected_value = (probabilityWin * potential_profit) - ((1 - probabilityWin) * recommended_stake);
    const confidence_adjusted_stake = recommended_stake * confidence;
    
    return {
      recommended_stake,
      kelly_fraction,
      risk_percentage,
      expected_value,
      potential_return: net_return,
      potential_profit,
      roi_percentage,
      confidence_adjusted_stake
    };
  }, [
    bettingSystem, bankroll, odds, confidence, maxRiskPercentage, 
    fixedAmount, percentageStake, riskTolerance, includeCommission, 
    commission, calculateKelly
  ]);

  // Calculate arbitrage opportunity
  const calculateArbitrage = useCallback((): ArbitrageOpportunity | null => {
    const implied1 = 1 / arbOdds1;
    const implied2 = 1 / arbOdds2;
    const totalImplied = implied1 + implied2;
    
    if (totalImplied >= 1) {
      return null; // No arbitrage opportunity
    }
    
    const stake1 = arbTotalStake * implied1 / totalImplied;
    const stake2 = arbTotalStake * implied2 / totalImplied;
    
    const return1 = stake1 * arbOdds1;
    const return2 = stake2 * arbOdds2;
    
    const guaranteed_profit = Math.min(return1, return2) - arbTotalStake;
    const profit_percentage = (guaranteed_profit / arbTotalStake) * 100;
    
    return {
      bookmaker1: 'Bookmaker A',
      odds1: arbOdds1,
      bookmaker2: 'Bookmaker B', 
      odds2: arbOdds2,
      stake1,
      stake2,
      guaranteed_profit,
      profit_percentage
    };
  }, [arbOdds1, arbOdds2, arbTotalStake]);

  const stakeCalculation = useMemo(() => calculateStake(), [calculateStake]);
  const arbitrageOpportunity = useMemo(() => calculateArbitrage(), [calculateArbitrage]);

  const getSystemDescription = (system: string): string => {
    return BETTING_SYSTEMS.find(s => s.value === system)?.description || '';
  };

  const getConfidenceColor = (conf: number): 'error' | 'warning' | 'success' => {
    if (conf >= 0.8) return 'success';
    if (conf >= 0.7) return 'warning';
    return 'error';
  };

  const getRiskColor = (risk: number): 'success' | 'warning' | 'error' => {
    if (risk <= 2) return 'success';
    if (risk <= 5) return 'warning';
    return 'error';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2" gutterBottom>
          💰 Professional Stake Calculator
        </Typography>
        
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
          <Tab label="Stake Calculator" />
          <Tab label="Arbitrage Finder" />
          <Tab label="Risk Management" />
        </Tabs>

        {/* Stake Calculator Tab */}
        {activeTab === 0 && (
          <Box>
            <Grid container spacing={3}>
              {/* Input Parameters */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Betting Parameters
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <FormControl fullWidth>
                          <InputLabel>Betting System</InputLabel>
                          <Select
                            value={bettingSystem}
                            label="Betting System"
                            onChange={(e) => setBettingSystem(e.target.value)}
                          >
                            {BETTING_SYSTEMS.map(system => (
                              <MenuItem key={system.value} value={system.value}>
                                <Box>
                                  <Typography>{system.label}</Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {system.description}
                                  </Typography>
                                </Box>
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Bankroll"
                          type="number"
                          value={bankroll}
                          onChange={(e) => setBankroll(parseFloat(e.target.value) || 0)}
                          InputProps={{
                            startAdornment: <InputAdornment position="start">£</InputAdornment>
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Odds"
                          type="number"
                          value={odds}
                          onChange={(e) => setOdds(parseFloat(e.target.value) || 1)}
                          InputProps={{
                            inputProps: { min: 1, step: 0.1 }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Typography gutterBottom>
                          Confidence Level: {(confidence * 100).toFixed(1)}%
                        </Typography>
                        <Slider
                          value={confidence}
                          onChange={(_, value) => setConfidence(value as number)}
                          min={0.5}
                          max={0.95}
                          step={0.01}
                          marks={[
                            { value: 0.5, label: '50%' },
                            { value: 0.7, label: '70%' },
                            { value: 0.8, label: '80%' },
                            { value: 0.9, label: '90%' }
                          ]}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${(value * 100).toFixed(1)}%`}
                        />
                      </Grid>
                      
                      {bettingSystem === 'fixed' && (
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Fixed Amount"
                            type="number"
                            value={fixedAmount}
                            onChange={(e) => setFixedAmount(parseFloat(e.target.value) || 0)}
                            InputProps={{
                              startAdornment: <InputAdornment position="start">£</InputAdornment>
                            }}
                          />
                        </Grid>
                      )}
                      
                      {bettingSystem === 'percentage' && (
                        <Grid item xs={12}>
                          <Typography gutterBottom>
                            Bankroll Percentage: {percentageStake}%
                          </Typography>
                          <Slider
                            value={percentageStake}
                            onChange={(_, value) => setPercentageStake(value as number)}
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
                            valueLabelFormat={(value) => `${value}%`}
                          />
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>

              {/* Results */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📈 Calculation Results
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Alert severity="info" sx={{ mb: 2 }}>
                        <Typography variant="subtitle2">
                          {getSystemDescription(bettingSystem)}
                        </Typography>
                      </Alert>
                    </Box>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Recommended Stake
                        </Typography>
                        <Typography variant="h6" color="primary">
                          £{stakeCalculation.recommended_stake.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Risk Percentage
                        </Typography>
                        <Typography variant="h6">
                          <Chip
                            label={`${stakeCalculation.risk_percentage.toFixed(2)}%`}
                            color={getRiskColor(stakeCalculation.risk_percentage)}
                            size="small"
                          />
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Potential Return
                        </Typography>
                        <Typography variant="h6" color="success.main">
                          £{stakeCalculation.potential_return.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Potential Profit
                        </Typography>
                        <Typography 
                          variant="h6" 
                          color={stakeCalculation.potential_profit >= 0 ? 'success.main' : 'error.main'}
                        >
                          £{stakeCalculation.potential_profit.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          ROI
                        </Typography>
                        <Typography variant="h6">
                          {stakeCalculation.roi_percentage.toFixed(1)}%
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Expected Value
                        </Typography>
                        <Typography 
                          variant="h6"
                          color={stakeCalculation.expected_value >= 0 ? 'success.main' : 'error.main'}
                        >
                          £{stakeCalculation.expected_value.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      {bettingSystem === 'kelly' && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="text.secondary">
                            Kelly Fraction
                          </Typography>
                          <Typography variant="h6">
                            {(stakeCalculation.kelly_fraction * 100).toFixed(2)}%
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Arbitrage Calculator Tab */}
        {activeTab === 1 && (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="h6">Arbitrage Betting Calculator</Typography>
              <Typography>
                Find risk-free profit opportunities by betting on all outcomes with different bookmakers.
              </Typography>
            </Alert>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Arbitrage Inputs
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Bookmaker A Odds"
                          type="number"
                          value={arbOdds1}
                          onChange={(e) => setArbOdds1(parseFloat(e.target.value) || 1)}
                          InputProps={{
                            inputProps: { min: 1, step: 0.01 }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Bookmaker B Odds"
                          type="number"
                          value={arbOdds2}
                          onChange={(e) => setArbOdds2(parseFloat(e.target.value) || 1)}
                          InputProps={{
                            inputProps: { min: 1, step: 0.01 }
                          }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Total Stake Amount"
                          type="number"
                          value={arbTotalStake}
                          onChange={(e) => setArbTotalStake(parseFloat(e.target.value) || 0)}
                          InputProps={{
                            startAdornment: <InputAdornment position="start">£</InputAdornment>
                          }}
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🎯 Arbitrage Results
                    </Typography>
                    
                    {arbitrageOpportunity ? (
                      <Box>
                        <Alert severity="success" sx={{ mb: 2 }}>
                          <Typography variant="subtitle1">
                            ✅ Arbitrage Opportunity Found!
                          </Typography>
                          <Typography>
                            Guaranteed profit: £{arbitrageOpportunity.guaranteed_profit.toFixed(2)} 
                            ({arbitrageOpportunity.profit_percentage.toFixed(2)}%)
                          </Typography>
                        </Alert>
                        
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Bookmaker</TableCell>
                                <TableCell>Odds</TableCell>
                                <TableCell>Stake</TableCell>
                                <TableCell>Return</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              <TableRow>
                                <TableCell>{arbitrageOpportunity.bookmaker1}</TableCell>
                                <TableCell>{arbitrageOpportunity.odds1.toFixed(2)}</TableCell>
                                <TableCell>£{arbitrageOpportunity.stake1.toFixed(2)}</TableCell>
                                <TableCell>£{(arbitrageOpportunity.stake1 * arbitrageOpportunity.odds1).toFixed(2)}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>{arbitrageOpportunity.bookmaker2}</TableCell>
                                <TableCell>{arbitrageOpportunity.odds2.toFixed(2)}</TableCell>
                                <TableCell>£{arbitrageOpportunity.stake2.toFixed(2)}</TableCell>
                                <TableCell>£{(arbitrageOpportunity.stake2 * arbitrageOpportunity.odds2).toFixed(2)}</TableCell>
                              </TableRow>
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Box>
                    ) : (
                      <Alert severity="warning">
                        <Typography variant="subtitle1">
                          ⚠️ No Arbitrage Opportunity
                        </Typography>
                        <Typography>
                          The combined implied probability exceeds 100%. 
                          Try finding better odds or different markets.
                        </Typography>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Risk Management Tab */}
        {activeTab === 2 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      ⚠️ Risk Management Settings
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Typography gutterBottom>
                          Maximum Risk Per Bet: {maxRiskPercentage}%
                        </Typography>
                        <Slider
                          value={maxRiskPercentage}
                          onChange={(_, value) => setMaxRiskPercentage(value as number)}
                          min={1}
                          max={20}
                          step={0.5}
                          marks={[
                            { value: 1, label: '1%' },
                            { value: 5, label: '5%' },
                            { value: 10, label: '10%' },
                            { value: 20, label: '20%' }
                          ]}
                          valueLabelDisplay="auto"
                          valueLabelFormat={(value) => `${value}%`}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <FormControl fullWidth>
                          <InputLabel>Risk Tolerance</InputLabel>
                          <Select
                            value={riskTolerance}
                            label="Risk Tolerance"
                            onChange={(e) => setRiskTolerance(e.target.value)}
                          >
                            <MenuItem value="conservative">Conservative (0.5x stakes)</MenuItem>
                            <MenuItem value="moderate">Moderate (1x stakes)</MenuItem>
                            <MenuItem value="aggressive">Aggressive (1.5x stakes)</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={includeCommission}
                              onChange={(e) => setIncludeCommission(e.target.checked)}
                            />
                          }
                          label="Include Commission/Tax"
                        />
                      </Grid>
                      
                      {includeCommission && (
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Commission/Tax Rate"
                            type="number"
                            value={commission}
                            onChange={(e) => setCommission(parseFloat(e.target.value) || 0)}
                            InputProps={{
                              endAdornment: <InputAdornment position="end">%</InputAdornment>,
                              inputProps: { min: 0, max: 50, step: 0.5 }
                            }}
                          />
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      📊 Account Overview
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Current Bankroll
                        </Typography>
                        <Typography variant="h6">
                          £{bankroll.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Today's P&L
                        </Typography>
                        <Typography 
                          variant="h6"
                          color={performance.daily_pnl >= 0 ? 'success.main' : 'error.main'}
                        >
                          £{performance.daily_pnl.toFixed(2)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Win Rate
                        </Typography>
                        <Typography variant="h6">
                          {performance.win_rate.toFixed(1)}%
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          ROI
                        </Typography>
                        <Typography 
                          variant="h6"
                          color={performance.roi >= 0 ? 'success.main' : 'error.main'}
                        >
                          {performance.roi.toFixed(1)}%
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Maximum Stake (Risk Limit)
                        </Typography>
                        <Typography variant="h6" color="warning.main">
                          £{(bankroll * maxRiskPercentage / 100).toFixed(2)}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ProfessionalStakeCalculator;
