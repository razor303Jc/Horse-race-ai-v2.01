import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Paper,
    Chip,
    IconButton,
    Menu,
    MenuItem,
    Switch,
    FormControlLabel,
    CircularProgress,
    Alert,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Avatar,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    Divider
} from '@mui/material';
import {
    MoreVert,
    ExpandMore,
    WbSunny,
    Cloud,
    Grain,
    Speed,
    TrendingUp,
    TrendingDown,
    Article,
    Twitter,
    Share,
    Refresh,
    Settings,
    Visibility,
    VisibilityOff
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
    PieChart,
    Pie,
    Cell
} from 'recharts';

interface WeatherData {
    location: string;
    condition: string;
    temperature: number;
    humidity: number;
    windSpeed: number;
    icon: string;
    trackCondition: string;
}

interface NewsItem {
    id: string;
    title: string;
    summary: string;
    source: string;
    publishedAt: string;
    category: 'racing' | 'general' | 'market';
    imageUrl?: string;
}

interface SocialFeedItem {
    id: string;
    platform: 'twitter' | 'reddit' | 'telegram';
    author: string;
    content: string;
    timestamp: string;
    engagement: number;
    sentiment: 'positive' | 'negative' | 'neutral';
}

interface WidgetConfig {
    id: string;
    title: string;
    visible: boolean;
    position: { x: number; y: number };
    size: { width: number; height: number };
}

