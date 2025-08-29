import React, { useState } from 'react';
import { Container, Typography, Box, Tabs, Tab } from '@mui/material';
import { RaceCardsList } from '../components/race/RaceCardsList';
import { EnhancedRaceCardDisplay } from '../components/race/EnhancedRaceCardDisplay';

export const RaceCards: React.FC = () => {
    const [tabValue, setTabValue] = useState(0);

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setTabValue(newValue);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Race Cards
            </Typography>
            
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={tabValue} onChange={handleTabChange}>
                    <Tab label="Standard View" />
                    <Tab label="Enhanced Analysis" />
                </Tabs>
            </Box>

            <Box sx={{ mt: 4 }}>
                {tabValue === 0 && <RaceCardsList />}
                {tabValue === 1 && <EnhancedRaceCardDisplay />}
            </Box>
        </Container>
    );
};

export default RaceCards;
