import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  Grid,
  Button,
  IconButton,
  Dialog,
  DialogContent,
  Fab,
  Zoom,
  Paper,
  Divider,
  useTheme,
  useMediaQuery,
  Alert,
  ButtonGroup,
  Slider,
  Switch,
  FormControlLabel,
  Container
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Refresh,
  Fullscreen,
  FullscreenExit,
  VolumeUp,
  VolumeOff,
  Speed,
  Flag,
  EmojiEvents,
  Timer,
  TrendingUp,
  TrendingDown,
  MonetizationOn,
  Visibility,
  Share,
  Bookmark,
  BookmarkBorder,
  Info,
  Close
} from '@mui/icons-material';

interface RacePosition {
  position: number;
  horseId: string;
  horseName: string;
  jockey: string;
  distance: number; // meters from finish
  speed: number; // current speed km/h
  odds: number;
  prediction?: number; // AI prediction confidence %
}

interface RaceProgress {
  raceId: string;
  raceName: string;
  track: string;
  distance: number; // total race distance in meters
  elapsed: number; // seconds elapsed
  status: 'pre-race' | 'running' | 'finished' | 'delayed';
  positions: RacePosition[];
  weather?: string;
  track_condition?: string;
  commentary?: string[];
}

interface MobileRaceViewerProps {
  raceProgress: RaceProgress;
  autoRefresh?: boolean;
  refreshInterval?: number;
  onBetPlaced?: (horseId: string, amount: number) => void;
  allowBetting?: boolean;
}

