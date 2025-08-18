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
    Chip
} from '@mui/material'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

const mockPerformanceData = [
    { name: 'Mon', value: 65 },
    { name: 'Tue', value: 78 },
    { name: 'Wed', value: 82 },
    { name: 'Thu', value: 76 },
    { name: 'Fri', value: 88 },
    { name: 'Sat', value: 95 },
    { name: 'Sun', value: 92 }
]

export default function Dashboard() {
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
                                <Typography variant="h6">ML Models</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>98.86%</Typography>
                            <Typography variant="body2">AUC Performance</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Speed sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">Active Models</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>5</Typography>
                            <Typography variant="body2">Ensemble Components</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <TrendingUp sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">Win Rate</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>76.2%</Typography>
                            <Typography variant="body2">Today's Performance</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Psychology sx={{ mr: 1, fontSize: 30 }} />
                                <Typography variant="h6">AI Insights</Typography>
                            </Box>
                            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>24</Typography>
                            <Typography variant="body2">Features Analyzed</Typography>
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
                                <AreaChart data={mockPerformanceData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Area 
                                        type="monotone" 
                                        dataKey="value" 
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
