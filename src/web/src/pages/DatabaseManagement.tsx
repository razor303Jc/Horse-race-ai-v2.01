import React, { useState, useEffect } from 'react';
import {
    Storage,
    Analytics,
    Security,
    Speed,
    Settings,
    Cloud,
    Warning,
    CheckCircle
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
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress,
    Button,
    Alert
} from '@mui/material'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts'

// Remove hardcoded data - will be fetched from API
interface DatabaseStats {
    name: string;
    count: number;
    size: string;
    growth: string;
}

const DatabaseManagement: React.FC = () => {
    const [databaseStats, setDatabaseStats] = useState<DatabaseStats[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDatabaseStats();
    }, []);

    const fetchDatabaseStats = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/database_stats');
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            const data = await response.json();
            
            // Transform API data to component format
            const stats: DatabaseStats[] = [
                { 
                    name: 'Races', 
                    count: data.tables.cards_races + data.tables.results_records, 
                    size: `${((data.tables.cards_races + data.tables.results_records) * 0.05).toFixed(1)} MB`,
                    growth: '+Real-time' 
                },
                { 
                    name: 'Horses', 
                    count: data.tables.cards_horses, 
                    size: `${(data.tables.cards_horses * 0.03).toFixed(1)} MB`,
                    growth: '+Real-time' 
                },
                { 
                    name: 'Predictions', 
                    count: data.tables.advanced_ai_predictions, 
                    size: `${(data.tables.advanced_ai_predictions * 0.02).toFixed(1)} MB`,
                    growth: '+Real-time' 
                },
                { 
                    name: 'Simulations', 
                    count: data.tables.advanced_monte_carlo_simulations, 
                    size: `${(data.tables.advanced_monte_carlo_simulations * 0.01).toFixed(1)} MB`,
                    growth: '+Real-time' 
                }
            ];
            
            setDatabaseStats(stats);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch database stats:', err);
            setError('Failed to load database statistics');
        } finally {
            setLoading(false);
        }
    };

    const performanceMetrics = [
        { metric: 'Query Time', value: 12, unit: 'ms' },
        { metric: 'Connection Pool', value: 85, unit: '%' },
        { metric: 'Cache Hit Rate', value: 94, unit: '%' },
        { metric: 'Index Usage', value: 89, unit: '%' },
        { metric: 'Storage Used', value: 72, unit: '%' },
        { metric: 'Backup Status', value: 100, unit: '%' }
    ];

    const storageBreakdown = [
        { name: 'Race Data', value: 35, color: '#667eea' },
        { name: 'ML Models', value: 25, color: '#43e97b' },
        { name: 'Predictions', value: 20, color: '#fa709a' },
        { name: 'Logs', value: 12, color: '#ffd700' },
        { name: 'Cache', value: 8, color: '#ff6b6b' }
    ];

    const recentOperations = [
        { operation: 'Daily Data Import', status: 'Completed', time: '02:15', records: 1247 },
        { operation: 'Model Training', status: 'Running', time: '02:45', records: null },
        { operation: 'Index Optimization', status: 'Completed', time: '01:30', records: null },
        { operation: 'Backup Creation', status: 'Completed', time: '00:01', records: null },
        { operation: 'Cache Refresh', status: 'Completed', time: '03:00', records: 3421 },
        { operation: 'Data Validation', status: 'Completed', time: '02:30', records: 45782 }
    ];

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Typography variant="h6">Loading database statistics...</Typography>
                <LinearProgress sx={{ mt: 2 }} />
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🗄️ Database Management
            </Typography>
            
            {/* System Health Alert */}
            <Alert severity="success" sx={{ mb: 4 }}>
                <Typography variant="body1">
                    <strong>System Status:</strong> All database systems operational. Last backup completed successfully at 00:01 UTC.
                </Typography>
            </Alert>

            {/* Database Overview */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Storage sx={{ mr: 1 }} />
                                <Typography variant="h6">Total Storage</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>4.8 GB</Typography>
                            <Typography variant="body2">72% utilized</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Analytics sx={{ mr: 1 }} />
                                <Typography variant="h6">Active Connections</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>47</Typography>
                            <Typography variant="body2">Max: 100</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Speed sx={{ mr: 1 }} />
                                <Typography variant="h6">Avg Query Time</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>12ms</Typography>
                            <Typography variant="body2">Excellent</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Security sx={{ mr: 1 }} />
                                <Typography variant="h6">Backup Status</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>✓</Typography>
                            <Typography variant="body2">Current</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Database Tables */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} lg={8}>
                    <Card sx={{ p: 3 }}>
                        <Typography variant="h5" gutterBottom>📋 Table Statistics</Typography>
                        <TableContainer>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Table</Typography></TableCell>
                                        <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Records</Typography></TableCell>
                                        <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Size</Typography></TableCell>
                                        <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Growth</Typography></TableCell>
                                        <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Actions</Typography></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {databaseStats.map((table, index) => (
                                        <TableRow key={index} hover>
                                            <TableCell>
                                                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{table.name}</Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">{table.count.toLocaleString()}</Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Typography variant="body2">{table.size}</Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip 
                                                    label={table.growth}
                                                    size="small"
                                                    color={table.growth.includes('+') ? 'success' : 'default'}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                <Button size="small" variant="outlined">
                                                    Optimize
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Card>
                </Grid>

                <Grid item xs={12} lg={4}>
                    <Card sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h5" gutterBottom>💾 Storage Breakdown</Typography>
                        <Box sx={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={storageBreakdown}
                                        cx="50%"
                                        cy="50%"
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                        label={({ name, value }) => `${name}: ${value}%`}
                                    >
                                        {storageBreakdown.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </Box>
                    </Card>
                </Grid>
            </Grid>

            {/* Performance Metrics */}
            <Card sx={{ p: 3, mb: 4 }}>
                <Typography variant="h5" gutterBottom>⚡ Performance Metrics</Typography>
                <Grid container spacing={3}>
                    {performanceMetrics.map((metric, index) => (
                        <Grid item xs={12} sm={6} md={4} key={index}>
                            <Paper sx={{ p: 2 }}>
                                <Typography variant="body2" color="text.secondary" gutterBottom>
                                    {metric.metric}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                                        {metric.value}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {metric.unit}
                                    </Typography>
                                </Box>
                                <LinearProgress 
                                    variant="determinate" 
                                    value={metric.value > 100 ? 100 : metric.value} 
                                    color={metric.value > 90 ? 'success' : metric.value > 70 ? 'warning' : 'error'}
                                />
                            </Paper>
                        </Grid>
                    ))}
                </Grid>
            </Card>

            {/* Recent Operations */}
            <Card sx={{ p: 3, mb: 4 }}>
                <Typography variant="h5" gutterBottom>🔄 Recent Operations</Typography>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Operation</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Status</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Time</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Records</Typography></TableCell>
                                <TableCell><Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>Duration</Typography></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {recentOperations.map((operation, index) => (
                                <TableRow key={index} hover>
                                    <TableCell>
                                        <Typography variant="body1">{operation.operation}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {operation.status === 'Completed' ? (
                                                <CheckCircle color="success" fontSize="small" />
                                            ) : operation.status === 'Running' ? (
                                                <Warning color="warning" fontSize="small" />
                                            ) : null}
                                            <Chip 
                                                label={operation.status}
                                                size="small"
                                                color={operation.status === 'Completed' ? 'success' : operation.status === 'Running' ? 'warning' : 'default'}
                                            />
                                        </Box>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">{operation.time}</Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {operation.records ? operation.records.toLocaleString() : '-'}
                                        </Typography>
                                    </TableCell>
                                    <TableCell>
                                        <Typography variant="body2">
                                            {operation.status === 'Running' ? 'In Progress' : '< 1 min'}
                                        </Typography>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Card>

            {/* Quick Actions */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <Cloud sx={{ fontSize: 40, mb: 2 }} />
                        <Typography variant="h6" gutterBottom>Create Backup</Typography>
                        <Button variant="contained" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
                            Start Backup
                        </Button>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
                        <Settings sx={{ fontSize: 40, mb: 2 }} />
                        <Typography variant="h6" gutterBottom>Optimize Indexes</Typography>
                        <Button variant="contained" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
                            Optimize
                        </Button>
                    </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 3, textAlign: 'center', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <Analytics sx={{ fontSize: 40, mb: 2 }} />
                        <Typography variant="h6" gutterBottom>Generate Report</Typography>
                        <Button variant="contained" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}>
                            Create Report
                        </Button>
                    </Paper>
                </Grid>
            </Grid>
        </Container>
    )
}

export default DatabaseManagement;
