import {
    AccessTime,
    TrendingUp,
    Speed,
    EmojiEvents,
    Place,
    Star
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
    LinearProgress
} from '@mui/material'

const raceCards = [
    {
        id: 1,
        venue: "Kempton Park",
        time: "14:30",
        name: "Handicap Stakes",
        distance: "1m 2f",
        prize: "£15,000",
        field: 12,
        going: "Good to Firm",
        status: "upcoming"
    },
    {
        id: 2,
        venue: "Newmarket",
        time: "15:00",
        name: "Maiden Stakes",
        distance: "7f",
        prize: "£8,500",
        field: 14,
        going: "Good",
        status: "upcoming"
    },
    {
        id: 3,
        venue: "Ascot",
        time: "15:30",
        name: "Listed Race",
        distance: "1m 4f",
        prize: "£25,000",
        field: 8,
        going: "Soft",
        status: "upcoming"
    },
    {
        id: 4,
        venue: "Cheltenham",
        time: "16:00",
        name: "Novice Hurdle",
        distance: "2m 1f",
        prize: "£12,000",
        field: 10,
        going: "Good to Soft",
        status: "running"
    }
]

const topHorses = [
    { name: "Lightning Strike", jockey: "R. Moore", odds: "3/1", confidence: 85, form: "11211" },
    { name: "Thunder Bay", jockey: "W. Buick", odds: "5/2", confidence: 78, form: "21131" },
    { name: "Storm Chaser", jockey: "F. Dettori", odds: "4/1", confidence: 72, form: "31121" },
    { name: "Wind Walker", jockey: "J. Murphy", odds: "6/1", confidence: 68, form: "12312" },
    { name: "Rain Dance", jockey: "T. Marquand", odds: "8/1", confidence: 65, form: "21321" }
]

export default function RaceCards() {
    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Today's Race Cards
            </Typography>
            
            {/* Race Overview */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <AccessTime sx={{ mr: 1 }} />
                                <Typography variant="h6">Today's Races</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>24</Typography>
                            <Typography variant="body2">Across 6 venues</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <TrendingUp sx={{ mr: 1 }} />
                                <Typography variant="h6">AI Predictions</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>87%</Typography>
                            <Typography variant="body2">Accuracy Rate</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <EmojiEvents sx={{ mr: 1 }} />
                                <Typography variant="h6">Total Prize Money</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>£847K</Typography>
                            <Typography variant="body2">Today</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Speed sx={{ mr: 1 }} />
                                <Typography variant="h6">Active Runners</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>287</Typography>
                            <Typography variant="body2">Horses</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Race Cards Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {raceCards.map((race) => (
                    <Grid item xs={12} md={6} key={race.id}>
                        <Card sx={{ p: 3, height: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{race.venue}</Typography>
                                <Chip 
                                    label={race.status === 'running' ? 'LIVE' : race.time} 
                                    color={race.status === 'running' ? 'error' : 'primary'}
                                    variant={race.status === 'running' ? 'filled' : 'outlined'}
                                />
                            </Box>
                            
                            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>{race.name}</Typography>
                            
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
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.field} runners</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <Typography variant="body2" color="text.secondary">Going</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{race.going}</Typography>
                                </Grid>
                            </Grid>
                            
                            {race.status === 'running' && (
                                <Box sx={{ mt: 2 }}>
                                    <Typography variant="body2" color="error" sx={{ mb: 1 }}>Race in Progress</Typography>
                                    <LinearProgress color="error" />
                                </Box>
                            )}
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Top Horses Table */}
            <Card sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>🌟 Featured Runners - Next Race</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Horse</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Jockey</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Odds</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>AI Confidence</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Recent Form</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Rating</Typography></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {topHorses.map((horse, index) => (
                                <TableRow key={index} hover>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                            <Avatar sx={{ bgcolor: index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : '#cd7f32' }}>
                                                {index + 1}
                                            </Avatar>
                                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{horse.name}</Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{horse.jockey}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Chip label={horse.odds} variant="outlined" color="primary" />
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Box sx={{ width: '100px' }}>
                                                <LinearProgress 
                                                    variant="determinate" 
                                                    value={horse.confidence} 
                                                    color={horse.confidence > 80 ? 'success' : horse.confidence > 70 ? 'warning' : 'error'}
                                                />
                                            </Box>
                                            <Typography variant="body2">{horse.confidence}%</Typography>
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                                            {horse.form.split('').map((position, i) => (
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
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                            {[...Array(5)].map((_, i) => (
                                                <Star 
                                                    key={i} 
                                                    sx={{ 
                                                        color: i < Math.floor(horse.confidence / 20) ? '#ffd700' : '#e0e0e0',
                                                        fontSize: '1rem'
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

            {/* Quick Stats */}
            <Grid container spacing={3} sx={{ mt: 4 }}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <Place sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>76%</Typography>
                        <Typography variant="body1">Win Rate (Last 30 days)</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                        <EmojiEvents sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>342</Typography>
                        <Typography variant="body1">Successful Predictions</Typography>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <Star sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>4.8</Typography>
                        <Typography variant="body1">Average Rating</Typography>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    )
}
