import React, { useState, useEffect } from 'react'
import {
    EmojiEvents,
    Speed,
    Timeline,
    TrendingUp,
    AccessTime,
    Place,
    Star,
    Person
} from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    Container,
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
    Divider
} from '@mui/material'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

const raceDetails = {
    id: "R7_KEMPTON_20241215",
    venue: "Kempton Park",
    raceNumber: 7,
    time: "15:30",
    name: "Betfair Exchange Handicap Stakes",
    distance: "1m 2f (1980m)",
    going: "Good to Firm",
    prizeMoneyTotal: "£15,000",
    prizeMoneyFirst: "£8,531",
    fieldSize: 12,
    raceClass: "Class 4",
    ageRestriction: "3yo+",
    weight: "9st 0lb - 9st 12lb"
}

const runners = [
    {
        number: 1,
        name: "Lightning Strike",
        jockey: "Ryan Moore",
        trainer: "A. O'Brien",
        age: 4,
        weight: "9st 7lb",
        odds: "3/1",
        aiPrediction: 85,
        form: "11211",
        lastRun: "14 days",
        rating: 95,
        draw: 3
    },
    {
        number: 2,
        name: "Thunder Bay",
        jockey: "William Buick",
        trainer: "C. Appleby",
        age: 5,
        weight: "9st 4lb",
        odds: "5/2",
        aiPrediction: 78,
        form: "21131",
        lastRun: "21 days",
        rating: 92,
        draw: 7
    },
    {
        number: 3,
        name: "Storm Chaser",
        jockey: "Frankie Dettori",
        trainer: "J. Gosden",
        age: 4,
        weight: "9st 2lb",
        odds: "4/1",
        aiPrediction: 72,
        form: "31121",
        lastRun: "28 days",
        rating: 89,
        draw: 1
    },
    {
        number: 4,
        name: "Wind Walker",
        jockey: "Jim Crowley",
        trainer: "M. Johnston",
        age: 3,
        weight: "9st 0lb",
        odds: "6/1",
        aiPrediction: 68,
        form: "12312",
        lastRun: "35 days",
        rating: 86,
        draw: 12
    },
    {
        number: 5,
        name: "Rain Dance",
        jockey: "Tom Marquand",
        trainer: "R. Hannon",
        age: 4,
        weight: "9st 8lb",
        odds: "8/1",
        aiPrediction: 65,
        form: "21321",
        lastRun: "42 days",
        rating: 84,
        draw: 5
    }
]

const oddsHistory = [
    { time: '9:00', lightning: 7/2, thunder: 3/1, storm: 9/2 },
    { time: '12:00', lightning: 3/1, thunder: 5/2, storm: 4/1 },
    { time: '15:00', lightning: 3/1, thunder: 5/2, storm: 4/1 },
    { time: '15:25', lightning: 3/1, thunder: 5/2, storm: 4/1 }
]

