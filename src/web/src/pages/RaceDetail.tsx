import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
    ArrowBack,
    AccessTime,
    Speed,
    EmojiEvents,
    Person,
    Star
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
    Link,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper
} from '@mui/material'
import { HorseRacingAPI } from '../services/api'

// Interfaces
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
}

interface RealHorse {
    horse_name: string;
    jockey: string;
    trainer: string;
    age: number;
    odds: string | null;
    form?: string;
}

export default function RaceDetail() {
    const { raceId } = useParams<{ raceId: string }>();
    const navigate = useNavigate();
    const [race, setRace] = useState<RealRaceCard | null>(null);
    const [horses, setHorses] = useState<RealHorse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadRaceDetail = async () => {
            if (!raceId) {
                setError('Race ID not provided');
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError(null);
                
                console.log('Loading race detail for ID:', raceId);
                
                // Load daily races to find the specific race
                const dailyRaces = await HorseRacingAPI.getDailyRaces();
                const raceDetail = dailyRaces.races.find(r => r.race_id === parseInt(raceId));
                
                if (!raceDetail) {
                    setError('Race not found');
                    setLoading(false);
                    return;
                }
                
                const raceCard: RealRaceCard = {
                    race_id: raceDetail.race_id,
                    race_number: raceDetail.race_number,
                    race_time: raceDetail.race_time,
                    course: raceDetail.course,
                    race_name: raceDetail.race_name,
                    class: raceDetail.class || 'Unknown',
                    distance: raceDetail.distance || 'Unknown',
                    surface: raceDetail.surface || 'Unknown',
                    prize: raceDetail.prize || 'Unknown',
                    runners: raceDetail.runners
                };
                
                setRace(raceCard);
                
                // Try to load race horses - for now, we'll create some placeholder data
                // since we need to implement the race horses API endpoint
                const placeholderHorses: RealHorse[] = Array.from({ length: raceCard.runners }, (_, i) => ({
                    horse_name: `Horse ${i + 1}`,
                    jockey: `Jockey ${i + 1}`,
                    trainer: `Trainer ${i + 1}`,
                    age: 3 + Math.floor(Math.random() * 5),
                    odds: `${2 + Math.floor(Math.random() * 10)}/1`,
                    form: '12345'.split('').sort(() => Math.random() - 0.5).join('')
                }));
                
                setHorses(placeholderHorses);
                console.log(`Loaded race ${raceId} with ${placeholderHorses.length} runners`);
                
            } catch (error) {
                console.error('Error loading race detail:', error);
                setError('Failed to load race details. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        loadRaceDetail();
    }, [raceId]);

    const handleBackToCourse = () => {
        if (race) {
            navigate(`/course/${encodeURIComponent(race.course)}`);
        } else {
            navigate('/cards');
        }
    };

    const handleBackToSummary = () => {
        navigate('/cards');
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ ml: 2 }}>Loading race details...</Typography>
            </Container>
        );
    }

    if (error || !race) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error" sx={{ mb: 4 }}>
                    {error || 'Race not found'}
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
                    <Link 
                        underline="hover" 
                        color="inherit" 
                        href="#" 
                        onClick={(e) => { e.preventDefault(); handleBackToCourse(); }}
                    >
                        {race.course}
                    </Link>
                    <Typography color="text.primary">Race {race.race_number}</Typography>
                </Breadcrumbs>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <IconButton onClick={handleBackToCourse} sx={{ bgcolor: 'primary.main', color: 'white' }}>
                        <ArrowBack />
                    </IconButton>
                    <Box>
                        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
                            🏇 {race.race_name}
                        </Typography>
                        <Typography variant="h6" color="text.secondary">
                            {race.course} - Race {race.race_number} - {race.race_time}
                        </Typography>
                    </Box>
                </Box>
            </Box>
            
            {/* Race Summary Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <AccessTime sx={{ mr: 1 }} />
                                <Typography variant="h6">Race Time</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>{race.race_time}</Typography>
                            <Typography variant="body2">{race.class}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Speed sx={{ mr: 1 }} />
                                <Typography variant="h6">Distance</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', fontSize: '1.8rem' }}>
                                {race.distance}
                            </Typography>
                            <Typography variant="body2">{race.surface}</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <EmojiEvents sx={{ mr: 1 }} />
                                <Typography variant="h6">Prize Money</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold', fontSize: '1.8rem' }}>
                                {race.prize}
                            </Typography>
                            <Typography variant="body2">Total Prize</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Person sx={{ mr: 1 }} />
                                <Typography variant="h6">Runners</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>{race.runners}</Typography>
                            <Typography variant="body2">Horses</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Runners Table */}
            <Card sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
                    🐎 Runners & Riders
                </Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>No.</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Horse</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Jockey</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Trainer</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Age</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Odds</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Form</Typography></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {horses.map((horse, index) => (
                                <TableRow key={index} hover>
                                    <TableCell>
                                        <Chip 
                                            label={index + 1} 
                                            color="primary" 
                                            variant="outlined"
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                                            {horse.horse_name}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{horse.jockey}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{horse.trainer}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{horse.age}yo</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip 
                                            label={horse.odds || 'NR'} 
                                            variant="outlined" 
                                            color="secondary"
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                                            {horse.form?.split('').map((position, i) => (
                                                <Chip 
                                                    key={i}
                                                    label={position}
                                                    size="small"
                                                    color={position === '1' ? 'success' : position === '2' ? 'warning' : 'default'}
                                                    sx={{ minWidth: '24px', fontSize: '0.75rem' }}
                                                />
                                            ))}
                                        </Box>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Card>

            {/* AI Analysis Section */}
            <Card sx={{ p: 3, mt: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
                    🔮 AI Analysis
                </Typography>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                        Detailed AI predictions and analysis coming soon
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        This section will display ML predictions, confidence scores, and betting recommendations
                    </Typography>
                    <Box sx={{ mt: 3 }}>
                        <Button variant="outlined" disabled>
                            Coming Soon
                        </Button>
                    </Box>
                </Box>
            </Card>
        </Container>
    );
}
