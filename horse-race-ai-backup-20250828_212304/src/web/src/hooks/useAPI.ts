/**
 * React hooks for Horse Racing AI API integration
 *       const cardsData = await HorseRacingAPI.getRaceCards();
      setData(cardsData);* These hooks provide state management and caching for API calls,
 * replacing mock data with real backend integration.
 */

import { useState, useEffect, useCallback } from 'react';
import HorseRacingAPI, {
  DailyRacesData,
  RaceCardsData,
  RaceCard,
  BettingRecommendation,
  BettingPerformance,
  Race
} from '../services/api';

// Hook for Daily Races data
export const useDailyRaces = () => {
  const [data, setData] = useState<DailyRacesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDailyRaces = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const racesData = await HorseRacingAPI.getDailyRaces();
      setData(racesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch daily races');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDailyRaces();
  }, [fetchDailyRaces]);

  return {
    data,
    loading,
    error,
    refetch: fetchDailyRaces
  };
};

// Hook for Real Race Cards data
export const useRealRaceCards = () => {
  const [data, setData] = useState<RaceCardsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRaceCards = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const cardsData = await HorseRacingAPI.getRealRaceCards();
      setData(cardsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch race cards');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRaceCards();
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchRaceCards, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchRaceCards]);

  return {
    data,
    loading,
    error,
    refetch: fetchRaceCards
  };
};

// Hook for individual Race Card details
export const useRaceCard = (raceId: string | null) => {
  const [data, setData] = useState<RaceCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRaceCard = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      const cardData = await HorseRacingAPI.getRaceDetails(parseInt(id));
      setData(cardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch race card');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (raceId) {
      fetchRaceCard(raceId);
    } else {
      setData(null);
      setError(null);
    }
  }, [raceId, fetchRaceCard]);

  return {
    data,
    loading,
    error,
    fetchRaceCard
  };
};

// Hook for Betting Recommendations
export const useBettingRecommendations = () => {
  const [recommendations, setRecommendations] = useState<BettingRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await HorseRacingAPI.getBettingRecommendations();
      setRecommendations(data.filter((r: BettingRecommendation) => r.recommended_action !== 'SKIP'));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
    // Auto-refresh every 30 seconds for live recommendations
    const interval = setInterval(fetchRecommendations, 30 * 1000);
    return () => clearInterval(interval);
  }, [fetchRecommendations]);

  return {
    recommendations,
    loading,
    error,
    refetch: fetchRecommendations
  };
};

// Hook for Stage 8 Performance data
export const useStage8Performance = () => {
  const [performance, setPerformance] = useState<BettingPerformance>({
    total_bets: 0,
    winning_bets: 0,
    total_stake: 0,
    total_return: 0,
    profit_loss: 0,
    roi: 0,
    win_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformance = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await HorseRacingAPI.getStage8Performance();
      setPerformance({
        total_bets: data.total_bets || 0,
        winning_bets: Math.round((data.win_rate || 0) * (data.total_bets || 0) / 100),
        total_stake: data.account_balance || 0,
        total_return: (data.account_balance || 0) + (data.daily_pnl || 0),
        profit_loss: data.daily_pnl || 0,
        roi: data.roi || 0,
        win_rate: data.win_rate || 0,
        // Add the additional properties for components
        account_balance: data.account_balance || 1000,
        daily_pnl: data.daily_pnl || 0,
        active_bets: data.active_bets || 0,
        recent_performance: (data as any).recent_performance || []
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch performance data');
      // Keep using fallback data on error
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPerformance();
    // Auto-refresh every 30 seconds for live performance tracking
    const interval = setInterval(fetchPerformance, 30 * 1000);
    return () => clearInterval(interval);
  }, [fetchPerformance]);

  return {
    performance,
    loading,
    error,
    refetch: fetchPerformance
  };
};

// Hook for Live Races
export const useLiveRaces = () => {
  const [liveRaces, setLiveRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLiveRaces = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await HorseRacingAPI.getLiveRaces();
      setLiveRaces(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch live races');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLiveRaces();
    // Auto-refresh every 10 seconds for live race updates
    const interval = setInterval(fetchLiveRaces, 10 * 1000);
    return () => clearInterval(interval);
  }, [fetchLiveRaces]);

  return {
    liveRaces,
    loading,
    error,
    refetch: fetchLiveRaces
  };
};

// Combined hook for Dashboard data
export const useDashboardData = () => {
  const dailyRaces = useDailyRaces();
  const performance = useStage8Performance();
  const recommendations = useBettingRecommendations();
  const liveRaces = useLiveRaces();

  const loading = dailyRaces.loading || performance.loading || 
                 recommendations.loading || liveRaces.loading;

  const error = dailyRaces.error || performance.error || 
               recommendations.error || liveRaces.error;

  const refetchAll = useCallback(() => {
    dailyRaces.refetch();
    performance.refetch();
    recommendations.refetch();
    liveRaces.refetch();
  }, [dailyRaces.refetch, performance.refetch, recommendations.refetch, liveRaces.refetch]);

  return {
    dailyRaces: dailyRaces.data,
    performance: performance.performance,
    recommendations: recommendations.recommendations,
    liveRaces: liveRaces.liveRaces,
    loading,
    error,
    refetchAll
  };
};

// WebSocket hook for real-time updates
export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const wsUrl = url.startsWith('ws') ? url : `ws://localhost:8000${url}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnected(true);
      setError(null);
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (event) => {
      setError('WebSocket connection error');
      console.error('WebSocket error:', event);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message: object) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, connected]);

  return {
    socket,
    connected,
    error,
    sendMessage
  };
};

// API status hook for health checking
export const useAPIStatus = () => {
  const [status, setStatus] = useState<'healthy' | 'error' | 'unknown'>('unknown');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkAPIStatus = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}/health`);
      if (response.ok) {
        setStatus('healthy');
      } else {
        setStatus('error');
      }
    } catch (error) {
      setStatus('error');
    }
    setLastChecked(new Date());
  }, []);

  useEffect(() => {
    checkAPIStatus();
    // Check API status every 60 seconds
    const interval = setInterval(checkAPIStatus, 60 * 1000);
    return () => clearInterval(interval);
  }, [checkAPIStatus]);

  return {
    status,
    lastChecked,
    checkAPIStatus
  };
};