export const MobileRaceViewer: React.FC<MobileRaceViewerProps> = ({
  raceProgress,
  autoRefresh = true,
  refreshInterval = 2000,
  onBetPlaced,
  allowBetting = true
}) => {
  const [isPlaying, setIsPlaying] = useState(autoRefresh);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedHorse, setSelectedHorse] = useState<string | null>(null);
  const [volume, setVolume] = useState(80);
  const [isMuted, setIsMuted] = useState(false);
  const [showPredictions, setShowPredictions] = useState(true);
  const [bookmarkedHorses, setBookmarkedHorses] = useState<Set<string>>(new Set());
  const [quickBetAmount, setQuickBetAmount] = useState(10);
  const [showQuickBet, setShowQuickBet] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState(Date.now());

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const containerRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-refresh effect
  useEffect(() => {
    if (isPlaying && raceProgress.status === 'running') {
      intervalRef.current = setInterval(() => {
        setLastUpdateTime(Date.now());
        // In a real app, this would trigger a data refresh
      }, refreshInterval);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, raceProgress.status, refreshInterval]);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current?.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleBookmark = (horseId: string) => {
    const newBookmarks = new Set(bookmarkedHorses);
    if (newBookmarks.has(horseId)) {
      newBookmarks.delete(horseId);
    } else {
      newBookmarks.add(horseId);
    }
    setBookmarkedHorses(newBookmarks);
  };

  const handleQuickBet = async (horseId: string) => {
    if (onBetPlaced) {
      await onBetPlaced(horseId, quickBetAmount);
      setShowQuickBet(false);
    }
  };

  const getPositionColor = (position: number) => {
    switch (position) {
      case 1: return theme.palette.success.main;
      case 2: return theme.palette.info.main;
      case 3: return theme.palette.warning.main;
      default: return theme.palette.grey[500];
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return theme.palette.success.main;
      case 'finished': return theme.palette.info.main;
      case 'delayed': return theme.palette.warning.main;
      default: return theme.palette.grey[500];
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressPercentage = (distance: number) => {
    return Math.max(0, Math.min(100, ((raceProgress.distance - distance) / raceProgress.distance) * 100));
  };

  // Race header component
  const RaceHeader = () => (
    <Paper sx={{ p: 2, mb: 2, backgroundColor: theme.palette.primary.main, color: 'white' }}>
      <Grid container alignItems="center" spacing={2}>
        <Grid item xs>
          <Typography variant="h6" noWrap>
            {raceProgress.raceName}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {raceProgress.track} • {raceProgress.distance}m
          </Typography>
        </Grid>
        <Grid item>
          <Chip
            label={raceProgress.status.toUpperCase()}
            sx={{
              backgroundColor: getStatusColor(raceProgress.status),
              color: 'white',
              fontWeight: 'bold'
            }}
          />
        </Grid>
      </Grid>
      
      {raceProgress.status === 'running' && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            Elapsed: {formatTime(raceProgress.elapsed)}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(raceProgress.elapsed / 180) * 100} // Assuming 3 min average race
            sx={{
              mt: 1,
              height: 6,
              borderRadius: 3,
              backgroundColor: 'rgba(255,255,255,0.3)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: 'white'
              }
            }}
          />
        </Box>
      )}
    </Paper>
  );

  // Horse position component
  const HorsePosition: React.FC<{ position: RacePosition; index: number }> = ({ position, index }) => (
    <Card
      sx={{
        mb: 1,
        cursor: 'pointer',
        transition: 'all 0.2s',
        backgroundColor: selectedHorse === position.horseId ? theme.palette.action.selected : 'inherit',
        '&:active': {
          transform: 'scale(0.98)'
        }
      }}
      onClick={() => setSelectedHorse(selectedHorse === position.horseId ? null : position.horseId)}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: getPositionColor(position.position),
              width: 32,
              height: 32,
              mr: 2,
              fontWeight: 'bold'
            }}
          >
            {position.position}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="h6" noWrap>
              {position.horseName}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {position.jockey}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); toggleBookmark(position.horseId); }}>
              {bookmarkedHorses.has(position.horseId) ? <Bookmark color="primary" /> : <BookmarkBorder />}
            </IconButton>
            {allowBetting && (
              <Button
                size="small"
                variant="outlined"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedHorse(position.horseId);
                  setShowQuickBet(true);
                }}
                sx={{ minWidth: 'auto', px: 1 }}
              >
                Bet
              </Button>
            )}
          </Box>
        </Box>

        {/* Progress bar showing race progress */}
        <Box sx={{ mb: 1 }}>
          <LinearProgress
            variant="determinate"
            value={getProgressPercentage(position.distance)}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: theme.palette.grey[200],
              '& .MuiLinearProgress-bar': {
                backgroundColor: getPositionColor(position.position),
                borderRadius: 4
              }
            }}
          />
          <Typography variant="caption" color="text.secondary">
            {position.distance}m to finish
          </Typography>
        </Box>

        {/* Horse details */}
        <Grid container spacing={2}>
          <Grid item xs={3}>
            <Typography variant="caption" color="text.secondary" display="block">
              Speed
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {position.speed}km/h
            </Typography>
          </Grid>
          <Grid item xs={3}>
            <Typography variant="caption" color="text.secondary" display="block">
              Odds
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {position.odds}/1
            </Typography>
          </Grid>
          {showPredictions && position.prediction && (
            <Grid item xs={3}>
              <Typography variant="caption" color="text.secondary" display="block">
                AI Conf.
              </Typography>
              <Typography 
                variant="body2" 
                fontWeight="bold"
                color={position.prediction > 70 ? 'success.main' : position.prediction > 40 ? 'warning.main' : 'error.main'}
              >
                {position.prediction}%
              </Typography>
            </Grid>
          )}
          <Grid item xs={3}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {position.position <= 3 && (
                <EmojiEvents sx={{ color: getPositionColor(position.position) }} />
              )}
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  // Control panel
  const ControlPanel = () => (
    <Paper 
      sx={{ 
        p: 2, 
        position: 'sticky', 
        bottom: 0, 
        zIndex: 1000,
        backgroundColor: theme.palette.background.paper,
        borderTop: `1px solid ${theme.palette.divider}`
      }}
    >
      <Grid container alignItems="center" spacing={1}>
        <Grid item>
          <IconButton onClick={togglePlayPause}>
            {isPlaying ? <Pause /> : <PlayArrow />}
          </IconButton>
        </Grid>
        <Grid item>
          <IconButton onClick={() => window.location.reload()}>
            <Refresh />
          </IconButton>
        </Grid>
        <Grid item>
          <IconButton onClick={toggleFullscreen}>
            {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
          </IconButton>
        </Grid>
        <Grid item>
          <IconButton onClick={toggleMute}>
            {isMuted ? <VolumeOff /> : <VolumeUp />}
          </IconButton>
        </Grid>
        <Grid item xs>
          <FormControlLabel
            control={
              <Switch
                checked={showPredictions}
                onChange={(e) => setShowPredictions(e.target.checked)}
                size="small"
              />
            }
            label="AI"
            sx={{ mr: 0 }}
          />
        </Grid>
        <Grid item>
          <Typography variant="caption" color="text.secondary">
            Last: {new Date(lastUpdateTime).toLocaleTimeString()}
          </Typography>
        </Grid>
      </Grid>
    </Paper>
  );

  // Quick bet dialog
  const QuickBetDialog = () => (
    <Dialog
      open={showQuickBet}
      onClose={() => setShowQuickBet(false)}
      fullWidth
      maxWidth="xs"
    >
      <DialogContent>
        <Box sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Quick Bet
          </Typography>
          {selectedHorse && (
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {raceProgress.positions.find(p => p.horseId === selectedHorse)?.horseName}
            </Typography>
          )}
          
          <Box sx={{ my: 3 }}>
            <Typography variant="body2" gutterBottom>
              Amount: £{quickBetAmount}
            </Typography>
            <Slider
              value={quickBetAmount}
              onChange={(_, value) => setQuickBetAmount(value as number)}
              min={5}
              max={100}
              step={5}
              marks={[
                { value: 5, label: '£5' },
                { value: 25, label: '£25' },
                { value: 50, label: '£50' },
                { value: 100, label: '£100' }
              ]}
            />
          </Box>

          <ButtonGroup fullWidth>
            <Button onClick={() => setShowQuickBet(false)}>
              Cancel
            </Button>
            <Button
              variant="contained"
              onClick={() => selectedHorse && handleQuickBet(selectedHorse)}
            >
              Place Bet
            </Button>
          </ButtonGroup>
        </Box>
      </DialogContent>
    </Dialog>
  );

  return (
    <Container maxWidth="md" ref={containerRef} sx={{ p: isMobile ? 1 : 2 }}>
      <RaceHeader />

      {/* Race conditions */}
      {(raceProgress.weather || raceProgress.track_condition) && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {raceProgress.weather && `Weather: ${raceProgress.weather}`}
          {raceProgress.weather && raceProgress.track_condition && ' • '}
          {raceProgress.track_condition && `Track: ${raceProgress.track_condition}`}
        </Alert>
      )}

      {/* Horse positions */}
      <Box sx={{ mb: 10 }}>
        {raceProgress.positions
          .sort((a, b) => a.position - b.position)
          .map((position, index) => (
            <HorsePosition key={position.horseId} position={position} index={index} />
          ))}
      </Box>

      {/* Commentary */}
      {raceProgress.commentary && raceProgress.commentary.length > 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Live Commentary
          </Typography>
          {raceProgress.commentary.slice(-3).map((comment, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1 }}>
              {comment}
            </Typography>
          ))}
        </Paper>
      )}

      <ControlPanel />
      <QuickBetDialog />

      {/* Floating share button */}
      <Zoom in={raceProgress.status === 'running'}>
        <Fab
          size="medium"
          sx={{
            position: 'fixed',
            bottom: 80,
            right: 16,
            backgroundColor: theme.palette.secondary.main
          }}
          onClick={() => {
            if (navigator.share) {
              navigator.share({
                title: `${raceProgress.raceName} - Live Race`,
                text: `Watch ${raceProgress.raceName} live!`,
                url: window.location.href
              });
            }
          }}
        >
          <Share />
        </Fab>
      </Zoom>
    </Container>
  );
};

export default MobileRaceViewer;
