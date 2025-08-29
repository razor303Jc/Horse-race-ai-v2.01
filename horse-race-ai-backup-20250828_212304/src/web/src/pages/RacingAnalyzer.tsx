import {
    Psychology,
    TrendingUp,
    Assessment,
    Speed
} from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    Container,
    Grid,
    Typography,
    Button,
    TextField,
    Paper,
    Chip
} from '@mui/material'

export default function RacingAnalyzer() {
    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🐦 Racing Media Analyzer
            </Typography>
            
            {/* Analysis Input Section */}
            <Card sx={{ p: 4, mb: 4, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <Typography variant="h4" gutterBottom>AI-Powered Race Analysis</Typography>
                <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
                    Upload race media, news articles, or social media content for advanced AI analysis
                </Typography>
                
                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            label="Paste URL or Text Content"
                            multiline
                            rows={4}
                            variant="outlined"
                            sx={{ 
                                backgroundColor: 'rgba(255,255,255,0.1)',
                                '& .MuiOutlinedInput-root': {
                                    color: 'white',
                                    '& fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.5)' },
                                }
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
                            <Typography variant="h6" gutterBottom>Supported Sources:</Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                                <Chip label="Racing News" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                                <Chip label="Twitter/X" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                                <Chip label="Racing Forums" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                                <Chip label="Video Content" sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                            </Box>
                            <Button 
                                variant="contained" 
                                size="large"
                                sx={{ 
                                    backgroundColor: 'rgba(255,255,255,0.2)', 
                                    color: 'white',
                                    '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' }
                                }}
                            >
                                🔍 Analyze Content
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
            </Card>

            {/* Analysis Results */}
            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                            <Psychology sx={{ mr: 1, color: '#667eea' }} />
                            Sentiment Analysis
                        </Typography>
                        
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="h6" color="success.main">Positive: 68%</Typography>
                            <Typography variant="body2" color="text.secondary">
                                Strong positive sentiment around trainer performance and recent form
                            </Typography>
                        </Box>
                        
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="h6" color="warning.main">Neutral: 22%</Typography>
                            <Typography variant="body2" color="text.secondary">
                                Mixed opinions on track conditions and weather impact
                            </Typography>
                        </Box>
                        
                        <Box>
                            <Typography variant="h6" color="error.main">Negative: 10%</Typography>
                            <Typography variant="body2" color="text.secondary">
                                Minor concerns about jockey change and barrier draw
                            </Typography>
                        </Box>
                    </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Card sx={{ p: 3, height: '100%' }}>
                        <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                            <TrendingUp sx={{ mr: 1, color: '#667eea' }} />
                            Key Insights
                        </Typography>
                        
                        <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
                            <Typography variant="body1" fontWeight="bold" gutterBottom>
                                🏆 Trainer Form Alert
                            </Typography>
                            <Typography variant="body2">
                                John Smith has 4 wins from last 6 starts - exceptional recent form detected
                            </Typography>
                        </Paper>
                        
                        <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
                            <Typography variant="body1" fontWeight="bold" gutterBottom>
                                📊 Market Movement
                            </Typography>
                            <Typography variant="body2">
                                Significant money flowing for Horse #5 - odds shortened from $4.50 to $3.20
                            </Typography>
                        </Paper>
                        
                        <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                            <Typography variant="body1" fontWeight="bold" gutterBottom>
                                🌦️ Track Conditions
                            </Typography>
                            <Typography variant="body2">
                                Heavy track favors horses with proven wet track form - check historical data
                            </Typography>
                        </Paper>
                    </Card>
                </Grid>
            </Grid>

            {/* Social Media Feed */}
            <Card sx={{ p: 3, mt: 4 }}>
                <Typography variant="h5" gutterBottom>Live Social Media Feed</Typography>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2, backgroundColor: '#e3f2fd' }}>
                            <Typography variant="body2" fontWeight="bold">@RacingExpert</Typography>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                                "Thunderbolt looks unbeatable in Race 7. Perfect barrier, top jockey, and loves this distance. 🏇 #RacingTips"
                            </Typography>
                            <Typography variant="caption" color="text.secondary">2 minutes ago</Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2, backgroundColor: '#f3e5f5' }}>
                            <Typography variant="body2" fontWeight="bold">@TrackInsider</Typography>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                                "Track bias favoring leaders today. Early pace will be crucial. Watch for horses that can sit handy. 📈"
                            </Typography>
                            <Typography variant="caption" color="text.secondary">5 minutes ago</Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2, backgroundColor: '#e8f5e8' }}>
                            <Typography variant="body2" fontWeight="bold">@PuntersClub</Typography>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                                "Late mail: Stable confident about Lightning Strike. Backed into favoritism. Worth following! ⚡"
                            </Typography>
                            <Typography variant="caption" color="text.secondary">8 minutes ago</Typography>
                        </Paper>
                    </Grid>
                </Grid>
            </Card>
        </Container>
    )
}
