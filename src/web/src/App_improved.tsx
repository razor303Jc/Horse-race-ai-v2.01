// App_improved.tsx - Refactored version demonstrating better architecture
import {
    Box,
    Container,
    CssBaseline,
    ThemeProvider
} from '@mui/material'
import React, { Suspense } from 'react'
import AppHeader from './components/layout/AppHeader'
import ErrorBoundary from './components/ui/ErrorBoundary'
import LoadingSpinner from './components/ui/LoadingSpinner'
import { DashboardProvider } from './contexts/DashboardContext'
import { theme } from './styles/theme'

// Lazy loaded components for better performance
const SystemStatus = React.lazy(() => import('./components/dashboard/SystemStatus'))
const TabContainer = React.lazy(() => import('./components/layout/TabContainer'))
const OverviewTab = React.lazy(() => import('./components/tabs/OverviewTab'))
const MLAnalyticsTab = React.lazy(() => import('./components/tabs/MLAnalyticsTab'))
const BettingPerformanceTab = React.lazy(() => import('./components/tabs/BettingPerformanceTab'))
const LivePredictionsTab = React.lazy(() => import('./components/tabs/LivePredictionsTab'))
const AIInsightsTab = React.lazy(() => import('./components/tabs/AIInsightsTab'))
const DailyRacesTab = React.lazy(() => import('./components/tabs/DailyRacesTab'))

const App: React.FC = () => {
  const tabComponents = [
    { label: 'Overview', icon: 'Assessment', component: OverviewTab },
    { label: 'ML Analytics', icon: 'TrendingUp', component: MLAnalyticsTab },
    { label: 'Betting Performance', icon: 'AttachMoney', component: BettingPerformanceTab },
    { label: 'Live Predictions', icon: 'Sports', component: LivePredictionsTab },
    { label: 'AI Insights', icon: 'Psychology', component: AIInsightsTab },
    { label: 'Daily Races', icon: 'Dashboard', component: DailyRacesTab },
  ]

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <DashboardProvider>
          <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
            <AppHeader />
            
            <Container maxWidth="xl" sx={{ mt: 4, pb: 4 }}>
              <Suspense fallback={<LoadingSpinner />}>
                <SystemStatus />
                <TabContainer tabs={tabComponents} />
              </Suspense>
            </Container>
          </Box>
        </DashboardProvider>
      </ErrorBoundary>
    </ThemeProvider>
  )
}

export default App

/*
Key Improvements in this refactored version:

1. **Separation of Concerns**:
   - App.tsx only handles high-level structure
   - Each tab is a separate component
   - State management moved to Context
   - UI components are reusable

2. **Performance Optimizations**:
   - Lazy loading for code splitting
   - Suspense boundaries for better UX
   - Context prevents unnecessary re-renders

3. **Better Architecture**:
   - ErrorBoundary for error handling
   - ThemeProvider for consistent styling
   - Modular component structure

4. **Scalability**:
   - Easy to add new tabs
   - Reusable components
   - Type-safe interfaces

5. **Maintainability**:
   - Clear file organization
   - Single responsibility principle
   - Easier testing and debugging

Component Structure:
├── App.tsx (this file)
├── components/
│   ├── dashboard/
│   │   ├── SystemStatus.tsx
│   │   ├── MLMetrics.tsx
│   │   └── BettingMetrics.tsx
│   ├── layout/
│   │   ├── AppHeader.tsx
│   │   └── TabContainer.tsx
│   ├── tabs/
│   │   ├── OverviewTab.tsx
│   │   ├── MLAnalyticsTab.tsx
│   │   └── ...
│   └── ui/
│       ├── MetricCard.tsx
│       ├── LoadingSpinner.tsx
│       └── ErrorBoundary.tsx
├── contexts/
│   └── DashboardContext.tsx
├── hooks/
│   ├── useSystemStatus.ts
│   └── useDashboardData.ts
├── styles/
│   └── theme.ts
└── types/
    └── dashboard.ts
*/
