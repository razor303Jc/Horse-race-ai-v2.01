import { AccessTime, InfoOutlined, LocationOn, MonetizationOn, Person, Psychology, TrendingUp, Visibility } from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    CardHeader,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    Grid,
    InputLabel,
    MenuItem,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    ToggleButton,
    ToggleButtonGroup,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

interface RaceData {
  race_id: string;
  meeting: string;
  race_number: number;
  time: string;
  race_name: string;
  class: string;
  distance: string;
  distance_meters: number;
  going: string;
  prize_money: number;
  field_size: number;
  age_restriction: string;
  race_type: string;
  surface: string;
  quality_rating: string;
  predicted_competitiveness: number;
  betting_volume: number;
  favorite: {
    horse: string;
    odds: number;
    probability: number;
  };
  race_insights: string[];
}

interface Horse {
  horse_name: string;
  jockey_name: string;
  trainer_name: string;
  age: number;
  weight_kg: number;
  win_odds: number;
  win_probability?: number;
  career_record: string;
  recent_form?: string;
  position?: number;
  silk_colors?: string;
}

interface RaceCardData {
  race_id: string;
  race_name: string;
  time: string;
  venue: string;
  distance: string;
  class: number;
  going: string;
  prize_money: number;
  horses: Horse[];
}

interface DailyRacesStats {
  total_races: number;
  total_meetings: number;
  daily_stats: {
    total_prize_money: number;
    group_races: number;
    average_field_size: number;
    handicaps: number;
    maiden_races: number;
    chase_hurdle_races: number;
    quality_distribution: Record<string, number>;
  };
  races: RaceData[];
}

const getQualityColor = (rating: string) => {
  switch (rating) {
    case 'A+': return '#4caf50';
    case 'A': return '#8bc34a';
    case 'A-': return '#cddc39';
    case 'B+': return '#ffeb3b';
    case 'B': return '#ffc107';
    case 'B-': return '#ff9800';
    default: return '#9e9e9e';
  }
};

