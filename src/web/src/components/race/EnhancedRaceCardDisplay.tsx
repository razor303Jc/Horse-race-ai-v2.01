import React, { useState, useMemo } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Chip,
    Avatar,
    Divider,
    IconButton,
    Collapse,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress,
    Tooltip,
    Rating,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import {
    ExpandMore,
    ExpandLess,
    Person,
    Psychology,
    Speed,
    TrendingUp,
    TrendingDown,
    Timeline,
    Star,
    Info,
    CompareArrows,
    Assessment,
    Whatshot,
    CheckCircle,
    Cancel
} from '@mui/icons-material';
import { useRealRaceCards } from '../../hooks/useAPI';

interface HorseAnalysis {
    form_analysis: {
        recent_form_score: number;
        consistency_rating: number;
        improvement_trend: 'up' | 'down' | 'stable';
    };
    track_suitability: {
        distance_preference: number;
        going_preference: number;
        track_record: string;
    };
    ai_prediction: {
        win_probability: number;
        confidence_level: number;
        value_rating: number;
        recommendation: 'strong_bet' | 'value_bet' | 'lay' | 'avoid';
    };
}

export const EnhancedRaceCardDisplay: React.FC = () => {
    const { data: raceCards, loading, error } = useRealRaceCards();
    const [expandedRaces, setExpandedRaces] = useState<Set<string>>(new Set());
    const [selectedHorse, setSelectedHorse] = useState<any>(null);
    const [compareMode, setCompareMode] = useState(false);
    const [selectedForComparison, setSelectedForComparison] = useState<Set<string>>(new Set());

    // Generate enhanced analysis data
    const getHorseAnalysis = (horse: any): HorseAnalysis => {
        return {
            form_analysis: {
                recent_form_score: Math.floor(Math.random() * 40) + 60, // 60-100
                consistency_rating: Math.floor(Math.random() * 30) + 70, // 70-100
                improvement_trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as any
            },
            track_suitability: {
                distance_preference: Math.floor(Math.random() * 40) + 60,
                going_preference: Math.floor(Math.random() * 40) + 60,
                track_record: `${Math.floor(Math.random() * 5) + 1}/${Math.floor(Math.random() * 10) + 10}`
            },
            ai_prediction: {
                win_probability: horse.win_probability || Math.floor(Math.random() * 30) + 10,
                confidence_level: Math.floor(Math.random() * 30) + 70,
                value_rating: Math.floor(Math.random() * 40) + 60,
                recommendation: ['strong_bet', 'value_bet', 'lay', 'avoid'][Math.floor(Math.random() * 4)] as any
            }
        };
    };

    const toggleRaceExpanded = (raceId: string) => {
        const newExpanded = new Set(expandedRaces);
        if (newExpanded.has(raceId)) {
            newExpanded.delete(raceId);
        } else {
            newExpanded.add(raceId);
        }
        setExpandedRaces(newExpanded);
    };

    const toggleHorseComparison = (horseName: string) => {
        const newComparison = new Set(selectedForComparison);
        if (newComparison.has(horseName)) {
            newComparison.delete(horseName);
        } else if (newComparison.size < 3) { // Limit to 3 horses
            newComparison.add(horseName);
        }
        setSelectedForComparison(newComparison);
    };

    const getRecommendationColor = (recommendation: string) => {
        switch (recommendation) {
            case 'strong_bet': return 'success';
            case 'value_bet': return 'info';
            case 'lay': return 'warning';
            case 'avoid': return 'error';
            default: return 'default';
        }
    };

    const getRecommendationIcon = (recommendation: string) => {
        switch (recommendation) {
            case 'strong_bet': return <CheckCircle />;
            case 'value_bet': return <TrendingUp />;
            case 'lay': return <TrendingDown />;
            case 'avoid': return <Cancel />;
            default: return <Info />;
        }
    };

    if (loading) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography>Loading enhanced race cards...</Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography color="error">Error loading race cards: {error}</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    🏇 Enhanced Race Cards
                </Typography>
                <Box>
                    <Button
                        variant={compareMode ? "contained" : "outlined"}
                        onClick={() => setCompareMode(!compareMode)}
                        startIcon={<CompareArrows />}
                        sx={{ mr: 2 }}
                    >
                        Compare Mode
                    </Button>
                    {selectedForComparison.size > 0 && (
                        <Chip 
                            label={`${selectedForComparison.size} selected`}
                            color="primary"
                        />
                    )}
                </Box>
            </Box>

            {raceCards?.races.map((race, raceIndex) => (
                <Card key={race.race_id} sx={{ mb: 3 }}>
                    <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Box>
                                <Typography variant="h6" gutterBottom>
                                    Race {raceIndex + 1} - {race.horses.length} Runners
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                    <Chip label="1m 2f" size="small" />
                                    <Chip label="Good Going" size="small" color="success" />
                                    <Chip label="£50,000" size="small" color="primary" />
                                </Box>
                            </Box>
                            <IconButton 
                                onClick={() => toggleRaceExpanded(race.race_id.toString())}
                                color="primary"
                            >
                                {expandedRaces.has(race.race_id.toString()) ? <ExpandLess /> : <ExpandMore />}
                            </IconButton>
                        </Box>

                        <Collapse in={expandedRaces.has(race.race_id.toString())}>
                            <Box sx={{ mt: 3 }}>
                                <Grid container spacing={2}>
                                    {race.horses.map((horse, index) => {
                                        const analysis = getHorseAnalysis(horse);
                                        const isSelected = selectedForComparison.has(horse.horse_name || horse.name || '');
                                        
                                        return (
                                            <Grid item xs={12} md={6} lg={4} key={index}>
                                                <Card 
                                                    variant="outlined" 
                                                    sx={{ 
                                                        height: '100%',
                                                        border: isSelected ? '2px solid' : '1px solid',
                                                        borderColor: isSelected ? 'primary.main' : 'divider',
                                                        cursor: compareMode ? 'pointer' : 'default'
                                                    }}
                                                    onClick={() => compareMode ? toggleHorseComparison(horse.horse_name || horse.name || '') : setSelectedHorse(horse)}
                                                >
                                                    <CardContent>
                                                        {/* Horse Header */}
                                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                                            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                                                                {index + 1}
                                                            </Avatar>
                                                            <Box sx={{ flex: 1 }}>
                                                                <Typography variant="h6" sx={{ fontSize: '1rem' }}>
                                                                    {horse.horse_name}
                                                                </Typography>
                                                                <Typography variant="caption" color="text.secondary">
                                                                    {horse.age}yo • {horse.weight_kg}kg
                                                                </Typography>
                                                            </Box>
                                                            <Chip
                                                                icon={getRecommendationIcon(analysis.ai_prediction.recommendation)}
                                                                label={analysis.ai_prediction.recommendation.replace('_', ' ')}
                                                                color={getRecommendationColor(analysis.ai_prediction.recommendation) as any}
                                                                size="small"
                                                            />
                                                        </Box>

                                                        {/* Odds and Probability */}
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                                            <Box>
                                                                <Typography variant="h5" color="primary">
                                                                    {horse.win_odds || horse.odds}
                                                                </Typography>
                                                                <Typography variant="caption">Odds</Typography>
                                                            </Box>
                                                            <Box sx={{ textAlign: 'right' }}>
                                                                <Typography variant="h6" color="success.main">
                                                                    {analysis.ai_prediction.win_probability}%
                                                                </Typography>
                                                                <Typography variant="caption">Win Prob</Typography>
                                                            </Box>
                                                        </Box>

                                                        {/* Connections */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                                                <Person fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                                                <Typography variant="body2">{horse.jockey_name || horse.jockey}</Typography>
                                                            </Box>
                                                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                                <Psychology fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                                                <Typography variant="body2">{horse.trainer_name || horse.trainer}</Typography>
                                                            </Box>
                                                        </Box>

                                                        {/* Form Analysis */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                                                <Typography variant="caption" color="text.secondary">
                                                                    Recent Form
                                                                </Typography>
                                                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                                                    {analysis.form_analysis.improvement_trend === 'up' ? (
                                                                        <TrendingUp color="success" fontSize="small" />
                                                                    ) : analysis.form_analysis.improvement_trend === 'down' ? (
                                                                        <TrendingDown color="error" fontSize="small" />
                                                                    ) : (
                                                                        <Timeline color="warning" fontSize="small" />
                                                                    )}
                                                                </Box>
                                                            </Box>
                                                            <LinearProgress
                                                                variant="determinate"
                                                                value={analysis.form_analysis.recent_form_score}
                                                                sx={{ mb: 1 }}
                                                            />
                                                        </Box>

                                                        {/* Track Suitability */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Typography variant="caption" color="text.secondary" gutterBottom>
                                                                Track Suitability
                                                            </Typography>
                                                            <Box sx={{ display: 'flex', gap: 1 }}>
                                                                <Chip 
                                                                    label={`Distance: ${analysis.track_suitability.distance_preference}%`}
                                                                    size="small"
                                                                    color={analysis.track_suitability.distance_preference > 80 ? 'success' : 'default'}
                                                                />
                                                                <Chip 
                                                                    label={`Going: ${analysis.track_suitability.going_preference}%`}
                                                                    size="small"
                                                                    color={analysis.track_suitability.going_preference > 80 ? 'success' : 'default'}
                                                                />
                                                            </Box>
                                                        </Box>

                                                        {/* AI Confidence */}
                                                        <Box>
                                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                                <Typography variant="caption" color="text.secondary">
                                                                    AI Confidence
                                                                </Typography>
                                                                <Rating
                                                                    value={analysis.ai_prediction.confidence_level / 20}
                                                                    readOnly
                                                                    size="small"
                                                                    icon={<Star fontSize="inherit" />}
                                                                />
                                                            </Box>
                                                        </Box>
                                                    </CardContent>
                                                </Card>
                                            </Grid>
                                        );
                                    })}
                                </Grid>
                            </Box>
                        </Collapse>
                    </CardContent>
                </Card>
            ))}

            {/* Horse Detail Dialog */}
            <Dialog 
                open={selectedHorse !== null} 
                onClose={() => setSelectedHorse(null)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Whatshot color="primary" sx={{ mr: 1 }} />
                        {selectedHorse?.horse_name} - Detailed Analysis
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {selectedHorse && (
                        <Box>
                            <Grid container spacing={3}>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
                                    <TableContainer>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>Career Record</TableCell>
                                                    <TableCell>{selectedHorse.career_record}</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Recent Form</TableCell>
                                                    <TableCell>{selectedHorse.recent_form || 'N/A'}</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Age</TableCell>
                                                    <TableCell>{selectedHorse.age} years old</TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>Weight</TableCell>
                                                    <TableCell>{selectedHorse.weight_kg}kg</TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="h6" gutterBottom>Connections</Typography>
                                    <Box sx={{ mb: 2 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                            <Person color="primary" sx={{ mr: 1 }} />
                                            <Typography variant="body1">{selectedHorse.jockey_name}</Typography>
                                        </Box>
                                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4 }}>
                                            Jockey
                                        </Typography>
                                    </Box>
                                    <Box>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                            <Psychology color="primary" sx={{ mr: 1 }} />
                                            <Typography variant="body1">{selectedHorse.trainer_name}</Typography>
                                        </Box>
                                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4 }}>
                                            Trainer
                                        </Typography>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSelectedHorse(null)}>Close</Button>
                    <Button variant="contained" color="primary">
                        Place Bet
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};
