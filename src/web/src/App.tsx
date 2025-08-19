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
  Storage 
} from '@mui/icons-material'

// Import all pages
import Dashboard from './pages/Dashboard'
import RacingAnalyzer from './pages/RacingAnalyzer'
import LiveAnalytics from './pages/LiveAnalytics'
import RaceCardsEnhanced from './pages/RaceCardsEnhanced'
import RaceDetails from './pages/RaceDetails'
import DatabaseManagement from './pages/DatabaseManagement'
import ErrorPage from './pages/ErrorPage'

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
                <Button color="inherit" href="/live" startIcon={<Assessment />}>
                  Live Analytics
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
              </Box>
            </Toolbar>
          </AppBar>

          <Container maxWidth={false} sx={{ mt: 0, p: 0 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Navigate to="/" replace />} />
              <Route path="/analyzer" element={<RacingAnalyzer />} />
              <Route path="/live" element={<LiveAnalytics />} />
              <Route path="/cards" element={<RaceCardsEnhanced />} />
              <Route path="/race/:id" element={<RaceDetails />} />
              <Route path="/database" element={<DatabaseManagement />} />
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
