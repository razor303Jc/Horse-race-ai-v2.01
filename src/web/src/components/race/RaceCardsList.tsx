import React from 'react';
import {
    Box,
    Card,
    CardContent,
    Grid,
    Typography,
    Paper,
    Chip,
    Avatar,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    LinearProgress
} from '@mui/material';
import {
    AccessTime,
    TrendingUp,
    Star,
    Place
} from '@mui/icons-material';

const mockRaceCards = [
    {
        id: 1,
        course: 'Ascot',
        time: '15:30',
        distance: '1m 2f',
        ground: 'Good',
        type: 'Handicap',
        prize: '£50,000',
        runners: [
            {
                number: 1,
                name: 'Thunder Strike',
                odds: '5/1',
                form: '1-2-3',
                jockey: 'R. Moore',
                trainer: 'A. O\'Brien',
                weight: '9-7',
                aiRating: 85,
                prediction: 'Strong chance'
            },
            {
                number: 2,
                name: 'Golden Arrow',
                odds: '3/1',
                form: '1-1-2',
                jockey: 'W. Buick',
                trainer: 'J. Gosden',
                weight: '9-5',
                aiRating: 92,
                prediction: 'Top pick'
            },
            {
                number: 3,
                name: 'Silver Bullet',
                odds: '7/1',
                form: '2-3-1',
                jockey: 'F. Dettori',
                trainer: 'M. Stoute',
                weight: '9-3',
                aiRating: 78,
                prediction: 'Each way value'
            }
        ]
    },
    {
        id: 2,
        course: 'Newmarket',
        time: '16:05',
        distance: '7f',
        ground: 'Good to Firm',
        type: 'Group 2',
        prize: '£100,000',
        runners: [
            {
                number: 1,
                name: 'Speed Demon',
                odds: '2/1',
                form: '1-1-1',
                jockey: 'R. Moore',
                trainer: 'A. O\'Brien',
                weight: '9-0',
                aiRating: 95,
                prediction: 'Banker'
            },
            {
                number: 2,
                name: 'Lightning Fast',
                odds: '5/2',
                form: '2-1-2',
                jockey: 'W. Buick',
                trainer: 'J. Gosden',
                weight: '9-0',
                aiRating: 88,
                prediction: 'Danger'
            }
        ]
    }
];

export const RaceCardsList: React.FC = () => {
    return (
        <Box>
            <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
                🏇 Today's Race Cards
            </Typography>
            
            <Grid container spacing={4}>
                {mockRaceCards.map((race) => (
                    <Grid item xs={12} key={race.id}>
                        <Card sx={{ mb: 3 }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                                    <Box>
                                        <Typography variant="h5" component="h3" gutterBottom>
                                            {race.course} - {race.time}
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                            <Chip icon={<AccessTime />} label={race.distance} />
                                            <Chip label={race.ground} color="success" />
                                            <Chip label={race.type} color="primary" />
                                            <Chip label={race.prize} color="secondary" />
                                        </Box>
                                    </Box>
                                </Box>
                                
                                <TableContainer component={Paper} sx={{ mt: 2 }}>
                                    <Table>
                                        <TableHead>
                                            <TableRow sx={{ backgroundColor: 'grey.50' }}>
                                                <TableCell><strong>No.</strong></TableCell>
                                                <TableCell><strong>Horse</strong></TableCell>
                                                <TableCell><strong>Odds</strong></TableCell>
                                                <TableCell><strong>Form</strong></TableCell>
                                                <TableCell><strong>Jockey</strong></TableCell>
                                                <TableCell><strong>Trainer</strong></TableCell>
                                                <TableCell><strong>Weight</strong></TableCell>
                                                <TableCell><strong>AI Rating</strong></TableCell>
                                                <TableCell><strong>Prediction</strong></TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {race.runners.map((horse) => (
                                                <TableRow key={horse.number} hover>
                                                    <TableCell>
                                                        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                                            {horse.number}
                                                        </Avatar>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body1" fontWeight="bold">
                                                            {horse.name}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="h6" color="primary">
                                                            {horse.odds}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                                            {horse.form}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.jockey}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.trainer}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">
                                                            {horse.weight}
                                                        </Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <LinearProgress
                                                                variant="determinate"
                                                                value={horse.aiRating}
                                                                sx={{ width: 60, height: 8, borderRadius: 4 }}
                                                            />
                                                            <Typography variant="body2" fontWeight="bold">
                                                                {horse.aiRating}/100
                                                            </Typography>
                                                        </Box>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Chip
                                                            icon={
                                                                horse.prediction === 'Top pick' || horse.prediction === 'Banker' ? <Star /> :
                                                                horse.prediction === 'Strong chance' || horse.prediction === 'Danger' ? <TrendingUp /> :
                                                                <Place />
                                                            }
                                                            label={horse.prediction}
                                                            color={
                                                                horse.prediction === 'Top pick' || horse.prediction === 'Banker' ? 'success' :
                                                                horse.prediction === 'Strong chance' || horse.prediction === 'Danger' ? 'primary' :
                                                                'default'
                                                            }
                                                            size="small"
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            
            <Box sx={{ mt: 4, p: 3, backgroundColor: 'grey.50', borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>
                    🤖 AI Insights
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Our AI models have analyzed today's races using advanced machine learning algorithms. 
                    The ratings consider form, track conditions, jockey/trainer combinations, and historical data.
                </Typography>
            </Box>
        </Box>
    );
};
