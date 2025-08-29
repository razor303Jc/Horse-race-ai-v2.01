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
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Button,
    Tabs,
    Tab,
    CircularProgress,
    Alert,
    Accordion,
    AccordionSummary,
    AccordionDetails
} from '@mui/material';
import {
    Timeline,
    TrendingUp,
    Speed,
    Assessment,
    ExpandMore,
    Analytics,
    Insights,
    ShowChart
} from '@mui/icons-material';
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    AreaChart,
    Area,
    ScatterChart,
    Scatter,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    BarChart,
    Bar,
    Cell
} from 'recharts';

interface FormPattern {
    pattern: string;
    frequency: number;
    winRate: number;
    avgOdds: number;
    trend: 'improving' | 'declining' | 'stable';
}

interface PerformanceMetric {
    metric: string;
    value: number;
    benchmark: number;
    trend: number;
    confidence: number;
}

interface FormAnalysisData {
    horseId: string;
    horseName: string;
    recentForm: string[];
    patterns: FormPattern[];
    metrics: PerformanceMetric[];
    correlations: Array<{
        factor: string;
        correlation: number;
        significance: number;
    }>;
    historicalTrends: Array<{
        date: string;
        performance: number;
        condition: string;
        distance: string;
    }>;
}

export const EnhancedFormAnalysisTools: React.FC = () => {
    const [selectedHorse, setSelectedHorse] = useState<string>('');
    const [analysisType, setAnalysisType] = useState<string>('patterns');
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState<FormAnalysisData | null>(null);
    const [availableHorses, setAvailableHorses] = useState<Array<{id: string, name: string}>>([]);

    useEffect(() => {
        fetchAvailableHorses();
    }, []);

    const fetchAvailableHorses = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/horses/available');
            if (response.ok) {
                const data = await response.json();
                setAvailableHorses(data.horses || []);
            } else {
                // Fallback data for demonstration
                setAvailableHorses([
                    {id: '1', name: 'Lightning Strike'},
                    {id: '2', name: 'Thunder Bay'},
                    {id: '3', name: 'Storm Chaser'},
                    {id: '4', name: 'Wind Walker'},
                    {id: '5', name: 'Fire Storm'}
                ]);
            }
        } catch (err) {
            console.error('Error fetching horses:', err);
            setAvailableHorses([
                {id: '1', name: 'Lightning Strike'},
                {id: '2', name: 'Thunder Bay'},
                {id: '3', name: 'Storm Chaser'},
                {id: '4', name: 'Wind Walker'},
                {id: '5', name: 'Fire Storm'}
            ]);
        } finally {
            setLoading(false);
        }
    };

    const fetchFormAnalysis = async (horseId: string) => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch(`/api/form_analysis/${horseId}`);
            
            if (response.ok) {
                const data = await response.json();
                setFormData(data);
            } else {
                // Generate demo data for visualization
                generateDemoFormData(horseId);
            }
        } catch (err) {
            setError('Failed to fetch form analysis data');
            generateDemoFormData(horseId);
        } finally {
            setLoading(false);
        }
    };

    const generateDemoFormData = (horseId: string) => {
        const horseName = availableHorses.find(h => h.id === horseId)?.name || 'Selected Horse';
        
        setFormData({
            horseId,
            horseName,
            recentForm: ['1', '2', '1', '3', '1', '4', '2', '1'],
            patterns: [
                { pattern: '1-2-1', frequency: 12, winRate: 75, avgOdds: 3.2, trend: 'improving' },
                { pattern: '2-1-1', frequency: 8, winRate: 62, avgOdds: 2.8, trend: 'stable' },
                { pattern: '1-3-2', frequency: 5, winRate: 40, avgOdds: 4.5, trend: 'declining' },
                { pattern: '1-1-1', frequency: 15, winRate: 85, avgOdds: 2.1, trend: 'improving' }
            ],
            metrics: [
                { metric: 'Speed Rating', value: 92, benchmark: 85, trend: 8, confidence: 87 },
                { metric: 'Consistency', value: 78, benchmark: 70, trend: 5, confidence: 92 },
                { metric: 'Class Rating', value: 85, benchmark: 80, trend: -2, confidence: 85 },
                { metric: 'Fitness Index', value: 94, benchmark: 88, trend: 12, confidence: 89 }
            ],
            correlations: [
                { factor: 'Track Condition', correlation: 0.72, significance: 0.95 },
                { factor: 'Distance', correlation: 0.68, significance: 0.89 },
                { factor: 'Jockey', correlation: 0.45, significance: 0.78 },
                { factor: 'Weight', correlation: -0.32, significance: 0.65 }
            ],
            historicalTrends: [
                { date: '2024-12-01', performance: 85, condition: 'Good', distance: '1200m' },
                { date: '2024-11-15', performance: 92, condition: 'Firm', distance: '1200m' },
                { date: '2024-11-01', performance: 78, condition: 'Soft', distance: '1400m' },
                { date: '2024-10-18', performance: 88, condition: 'Good', distance: '1200m' },
                { date: '2024-10-05', performance: 94, condition: 'Firm', distance: '1000m' },
                { date: '2024-09-22', performance: 82, condition: 'Good', distance: '1200m' }
            ]
        });
    };

    const handleHorseSelect = (horseId: string) => {
        setSelectedHorse(horseId);
        if (horseId) {
            fetchFormAnalysis(horseId);
        }
    };

    const renderPatternAnalysis = () => (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <ShowChart sx={{ mr: 1 }} />
                    Form Patterns Recognition
                </Typography>
            </Grid>
            
            {formData?.patterns.map((pattern, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card sx={{ height: '100%' }}>
                        <CardContent>
                            <Typography variant="h6" color="primary" gutterBottom>
                                {pattern.pattern}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                Frequency: {pattern.frequency} occurrences
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                                <Chip 
                                    label={`${pattern.winRate}% Win Rate`}
                                    color={pattern.winRate > 70 ? 'success' : pattern.winRate > 50 ? 'warning' : 'error'}
                                    size="small"
                                    sx={{ mr: 1, mb: 1 }}
                                />
                                <Chip 
                                    label={`${pattern.avgOdds.toFixed(1)} Avg Odds`}
                                    variant="outlined"
                                    size="small"
                                    sx={{ mr: 1, mb: 1 }}
                                />
                                <Chip 
                                    label={pattern.trend}
                                    color={
                                        pattern.trend === 'improving' ? 'success' : 
                                        pattern.trend === 'declining' ? 'error' : 'default'
                                    }
                                    size="small"
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
            
            <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Form Pattern Visualization</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={formData?.patterns}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="pattern" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="winRate" fill="#8884d8" name="Win Rate %" />
                            <Bar dataKey="frequency" fill="#82ca9d" name="Frequency" />
                        </BarChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>
        </Grid>
    );

    const renderPerformanceMetrics = () => (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <Assessment sx={{ mr: 1 }} />
                    Performance Metrics Analysis
                </Typography>
            </Grid>
            
            {formData?.metrics.map((metric, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {metric.metric}
                            </Typography>
                            <Typography variant="h4" color="primary" gutterBottom>
                                {metric.value}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Benchmark: {metric.benchmark}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                {metric.trend > 0 ? 
                                    <TrendingUp color="success" /> : 
                                    <TrendingUp color="error" sx={{ transform: 'rotate(180deg)' }} />
                                }
                                <Typography 
                                    variant="body2" 
                                    color={metric.trend > 0 ? 'success.main' : 'error.main'}
                                    sx={{ ml: 0.5 }}
                                >
                                    {metric.trend > 0 ? '+' : ''}{metric.trend}%
                                </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                                Confidence: {metric.confidence}%
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
            
            <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Performance Radar Chart</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={formData?.metrics}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="metric" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar 
                                name="Current" 
                                dataKey="value" 
                                stroke="#8884d8" 
                                fill="#8884d8" 
                                fillOpacity={0.6} 
                            />
                            <Radar 
                                name="Benchmark" 
                                dataKey="benchmark" 
                                stroke="#82ca9d" 
                                fill="#82ca9d" 
                                fillOpacity={0.3} 
                            />
                            <Tooltip />
                        </RadarChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Performance Trends</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={formData?.historicalTrends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line 
                                type="monotone" 
                                dataKey="performance" 
                                stroke="#8884d8" 
                                strokeWidth={2}
                                dot={{ fill: '#8884d8' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>
        </Grid>
    );

    const renderCorrelationAnalysis = () => (
        <Grid container spacing={3}>
            <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                    <Analytics sx={{ mr: 1 }} />
                    Performance Correlation Analysis
                </Typography>
            </Grid>
            
            {formData?.correlations.map((correlation, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                {correlation.factor}
                            </Typography>
                            <Typography 
                                variant="h4" 
                                color={Math.abs(correlation.correlation) > 0.5 ? 'primary' : 'text.secondary'}
                                gutterBottom
                            >
                                {correlation.correlation.toFixed(2)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Significance: {(correlation.significance * 100).toFixed(0)}%
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                                <Chip 
                                    label={
                                        Math.abs(correlation.correlation) > 0.7 ? 'Strong' :
                                        Math.abs(correlation.correlation) > 0.4 ? 'Moderate' : 'Weak'
                                    }
                                    color={
                                        Math.abs(correlation.correlation) > 0.7 ? 'success' :
                                        Math.abs(correlation.correlation) > 0.4 ? 'warning' : 'default'
                                    }
                                    size="small"
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            ))}
            
            <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                    <Typography variant="h6" gutterBottom>Correlation Strength Visualization</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={formData?.correlations}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="factor" />
                            <YAxis domain={[-1, 1]} />
                            <Tooltip />
                            <Bar dataKey="correlation" name="Correlation">
                                {formData?.correlations.map((entry, index) => (
                                    <Cell 
                                        key={`cell-${index}`} 
                                        fill={entry.correlation > 0 ? '#82ca9d' : '#ff7c7c'} 
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </Paper>
            </Grid>
        </Grid>
    );

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🔍 Enhanced Form Analysis Tools
            </Typography>
            
            {/* Horse Selection Controls */}
            <Paper sx={{ p: 3, mb: 4 }}>
                <Grid container spacing={3} alignItems="center">
                    <Grid item xs={12} sm={6} md={4}>
                        <FormControl fullWidth>
                            <InputLabel>Select Horse</InputLabel>
                            <Select
                                value={selectedHorse}
                                label="Select Horse"
                                onChange={(e) => handleHorseSelect(e.target.value)}
                            >
                                {availableHorses.map((horse) => (
                                    <MenuItem key={horse.id} value={horse.id}>
                                        {horse.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <FormControl fullWidth>
                            <InputLabel>Analysis Type</InputLabel>
                            <Select
                                value={analysisType}
                                label="Analysis Type"
                                onChange={(e) => setAnalysisType(e.target.value)}
                            >
                                <MenuItem value="patterns">Pattern Recognition</MenuItem>
                                <MenuItem value="metrics">Performance Metrics</MenuItem>
                                <MenuItem value="correlations">Correlation Analysis</MenuItem>
                                <MenuItem value="comprehensive">Comprehensive Analysis</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={12} md={4}>
                        <Button 
                            variant="contained" 
                            fullWidth
                            onClick={() => selectedHorse && fetchFormAnalysis(selectedHorse)}
                            disabled={!selectedHorse || loading}
                            startIcon={loading ? <CircularProgress size={20} /> : <Analytics />}
                        >
                            {loading ? 'Analyzing...' : 'Analyze Form'}
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {formData && (
                <Box>
                    {/* Analysis Results Header */}
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h5" gutterBottom>
                            Analysis Results: {formData.horseName}
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Recent Form: {formData.recentForm.join('-')}
                        </Typography>
                    </Paper>

                    {/* Analysis Tabs */}
                    <Paper sx={{ mb: 3 }}>
                        <Tabs 
                            value={activeTab} 
                            onChange={(_, newValue) => setActiveTab(newValue)}
                            variant="scrollable"
                            scrollButtons="auto"
                        >
                            <Tab label="Pattern Analysis" icon={<ShowChart />} />
                            <Tab label="Performance Metrics" icon={<Assessment />} />
                            <Tab label="Correlation Analysis" icon={<Analytics />} />
                        </Tabs>
                    </Paper>

                    {/* Tab Content */}
                    <Box>
                        {activeTab === 0 && renderPatternAnalysis()}
                        {activeTab === 1 && renderPerformanceMetrics()}
                        {activeTab === 2 && renderCorrelationAnalysis()}
                    </Box>
                </Box>
            )}

            {!selectedHorse && (
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="h6" color="text.secondary">
                        Select a horse to begin form analysis
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Choose a horse from the dropdown above to analyze patterns, performance metrics, and correlations
                    </Typography>
                </Paper>
            )}
        </Container>
    );
};

export default EnhancedFormAnalysisTools;
