import React, { useState, useEffect, useMemo, useCallback } from 'react';
import SwipeableViews from 'react-swipeable-views';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Chip,
  Avatar,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  IconButton,
  Fab,
  Zoom,
  Tab,
  Tabs,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  useTheme,
  useMediaQuery,
  ButtonGroup,
  Tooltip,
  Badge,
  Paper,
  Container
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Timer,
  ExpandMore,
  Add,
  Remove,
  Share,
  Bookmark,
  BookmarkBorder,
  Speed,
  Visibility,
  VisibilityOff,
  TouchApp,
  SwipeVertical,
  MonetizationOn,
  Assessment,
  History,
  Settings,
  Info,
  Warning,
  CheckCircle,
  Cancel,
  PlayArrow,
  Pause,
  Refresh,
  AccountBalance
} from '@mui/icons-material';
import { useSwipeable } from 'react-swipeable';

interface Horse {
  id: string;
  name: string;
  number: number;
  jockey: string;
  trainer: string;
  odds: number;
  probability: number;
  form: string;
  age: number;
  weight: number;
  prediction: {
    confidence: number;
    recommendation: 'strong_buy' | 'buy' | 'hold' | 'avoid';
    expectedValue: number;
  };
  isBookmarked?: boolean;
}

interface Race {
  id: string;
  name: string;
  track: string;
  time: string;
  distance: string;
  surface: string;
  horses: Horse[];
  status: 'upcoming' | 'live' | 'finished';
  timeToStart: number; // minutes
}

interface Bet {
  id: string;
  horse: Horse;
  race: Race;
  stake: number;
  betType: 'win' | 'place' | 'each_way';
  odds: number;
  timestamp: Date;
  status: 'pending' | 'placed' | 'won' | 'lost';
}

interface MobileBettingInterfaceProps {
  races: Race[];
  onPlaceBet: (bet: Omit<Bet, 'id' | 'timestamp' | 'status'>) => Promise<void>;
  accountBalance: number;
  totalExposure: number;
  maxStake?: number;
}