export default function RaceDetails() {
    const [raceData, setRaceData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRaceDetails = async () => {
            try {
                setLoading(true);
                const response = await fetch('/api/race_details');
                if (!response.ok) {
                    throw new Error('Failed to fetch race details');
                }
                const data = await response.json();
                setRaceData(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
                setLoading(false);
            }
        };

        fetchRaceDetails();
    }, []);

    if (loading) return <div>Loading race details...</div>;
    if (error) return <div>Error: {error}</div>;
    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            {/* Race Header */}
            <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <CardContent sx={{ p: 4 }}>
                    <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                        Race {raceDetails.raceNumber}: {raceDetails.name}
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 3, opacity: 0.9 }}>
                        {raceDetails.venue} • {raceDetails.time} • {raceDetails.distance}
                    </Typography>
                    
                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <EmojiEvents sx={{ fontSize: 40, mb: 1 }} />
                                <Typography variant="body2" sx={{ opacity: 0.8 }}>Prize Money</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{raceDetails.prizeMoneyTotal}</Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Speed sx={{ fontSize: 40, mb: 1 }} />
                                <Typography variant="body2" sx={{ opacity: 0.8 }}>Going</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{raceDetails.going}</Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Person sx={{ fontSize: 40, mb: 1 }} />
                                <Typography variant="body2" sx={{ opacity: 0.8 }}>Field Size</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{raceDetails.fieldSize} runners</Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Star sx={{ fontSize: 40, mb: 1 }} />
                                <Typography variant="body2" sx={{ opacity: 0.8 }}>Class</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{raceDetails.raceClass}</Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* AI Analysis */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={8}>
                    <Card sx={{ p: 3 }}>
                        <Typography variant="h5" gutterBottom>🤖 AI Performance Analysis</Typography>
                        <Box sx={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart data={performanceData}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="metric" />
                                    <PolarRadiusAxis domain={[0, 100]} />
                                    <Radar 
                                        name="Performance" 
                                        dataKey="value" 
                                        stroke="#667eea" 
                                        fill="#667eea" 
                                        fillOpacity={0.3}
                                        strokeWidth={2}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </Box>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h5" gutterBottom>🎯 AI Prediction</Typography>
                        
                        <Box sx={{ textAlign: 'center', mb: 3 }}>
                            <Typography variant="h2" color="primary" sx={{ fontWeight: 'bold' }}>85%</Typography>
                            <Typography variant="body1" color="text.secondary">Confidence Level</Typography>
                        </Box>

                        <Divider sx={{ mb: 3 }} />

                        <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" gutterBottom>Predicted Winner</Typography>
                            <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                                Lightning Strike
                            </Typography>
                        </Box>

                        <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" gutterBottom>Expected Margin</Typography>
                            <Typography variant="body1">1.5 lengths</Typography>
                        </Box>

                        <Box>
                            <Typography variant="body2" gutterBottom>Race Time Prediction</Typography>
                            <Typography variant="body1">2:04.8</Typography>
                        </Box>
                    </Card>
                </Grid>
            </Grid>

            {/* Runners Table */}
            <Card sx={{ p: 3, mb: 4 }}>
                <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>🏇 Full Field Analysis</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>#</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Horse</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Jockey/Trainer</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Details</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Odds</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>AI Score</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Form</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Rating</Typography></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {runners.map((runner, index) => (
                                <TableRow key={runner.number} hover>
                                    <TableCell>
                                        <Avatar sx={{ 
                                            bgcolor: index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : 'primary.main',
                                            fontWeight: 'bold'
                                        }}>
                                            {runner.number}
                                        </Avatar>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{runner.name}</Typography>
                                        <Typography variant="caption" color="text.secondary">
                                            Age: {runner.age} • Weight: {runner.weight} • Draw: {runner.draw}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{runner.jockey}</Typography>
                                        <Typography variant="caption" color="text.secondary">{runner.trainer}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="caption" display="block">Last run: {runner.lastRun}</Typography>
                                        <Typography variant="caption" display="block">Rating: {runner.rating}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip 
                                            label={runner.odds} 
                                            variant="outlined" 
                                            color={index < 3 ? 'success' : 'primary'}
                                            sx={{ fontWeight: 'bold' }}
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Box sx={{ width: '80px' }}>
                                                <LinearProgress 
                                                    variant="determinate" 
                                                    value={runner.aiPrediction} 
                                                    color={runner.aiPrediction > 80 ? 'success' : runner.aiPrediction > 70 ? 'warning' : 'error'}
                                                />
                                            </Box>
                                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                                {runner.aiPrediction}%
                                            </Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                                            {runner.form.split('').map((position, i) => (
                                                <Chip 
                                                    key={i}
                                                    label={position}
                                                    size="small"
                                                    color={position === '1' ? 'success' : position === '2' ? 'warning' : 'default'}
                                                    sx={{ minWidth: '20px', fontSize: '0.7rem' }}
                                                />
                                            ))}
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                            {[...Array(5)].map((_, i) => (
                                                <Star 
                                                    key={i} 
                                                    sx={{ 
                                                        color: i < Math.floor(runner.rating / 20) ? '#ffd700' : '#e0e0e0',
                                                        fontSize: '0.9rem'
                                                    }} 
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

            {/* Odds Movement */}
            <Card sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>📈 Odds Movement (Top 3)</Typography>
                <Box sx={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={oddsHistory}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />
                            <Line 
                                type="monotone" 
                                dataKey="lightning" 
                                stroke="#ffd700" 
                                strokeWidth={3}
                                name="Lightning Strike"
                                dot={{ fill: '#ffd700', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="thunder" 
                                stroke="#667eea" 
                                strokeWidth={3}
                                name="Thunder Bay"
                                dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
                            />
                            <Line 
                                type="monotone" 
                                dataKey="storm" 
                                stroke="#43e97b" 
                                strokeWidth={3}
                                name="Storm Chaser"
                                dot={{ fill: '#43e97b', strokeWidth: 2, r: 4 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </Box>
            </Card>

            {/* Track Conditions */}
            <Grid container spacing={3} sx={{ mt: 4 }}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                        <AccessTime sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>15°C</Typography>
                        <Typography variant="body1">Temperature</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <Timeline sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>8mph</Typography>
                        <Typography variant="body1">Wind Speed</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <TrendingUp sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>0%</Typography>
                        <Typography variant="body1">Rain Chance</Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    )
}
