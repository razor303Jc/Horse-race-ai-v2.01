import {
    ExpandMore,
    Person,
    Psychology,
    Speed,
    TrendingUp
} from '@mui/icons-material';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

interface Horse {
    horse_name: string;
    jockey_name: string;
    trainer_name: string;
    age: number;
    weight_kg: number;
    handicap_weight: number;
    draw: number;
    barrier: number;
    form: string;
    win_odds: string;
    place_odds: string;
    win_probability: number;
    decimal_odds: number;
    last_run_days: number;
    career_record: string;
    win_rate: number;
    distance_record: string;
    track_record: string;
}

interface RaceCard {
    race_id: string;
    horses: Horse[];
    total_runners: number;
}

interface RaceCardsData {
    total_races: number;
    total_horses: number;
    data_source: string;
    timestamp: string;
    races: RaceCard[];
}

const RealRaceCards: React.FC = () => {
    const [raceCards, setRaceCards] = useState<RaceCardsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedRace, setSelectedRace] = useState<RaceCard | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);

    const fetchRaceCards = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/real_race_cards');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setRaceCards(data);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch race cards');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRaceCards();
        // Refresh every 5 minutes
        const interval = setInterval(fetchRaceCards, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

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

    const handleRaceClick = (race: RaceCard) => {
        setSelectedRace(race);
        setDialogOpen(true);
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
                <Typography variant="h6" ml={2}>Loading race cards...</Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Alert severity="error" sx={{ m: 2 }}>
                Error loading race cards: {error}
                <Button onClick={fetchRaceCards} sx={{ ml: 2 }}>Retry</Button>
            </Alert>
        );
    }

    if (!raceCards || raceCards.races.length === 0) {
        return (
            <Alert severity="info" sx={{ m: 2 }}>
                No race card data available. Check database connection.
                <Button onClick={fetchRaceCards} sx={{ ml: 2 }}>Refresh</Button>
            </Alert>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            {/* Header Stats */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Total Races
                            </Typography>
                            <Typography variant="h4">
                                {raceCards.total_races}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Total Horses
                            </Typography>
                            <Typography variant="h4">
                                {raceCards.total_horses}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Data Source
                            </Typography>
                            <Chip 
                                label={raceCards.data_source}
                                color={raceCards.data_source === 'live_database' ? 'success' : 'warning'}
                            />
                        </CardContent>
                    </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                                Last Updated
                            </Typography>
                            <Typography variant="body2">
                                {new Date(raceCards.timestamp).toLocaleTimeString()}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Race Cards */}
            <Typography variant="h4" gutterBottom>
                🏇 Live Race Cards
            </Typography>

            {raceCards.races.map((race) => (
                <Accordion key={race.race_id} sx={{ mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                            <Typography variant="h6" sx={{ flexGrow: 1 }}>
                                Race {race.race_id} - {race.total_runners} Runners
                            </Typography>
                            <Chip 
                                label={`${race.horses.length} entries`}
                                color="primary"
                                size="small"
                            />
                        </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                        <TableContainer component={Paper}>
                            <Table size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Horse</TableCell>
                                        <TableCell>Jockey</TableCell>
                                        <TableCell>Trainer</TableCell>
                                        <TableCell>Age</TableCell>
                                        <TableCell>Weight</TableCell>
                                        <TableCell>Odds</TableCell>
                                        <TableCell>Probability</TableCell>
                                        <TableCell>Form</TableCell>
                                        <TableCell>Record</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {race.horses.map((horse, idx) => (
                                        <TableRow 
                                            key={idx}
                                            hover
                                            sx={{ 
                                                cursor: 'pointer',
                                                '&:hover': { backgroundColor: '#f5f5f5' }
                                            }}
                                        >
                                            <TableCell>
                                                <Typography variant="subtitle2" fontWeight="bold">
                                                    {horse.horse_name}
                                                </Typography>
                                                {horse.draw && (
                                                    <Typography variant="caption" color="textSecondary">
                                                        Draw: {horse.draw}
                                                    </Typography>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Box display="flex" alignItems="center">
                                                    <Person fontSize="small" sx={{ mr: 0.5 }} />
                                                    {horse.jockey_name}
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Box display="flex" alignItems="center">
                                                    <Psychology fontSize="small" sx={{ mr: 0.5 }} />
                                                    {horse.trainer_name}
                                                </Box>
                                            </TableCell>
                                            <TableCell>{horse.age}yo</TableCell>
                                            <TableCell>
                                                {horse.weight_kg}kg
                                                {horse.handicap_weight && (
                                                    <Typography variant="caption" display="block">
                                                        H: {horse.handicap_weight}kg
                                                    </Typography>
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={horse.win_odds}
                                                    size="small"
                                                    sx={{ 
                                                        backgroundColor: getOddsColor(horse.win_probability),
                                                        color: 'white',
                                                        fontWeight: 'bold'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2" fontWeight="bold">
                                                    {horse.win_probability}%
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={horse.form}
                                                    size="small"
                                                    sx={{ 
                                                        backgroundColor: getFormColor(horse.form),
                                                        color: 'white'
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">
                                                    {horse.career_record}
                                                </Typography>
                                                <Typography variant="caption" color="textSecondary">
                                                    {horse.win_rate}% SR
                                                </Typography>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                        
                        <Box sx={{ mt: 2, textAlign: 'center' }}>
                            <Button 
                                variant="outlined" 
                                onClick={() => handleRaceClick(race)}
                                startIcon={<TrendingUp />}
                            >
                                Detailed Analysis
                            </Button>
                        </Box>
                    </AccordionDetails>
                </Accordion>
            ))}

            {/* Race Detail Dialog */}
            <Dialog 
                open={dialogOpen} 
                onClose={() => setDialogOpen(false)}
                maxWidth="lg"
                fullWidth
            >
                <DialogTitle>
                    Race {selectedRace?.race_id} - Detailed Analysis
                </DialogTitle>
                <DialogContent>
                    {selectedRace && (
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                Field Analysis
                            </Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={12} md={4}>
                                    <Card>
                                        <CardContent>
                                            <Typography color="textSecondary">
                                                Field Size
                                            </Typography>
                                            <Typography variant="h4">
                                                {selectedRace.total_runners}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <Card>
                                        <CardContent>
                                            <Typography color="textSecondary">
                                                Favorite
                                            </Typography>
                                            <Typography variant="h6">
                                                {selectedRace.horses[0]?.horse_name || 'TBA'}
                                            </Typography>
                                            <Typography variant="body2" color="textSecondary">
                                                {selectedRace.horses[0]?.win_odds || 'N/A'}
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                                <Grid item xs={12} md={4}>
                                    <Card>
                                        <CardContent>
                                            <Typography color="textSecondary">
                                                Competitiveness
                                            </Typography>
                                            <Typography variant="h6">
                                                High
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            </Grid>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDialogOpen(false)}>Close</Button>
                    <Button variant="contained" color="primary">
                        Analyze with AI
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Refresh Button */}
            <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Button 
                    variant="contained" 
                    onClick={fetchRaceCards}
                    startIcon={<Speed />}
                >
                    Refresh Race Cards
                </Button>
            </Box>
        </Box>
    );
};

export default RealRaceCards;