export const EnhancedDashboardWidgets: React.FC = () => {
    const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
    const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
    const [socialFeed, setSocialFeed] = useState<SocialFeedItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedWidget, setSelectedWidget] = useState<string | null>(null);
    
    const [widgetConfig, setWidgetConfig] = useState<WidgetConfig[]>([
        { id: 'weather', title: 'Track Weather', visible: true, position: { x: 0, y: 0 }, size: { width: 4, height: 2 } },
        { id: 'news', title: 'Racing News', visible: true, position: { x: 4, y: 0 }, size: { width: 4, height: 2 } },
        { id: 'social', title: 'Social Sentiment', visible: true, position: { x: 8, y: 0 }, size: { width: 4, height: 2 } },
        { id: 'performance', title: 'Market Performance', visible: true, position: { x: 0, y: 2 }, size: { width: 6, height: 2 } },
        { id: 'trends', title: 'Betting Trends', visible: true, position: { x: 6, y: 2 }, size: { width: 6, height: 2 } }
    ]);

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, 300000); // Refresh every 5 minutes
        return () => clearInterval(interval);
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch all dashboard data in parallel
            await Promise.all([
                fetchWeatherData(),
                fetchNewsData(),
                fetchSocialData()
            ]);
        } catch (err) {
            setError('Failed to fetch dashboard data');
            generateDemoData(); // Fallback to demo data
        } finally {
            setLoading(false);
        }
    };

    const fetchWeatherData = async () => {
        try {
            const response = await fetch('/api/track_weather');
            if (response.ok) {
                const data = await response.json();
                setWeatherData(data.tracks || []);
            } else {
                generateDemoWeatherData();
            }
        } catch (err) {
            generateDemoWeatherData();
        }
    };

    const fetchNewsData = async () => {
        try {
            const response = await fetch('/api/racing_news');
            if (response.ok) {
                const data = await response.json();
                setNewsItems(data.articles || []);
            } else {
                generateDemoNewsData();
            }
        } catch (err) {
            generateDemoNewsData();
        }
    };

    const fetchSocialData = async () => {
        try {
            const response = await fetch('/api/social_sentiment');
            if (response.ok) {
                const data = await response.json();
                setSocialFeed(data.posts || []);
            } else {
                generateDemoSocialData();
            }
        } catch (err) {
            generateDemoSocialData();
        }
    };

    const generateDemoData = () => {
        generateDemoWeatherData();
        generateDemoNewsData();
        generateDemoSocialData();
    };

    const generateDemoWeatherData = () => {
        setWeatherData([
            {
                location: 'Randwick',
                condition: 'Sunny',
                temperature: 22,
                humidity: 65,
                windSpeed: 12,
                icon: 'sunny',
                trackCondition: 'Good'
            },
            {
                location: 'Flemington',
                condition: 'Partly Cloudy',
                temperature: 18,
                humidity: 72,
                windSpeed: 8,
                icon: 'cloudy',
                trackCondition: 'Good'
            },
            {
                location: 'Eagle Farm',
                condition: 'Overcast',
                temperature: 26,
                humidity: 80,
                windSpeed: 15,
                icon: 'overcast',
                trackCondition: 'Soft'
            }
        ]);
    };

    const generateDemoNewsData = () => {
        setNewsItems([
            {
                id: '1',
                title: 'Spring Carnival Preparations Heat Up',
                summary: 'Top trainers finalizing preparations for the upcoming Spring Racing Carnival with several international entries confirmed.',
                source: 'Racing.com',
                publishedAt: '2025-08-26T14:30:00Z',
                category: 'racing'
            },
            {
                id: '2',
                title: 'New Jockey Licensing Requirements Announced',
                summary: 'Racing authorities introduce enhanced safety and training requirements for apprentice jockeys starting next season.',
                source: 'Thoroughbred Daily',
                publishedAt: '2025-08-26T12:15:00Z',
                category: 'racing'
            },
            {
                id: '3',
                title: 'Betting Exchange Volumes Surge',
                summary: 'Online betting exchange platforms report 25% increase in trading volumes compared to last year.',
                source: 'Market Watch',
                publishedAt: '2025-08-26T10:45:00Z',
                category: 'market'
            }
        ]);
    };

    const generateDemoSocialData = () => {
        setSocialFeed([
            {
                id: '1',
                platform: 'twitter',
                author: '@RacingTips_Pro',
                content: 'Strong field assembling for Saturday\'s Group 1. Watch for the imported horse making debut.',
                timestamp: '2025-08-26T16:20:00Z',
                engagement: 245,
                sentiment: 'positive'
            },
            {
                id: '2',
                platform: 'reddit',
                author: 'u/horseplayer2024',
                content: 'Track conditions favoring front runners this week. Backing speed horses in early races.',
                timestamp: '2025-08-26T15:45:00Z',
                engagement: 89,
                sentiment: 'neutral'
            },
            {
                id: '3',
                platform: 'telegram',
                author: 'Racing Insider',
                content: 'Market move on #8 in Race 7. Stable confident after impressive trackwork.',
                timestamp: '2025-08-26T15:10:00Z',
                engagement: 156,
                sentiment: 'positive'
            }
        ]);
    };

    const handleWidgetMenu = (event: React.MouseEvent<HTMLElement>, widgetId: string) => {
        setAnchorEl(event.currentTarget);
        setSelectedWidget(widgetId);
    };

    const handleCloseMenu = () => {
        setAnchorEl(null);
        setSelectedWidget(null);
    };

    const toggleWidgetVisibility = (widgetId: string) => {
        setWidgetConfig(config =>
            config.map(widget =>
                widget.id === widgetId
                    ? { ...widget, visible: !widget.visible }
                    : widget
            )
        );
        handleCloseMenu();
    };

    const getWeatherIcon = (condition: string) => {
        switch (condition.toLowerCase()) {
            case 'sunny': return <WbSunny color="warning" />;
            case 'cloudy':
            case 'partly cloudy': return <Cloud color="action" />;
            case 'overcast': return <Cloud color="disabled" />;
            default: return <WbSunny color="warning" />;
        }
    };

    const getSentimentColor = (sentiment: string) => {
        switch (sentiment) {
            case 'positive': return 'success';
            case 'negative': return 'error';
            default: return 'default';
        }
    };

    const formatTimeAgo = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    };

    const renderWeatherWidget = () => (
        <Card sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Track Weather</Typography>
                    <IconButton onClick={(e) => handleWidgetMenu(e, 'weather')}>
                        <MoreVert />
                    </IconButton>
                </Box>
                
                <Grid container spacing={2}>
                    {weatherData.map((weather, index) => (
                        <Grid item xs={12} sm={4} key={index}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    {weather.location}
                                </Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                                    {getWeatherIcon(weather.condition)}
                                    <Typography variant="h4" sx={{ ml: 1 }}>
                                        {weather.temperature}°
                                    </Typography>
                                </Box>
                                <Typography variant="body2" color="text.secondary">
                                    {weather.condition}
                                </Typography>
                                <Chip 
                                    label={weather.trackCondition}
                                    size="small"
                                    color={weather.trackCondition === 'Good' ? 'success' : 'warning'}
                                    sx={{ mt: 1 }}
                                />
                            </Paper>
                        </Grid>
                    ))}
                </Grid>
            </CardContent>
        </Card>
    );

    const renderNewsWidget = () => (
        <Card sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Racing News</Typography>
                    <IconButton onClick={(e) => handleWidgetMenu(e, 'news')}>
                        <MoreVert />
                    </IconButton>
                </Box>
                
                <List sx={{ pt: 0 }}>
                    {newsItems.slice(0, 3).map((news, index) => (
                        <React.Fragment key={news.id}>
                            <ListItem sx={{ px: 0 }}>
                                <ListItemAvatar>
                                    <Avatar>
                                        <Article />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText
                                    primary={news.title}
                                    secondary={
                                        <Box>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                                {news.summary}
                                            </Typography>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="caption" color="text.secondary">
                                                    {news.source}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    {formatTimeAgo(news.publishedAt)}
                                                </Typography>
                                            </Box>
                                        </Box>
                                    }
                                />
                            </ListItem>
                            {index < newsItems.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            </CardContent>
        </Card>
    );

    const renderSocialWidget = () => (
        <Card sx={{ height: '100%' }}>
            <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Social Sentiment</Typography>
                    <IconButton onClick={(e) => handleWidgetMenu(e, 'social')}>
                        <MoreVert />
                    </IconButton>
                </Box>
                
                <List sx={{ pt: 0 }}>
                    {socialFeed.slice(0, 3).map((post, index) => (
                        <React.Fragment key={post.id}>
                            <ListItem sx={{ px: 0 }}>
                                <ListItemAvatar>
                                    <Avatar sx={{ bgcolor: post.platform === 'twitter' ? '#1DA1F2' : '#FF4500' }}>
                                        <Twitter />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText
                                    primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="subtitle2">
                                                {post.author}
                                            </Typography>
                                            <Chip 
                                                label={post.sentiment}
                                                size="small"
                                                color={getSentimentColor(post.sentiment) as any}
                                            />
                                        </Box>
                                    }
                                    secondary={
                                        <Box>
                                            <Typography variant="body2" sx={{ mb: 1 }}>
                                                {post.content}
                                            </Typography>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <Typography variant="caption" color="text.secondary">
                                                    {post.engagement} reactions
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    {formatTimeAgo(post.timestamp)}
                                                </Typography>
                                            </Box>
                                        </Box>
                                    }
                                />
                            </ListItem>
                            {index < socialFeed.length - 1 && <Divider />}
                        </React.Fragment>
                    ))}
                </List>
            </CardContent>
        </Card>
    );

    const renderPerformanceWidget = () => {
        const data = [
            { time: '09:00', volume: 120000, confidence: 85 },
            { time: '10:00', volume: 145000, confidence: 78 },
            { time: '11:00', volume: 180000, confidence: 82 },
            { time: '12:00', volume: 165000, confidence: 89 },
            { time: '13:00', volume: 195000, confidence: 91 },
            { time: '14:00', volume: 175000, confidence: 87 }
        ];

        return (
            <Card sx={{ height: '100%' }}>
                <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Market Performance</Typography>
                        <IconButton onClick={(e) => handleWidgetMenu(e, 'performance')}>
                            <MoreVert />
                        </IconButton>
                    </Box>
                    
                    <ResponsiveContainer width="100%" height={200}>
                        <AreaChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />
                            <Area 
                                type="monotone" 
                                dataKey="volume" 
                                stroke="#8884d8" 
                                fill="#8884d8" 
                                fillOpacity={0.3}
                            />
                            <Area 
                                type="monotone" 
                                dataKey="confidence" 
                                stroke="#82ca9d" 
                                fill="#82ca9d" 
                                fillOpacity={0.3}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        );
    };

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    🎛️ Enhanced Dashboard Widgets
                </Typography>
                <Box>
                    <IconButton onClick={fetchDashboardData} disabled={loading}>
                        <Refresh />
                    </IconButton>
                    <IconButton>
                        <Settings />
                    </IconButton>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                {widgetConfig.filter(w => w.visible).map(widget => (
                    <Grid item xs={12} md={widget.size.width} key={widget.id}>
                        {widget.id === 'weather' && renderWeatherWidget()}
                        {widget.id === 'news' && renderNewsWidget()}
                        {widget.id === 'social' && renderSocialWidget()}
                        {widget.id === 'performance' && renderPerformanceWidget()}
                    </Grid>
                ))}
            </Grid>

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleCloseMenu}
            >
                <MenuItem onClick={() => selectedWidget && toggleWidgetVisibility(selectedWidget)}>
                    {widgetConfig.find(w => w.id === selectedWidget)?.visible ? 
                        <><VisibilityOff sx={{ mr: 1 }} /> Hide Widget</> :
                        <><Visibility sx={{ mr: 1 }} /> Show Widget</>
                    }
                </MenuItem>
                <MenuItem onClick={handleCloseMenu}>
                    <Settings sx={{ mr: 1 }} /> Configure
                </MenuItem>
                <MenuItem onClick={handleCloseMenu}>
                    <Share sx={{ mr: 1 }} /> Share
                </MenuItem>
            </Menu>

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                    <CircularProgress />
                </Box>
            )}
        </Box>
    );
};

export default EnhancedDashboardWidgets;
