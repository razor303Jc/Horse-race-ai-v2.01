import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    AccessTime,
    Place,
    Speed,
    EmojiEvents
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
    CircularProgress,
    Alert,
    Button,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Avatar,
    Divider
} from '@mui/material'
import { HorseRacingAPI } from '../services/api'

// Interfaces
interface RealRaceCard {
    race_id: number;
    race_number: number;
    race_time: string;
    course: string;
    race_name: string;
    class: string;
    distance: string;
    surface: string;
    prize: string;
    runners: number;
    status?: string;
}

interface CourseData {
    course: string;
    races: RealRaceCard[];
    totalRaces: number;
    totalPrizeMoney: string;
    firstRace: string;
    lastRace: string;
}

export default function CourseSummary() {
    const [courseData, setCourseData] = useState<CourseData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [totalRaces, setTotalRaces] = useState(0);
    const [totalVenues, setTotalVenues] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        const loadCourseData = async () => {
            try {
                setLoading(true);
                setError(null);
                
                console.log('Loading race data for course summary...');
                const dailyRaces = await HorseRacingAPI.getDailyRaces();
                
                // Group races by course
                const courseMap = new Map<string, RealRaceCard[]>();
                
                dailyRaces.races.forEach(race => {
                    const raceCard: RealRaceCard = {
                        race_id: race.race_id,
                        race_number: race.race_number,
                        race_time: race.race_time,
                        course: race.course,
                        race_name: race.race_name,
                        class: race.class || 'Unknown',
                        distance: race.distance || 'Unknown',
                        surface: race.surface || 'Unknown',
                        prize: race.prize || 'Unknown',
                        runners: race.runners,
                        status: 'upcoming'
                    };
                    
                    if (!courseMap.has(race.course)) {
                        courseMap.set(race.course, []);
                    }
                    courseMap.get(race.course)!.push(raceCard);
                });
                
                // Convert to CourseData array
                const courses: CourseData[] = Array.from(courseMap.entries()).map(([courseName, races]) => {
                    const sortedRaces = races.sort((a, b) => a.race_time.localeCompare(b.race_time));
                    
                    return {
                        course: courseName,
                        races: sortedRaces,
                        totalRaces: races.length,
                        totalPrizeMoney: calculateTotalPrize(races),
                        firstRace: sortedRaces[0]?.race_time || '',
                        lastRace: sortedRaces[sortedRaces.length - 1]?.race_time || ''
                    };
                }).sort((a, b) => a.firstRace.localeCompare(b.firstRace));
                
                setCourseData(courses);
                setTotalRaces(dailyRaces.total_races);
                setTotalVenues(courses.length);
                
                console.log(`Loaded ${courses.length} courses with ${dailyRaces.total_races} total races`);
                
            } catch (error) {
                console.error('Error loading course data:', error);
                setError('Failed to load course data. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        loadCourseData();
    }, []);

    const calculateTotalPrize = (races: RealRaceCard[]): string => {
        // Extract numeric values from prize strings and sum them
        let total = 0;
        races.forEach(race => {
            const prizeMatch = race.prize.match(/[\d,]+/);
            if (prizeMatch) {
                const prizeValue = parseFloat(prizeMatch[0].replace(/,/g, ''));
                total += prizeValue;
            }
        });
        return total > 0 ? `£${total.toLocaleString()}` : 'Unknown';
    };

    const handleCourseClick = (courseName: string) => {
        navigate(`/course/${encodeURIComponent(courseName)}`);
    };

    const handleRaceClick = (raceId: number) => {
        navigate(`/race/${raceId}`);
    };

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ ml: 2 }}>Loading course summary...</Typography>
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
                <Alert severity="error" sx={{ mb: 4 }}>
                    {error}
                    <Button variant="outlined" sx={{ ml: 2 }} onClick={() => window.location.reload()}>
                        Retry
                    </Button>
                </Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Today's Racing Summary
            </Typography>
            
            {/* Overview Stats */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <AccessTime sx={{ mr: 1 }} />
                                <Typography variant="h6">Total Races</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>{totalRaces}</Typography>
                            <Typography variant="body2">Today</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Place sx={{ mr: 1 }} />
                                <Typography variant="h6">Venues</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>{totalVenues}</Typography>
                            <Typography variant="body2">Racecourses</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <EmojiEvents sx={{ mr: 1 }} />
                                <Typography variant="h6">Racing Time</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>8hrs</Typography>
                            <Typography variant="body2">13:50 - 21:00</Typography>
                        </CardContent>
                    </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)', color: '#333' }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Speed sx={{ mr: 1 }} />
                                <Typography variant="h6">Avg Runners</Typography>
                            </Box>
                            <Typography variant="h3" sx={{ fontWeight: 'bold' }}>12</Typography>
                            <Typography variant="body2">Per Race</Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Course Cards */}
            <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
                📍 Racecourses Today
            </Typography>
            
            <Grid container spacing={3}>
                {courseData.map((course) => (
                    <Grid item xs={12} md={6} lg={4} key={course.course}>
                        <Card sx={{ height: '100%', cursor: 'pointer', '&:hover': { elevation: 8 } }} 
                              onClick={() => handleCourseClick(course.course)}>
                            <CardContent sx={{ p: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                                        {course.course}
                                    </Typography>
                                    <Avatar sx={{ bgcolor: 'primary.main' }}>
                                        {course.totalRaces}
                                    </Avatar>
                                </Box>
                                
                                <Grid container spacing={2} sx={{ mb: 2 }}>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="text.secondary">First Race</Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{course.firstRace}</Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="text.secondary">Last Race</Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{course.lastRace}</Typography>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography variant="body2" color="text.secondary">Prize Money</Typography>
                                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{course.totalPrizeMoney}</Typography>
                                    </Grid>
                                </Grid>
                                
                                <Divider sx={{ my: 2 }} />
                                
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                    Today's Races:
                                </Typography>
                                <List dense sx={{ py: 0 }}>
                                    {course.races.slice(0, 3).map((race) => (
                                        <ListItem key={race.race_id} disablePadding>
                                            <ListItemButton 
                                                sx={{ py: 0.5 }}
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleRaceClick(race.race_id);
                                                }}
                                            >
                                                <ListItemText 
                                                    primary={
                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                                                {race.race_name.length > 25 ? race.race_name.substring(0, 25) + '...' : race.race_name}
                                                            </Typography>
                                                            <Chip label={race.race_time} size="small" variant="outlined" />
                                                        </Box>
                                                    }
                                                />
                                            </ListItemButton>
                                        </ListItem>
                                    ))}
                                    {course.races.length > 3 && (
                                        <ListItem>
                                            <ListItemText 
                                                primary={
                                                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                                                        +{course.races.length - 3} more races...
                                                    </Typography>
                                                }
                                            />
                                        </ListItem>
                                    )}
                                </List>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
}
