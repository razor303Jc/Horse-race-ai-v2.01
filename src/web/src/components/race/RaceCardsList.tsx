import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Paper,
    Chip,
    Avatar,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress,
    Alert,
    CircularProgress
} from '@mui/material';
import {
    AccessTime,
    TrendingUp,
    Star,
    Place
} from '@mui/icons-material';
import { HorseRacingAPI } from '../../services/api';

export const RaceCardsList: React.FC = () => {
    const [raceCards, setRaceCards] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRealRaceCards = async () => {
            try {
                setLoading(true);
                setError(null);
                
                // Get real race data with horses from PostgreSQL
                const realData = await HorseRacingAPI.getRaceCardsWithHorses();
                console.log('Loaded real race data:', realData);
                
                // Transform data for display
                const transformedData = realData.races.map(race => ({
                    id: race.race_id,
                    course: race.venue,
                    time: race.time,
                    distance: race.distance,
                    ground: race.going,
                    type: `Class ${race.class}`,
                    prize: `£${race.prize_money.toLocaleString()}`,
                    runners: race.horses.map((horse, index) => ({
                        number: horse.position || (index + 1),
                        name: horse.horse_name || 'Unknown Horse',
                        odds: `${Math.round(horse.win_odds || 10)}/1`,
                        form: horse.recent_form || 'N/A',
                        jockey: horse.jockey_name || 'TBA',
                        trainer: horse.trainer_name || 'TBA',
                        weight: `${Math.round((horse.weight_kg || 60) / 0.453592)}-0`,
                        aiRating: Math.round((horse.win_probability || 10)),
                        prediction: horse.win_probability ? (
                            horse.win_probability > 70 ? 'Top pick' :
                            horse.win_probability > 60 ? 'Banker' :
                            horse.win_probability > 40 ? 'Strong chance' :
                            horse.win_probability > 20 ? 'Danger' : 
                            horse.win_probability > 10 ? 'Each way value' : 'Outsider'
                        ) : 'Analysis pending'
                    }))
                }));
                
                setRaceCards(transformedData);
            } catch (err) {
                console.error('Error fetching real race cards:', err);
                setError(`Failed to load race data from database: ${err}`);
            } finally {
                setLoading(false);
            }
        };

        fetchRealRaceCards();
    }, []);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ ml: 2 }}>
                    Loading real race data from PostgreSQL...
                </Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box sx={{ mb: 3 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <Typography variant="body1">
                    Unable to connect to the PostgreSQL database. Please ensure the API server is running on port 3000.
                </Typography>
            </Box>
        );
    }

    if (!raceCards || raceCards.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 4 }}>
                <Alert severity="info" sx={{ mb: 2 }}>
                    No races found in the database for today.
                </Alert>
                <Typography variant="body1" color="text.secondary">
                    Race data will appear here when available in the PostgreSQL database.
                </Typography>
            </Box>
        );
    }

    return (
        <Box>
            <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Today's Race Cards ({raceCards.length} races) - LIVE DATABASE
            </Typography>
            
            <Grid container spacing={4}>
                {raceCards.map((race) => (
                    <Grid item xs={12} key={race.id}>
                        <Card sx={{ mb: 3 }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                                    <Box>
                                        <Typography variant="h5" component="h3" gutterBottom>
                                            {race.course} - {race.time}
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                            <Chip icon={<AccessTime />} label={race.distance} />
                                            <Chip label={race.ground} color="success" />
                                            <Chip label={race.type} color="primary" />
                                            <Chip label={race.prize} color="secondary" />
                                        </Box>
                                    </Box>
                                </Box>
                                
                                <TableContainer component={Paper} sx={{ mt: 2 }}>
                                    <Table>
                                        <TableHead>
                                            <TableRow sx={{ backgroundColor: 'grey.50' }}>
                                                <TableCell><strong>No.</strong></TableCell>
                                                <TableCell><strong>Horse</strong></TableCell>
                                                <TableCell><strong>Odds</strong></TableCell>
                                                <TableCell><strong>Form</strong></TableCell>
                                                <TableCell><strong>Jockey</strong></TableCell>
                                                <TableCell><strong>Trainer</strong></TableCell>
                                                <TableCell><strong>Weight</strong></TableCell>
                                                <TableCell><strong>AI Rating</strong></TableCell>
                                                <TableCell><strong>Prediction</strong></TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {race.runners.map((horse) => (
                                                <TableRow key={horse.number} hover>
                                                    <TableCell>
                                                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                                            {horse.number}
                                                        </Avatar>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body1" fontWeight="bold">
                                                            {horse.name}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="h6" color="primary">
                                                            {horse.odds}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                                            {horse.form}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.jockey}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.trainer}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.weight}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <LinearProgress
                                                                variant="determinate"
                                                                value={horse.aiRating}
                                                                sx={{ width: 60, height: 8, borderRadius: 4 }}
                                                            />
                                                            <Typography variant="body2" fontWeight="bold">
                                                                {horse.aiRating}/100
                                                            </Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={
                                                                horse.prediction === 'Top pick' || horse.prediction === 'Banker' ? <Star /> :
                                                                horse.prediction === 'Strong chance' || horse.prediction === 'Danger' ? <TrendingUp /> :
                                                                <Place />
                                                            }
                                                            label={horse.prediction}
                                                            color={
                                                                horse.prediction === 'Top pick' || horse.prediction === 'Banker' ? 'success' :
                                                                horse.prediction === 'Strong chance' || horse.prediction === 'Danger' ? 'primary' :
                                                                'default'
                                                            }
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            
            <Box sx={{ mt: 4, p: 3, backgroundColor: 'grey.50', borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>
                    🤖 AI Insights
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Our AI models have analyzed today's races using advanced machine learning algorithms. 
                    The ratings consider form, track conditions, jockey/trainer combinations, and historical data.
                    Live data updated from our racing database with {raceCards.length} active race cards.
                </Typography>
            </Box>
        </Box>
    );
};
