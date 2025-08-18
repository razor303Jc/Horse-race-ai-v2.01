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

const databaseStats = [
    { name: 'Races', count: 45782, size: '2.1 GB', growth: '+12%' },
    { name: 'Horses', count: 23456, size: '890 MB', growth: '+8%' },
    { name: 'Jockeys', count: 3421, size: '45 MB', growth: '+3%' },
    { name: 'Trainers', count: 1876, size: '32 MB', growth: '+5%' },
    { name: 'Venues', count: 127, size: '8 MB', growth: '+1%' },
    { name: 'Predictions', count: 156789, size: '1.5 GB', growth: '+25%' }
]

const performanceMetrics = [
    { metric: 'Query Time', value: 12, unit: 'ms' },
    { metric: 'Connection Pool', value: 85, unit: '%' },
    { metric: 'Cache Hit Rate', value: 94, unit: '%' },
    { metric: 'Index Usage', value: 89, unit: '%' },
    { metric: 'Storage Used', value: 72, unit: '%' },
    { metric: 'Backup Status', value: 100, unit: '%' }
]

const storageBreakdown = [
    { name: 'Race Data', value: 35, color: '#667eea' },
    { name: 'ML Models', value: 25, color: '#43e97b' },
    { name: 'Predictions', value: 20, color: '#fa709a' },
    { name: 'Logs', value: 12, color: '#ffd700' },
    { name: 'Cache', value: 8, color: '#ff6b6b' }
]

const recentOperations = [
    { operation: 'Daily Data Import', status: 'Completed', time: '02:15', records: 1247 },
    { operation: 'Model Training', status: 'Running', time: '02:45', records: null },
    { operation: 'Index Optimization', status: 'Completed', time: '01:30', records: null },
    { operation: 'Backup Creation', status: 'Completed', time: '00:01', records: null },
    { operation: 'Cache Refresh', status: 'Completed', time: '03:00', records: 3421 },
    { operation: 'Data Validation', status: 'Completed', time: '02:30', records: 45782 }
]

export default function DatabaseManagement() {
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
