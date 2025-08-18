import {
    Error as ErrorIcon,
    Home,
    Refresh,
    BugReport
} from '@mui/icons-material'
import {
    Box,
    Card,
    CardContent,
    Container,
    Typography,
    Button,
    Paper,
    Grid
} from '@mui/material'

export default function ErrorPage() {
    return (
        <Container maxWidth="md" sx={{ mt: 8, mb: 4 }}>
            <Box sx={{ textAlign: 'center' }}>
                <Paper 
                    sx={{ 
                        p: 6, 
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                        color: 'white',
                        mb: 4
                    }}
                >
                    <ErrorIcon sx={{ fontSize: 120, mb: 3, opacity: 0.8 }} />
                    <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                        404
                    </Typography>
                    <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
                        Oops! Page Not Found
                    </Typography>
                    <Typography variant="h6" sx={{ opacity: 0.9, mb: 4 }}>
                        The page you're looking for seems to have wandered off track. 
                        Don't worry, even the best racehorses sometimes take a wrong turn!
                    </Typography>
                </Paper>

                <Grid container spacing={3} justifyContent="center">
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                            <Home sx={{ fontSize: 40, mb: 2, color: '#667eea' }} />
                            <Typography variant="h6" gutterBottom>Go Home</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Return to the main dashboard
                            </Typography>
                            <Button 
                                variant="contained" 
                                sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                                href="/"
                            >
                                Dashboard
                            </Button>
                        </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                            <Refresh sx={{ fontSize: 40, mb: 2, color: '#43e97b' }} />
                            <Typography variant="h6" gutterBottom>Try Again</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Refresh the page and try again
                            </Typography>
                            <Button 
                                variant="contained" 
                                sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}
                                onClick={() => window.location.reload()}
                            >
                                Refresh
                            </Button>
                        </Card>
                    </Grid>

                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                            <BugReport sx={{ fontSize: 40, mb: 2, color: '#fa709a' }} />
                            <Typography variant="h6" gutterBottom>Report Issue</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Let us know about this problem
                            </Typography>
                            <Button 
                                variant="contained" 
                                sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}
                            >
                                Contact Support
                            </Button>
                        </Card>
                    </Grid>
                </Grid>

                <Box sx={{ mt: 6 }}>
                    <Typography variant="body1" color="text.secondary">
                        🏇 While you're here, did you know our AI has analyzed over 100,000 races 
                        and maintains an 87% accuracy rate in predictions?
                    </Typography>
                </Box>
            </Box>
        </Container>
    )
}
