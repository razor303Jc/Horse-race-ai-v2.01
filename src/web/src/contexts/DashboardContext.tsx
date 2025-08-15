// contexts/DashboardContext.tsx
import React, { createContext, ReactNode, useContext, useEffect, useReducer } from 'react'

// Types
interface SystemStatus {
  overall_status: string
  timestamp: string
  ml_models: string
  betting_integration: string
  contextual_ai: string
  notifications: string
  performance_tracker: string
}

interface DashboardData {
  ml_models: {
    ensemble_auc: number
    models_active: number
    status: string
    predictions_today: number
    features_per_horse: number
    training_records: number
    model_accuracy: {
      gradient_boost: number
      neural_network: number
      random_forest: number
      svm: number
    }
    feature_importance: Array<{
      name: string
      importance: number
    }>
  }
  betting_performance: {
    total_pnl: number
    win_rate: number
    roi: number
    trades_today: number
    weekly_performance: Array<{
      day: string
      pnl: number
    }>
    bet_types: {
      win: { count: number; success_rate: number; avg_odds: number }
      place: { count: number; success_rate: number; avg_odds: number }
      each_way: { count: number; success_rate: number; avg_odds: number }
    }
    risk_metrics: {
      max_drawdown: number
      sharpe_ratio: number
      kelly_criterion: number
    }
  }
  contextual_ai: {
    processing_threads: number
    last_insight: string
    confidence_level: number
    insights_generated: number
    sentiment_analysis: {
      market_sentiment: string
      social_buzz: string
      expert_consensus: number
    }
    recent_insights: Array<{
      timestamp: string
      insight: string
      confidence: number
      races_affected: string[]
    }>
  }
  live_predictions: Array<{
    horse: string
    race: string
    probability: number
    confidence: number
    value_rating: number
    status: string
    odds?: number
    suggested_stake?: number
    form_rating?: string
    jockey?: string
    trainer?: string
    result?: string
    profit?: number
  }>
  market_data: {
    active_races: number
    total_volume: number
    avg_odds_movement: number
    liquidity_index: number
    top_tracks: Array<{
      name: string
      races: number
      volume: number
    }>
  }
}

interface BettingOpportunities {
  opportunities: Array<{
    race: string
    horse: string
    bet_type: string
    bookmaker_odds: number
    fair_odds: number
    value_percentage: number
    confidence: number
    suggested_stake: number
    expected_value: number
  }>
  portfolio_stats: {
    total_opportunities: number
    avg_value: number
    recommended_total_stake: number
    potential_profit: number
  }
}

// State interface
interface DashboardState {
  systemStatus: SystemStatus | null
  dashboardData: DashboardData | null
  bettingOpportunities: BettingOpportunities | null
  loading: boolean
  error: string | null
  lastUpdate: Date | null
  currentTab: number
}

// Action types
type DashboardAction =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: { systemStatus: SystemStatus; dashboardData: DashboardData; bettingOpportunities: BettingOpportunities } }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'SET_TAB'; payload: number }
  | { type: 'CLEAR_ERROR' }

// Initial state
const initialState: DashboardState = {
  systemStatus: null,
  dashboardData: null,
  bettingOpportunities: null,
  loading: true,
  error: null,
  lastUpdate: null,
  currentTab: 0,
}

// Reducer
const dashboardReducer = (state: DashboardState, action: DashboardAction): DashboardState => {
  switch (action.type) {
    case 'FETCH_START':
      return {
        ...state,
        loading: true,
        error: null,
      }
    case 'FETCH_SUCCESS':
      return {
        ...state,
        loading: false,
        error: null,
        systemStatus: action.payload.systemStatus,
        dashboardData: action.payload.dashboardData,
        bettingOpportunities: action.payload.bettingOpportunities,
        lastUpdate: new Date(),
      }
    case 'FETCH_ERROR':
      return {
        ...state,
        loading: false,
        error: action.payload,
      }
    case 'SET_TAB':
      return {
        ...state,
        currentTab: action.payload,
      }
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      }
    default:
      return state
  }
}

// Context
interface DashboardContextType {
  state: DashboardState
  dispatch: React.Dispatch<DashboardAction>
  fetchData: () => Promise<void>
  setCurrentTab: (tab: number) => void
  clearError: () => void
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

// Provider
interface DashboardProviderProps {
  children: ReactNode
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(dashboardReducer, initialState)

  const fetchData = async () => {
    dispatch({ type: 'FETCH_START' })
    
    try {
      // Simulated API calls - replace with actual API implementation
      const [statusResponse, dashboardResponse, bettingResponse] = await Promise.all([
        fetch('/api/system_status').then(res => res.json()),
        fetch('/api/dashboard_data').then(res => res.json()),
        fetch('/api/betting_opportunities').then(res => res.json()),
      ])

      dispatch({
        type: 'FETCH_SUCCESS',
        payload: {
          systemStatus: statusResponse,
          dashboardData: dashboardResponse,
          bettingOpportunities: bettingResponse,
        },
      })
    } catch (error) {
      dispatch({
        type: 'FETCH_ERROR',
        payload: error instanceof Error ? error.message : 'Failed to fetch data',
      })
    }
  }

  const setCurrentTab = (tab: number) => {
    dispatch({ type: 'SET_TAB', payload: tab })
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  // Auto-refresh every 30 seconds
  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const contextValue: DashboardContextType = {
    state,
    dispatch,
    fetchData,
    setCurrentTab,
    clearError,
  }

  return (
    <DashboardContext.Provider value={contextValue}>
      {children}
    </DashboardContext.Provider>
  )
}

// Hook to use dashboard context
export const useDashboard = (): DashboardContextType => {
  const context = useContext(DashboardContext)
  if (context === undefined) {
    throw new Error('useDashboard must be used within a DashboardProvider')
  }
  return context
}

// Helper hooks for specific data
export const useSystemStatus = () => {
  const { state } = useDashboard()
  return state.systemStatus
}

export const useDashboardData = () => {
  const { state } = useDashboard()
  return state.dashboardData
}

export const useBettingOpportunities = () => {
  const { state } = useDashboard()
  return state.bettingOpportunities
}

export const useLoadingState = () => {
  const { state } = useDashboard()
  return state.loading
}

export const useErrorState = () => {
  const { state, clearError } = useDashboard()
  return { error: state.error, clearError }
}
