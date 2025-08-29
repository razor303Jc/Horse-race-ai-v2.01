import React, { useState, useMemo } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    ToggleButton,
    ToggleButtonGroup,
    Chip,
    Paper,
    Divider
} from '@mui/material';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    RadialBarChart,
    RadialBar
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    AccountBalance,
    Percent,
    Timeline,
    PieChart as PieChartIcon,
    ShowChart,
    BarChart as BarChartIcon
} from '@mui/icons-material';
import { useStage8Performance } from '../../hooks/useAPI';

interface PerformanceMetric {
    name: string;
    value: number;
    change: number;
    trend: 'up' | 'down' | 'neutral';
    color: string;
}

interface ChartDataPoint {
    date: string;
    pnl: number;
    cumulativePnl: number;
    winRate: number;
    roi: number;
    stakes: number;
    wins: number;
    losses: number;
}

export const PerformanceMetricsDashboard: React.FC = () => {
    const { performance, loading, error } = useStage8Performance();
    const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
    const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('area');
    const [selectedMetric, setSelectedMetric] = useState<'pnl' | 'winRate' | 'roi' | 'stakes'>('pnl');

    // Generate extended historical data for demonstration
    const chartData = useMemo<ChartDataPoint[]>(() => {
        if (!performance.recent_performance) return [];
        
        let cumulativePnl = 1000; // Starting balance
        return performance.recent_performance.map((item: any, index: number) => {
            cumulativePnl += item.pnl;
            return {
                date: item.date,
                pnl: item.pnl,
                cumulativePnl,
                winRate: Math.max(50, Math.min(90, 75 + (Math.random() - 0.5) * 20)),
                roi: Math.max(-5, Math.min(25, performance.roi + (Math.random() - 0.5) * 10)),
                stakes: Math.floor(Math.random() * 200) + 50,
                wins: Math.floor(Math.random() * 5) + 1,
                losses: Math.floor(Math.random() * 3)
            };
        });
    }, [performance]);

    // Key metrics with trend analysis
    const keyMetrics: PerformanceMetric[] = useMemo(() => [
        {
            name: 'Total P&L',
            value: performance.daily_pnl || 0,
            change: 12.5,
            trend: 'up',
            color: '#4caf50'
        },
        {
            name: 'Win Rate',
            value: performance.win_rate,
            change: -2.3,
            trend: 'down',
            color: '#2196f3'
        },
        {
            name: 'ROI',
            value: performance.roi,
            change: 5.7,
            trend: 'up',
            color: '#ff9800'
        },
        {
            name: 'Active Bets',
            value: performance.active_bets || 0,
            change: 0,
            trend: 'neutral',
            color: '#9c27b0'
        }
    ], [performance]);

    // Distribution data for pie charts
    const bettingDistribution = [
        { name: 'Win Bets', value: 45, color: '#4caf50' },
        { name: 'Place Bets', value: 30, color: '#2196f3' },
        { name: 'Each-Way', value: 20, color: '#ff9800' },
        { name: 'Accumulators', value: 5, color: '#f44336' }
    ];

    const riskDistribution = [
        { name: 'Low Risk', value: 60, color: '#4caf50' },
        { name: 'Medium Risk', value: 30, color: '#ff9800' },
        { name: 'High Risk', value: 10, color: '#f44336' }
    ];

    if (loading) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography>Loading performance metrics...</Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box sx={{ p: 3 }}>
                <Typography color="error">Error loading performance data: {error}</Typography>
            </Box>
        );
    }

    const renderChart = () => {
        const dataKey = selectedMetric === 'pnl' ? 'cumulativePnl' : selectedMetric;
        
        switch (chartType) {
            case 'line':
                return (
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey={dataKey}
                            stroke="#2196f3" 
                            strokeWidth={2}
                            dot={{ fill: '#2196f3', strokeWidth: 2, r: 4 }}
                        />
                    </LineChart>
                );
            case 'area':
                return (
                    <AreaChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area 
                            type="monotone" 
                            dataKey={dataKey}
                            stroke="#2196f3" 
                            fill="url(#colorGradient)"
                        />
                        <defs>
                            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#2196f3" stopOpacity={0.1}/>
                            </linearGradient>
                        </defs>
                    </AreaChart>
                );
            case 'bar':
                return (
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey={dataKey} fill="#2196f3" />
                    </BarChart>
                );
            default:
                return null;
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                📊 Performance Analytics Dashboard
            </Typography>

            {/* Key Metrics Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                {keyMetrics.map((metric, index) => (
                    <Grid item xs={12} sm={6} md={3} key={index}>
                        <Card sx={{ 
                            height: '100%',
                            background: `linear-gradient(135deg, ${metric.color}20 0%, ${metric.color}10 100%)`,
                            border: `1px solid ${metric.color}30`
                        }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Box>
                                        <Typography variant="h6" color="textSecondary" gutterBottom>
                                            {metric.name}
                                        </Typography>
                                        <Typography variant="h4" sx={{ fontWeight: 'bold', color: metric.color }}>
                                            {metric.name.includes('Rate') || metric.name.includes('ROI') 
                                                ? `${metric.value.toFixed(1)}%` 
                                                : metric.name.includes('P&L') 
                                                    ? `£${metric.value.toFixed(2)}`
                                                    : metric.value}
                                        </Typography>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                            {metric.trend === 'up' ? (
                                                <TrendingUp color="success" fontSize="small" />
                                            ) : metric.trend === 'down' ? (
                                                <TrendingDown color="error" fontSize="small" />
                                            ) : (
                                                <Timeline color="disabled" fontSize="small" />
                                            )}
                                            <Typography 
                                                variant="body2" 
                                                sx={{ 
                                                    ml: 0.5,
                                                    color: metric.trend === 'up' ? 'success.main' : 
                                                           metric.trend === 'down' ? 'error.main' : 'text.secondary'
                                                }}
                                            >
                                                {metric.change > 0 ? '+' : ''}{metric.change}%
                                            </Typography>
                                        </Box>
                                    </Box>
                                    <Box sx={{ 
                                        width: 60, 
                                        height: 60, 
                                        borderRadius: '50%', 
                                        backgroundColor: `${metric.color}20`,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        {metric.name.includes('P&L') ? <AccountBalance sx={{ color: metric.color }} /> :
                                         metric.name.includes('Rate') || metric.name.includes('ROI') ? <Percent sx={{ color: metric.color }} /> :
                                         <ShowChart sx={{ color: metric.color }} />}
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Main Chart Section */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h6">Performance Trends</Typography>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <FormControl size="small" sx={{ minWidth: 120 }}>
                                <InputLabel>Metric</InputLabel>
                                <Select
                                    value={selectedMetric}
                                    label="Metric"
                                    onChange={(e) => setSelectedMetric(e.target.value as any)}
                                >
                                    <MenuItem value="pnl">Cumulative P&L</MenuItem>
                                    <MenuItem value="winRate">Win Rate</MenuItem>
                                    <MenuItem value="roi">ROI</MenuItem>
                                    <MenuItem value="stakes">Stakes</MenuItem>
                                </Select>
                            </FormControl>
                            
                            <FormControl size="small" sx={{ minWidth: 120 }}>
                                <InputLabel>Period</InputLabel>
                                <Select
                                    value={timeRange}
                                    label="Period"
                                    onChange={(e) => setTimeRange(e.target.value as any)}
                                >
                                    <MenuItem value="7d">Last 7 Days</MenuItem>
                                    <MenuItem value="30d">Last 30 Days</MenuItem>
                                    <MenuItem value="90d">Last 90 Days</MenuItem>
                                    <MenuItem value="1y">Last Year</MenuItem>
                                </Select>
                            </FormControl>

                            <ToggleButtonGroup
                                value={chartType}
                                exclusive
                                onChange={(_, newType) => newType && setChartType(newType)}
                                size="small"
                            >
                                <ToggleButton value="line">
                                    <ShowChart fontSize="small" />
                                </ToggleButton>
                                <ToggleButton value="area">
                                    <Timeline fontSize="small" />
                                </ToggleButton>
                                <ToggleButton value="bar">
                                    <BarChartIcon fontSize="small" />
                                </ToggleButton>
                            </ToggleButtonGroup>
                        </Box>
                    </Box>
                    
                    <ResponsiveContainer width="100%" height={400}>
                        <div>{renderChart()}</div>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Distribution Charts */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Betting Distribution
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={bettingDistribution}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {bettingDistribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Risk Distribution
                            </Typography>
                            <ResponsiveContainer width="100%" height={300}>
                                <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={riskDistribution}>
                                    <RadialBar 
                                        label={{ position: 'insideStart', fill: '#fff' }}
                                        background 
                                        dataKey="value" 
                                    />
                                    <Legend iconSize={18} layout="horizontal" verticalAlign="bottom" />
                                    <Tooltip />
                                </RadialBarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Statistics Summary */}
            <Card sx={{ mt: 3 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        📈 Quick Statistics
                    </Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={6} sm={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h5" color="primary">£{(performance.account_balance || 0).toFixed(2)}</Typography>
                                <Typography variant="caption">Current Balance</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h5" color="success.main">{performance.total_bets}</Typography>
                                <Typography variant="caption">Total Bets</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h5" color="warning.main">{performance.active_bets}</Typography>
                                <Typography variant="caption">Active Bets</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} sm={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h5" color="info.main">{performance.win_rate.toFixed(1)}%</Typography>
                                <Typography variant="caption">Success Rate</Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Box>
    );
};