export const MobileBettingInterface: React.FC<MobileBettingInterfaceProps> = ({
  races,
  onPlaceBet,
  accountBalance,
  totalExposure,
  maxStake = 1000
}) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedRace, setSelectedRace] = useState<Race | null>(null);
  const [selectedHorse, setSelectedHorse] = useState<Horse | null>(null);
  const [betSlipOpen, setBetSlipOpen] = useState(false);
  const [stake, setStake] = useState(10);
  const [betType, setBetType] = useState<'win' | 'place' | 'each_way'>('win');
  const [quickStakes] = useState([5, 10, 25, 50, 100]);
  const [autoStaking, setAutoStaking] = useState(false);
  const [showPredictions, setShowPredictions] = useState(true);
  const [bookmarkedHorses, setBookmarkedHorses] = useState<Set<string>>(new Set());
  const [bets, setBets] = useState<Bet[]>([]);
  const [notification, setNotification] = useState<{ message: string; severity: 'success' | 'error' | 'warning' } | null>(null);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Quick bet functionality
  const handleQuickBet = useCallback(async (horse: Horse, race: Race, quickStake: number) => {
    try {
      await onPlaceBet({
        horse,
        race,
        stake: quickStake,
        betType: 'win',
        odds: horse.odds
      });
      setNotification({ message: `Quick bet placed: £${quickStake} on ${horse.name}`, severity: 'success' });
    } catch (error) {
      setNotification({ message: 'Failed to place bet', severity: 'error' });
    }
  }, [onPlaceBet]);

  // Auto-staking calculation based on Kelly Criterion
  const calculateOptimalStake = useCallback((horse: Horse) => {
    const probability = horse.probability / 100;
    const odds = horse.odds;
    const kelly = (probability * odds - 1) / (odds - 1);
    return Math.max(0, Math.min(kelly * accountBalance * 0.1, maxStake)); // Conservative 10% of Kelly
  }, [accountBalance, maxStake]);

  // Swipe handlers for mobile interaction
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (selectedTab < 2) setSelectedTab(selectedTab + 1);
    },
    onSwipedRight: () => {
      if (selectedTab > 0) setSelectedTab(selectedTab - 1);
    },
    onSwipedUp: () => {
      if (selectedHorse && selectedRace) {
        setBetSlipOpen(true);
      }
    },
    trackMouse: true,
    preventScrollOnSwipe: true
  });

  const toggleBookmark = (horseId: string) => {
    const newBookmarks = new Set(bookmarkedHorses);
    if (newBookmarks.has(horseId)) {
      newBookmarks.delete(horseId);
    } else {
      newBookmarks.add(horseId);
    }
    setBookmarkedHorses(newBookmarks);
  };

  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case 'strong_buy': return theme.palette.success.main;
      case 'buy': return theme.palette.info.main;
      case 'hold': return theme.palette.warning.main;
      case 'avoid': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };

  const getRecommendationIcon = (recommendation: string) => {
    switch (recommendation) {
      case 'strong_buy': return <TrendingUp />;
      case 'buy': return <TrendingUp />;
      case 'hold': return <Remove />;
      case 'avoid': return <TrendingDown />;
      default: return <Remove />;
    }
  };

  // Mobile-optimized horse card component
  const HorseCard: React.FC<{ horse: Horse; race: Race; compact?: boolean }> = ({ horse, race, compact = false }) => (
    <Card 
      sx={{ 
        mb: 1, 
        cursor: 'pointer',
        transition: 'all 0.2s',
        '&:active': {
          transform: 'scale(0.98)',
          backgroundColor: theme.palette.action.selected
        }
      }}
      onClick={() => {
        setSelectedHorse(horse);
        setSelectedRace(race);
        if (autoStaking) {
          setStake(calculateOptimalStake(horse));
        }
      }}
    >
      <CardContent sx={{ p: compact ? 1 : 2, '&:last-child': { pb: compact ? 1 : 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Avatar sx={{ bgcolor: getRecommendationColor(horse.prediction.recommendation), mr: 1, width: 32, height: 32 }}>
            {horse.number}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant={compact ? "body2" : "h6"} noWrap>
              {horse.name}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {horse.jockey}
            </Typography>
          </Box>
          <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleBookmark(horse.id); }}>
            {bookmarkedHorses.has(horse.id) ? <Bookmark color="primary" /> : <BookmarkBorder />}
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Chip
            icon={getRecommendationIcon(horse.prediction.recommendation)}
            label={`${horse.odds}/1`}
            size="small"
            sx={{ 
              backgroundColor: getRecommendationColor(horse.prediction.recommendation),
              color: 'white',
              fontWeight: 'bold'
            }}
          />
          {showPredictions && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="caption" sx={{ mr: 1 }}>
                {horse.probability}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={horse.prediction.confidence}
                sx={{ width: 40, height: 4 }}
              />
            </Box>
          )}
        </Box>

        {!compact && (
          <Grid container spacing={1} sx={{ mt: 1 }}>
            <Grid item xs={4}>
              <Typography variant="caption" color="text.secondary" display="block">
                Form
              </Typography>
              <Typography variant="body2">{horse.form}</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" color="text.secondary" display="block">
                Age
              </Typography>
              <Typography variant="body2">{horse.age}y</Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" color="text.secondary" display="block">
                Weight
              </Typography>
              <Typography variant="body2">{horse.weight}kg</Typography>
            </Grid>
          </Grid>
        )}

        {/* Quick bet buttons */}
        <Box sx={{ display: 'flex', gap: 0.5, mt: 1, flexWrap: 'wrap' }}>
          {quickStakes.slice(0, 3).map(quickStake => (
            <Button
              key={quickStake}
              size="small"
              variant="outlined"
              onClick={(e) => {
                e.stopPropagation();
                handleQuickBet(horse, race, quickStake);
              }}
              sx={{ 
                minWidth: 'auto',
                px: 1,
                fontSize: '0.7rem'
              }}
            >
              £{quickStake}
            </Button>
          ))}
        </Box>
      </CardContent>
    </Card>
  );

  // Race list component
  const RaceList: React.FC<{ races: Race[] }> = ({ races }) => (
    <Box>
      {races.map((race) => (
        <Accordion key={race.id} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6">{race.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {race.track} • {race.time} • {race.distance}
                </Typography>
              </Box>
              <Chip
                label={race.status === 'live' ? 'LIVE' : `${race.timeToStart}m`}
                color={race.status === 'live' ? 'error' : 'primary'}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ p: 1 }}>
            {race.horses.map((horse) => (
              <HorseCard key={horse.id} horse={horse} race={race} compact />
            ))}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );

  // Bet slip dialog
  const BetSlipDialog = () => (
    <Dialog
      fullScreen={isMobile}
      open={betSlipOpen}
      onClose={() => setBetSlipOpen(false)}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        Place Bet
        {selectedHorse && (
          <Typography variant="subtitle2" color="text.secondary">
            {selectedHorse.name} - {selectedRace?.name}
          </Typography>
        )}
      </DialogTitle>
      <DialogContent>
        {selectedHorse && selectedRace && (
          <Box>
            {/* Bet type selection */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Bet Type
              </Typography>
              <ButtonGroup fullWidth variant="outlined">
                {(['win', 'place', 'each_way'] as const).map((type) => (
                  <Button
                    key={type}
                    variant={betType === type ? 'contained' : 'outlined'}
                    onClick={() => setBetType(type)}
                  >
                    {type.replace('_', ' ').toUpperCase()}
                  </Button>
                ))}
              </ButtonGroup>
            </Box>

            {/* Stake input */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Stake: £{stake}
              </Typography>
              <Slider
                value={stake}
                onChange={(_, value) => setStake(value as number)}
                min={1}
                max={Math.min(maxStake, accountBalance)}
                step={1}
                marks={quickStakes.map(value => ({ value, label: `£${value}` }))}
              />
              <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                {quickStakes.map(quickStake => (
                  <Button
                    key={quickStake}
                    size="small"
                    variant={stake === quickStake ? 'contained' : 'outlined'}
                    onClick={() => setStake(quickStake)}
                  >
                    £{quickStake}
                  </Button>
                ))}
              </Box>
            </Box>

            {/* Auto-staking option */}
            <FormControlLabel
              control={
                <Switch
                  checked={autoStaking}
                  onChange={(e) => {
                    setAutoStaking(e.target.checked);
                    if (e.target.checked) {
                      setStake(calculateOptimalStake(selectedHorse));
                    }
                  }}
                />
              }
              label="Auto-stake (Kelly Criterion)"
            />

            {/* Bet summary */}
            <Paper sx={{ p: 2, mt: 2, backgroundColor: theme.palette.background.default }}>
              <Typography variant="subtitle2" gutterBottom>
                Bet Summary
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Stake:</Typography>
                <Typography>£{stake}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Odds:</Typography>
                <Typography>{selectedHorse.odds}/1</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Potential Return:</Typography>
                <Typography fontWeight="bold">
                  £{(stake * selectedHorse.odds).toFixed(2)}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography>Potential Profit:</Typography>
                <Typography 
                  fontWeight="bold"
                  color={stake * selectedHorse.odds - stake > 0 ? 'success.main' : 'error.main'}
                >
                  £{(stake * selectedHorse.odds - stake).toFixed(2)}
                </Typography>
              </Box>
            </Paper>

            {/* Risk warnings */}
            {stake > accountBalance * 0.05 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                This bet represents more than 5% of your account balance.
              </Alert>
            )}
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setBetSlipOpen(false)}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={async () => {
            if (selectedHorse && selectedRace) {
              await handleQuickBet(selectedHorse, selectedRace, stake);
              setBetSlipOpen(false);
            }
          }}
          disabled={stake > accountBalance}
        >
          Place Bet
        </Button>
      </DialogActions>
    </Dialog>
  );

  return (
    <Container maxWidth="md" sx={{ p: 1 }} {...swipeHandlers}>
      {/* Account summary */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Balance
            </Typography>
            <Typography variant="h6">£{accountBalance.toFixed(2)}</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Exposure
            </Typography>
            <Typography variant="h6">£{totalExposure.toFixed(2)}</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="caption" color="text.secondary">
              Available
            </Typography>
            <Typography variant="h6">£{(accountBalance - totalExposure).toFixed(2)}</Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Settings bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={showPredictions}
              onChange={(e) => setShowPredictions(e.target.checked)}
              size="small"
            />
          }
          label="AI Predictions"
        />
        <FormControlLabel
          control={
            <Switch
              checked={autoStaking}
              onChange={(e) => setAutoStaking(e.target.checked)}
              size="small"
            />
          }
          label="Auto-stake"
        />
      </Box>

      {/* Main content tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={selectedTab} onChange={(_, value) => setSelectedTab(value)} variant="fullWidth">
          <Tab label="Live Races" />
          <Tab label="Upcoming" />
          <Tab label="My Bets" />
        </Tabs>
      </Box>

      {/* Tab content */}
      {selectedTab === 0 && (
        <RaceList races={races.filter(race => race.status === 'live')} />
      )}
      {selectedTab === 1 && (
        <RaceList races={races.filter(race => race.status === 'upcoming')} />
      )}
      {selectedTab === 2 && (
        <Box>
          {bets.length === 0 ? (
            <Typography variant="body1" color="text.secondary" textAlign="center" sx={{ py: 4 }}>
              No active bets
            </Typography>
          ) : (
            bets.map((bet) => (
              <Card key={bet.id} sx={{ mb: 1 }}>
                <CardContent>
                  <Typography variant="h6">{bet.horse.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {bet.race.name} • £{bet.stake} @ {bet.odds}/1
                  </Typography>
                  <Chip 
                    label={bet.status.toUpperCase()} 
                    size="small" 
                    color={bet.status === 'won' ? 'success' : bet.status === 'lost' ? 'error' : 'default'}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            ))
          )}
        </Box>
      )}

      {/* Bet slip dialog */}
      <BetSlipDialog />

      {/* Quick action FAB */}
      <Zoom in={selectedHorse !== null}>
        <Fab
          color="primary"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => setBetSlipOpen(true)}
        >
          <Add />
        </Fab>
      </Zoom>

      {/* Notification snackbar */}
      <Snackbar
        open={notification !== null}
        autoHideDuration={6000}
        onClose={() => setNotification(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        {notification ? (
          <Alert severity={notification.severity} onClose={() => setNotification(null)}>
            {notification.message}
          </Alert>
        ) : (
          <Alert severity="info" style={{ display: 'none' }}>
            Hidden
          </Alert>
        )}
      </Snackbar>

      {/* Swipe hint */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 8,
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          opacity: 0.6,
          fontSize: '0.7rem',
          color: 'text.secondary'
        }}
      >
        <SwipeVertical fontSize="small" />
        <Typography variant="caption">Swipe to navigate</Typography>
        <SwipeVertical fontSize="small" />
        <Typography variant="caption">Swipe up to bet</Typography>
      </Box>
    </Container>
  );
};

export default MobileBettingInterface;
