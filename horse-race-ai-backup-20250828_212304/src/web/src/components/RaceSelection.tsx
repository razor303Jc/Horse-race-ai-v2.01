import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Avatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  Schedule,
  LocationOn,
  SportsTennis,
  Search,
  LiveTv,
  Timer,
  Flag,
} from '@mui/icons-material';
import { useApiService } from '../hooks/useApiService';
import { LiveRaceTracker } from './LiveRaceTracker';

interface RaceInfo {
  id: string;
  name: string;
  track: string;
  startTime: string;
  distance: string;
  going: string;
  status: 'scheduled' | 'running' | 'finished' | 'abandoned';
  horses: number;
  prize: string;
  grade: string;
  weather: string;
  isLive: boolean;
}

export const RaceSelection: React.FC = () => {
  const [races, setRaces] = useState<RaceInfo[]>([]);
  const [filteredRaces, setFilteredRaces] = useState<RaceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRaceId, setSelectedRaceId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [trackFilter, setTrackFilter] = useState<string>('all');
  
  const apiService = useApiService();

  // Load races
  useEffect(() => {
    const loadRaces = async () => {
      try {
        setLoading(true);
        const response = await apiService.get('/races/today');
        setRaces(response.data);
        setFilteredRaces(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load races');
        console.error('Error loading races:', err);
      } finally {
        setLoading(false);
      }
    };

    loadRaces();
    
    // Refresh races every 30 seconds
    const interval = setInterval(loadRaces, 30000);
    return () => clearInterval(interval);
  }, [apiService]);

  // Filter races
  useEffect(() => {
    let filtered = races;

    if (searchTerm) {
      filtered = filtered.filter(race =>
        race.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        race.track.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(race => race.status === statusFilter);
    }

    if (trackFilter !== 'all') {
      filtered = filtered.filter(race => race.track === trackFilter);
    }

    setFilteredRaces(filtered);
  }, [races, searchTerm, statusFilter, trackFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'info';
      case 'running': return 'success';
      case 'finished': return 'primary';
      case 'abandoned': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled': return <Schedule />;
      case 'running': return <LiveTv />;
      case 'finished': return <Flag />;
      case 'abandoned': return <Timer />;
      default: return <Schedule />;
    }
  };

  const formatTime = (timeString: string) => {
    const time = new Date(timeString);
    return time.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getUniqueValues = (key: keyof RaceInfo): string[] => {
    return [...new Set(races.map(race => String(race[key])))].filter(Boolean);
  };

  if (selectedRaceId) {
    return (
      <Dialog
        open={!!selectedRaceId}
        onClose={() => setSelectedRaceId(null)}
        maxWidth="xl"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        <DialogTitle>
          Live Race Tracking
          <Button
            onClick={() => setSelectedRaceId(null)}
            sx={{ float: 'right' }}
          >
            Close
          </Button>
        </DialogTitle>
        <DialogContent>
          <LiveRaceTracker raceId={selectedRaceId} autoStart={true} />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Live Race Tracking
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Select a race to start live tracking with real-time updates
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search races or tracks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="running">Running</MenuItem>
                  <MenuItem value="finished">Finished</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Track</InputLabel>
                <Select
                  value={trackFilter}
                  onChange={(e) => setTrackFilter(e.target.value)}
                  label="Track"
                >
                  <MenuItem value="all">All Tracks</MenuItem>
                  {getUniqueValues('track').map((track) => (
                    <MenuItem key={String(track)} value={track}>
                      {track}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Race Cards */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading races...
          </Typography>
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
          <Button onClick={() => window.location.reload()} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {filteredRaces.map((race) => (
            <Grid item xs={12} md={6} lg={4} key={race.id}>
              <Card
                data-testid="race-card"
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  '&:hover': {
                    boxShadow: 6,
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                {race.isLive && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      backgroundColor: '#ff4444',
                      color: 'white',
                      px: 1,
                      py: 0.5,
                      borderRadius: 1,
                      fontSize: '0.75rem',
                      fontWeight: 'bold',
                      zIndex: 1,
                    }}
                  >
                    LIVE
                  </Box>
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <Avatar
                      sx={{
                        bgcolor: getStatusColor(race.status) === 'success' ? '#4caf50' : '#1976d2',
                        width: 32,
                        height: 32,
                      }}
                    >
                      {getStatusIcon(race.status)}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" noWrap>
                        {race.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatTime(race.startTime)}
                      </Typography>
                    </Box>
                  </Box>

                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <LocationOn fontSize="small" color="action" />
                    <Typography variant="body2">{race.track}</Typography>
                  </Box>

                  <Grid container spacing={1} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Distance
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {race.distance}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Runners
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {race.horses}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Going
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {race.going}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Grade
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {race.grade}
                      </Typography>
                    </Grid>
                  </Grid>

                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Chip
                      label={race.status.toUpperCase()}
                      color={getStatusColor(race.status) as any}
                      size="small"
                    />
                    <Typography variant="body2" fontWeight="bold" color="primary">
                      {race.prize}
                    </Typography>
                  </Box>
                </CardContent>

                <Divider />
                
                <Box sx={{ p: 2 }}>
                  <Button
                    fullWidth
                    variant={race.status === 'running' ? 'contained' : 'outlined'}
                    color={race.status === 'running' ? 'success' : 'primary'}
                    startIcon={<LiveTv />}
                    onClick={() => setSelectedRaceId(race.id)}
                    disabled={race.status === 'abandoned'}
                  >
                    {race.status === 'running' ? 'Watch Live' : 'View Race'}
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {filteredRaces.length === 0 && !loading && (
        <Box textAlign="center" py={4}>
          <SportsTennis sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No races found matching your criteria
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search filters
          </Typography>
        </Box>
      )}
    </Box>
  );
};
