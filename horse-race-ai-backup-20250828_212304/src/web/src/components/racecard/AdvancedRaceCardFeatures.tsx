import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Container,
    Grid,
    Typography,
    Paper,
    Chip,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Avatar,
    Rating,
    LinearProgress,
    Tooltip,
    IconButton,
    Tabs,
    Tab,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import {
    ExpandMore,
    CompareArrows,
    Timeline,
    Speed,
    TrendingUp,
    Star,
    Info,
    Visibility,
    Share,
    Download,
    FilterList,
    Sort
} from '@mui/icons-material';
import {
    ResponsiveContainer,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip as RechartsTooltip,
    BarChart,
    Bar,
    ScatterChart,
    Scatter
} from 'recharts';

interface Horse {
    id: string;
    name: string;
    number: number;
    jockey: string;
    trainer: string;
    weight: number;
    odds: number;
    form: string[];
    age: number;
    rating: number;
    lastWin: string;
    earnings: number;
    speedRating: number;
    classRating: number;
    fitnessIndex: number;
    consistency: number;
}

interface JockeyStats {
    name: string;
    winRate: number;
    strikes: number;
    recentForm: string;
    trackRecord: number;
    experience: number;
}

interface TrainerStats {
    name: string;
    winRate: number;
    recentForm: string;
    trackSpecialty: string;
    yearsActive: number;
    reputation: number;
}

interface TrackCondition {
    surface: string;
    condition: string;
    weather: string;
    temperature: number;
    windSpeed: number;
    bias: string;
    impact: 'high' | 'medium' | 'low';
}