const getRaceTypeColor = (type: string) => {
  switch (type) {
    case 'Group 1': return '#e91e63';
    case 'Group 2': return '#9c27b0';
    case 'Group 3': return '#673ab7';
    case 'Listed': return '#3f51b5';
    case 'Handicap': return '#2196f3';
    case 'Hurdle': return '#00bcd4';
    case 'Chase': return '#009688';
    default: return '#795548';
  }
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const DailyRaces: React.FC = () => {
  const [data, setData] = useState<DailyRacesStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedRaceCard, setSelectedRaceCard] = useState<RaceCardData | null>(null);
  const [raceCardDialogOpen, setRaceCardDialogOpen] = useState(false);
  const [loadingRaceCard, setLoadingRaceCard] = useState(false);
  const [raceCardError, setRaceCardError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<string>('time');
  const [filterMeeting, setFilterMeeting] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [viewMode, setViewMode] = useState<string>('table');

  useEffect(() => {
    const fetchDailyRaces = async () => {
      try {
        const response = await fetch('/api/daily_races');
        const racesData = await response.json();
        setData(racesData);
      } catch (error) {
        console.error('Error fetching daily races:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDailyRaces();
  }, []);

  const fetchRaceCard = async (raceId: string) => {
    setLoadingRaceCard(true);
    setRaceCardError(null);
    
    try {
      const response = await fetch(`/api/race_details/${raceId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const raceCardData = await response.json();
      setSelectedRaceCard(raceCardData);
      setRaceCardDialogOpen(true);
    } catch (error) {
      setRaceCardError(error instanceof Error ? error.message : 'Failed to fetch race card');
    } finally {
      setLoadingRaceCard(false);
    }
  };

  const getOddsColor = (probability: number) => {
    if (probability > 40) return '#4caf50'; // Green for favorites
    if (probability > 20) return '#ff9800'; // Orange for decent chances  
    if (probability > 10) return '#2196f3'; // Blue for outsiders
    return '#9e9e9e'; // Gray for long shots
  };

  const getFormColor = (form: string) => {
    if (form.includes('1') || form.includes('2')) return '#4caf50';
    if (form.includes('3') || form.includes('4')) return '#ff9800';
    return '#9e9e9e';
  };

  if (loading) {
    return <Typography>Loading daily races...</Typography>;
  }

  if (!data) {
    return <Typography>No race data available</Typography>;
  }

  const meetings = [...new Set(data.races.map(race => race.meeting))];
  const raceTypes = [...new Set(data.races.map(race => race.race_type))];

  let filteredRaces = data.races;
  if (filterMeeting !== 'all') {
    filteredRaces = filteredRaces.filter(race => race.meeting === filterMeeting);
  }
  if (filterType !== 'all') {
    filteredRaces = filteredRaces.filter(race => race.race_type === filterType);
  }

  const sortedRaces = [...filteredRaces].sort((a, b) => {
    switch (sortBy) {
      case 'time':
        return a.time.localeCompare(b.time);
      case 'quality':
        return b.quality_rating.localeCompare(a.quality_rating);
      case 'prize':
        return b.prize_money - a.prize_money;
      case 'competitiveness':
        return b.predicted_competitiveness - a.predicted_competitiveness;
      default:
        return 0;
    }
  });

  return (
    <Box>
      {/* Daily Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccessTime sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Today's Racing</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {data.total_races}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Races across {data.total_meetings} meetings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <MonetizationOn sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Prize Money</Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {formatCurrency(data.daily_stats.total_prize_money)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total on offer today
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Group Races</Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {data.daily_stats.group_races}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Premium quality races
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <InfoOutlined sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Avg Field Size</Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                {data.daily_stats.average_field_size}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Runners per race
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Sort by</InputLabel>
                <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <MenuItem value="time">Time</MenuItem>
                  <MenuItem value="quality">Quality</MenuItem>
                  <MenuItem value="prize">Prize Money</MenuItem>
                  <MenuItem value="competitiveness">Competitiveness</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Meeting</InputLabel>
                <Select value={filterMeeting} onChange={(e) => setFilterMeeting(e.target.value)}>
                  <MenuItem value="all">All Meetings</MenuItem>
                  {meetings.map(meeting => (
                    <MenuItem key={meeting} value={meeting}>{meeting}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Race Type</InputLabel>
                <Select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
                  <MenuItem value="all">All Types</MenuItem>
                  {raceTypes.map(type => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(_, newValue) => newValue && setViewMode(newValue)}
                size="small"
              >
                <ToggleButton value="table">Table View</ToggleButton>
                <ToggleButton value="cards">Card View</ToggleButton>
              </ToggleButtonGroup>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Race Table */}
      <Card>
        <CardHeader title={`Race Schedule (${sortedRaces.length} races)`} />
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Meeting</TableCell>
                  <TableCell>Race</TableCell>
                  <TableCell>Class</TableCell>
                  <TableCell>Distance</TableCell>
                  <TableCell>Going</TableCell>
                  <TableCell>Quality</TableCell>
                  <TableCell>Prize</TableCell>
                  <TableCell>Field</TableCell>
                  <TableCell>Favorite</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedRaces.map((race) => (
                  <TableRow 
                    key={race.race_id} 
                    hover 
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'rgba(25, 118, 210, 0.08)'
                      }
                    }}
                    onClick={() => fetchRaceCard(race.race_id)}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {race.time}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {race.meeting}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {race.race_name}
                        </Typography>
                        <Chip
                          label={race.race_type}
                          size="small"
                          sx={{ 
                            mt: 0.5,
                            backgroundColor: getRaceTypeColor(race.race_type),
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        Class {race.class}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {race.distance}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {race.going}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={race.quality_rating}
                        size="small"
                        sx={{ 
                          backgroundColor: getQualityColor(race.quality_rating),
                          color: 'white',
                          fontWeight: 'bold'
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatCurrency(race.prize_money)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {race.field_size} runners
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {race.favorite.horse}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {race.favorite.odds}/1 ({race.favorite.probability.toFixed(1)}%)
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Race Card Details Dialog */}
      <Dialog 
        open={raceCardDialogOpen} 
        onClose={() => setRaceCardDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          {selectedRaceCard && (
            <Box>
              <Typography variant="h5" component="div" gutterBottom>
                {selectedRaceCard.race_name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip icon={<AccessTime />} label={selectedRaceCard.time} size="small" color="primary" />
                <Chip icon={<LocationOn />} label={selectedRaceCard.venue} size="small" color="secondary" />
                <Chip label={`${selectedRaceCard.distance}`} size="small" />
                <Chip label={`Class ${selectedRaceCard.class}`} size="small" />
                <Chip label={selectedRaceCard.going} size="small" />
                <Chip label={`${formatCurrency(selectedRaceCard.prize_money)}`} size="small" color="success" />
              </Box>
            </Box>
          )}
        </DialogTitle>
        
        <DialogContent>
          {loadingRaceCard ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : raceCardError ? (
            <Box sx={{ textAlign: 'center', p: 3 }}>
              <Typography color="error" gutterBottom>
                Error loading race card: {raceCardError}
              </Typography>
              <Button 
                onClick={() => selectedRaceCard && fetchRaceCard(selectedRaceCard.race_id)}
                variant="outlined"
              >
                Retry
              </Button>
            </Box>
          ) : selectedRaceCard ? (
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Horse</TableCell>
                    <TableCell>Jockey</TableCell>
                    <TableCell>Trainer</TableCell>
                    <TableCell>Age/Wgt</TableCell>
                    <TableCell>Odds</TableCell>
                    <TableCell>Form</TableCell>
                    <TableCell>Record</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {selectedRaceCard.horses.map((horse, index) => (
                    <TableRow key={index} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {horse.position || index + 1}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {horse.horse_name}
                          </Typography>
                          {horse.silk_colors && (
                            <Typography variant="caption" color="text.secondary">
                              {horse.silk_colors}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Person fontSize="small" color="action" />
                          <Typography variant="body2">
                            {horse.jockey_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Psychology fontSize="small" color="action" />
                          <Typography variant="body2">
                            {horse.trainer_name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {horse.age}y / {horse.weight_kg}kg
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${horse.win_odds}/1`}
                          size="small"
                          sx={{
                            backgroundColor: getOddsColor(horse.win_probability || 0),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={horse.recent_form || 'N/A'}
                          size="small"
                          sx={{
                            backgroundColor: getFormColor(horse.recent_form || ''),
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Visibility fontSize="small" color="action" />
                          <Typography variant="body2">
                            {horse.career_record}
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : null}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setRaceCardDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
