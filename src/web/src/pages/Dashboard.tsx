import {
    Assessment,
    Speed,
    TrendingUp,
    Psychology
} from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    Container,
    Grid,
    Typography,
    LinearProgress,
    Chip,
    CircularProgress,
    Alert,
    Button
} from '@mui/material'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { useDailyRaces, useStage8Performance } from '../hooks/useAPI'

export default function Dashboard() {
    // Use API hooks for real data
    const { 
        data: racesData, 
        loading: racesLoading, 
        error: racesError,
        refetch: refetchRaces 
    } = useDailyRaces();
    
    const { 
        performance, 
        loading: performanceLoading, 
        error: performanceError,
        refetch: refetchPerformance 
    } = useStage8Performance();

    // Show loading state
    if (racesLoading || performanceLoading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                    <CircularProgress />
                    <Typography variant="h6" sx={{ ml: 2 }}>Loading dashboard...</Typography>
                </Box>
            </Container>
        );
    }

    // Show error state
    if (racesError || performanceError) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    Error loading dashboard data: {racesError || performanceError}
                    <Button 
                        onClick={() => {
                            refetchRaces();
                            refetchPerformance();
                        }} 
                        sx={{ ml: 2 }}
                    >
                        Retry
                    </Button>
                </Alert>
            </Container>
        );
    }

    // Prepare chart data from performance
    const chartData = performance.recent_performance || [
        { date: 'Mon', pnl: 65 },
        { date: 'Tue', pnl: 78 },
        { date: 'Wed', pnl: 82 },
        { date: 'Thu', pnl: 76 },
        { date: 'Fri', pnl: 88 },
        { date: 'Sat', pnl: 95 },
        { date: 'Sun', pnl: 92 }
    ];

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Enhanced Dashboard
            </Typography>
            
            {/* Key Metrics Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Assessment sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">Total Races</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{racesData?.total_races || 0}</Typography>
                            <Typography variant="body2">Today's Schedule</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Speed sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">Win Rate</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{performance.win_rate.toFixed(1)}%</Typography>
                            <Typography variant="body2">Model Performance</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <TrendingUp sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">ROI</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{performance.roi.toFixed(1)}%</Typography>
                            <Typography variant="body2">Return on Investment</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Psychology sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">Active Bets</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>{performance.active_bets}</Typography>
                            <Typography variant="body2">Current Positions</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Performance Chart */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Card sx={{ p: 3 }}>
                        <Typography variant="h5" gutterBottom>Weekly Performance Trends</Typography>
                        <Box sx={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Area 
                                        type="monotone" 
                                        dataKey="pnl" 
                                        stroke="#667eea" 
                                        fill="url(#colorGradient)" 
                                    />
                                    <defs>
                                        <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                                            <stop offset="95%" stopColor="#764ba2" stopOpacity={0.1}/>
                                        </linearGradient>
                                    </defs>
                                </AreaChart>
                            </ResponsiveContainer>
                        </Box>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h5" gutterBottom>System Status</Typography>
                        
                        <Box sx={{ mb: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2">ML Models</Typography>
                                <Chip label="Active" color="success" size="small" />
                            </Box>
                            <LinearProgress variant="determinate" value={98} sx={{ mb: 2 }} />
                        </Box>

                        <Box sx={{ mb: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2">Data Pipeline</Typography>
                                <Chip label="Running" color="success" size="small" />
                            </Box>
                            <LinearProgress variant="determinate" value={95} sx={{ mb: 2 }} />
                        </Box>

                        <Box sx={{ mb: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2">API Responses</Typography>
                                <Chip label="Optimal" color="success" size="small" />
                            </Box>
                            <LinearProgress variant="determinate" value={92} />
                        </Box>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    )
}