export const AdvancedRaceCardFeatures: React.FC = () => {
    const [selectedHorses, setSelectedHorses] = useState<string[]>([]);
    const [activeTab, setActiveTab] = useState(0);
    const [comparisonOpen, setComparisonOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [raceData, setRaceData] = useState<{
        horses: Horse[];
        trackCondition: TrackCondition;
        raceDetails: any;
    } | null>(null);

    useEffect(() => {
        fetchRaceCardData();
    }, []);

    const fetchRaceCardData = async () => {
        try {
            setLoading(true);
            // Generate comprehensive demo data
            generateAdvancedRaceData();
        } catch (err) {
            console.error('Error fetching race data:', err);
            generateAdvancedRaceData();
        } finally {
            setLoading(false);
        }
    };

    const generateAdvancedRaceData = () => {
        const horses: Horse[] = [
            {
                id: '1',
                name: 'Lightning Strike',
                number: 1,
                jockey: 'J. Smith',
                trainer: 'M. Johnson',
                weight: 56.5,
                odds: 3.2,
                form: ['1', '2', '1', '3', '1'],
                age: 4,
                rating: 92,
                lastWin: '2025-08-10',
                earnings: 245000,
                speedRating: 95,
                classRating: 88,
                fitnessIndex: 92,
                consistency: 85
            },
            {
                id: '2',
                name: 'Thunder Bay',
                number: 2,
                jockey: 'R. Williams',
                trainer: 'S. Davis',
                weight: 57.0,
                odds: 4.5,
                form: ['2', '1', '3', '1', '2'],
                age: 5,
                rating: 89,
                lastWin: '2025-07-28',
                earnings: 198000,
                speedRating: 90,
                classRating: 91,
                fitnessIndex: 88,
                consistency: 78
            },
            {
                id: '3',
                name: 'Storm Chaser',
                number: 3,
                jockey: 'L. Brown',
                trainer: 'K. Wilson',
                weight: 55.5,
                odds: 6.0,
                form: ['3', '2', '4', '1', '2'],
                age: 3,
                rating: 85,
                lastWin: '2025-08-05',
                earnings: 156000,
                speedRating: 87,
                classRating: 85,
                fitnessIndex: 90,
                consistency: 72
            },
            {
                id: '4',
                name: 'Wind Walker',
                number: 4,
                jockey: 'D. Taylor',
                trainer: 'P. Anderson',
                weight: 56.0,
                odds: 8.0,
                form: ['4', '3', '2', '5', '1'],
                age: 6,
                rating: 82,
                lastWin: '2025-07-15',
                earnings: 134000,
                speedRating: 82,
                classRating: 84,
                fitnessIndex: 85,
                consistency: 68
            },
            {
                id: '5',
                name: 'Fire Storm',
                number: 5,
                jockey: 'A. Garcia',
                trainer: 'T. Martinez',
                weight: 54.5,
                odds: 12.0,
                form: ['5', '4', '3', '2', '6'],
                age: 4,
                rating: 78,
                lastWin: '2025-06-20',
                earnings: 98000,
                speedRating: 78,
                classRating: 80,
                fitnessIndex: 82,
                consistency: 64
            }
        ];

        const trackCondition: TrackCondition = {
            surface: 'Turf',
            condition: 'Good',
            weather: 'Sunny',
            temperature: 22,
            windSpeed: 8,
            bias: 'None detected',
            impact: 'low'
        };

        setRaceData({
            horses,
            trackCondition,
            raceDetails: {
                name: 'Group 1 Championship Stakes',
                distance: '1600m',
                prize: '$500,000',
                class: 'Group 1',
                time: '3:45 PM'
            }
        });
    };

    const handleHorseSelection = (horseId: string) => {
        setSelectedHorses(prev => 
            prev.includes(horseId) 
                ? prev.filter(id => id !== horseId)
                : prev.length < 3 ? [...prev, horseId] : prev
        );
    };

    const getFormColor = (position: string) => {
        const pos = parseInt(position);
        if (pos === 1) return 'success';
        if (pos <= 3) return 'warning';
        return 'error';
    };

    const renderHorseComparisonDialog = () => {
        if (selectedHorses.length === 0 || !raceData) return null;

        const selectedHorseData = raceData.horses.filter(h => selectedHorses.includes(h.id));
        
        const comparisonMetrics = [
            { key: 'speedRating', label: 'Speed Rating', max: 100 },
            { key: 'classRating', label: 'Class Rating', max: 100 },
            { key: 'fitnessIndex', label: 'Fitness Index', max: 100 },
            { key: 'consistency', label: 'Consistency', max: 100 }
        ];

        const radarData = comparisonMetrics.map(metric => {
            const dataPoint: any = { metric: metric.label };
            selectedHorseData.forEach(horse => {
                dataPoint[horse.name] = horse[metric.key as keyof Horse];
            });
            return dataPoint;
        });

        return (
            <Dialog open={comparisonOpen} onClose={() => setComparisonOpen(false)} maxWidth="lg" fullWidth>
                <DialogTitle>
                    Horse Comparison Analysis
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>Performance Radar</Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <RadarChart data={radarData}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="metric" />
                                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                                    {selectedHorseData.map((horse, index) => (
                                        <Radar 
                                            key={horse.id}
                                            name={horse.name}
                                            dataKey={horse.name}
                                            stroke={`hsl(${index * 120}, 70%, 50%)`}
                                            fill={`hsl(${index * 120}, 70%, 50%)`}
                                            fillOpacity={0.3}
                                        />
                                    ))}
                                    <RechartsTooltip />
                                </RadarChart>
                            </ResponsiveContainer>
                        </Grid>
                        
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>Detailed Comparison</Typography>
                            <TableContainer component={Paper}>
                                <Table size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Metric</TableCell>
                                            {selectedHorseData.map(horse => (
                                                <TableCell key={horse.id} align="center">
                                                    {horse.name}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        <TableRow>
                                            <TableCell>Current Odds</TableCell>
                                            {selectedHorseData.map(horse => (
                                                <TableCell key={horse.id} align="center">
                                                    ${horse.odds.toFixed(1)}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Speed Rating</TableCell>
                                            {selectedHorseData.map(horse => (
                                                <TableCell key={horse.id} align="center">
                                                    {horse.speedRating}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Earnings</TableCell>
                                            {selectedHorseData.map(horse => (
                                                <TableCell key={horse.id} align="center">
                                                    ${horse.earnings.toLocaleString()}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Last Win</TableCell>
                                            {selectedHorseData.map(horse => (
                                                <TableCell key={horse.id} align="center">
                                                    {horse.lastWin}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setComparisonOpen(false)}>Close</Button>
                    <Button variant="contained" startIcon={<Download />}>
                        Export Analysis
                    </Button>
                </DialogActions>
            </Dialog>
        );
    };

    const renderTrackConditionAnalysis = () => {
        if (!raceData) return null;

        const { trackCondition } = raceData;
        
        return (
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <Timeline sx={{ mr: 1 }} />
                    Track Condition Analysis
                </Typography>
                
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box textAlign="center">
                            <Typography variant="h4" color="primary">
                                {trackCondition.temperature}°C
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Temperature
                            </Typography>
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={3}>
                        <Box textAlign="center">
                            <Typography variant="h4" color="primary">
                                {trackCondition.windSpeed}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Wind Speed (km/h)
                            </Typography>
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={3}>
                        <Box textAlign="center">
                            <Chip 
                                label={trackCondition.condition}
                                color={trackCondition.condition === 'Good' ? 'success' : 'warning'}
                                size="large"
                            />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                Track Condition
                            </Typography>
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={3}>
                        <Box textAlign="center">
                            <Chip 
                                label={trackCondition.impact.toUpperCase()}
                                color={
                                    trackCondition.impact === 'low' ? 'success' :
                                    trackCondition.impact === 'medium' ? 'warning' : 'error'
                                }
                                variant="outlined"
                            />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                Expected Impact
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
                
                <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                        <strong>Track Bias:</strong> {trackCondition.bias}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        <strong>Recommendation:</strong> Current conditions favor front-running horses with good early speed.
                    </Typography>
                </Box>
            </Paper>
        );
    };

    const renderHorseDetailCard = (horse: Horse) => (
        <Card 
            key={horse.id} 
            sx={{ 
                mb: 2, 
                border: selectedHorses.includes(horse.id) ? '2px solid #1976d2' : 'none',
                cursor: 'pointer'
            }}
            onClick={() => handleHorseSelection(horse.id)}
        >
            <CardContent>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                                {horse.number}
                            </Avatar>
                            <Box>
                                <Typography variant="h6">{horse.name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {horse.age}yo • ${horse.odds.toFixed(1)}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} sm={2}>
                        <Typography variant="body2" color="text.secondary">Jockey</Typography>
                        <Typography variant="body1">{horse.jockey}</Typography>
                        <Typography variant="body2" color="text.secondary">Trainer</Typography>
                        <Typography variant="body1">{horse.trainer}</Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={2}>
                        <Typography variant="body2" color="text.secondary">Recent Form</Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                            {horse.form.map((pos, index) => (
                                <Chip 
                                    key={index}
                                    label={pos}
                                    size="small"
                                    color={getFormColor(pos) as any}
                                />
                            ))}
                        </Box>
                    </Grid>
                    
                    <Grid item xs={12} sm={3}>
                        <Typography variant="body2" color="text.secondary">Performance Rating</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                            <Rating value={horse.rating / 20} readOnly precision={0.1} />
                            <Typography variant="body2" sx={{ ml: 1 }}>
                                {horse.rating}
                            </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Speed: {horse.speedRating} • Consistency: {horse.consistency}%
                        </Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={2}>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Tooltip title="Speed Rating">
                                <Box>
                                    <Typography variant="caption">Speed</Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={horse.speedRating} 
                                        color="primary"
                                    />
                                </Box>
                            </Tooltip>
                            <Tooltip title="Fitness Index">
                                <Box>
                                    <Typography variant="caption">Fitness</Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={horse.fitnessIndex} 
                                        color="secondary"
                                    />
                                </Box>
                            </Tooltip>
                        </Box>
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Advanced Race Card Features
            </Typography>
            
            {raceData && (
                <>
                    {/* Race Header */}
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Grid container spacing={3} alignItems="center">
                            <Grid item xs={12} sm={8}>
                                <Typography variant="h4" gutterBottom>
                                    {raceData.raceDetails.name}
                                </Typography>
                                <Typography variant="h6" color="text.secondary">
                                    {raceData.raceDetails.distance} • {raceData.raceDetails.class} • {raceData.raceDetails.prize}
                                </Typography>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                                    <Button 
                                        variant="contained" 
                                        startIcon={<CompareArrows />}
                                        onClick={() => setComparisonOpen(true)}
                                        disabled={selectedHorses.length < 2}
                                    >
                                        Compare ({selectedHorses.length})
                                    </Button>
                                    <IconButton>
                                        <FilterList />
                                    </IconButton>
                                    <IconButton>
                                        <Share />
                                    </IconButton>
                                </Box>
                            </Grid>
                        </Grid>
                    </Paper>

                    {/* Track Conditions */}
                    {renderTrackConditionAnalysis()}

                    {/* Horse Cards */}
                    <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
                        Field Analysis
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                        Click on horses to select them for comparison analysis (max 3)
                    </Typography>
                    
                    {raceData.horses.map(horse => renderHorseDetailCard(horse))}

                    {/* Comparison Dialog */}
                    {renderHorseComparisonDialog()}
                </>
            )}
        </Container>
    );
};

export default AdvancedRaceCardFeatures;
