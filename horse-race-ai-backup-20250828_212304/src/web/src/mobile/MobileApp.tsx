import React, { useState, useEffect, Suspense } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Box,
  useMediaQuery,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { createMobileTheme } from '../theme/mobileTheme';

// Mobile components
import MobileNavigation from '../components/mobile/MobileNavigation';
import ResponsiveLayout from '../components/mobile/ResponsiveLayout';
import PWAInstallPrompt, { usePWA } from '../components/mobile/PWAInstallPrompt';

// Simple placeholder components
const DashboardPlaceholder = () => (
  <Box sx={{ p: 2, textAlign: 'center' }}>
    <h2>Dashboard</h2>
    <p>Welcome to Racing AI Mobile</p>
  </Box>
);

const RaceCardsPlaceholder = () => (
  <Box sx={{ p: 2, textAlign: 'center' }}>
    <h2>Race Cards</h2>
    <p>Today's races will appear here</p>
  </Box>
);

const BettingPlaceholder = () => (
  <Box sx={{ p: 2, textAlign: 'center' }}>
    <h2>Betting Dashboard</h2>
    <p>Betting interface coming soon</p>
  </Box>
);

// Lazy load components for better performance
const MobileBettingInterface = React.lazy(() => import('../components/mobile/MobileBettingInterface'));
const MobileRaceViewer = React.lazy(() => import('../components/mobile/MobileRaceViewer'));
const AdvancedAnalyticsDashboard = React.lazy(() => import('../components/analytics/AdvancedAnalyticsDashboard'));

interface MobileAppProps {
  isStandalone?: boolean;
}

export const MobileApp: React.FC<MobileAppProps> = ({ isStandalone = false }) => {
  const [darkMode, setDarkMode] = useState(() => {
    // Check system preference or saved preference
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) return JSON.parse(saved);
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  const [user, setUser] = useState({
    name: 'Demo User',
    email: 'demo@racing-ai.com',
    subscription: 'premium' as 'free' | 'premium' | 'professional'
  });

  const [notifications, setNotifications] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const theme = createMobileTheme(darkMode ? 'dark' : 'light');
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { isInstallable, isInstalled, isOnline } = usePWA();

  // Initialize app
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Simulate app initialization
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Register service worker for PWA functionality
        if ('serviceWorker' in navigator && isStandalone) {
          try {
            await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registered');
          } catch (error) {
            console.error('Service Worker registration failed:', error);
          }
        }

        setIsLoading(false);
      } catch (error) {
        setError('Failed to initialize app');
        setIsLoading(false);
      }
    };

    initializeApp();
  }, [isStandalone]);

  // Handle theme changes
  const handleThemeToggle = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', JSON.stringify(newDarkMode));
  };

  // Mock data for demonstrations
  const mockRaces = [
    {
      id: 'race-1',
      name: 'Ascot Gold Cup',
      track: 'Ascot',
      time: '15:30',
      distance: '2400m',
      surface: 'Turf',
      status: 'upcoming' as const,
      timeToStart: 25,
      horses: [
        {
          id: 'horse-1',
          name: 'Thunder Strike',
          number: 1,
          jockey: 'J. Smith',
          trainer: 'M. Johnson',
          odds: 3.5,
          probability: 75,
          form: '11321',
          age: 5,
          weight: 58,
          prediction: {
            confidence: 85,
            recommendation: 'strong_buy' as const,
            expectedValue: 12.5
          }
        },
        {
          id: 'horse-2',
          name: 'Swift Arrow',
          number: 2,
          jockey: 'R. Williams',
          trainer: 'S. Brown',
          odds: 5.2,
          probability: 65,
          form: '21132',
          age: 4,
          weight: 56,
          prediction: {
            confidence: 72,
            recommendation: 'buy' as const,
            expectedValue: 8.3
          }
        }
      ]
    }
  ];

  const mockRaceProgress = {
    raceId: 'race-live-1',
    raceName: 'Newmarket Stakes',
    track: 'Newmarket',
    distance: 1600,
    elapsed: 45,
    status: 'running' as const,
    weather: 'Sunny, 18°C',
    track_condition: 'Good',
    positions: [
      {
        position: 1,
        horseId: 'horse-1',
        horseName: 'Lightning Bolt',
        jockey: 'F. Dettori',
        distance: 200,
        speed: 65,
        odds: 2.8,
        prediction: 82
      },
      {
        position: 2,
        horseId: 'horse-2',
        horseName: 'Storm Chaser',
        jockey: 'W. Buick',
        distance: 220,
        speed: 63,
        odds: 4.1,
        prediction: 71
      }
    ],
    commentary: [
      'Lightning Bolt takes the lead as they approach the final furlong',
      'Storm Chaser is making a strong challenge on the outside',
      'The field is tightly packed with 200m to go'
    ]
  };

  // Loading screen
  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            background: theme.palette.gradient.primary,
            color: 'white'
          }}
        >
          <CircularProgress size={60} sx={{ color: 'white', mb: 2 }} />
          <Box sx={{ textAlign: 'center' }}>
            <h1>Racing AI</h1>
            <p>Loading your racing experience...</p>
          </Box>
        </Box>
      </ThemeProvider>
    );
  }

  // Error screen
  if (error) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            p: 2
          }}
        >
          <Alert severity="error" sx={{ maxWidth: 400 }}>
            {error}
          </Alert>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          {/* Mobile Navigation */}
          {isMobile && (
            <MobileNavigation
              user={user}
              notifications={notifications}
              onThemeToggle={handleThemeToggle}
              isDarkMode={darkMode}
            />
          )}

          {/* Main Content with Responsive Layout */}
          <ResponsiveLayout
            showBottomNav={isMobile}
            showSpeedDial={isMobile}
            showScrollToTop={true}
            maxWidth="lg"
          >
            <Suspense
              fallback={
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              }
            >
              <Routes>
                <Route path="/" element={<DashboardPlaceholder />} />
                <Route path="/dashboard" element={<DashboardPlaceholder />} />
                <Route path="/races" element={<RaceCardsPlaceholder />} />
                <Route path="/races/today" element={<RaceCardsPlaceholder />} />
                <Route
                  path="/races/live/:raceId"
                  element={
                    <MobileRaceViewer
                      raceProgress={mockRaceProgress}
                      autoRefresh={true}
                      allowBetting={true}
                      onBetPlaced={async (horseId, amount) => {
                        console.log(`Bet placed: ${horseId} - £${amount}`);
                      }}
                    />
                  }
                />
                <Route path="/betting" element={<BettingPlaceholder />} />
                <Route
                  path="/betting/mobile"
                  element={
                    <MobileBettingInterface
                      races={mockRaces}
                      accountBalance={1500}
                      totalExposure={250}
                      onPlaceBet={async (bet) => {
                        console.log('Bet placed:', bet);
                      }}
                    />
                  }
                />
                <Route path="/analytics" element={<AdvancedAnalyticsDashboard />} />
                <Route path="/profile" element={<DashboardPlaceholder />} />
                <Route path="/menu" element={<DashboardPlaceholder />} />
              </Routes>
            </Suspense>
          </ResponsiveLayout>

          {/* PWA Install Prompt */}
          <PWAInstallPrompt />

          {/* Offline notification */}
          <Snackbar
            open={!isOnline}
            anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
          >
            <Alert severity="warning">
              You are offline. Some features may be limited.
            </Alert>
          </Snackbar>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

// Detect if running as PWA
export const detectPWAMode = () => {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone ||
    document.referrer.includes('android-app://')
  );
};

export default MobileApp;
