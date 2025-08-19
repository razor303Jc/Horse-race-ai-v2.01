import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Grid,
  Chip,
  Avatar,
  Button,
  IconButton,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Refresh,
  TrendingUp,
  SportsTennis,
  Timer,
  Flag,
  LocalFireDepartment,
  Speed,
  EmojiEvents,
} from '@mui/icons-material';
import { useWebSocket } from '../hooks/useWebSocket';
import { useApiService } from '../hooks/useApiService';

interface Horse {
  id: string;
  name: string;
  jockey: string;
  position: number;
  distance: number;
  speed: number;
  odds: number;
  form: string;
  silks: string;
  trainer: string;
}

interface RaceData {
  id: string;
  name: string;
  track: string;
  distance: string;
  startTime: string;
  status: 'scheduled' | 'running' | 'finished' | 'abandoned';
  progress: number;
  horses: Horse[];
  commentary: string[];
  weather: string;
  going: string;
  currentTime?: string;
  winner?: string;
}

interface LiveRaceTrackerProps {
  raceId: string;
  autoStart?: boolean;
}

export const LiveRaceTracker: React.FC<LiveRaceTrackerProps> = ({
  raceId,
  autoStart = false,
}) => {
  const [raceData, setRaceData] = useState<RaceData | null>(null);
  const [isTracking, setIsTracking] = useState(autoStart);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const commentaryRef = useRef<HTMLDivElement>(null);

  const apiService = useApiService();
  
  // WebSocket for real-time updates
  const { 
    isConnected, 
    lastMessage, 
    sendMessage 
  } = useWebSocket(`ws://localhost:8000/ws/race/${raceId}`, {
    enabled: isTracking,
    reconnectInterval: 5000,
    maxReconnectAttempts: 10,
  });

  // Load initial race data
  useEffect(() => {
    const loadRaceData = async () => {
      try {
        setLoading(true);
        const response = await apiService.get(`/races/${raceId}/live`);
        setRaceData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load race data');
        console.error('Error loading race data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadRaceData();
  }, [raceId, apiService]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const update = JSON.parse(lastMessage);
        
        if (update.type === 'race_update') {
          setRaceData(prev => prev ? { ...prev, ...update.data } : null);
          setLastUpdate(new Date());
        } else if (update.type === 'position_update') {
          setRaceData(prev => {
            if (!prev) return null;
            const updatedHorses = prev.horses.map(horse => {
              const positionUpdate = update.positions.find((p: any) => p.id === horse.id);
              return positionUpdate ? { ...horse, ...positionUpdate } : horse;
            });
            return { ...prev, horses: updatedHorses };
          });
        } else if (update.type === 'commentary') {
          setRaceData(prev => {
            if (!prev) return null;
            return {
              ...prev,
              commentary: [...prev.commentary, update.message],
            };
          });
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    }
  }, [lastMessage]);

  // Auto-scroll commentary
  useEffect(() => {
    if (commentaryRef.current) {
      commentaryRef.current.scrollTop = commentaryRef.current.scrollHeight;
    }
  }, [raceData?.commentary]);

  const handleStartStopTracking = () => {
    setIsTracking(!isTracking);
    if (!isTracking) {
      sendMessage(JSON.stringify({ action: 'subscribe', raceId }));
    } else {
      sendMessage(JSON.stringify({ action: 'unsubscribe', raceId }));
    }
  };

  const getPositionColor = (position: number) => {
    switch (position) {
      case 1: return '#FFD700'; // Gold
      case 2: return '#C0C0C0'; // Silver
      case 3: return '#CD7F32'; // Bronze
      default: return '#e0e0e0';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'info';
      case 'running': return 'success';
      case 'finished': return 'primary';
      case 'abandoned': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading race data...
        </Typography>
      </Box>
    );
  }

  if (error || !raceData) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error || 'Race data not available'}
        <Button onClick={() => window.location.reload()} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      {/* Race Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box>
              <Typography variant="h4" gutterBottom>
                {raceData.name}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                {raceData.track} • {raceData.distance} • {raceData.going} going
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={2}>
              <Chip
                label={raceData.status.toUpperCase()}
                color={getStatusColor(raceData.status) as any}
                size="large"
              />
              <Button
                variant={isTracking ? "outlined" : "contained"}
                startIcon={isTracking ? <Pause /> : <PlayArrow />}
                onClick={handleStartStopTracking}
                color={isTracking ? "secondary" : "primary"}
              >
                {isTracking ? 'Stop Tracking' : 'Start Tracking'}
              </Button>
            </Box>
          </Box>

          {/* Race Progress */}
          {raceData.status === 'running' && (
            <Box sx={{ mb: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Race Progress</Typography>
                <Typography variant="body2">{raceData.progress}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={raceData.progress}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          )}

          {/* Connection Status */}
          <Box display="flex" alignItems="center" gap={1}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: isConnected ? '#4caf50' : '#f44336',
              }}
            />
            <Typography variant="body2" color="text.secondary">
              {isConnected ? 'Live updates connected' : 'Connection lost'}
              {lastUpdate && (
                <span> • Last update: {lastUpdate.toLocaleTimeString()}</span>
              )}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Horse Positions */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <EmojiEvents sx={{ mr: 1 }} />
                Live Positions
              </Typography>
              
              <List sx={{ maxHeight: 500, overflow: 'auto' }}>
                {raceData.horses
                  .sort((a, b) => a.position - b.position)
                  .map((horse, index) => (
                    <React.Fragment key={horse.id}>
                      <ListItem sx={{ py: 2 }}>
                        <ListItemIcon>
                          <Avatar
                            sx={{
                              bgcolor: getPositionColor(horse.position),
                              color: horse.position <= 3 ? '#000' : '#fff',
                              fontWeight: 'bold',
                            }}
                          >
                            {horse.position}
                          </Avatar>
                        </ListItemIcon>
                        
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={2}>
                              <Typography variant="h6" component="span">
                                {horse.name}
                              </Typography>
                              <Chip
                                label={`${horse.odds}/1`}
                                size="small"
                                variant="outlined"
                              />
                              {horse.position === 1 && raceData.status === 'running' && (
                                <LocalFireDepartment color="error" />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                Jockey: {horse.jockey} • Trainer: {horse.trainer}
                              </Typography>
                              <Box display="flex" alignItems="center" gap={2} mt={1}>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Speed fontSize="small" />
                                  <Typography variant="body2">
                                    {horse.speed} km/h
                                  </Typography>
                                </Box>
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Flag fontSize="small" />
                                  <Typography variant="body2">
                                    {horse.distance}m
                                  </Typography>
                                </Box>
                              </Box>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < raceData.horses.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Live Commentary */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <SportsTennis sx={{ mr: 1 }} />
                Live Commentary
              </Typography>
              
              <Paper
                ref={commentaryRef}
                sx={{
                  height: 400,
                  p: 2,
                  backgroundColor: '#f5f5f5',
                  overflow: 'auto',
                }}
              >
                {raceData.commentary.length > 0 ? (
                  raceData.commentary.map((comment, index) => (
                    <Typography
                      key={index}
                      variant="body2"
                      paragraph
                      sx={{
                        mb: 1,
                        p: 1,
                        backgroundColor: '#fff',
                        borderRadius: 1,
                        borderLeft: '4px solid #1976d2',
                      }}
                    >
                      {comment}
                    </Typography>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary" textAlign="center">
                    No commentary available yet...
                  </Typography>
                )}
              </Paper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Race Result */}
      {raceData.status === 'finished' && raceData.winner && (
        <Card sx={{ mt: 3, background: 'linear-gradient(45deg, #FFD700 30%, #FFA000 90%)' }}>
          <CardContent>
            <Typography variant="h5" textAlign="center" color="white" gutterBottom>
              🏆 Race Winner: {raceData.winner} 🏆
            </Typography>
            <Typography variant="body1" textAlign="center" color="white">
              Congratulations to the winning connections!
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
