import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ArrowBack,
    AccessTime,
    Speed,
    EmojiEvents,
    Refresh
} from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    Container,
    Grid,
    Typography,
    Chip,
    CircularProgress,
    Alert,
    Button,
    IconButton,
    Breadcrumbs,
    Link
} from '@mui/material'
import { HorseRacingAPI } from '../services/api'

// Interface
interface RealRaceCard {
    race_id: number;
    race_number: number;
    race_time: string;
    course: string;
    race_name: string;
    class: string;
    distance: string;
    surface: string;
    prize: string;
    runners: number;
    status?: string;
}

export default function CourseDetail() {
    const { courseName } = useParams<{ courseName: string }>();
    const navigate = useNavigate();
    const [races, setRaces] = useState<RealRaceCard[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadCourseRaces = async () => {
            if (!courseName) {
                setError('Course name not provided');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                
                console.log('Loading races for course:', courseName);
                const dailyRaces = await HorseRacingAPI.getDailyRaces();
                
                // Filter races for this specific course
                const courseRaces = dailyRaces.races
                    .filter(race => race.course === decodeURIComponent(courseName))
                    .map(race => ({
                        race_id: race.race_id,
                        race_number: race.race_number,
                        race_time: race.race_time,
                        course: race.course,
                        race_name: race.race_name,
                        class: race.class || 'Unknown',
                        distance: race.distance || 'Unknown',
                        surface: race.surface || 'Unknown',
                        prize: race.prize || 'Unknown',
                        runners: race.runners,
                        status: 'upcoming'
                    }))
                    .sort((a, b) => a.race_time.localeCompare(b.race_time));
                
                setRaces(courseRaces);
                console.log(`Loaded ${courseRaces.length} races for ${courseName}`);
                
            } catch (error) {
                console.error('Error loading course races:', error);
                setError('Failed to load course races. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        loadCourseRaces();
    }, [courseName]);

    const handleRaceClick = (raceId: number) => {
        navigate(`/race/${raceId}`);
    };

    const handleBackToSummary = () => {
        navigate('/cards');
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ ml: 2 }}>Loading {courseName} races...</Typography>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error" sx={{ mb: 4 }}>
                    {error}
                    <Button variant="outlined" sx={{ ml: 2 }} onClick={() => window.location.reload()}>
                        Retry
                    </Button>
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Header with Navigation */}
            <Box sx={{ mb: 4 }}>
                <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
                    <Link 
                        underline="hover" 
                        color="inherit" 
                        href="#" 
                        onClick={(e) => { e.preventDefault(); handleBackToSummary(); }}
                    >
                        Race Cards
                    </Link>
                    <Typography color="text.primary">{decodeURIComponent(courseName || '')}</Typography>
                </Breadcrumbs>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <IconButton onClick={handleBackToSummary} sx={{ bgcolor: 'primary.main', color: 'white' }}>
                        <ArrowBack />
                    </IconButton>
                    <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
                        🏇 {decodeURIComponent(courseName || '')} - Today's Races
                    </Typography>
                </Box>
            </Box>
            
            {/* Course Summary Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <AccessTime sx={{ mr: 1 }} />
                                <Typography variant="h6">Total Races</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>{races.length}</Typography>
                            <Typography variant="body2">Today</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Speed sx={{ mr: 1 }} />
                                <Typography variant="h6">First Race</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                                {races.length > 0 ? races[0].race_time : '--:--'}
                            </Typography>
                            <Typography variant="body2">Start Time</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <EmojiEvents sx={{ mr: 1 }} />
                                <Typography variant="h6">Last Race</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                                {races.length > 0 ? races[races.length - 1].race_time : '--:--'}
                            </Typography>
                            <Typography variant="body2">End Time</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Refresh sx={{ mr: 1 }} />
                                <Typography variant="h6">Surface</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', fontSize: '1.8rem' }}>
                                {races.length > 0 ? races[0].surface.split(' ')[0] : 'Unknown'}
                            </Typography>
                            <Typography variant="body2">Going</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Race Cards */}
            <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
                📅 Today's Race Schedule
            </Typography>
            
            <Grid container spacing={3}>
                {races.map((race) => (
                    <Grid item xs={12} md={6} key={race.race_id}>
                        <Card 
                            sx={{ 
                                p: 3, 
                                height: '100%', 
                                cursor: 'pointer',
                                '&:hover': { 
                                    elevation: 8,
                                    transform: 'translateY(-2px)',
                                    transition: 'all 0.2s ease-in-out'
                                }
                            }}
                            onClick={() => handleRaceClick(race.race_id)}
                        >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                                    Race {race.race_number}
                                </Typography>
                                <Chip 
                                    label={race.race_time} 
                                    color="primary"
                                    variant="filled"
                                    sx={{ fontWeight: 'bold' }}
                                />
                            </Box>
                            
                            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
                                {race.race_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                {race.class}
                            </Typography>
                            
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="text.secondary">Distance</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.distance}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="text.secondary">Prize Money</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.prize}</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="text.secondary">Field Size</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.runners} runners</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="text.secondary">Going</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.surface}</Typography>
                                </Grid>
                            </Grid>
                            
                            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="body2" color="text.secondary">
                                    Click to view runners and predictions
                                </Typography>
                                <Button variant="outlined" size="small">
                                    View Details
                                </Button>
                            </Box>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            
            {races.length === 0 && (
                <Alert severity="info" sx={{ mt: 4 }}>
                    No races found for {decodeURIComponent(courseName || '')} today.
                </Alert>
            )}
        </Container>
    );
}
