import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { AppBar, Toolbar, Typography, Container, Button, Box } from '@mui/material'
import { 
  Dashboard as DashboardIcon, 
  Analytics as AnalyticsIcon, 
  Assessment, 
  Schedule, 
  Sports,
  Storage,
  LiveTv,
  MonetizationOn,
  AccountCircle,
  Settings,
  Security
} from '@mui/icons-material'

// Import all pages
import Dashboard from './pages/Dashboard'
import RacingAnalyzer from './pages/RacingAnalyzer'
import LiveAnalytics from './pages/LiveAnalytics'
import RaceCardsEnhanced from './pages/RaceCardsEnhanced'
import RaceCards from './pages/RaceCards'
import CourseSummary from './pages/CourseSummary'
import CourseDetail from './pages/CourseDetail'
import RaceDetail from './pages/RaceDetail'
import RaceDetails from './pages/RaceDetails'
import DatabaseManagement from './pages/DatabaseManagement'
import EnhancedFormAnalysisTools from './components/analysis/EnhancedFormAnalysisTools'
import EnhancedDashboardWidgets from './components/dashboard/EnhancedDashboardWidgets'
import AdvancedRaceCardFeatures from './components/racecard/AdvancedRaceCardFeatures'
import ErrorPage from './pages/ErrorPage'
import { RaceSelection } from './components/RaceSelection'
import AdvancedBettingDashboard from './components/betting/AdvancedBettingDashboard'
import UserManagementDashboard from './components/user/UserManagementDashboard'
import PersonalizationEngine from './components/user/PersonalizationEngine'
import SubscriptionManager from './components/user/SubscriptionManager'
import UserSettings from './components/user/UserSettings'
import SecurityCompliance from './components/security/SecurityCompliance'

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#43e97b',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static" sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Toolbar>
              <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
                🏇 Horse Racing AI v2.03
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button color="inherit" href="/" startIcon={<DashboardIcon />}>
                  Dashboard
                </Button>
                <Button color="inherit" href="/analyzer" startIcon={<AnalyticsIcon />}>
                  AI Analyzer
                </Button>
                <Button color="inherit" href="/form-analysis" startIcon={<Assessment />}>
                  Form Analysis
                </Button>
                <Button color="inherit" href="/live" startIcon={<LiveTv />}>
                  Live Analytics
                </Button>
                <Button color="inherit" href="/live-racing" startIcon={<LiveTv />}>
                  Live Racing
                </Button>
                <Button color="inherit" href="/betting" startIcon={<MonetizationOn />}>
                  Pro Betting
                </Button>
                <Button color="inherit" href="/cards" startIcon={<Schedule />}>
                  Race Cards
                </Button>
                <Button color="inherit" href="/race/1" startIcon={<Sports />}>
                  Race Details
                </Button>
                <Button color="inherit" href="/database" startIcon={<Storage />}>
                  Database
                </Button>
                <Button color="inherit" href="/user/dashboard" startIcon={<AccountCircle />}>
                  My Account
                </Button>
                <Button color="inherit" href="/user/settings" startIcon={<Settings />}>
                  Settings
                </Button>
                <Button color="inherit" href="/security" startIcon={<Security />}>
                  Security
                </Button>
              </Box>
            </Toolbar>
          </AppBar>

          <Container maxWidth={false} sx={{ mt: 0, p: 0 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Navigate to="/" replace />} />
              <Route path="/analyzer" element={<RacingAnalyzer />} />
              <Route path="/form-analysis" element={<EnhancedFormAnalysisTools />} />
              <Route path="/widgets" element={<EnhancedDashboardWidgets />} />
              <Route path="/advanced-cards" element={<AdvancedRaceCardFeatures />} />
              <Route path="/live" element={<LiveAnalytics />} />
              <Route path="/live-racing" element={<RaceSelection />} />
              <Route path="/betting" element={<AdvancedBettingDashboard />} />
              {/* New Race Card Structure */}
              <Route path="/cards" element={<CourseSummary />} />
              <Route path="/course/:courseName" element={<CourseDetail />} />
              <Route path="/race/:raceId" element={<RaceDetail />} />
              {/* Legacy Routes */}
              <Route path="/cards-enhanced" element={<RaceCardsEnhanced />} />
              <Route path="/race-details/:id" element={<RaceDetails />} />
              <Route path="/database" element={<DatabaseManagement />} />
              {/* User Management Routes */}
              <Route path="/user/dashboard" element={<UserManagementDashboard />} />
              <Route path="/user/personalization" element={<PersonalizationEngine />} />
              <Route path="/user/subscription" element={<SubscriptionManager />} />
              <Route path="/user/settings" element={<UserSettings />} />
              {/* Security & Compliance Routes */}
              <Route path="/security" element={<SecurityCompliance />} />
              <Route path="/error" element={<ErrorPage />} />
              <Route path="*" element={<ErrorPage />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  )
}

export default App
