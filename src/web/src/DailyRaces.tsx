import { AccessTime, InfoOutlined, MonetizationOn, TrendingUp } from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    CardHeader,
    Chip,
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
    Typography,
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

interface DailyRacesData {
  date: string;
  total_races: number;
  total_meetings: number;
  races: RaceData[];
  daily_stats: {
    total_prize_money: number;
    average_field_size: number;
    group_races: number;
    handicaps: number;
    maiden_races: number;
    chase_hurdle_races: number;
    quality_distribution: Record<string, number>;
  };
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
  const [data, setData] = useState<DailyRacesData | null>(null);
  const [loading, setLoading] = useState(true);
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
                  <TableRow key={race.race_id} hover>
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
    </Box>
  );
};
