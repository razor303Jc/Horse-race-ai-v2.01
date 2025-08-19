/**
 * API Service for Horse Racing AI Frontend
 * 
 * This service handles all API calls to replace mock data in React components
 * with real backend integration.
 */

// API Base URL - adjust based on your deployment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// API Response Types
export interface BettingRecommendation {
  horse_name: string;
  confidence: number;
  current_odds: number;
  value: number;
  stake_recommendation: number;
  recommended_action: string;
  race_id?: string;
  race_time?: string;
  venue?: string;
}

export interface PaperBet {
  bet_id: string;
  horse_name: string;
  stake: number;
  odds: number;
  status: string;
  pnl: number;
  timestamp: string;
}

export interface BettingPerformance {
  account_balance: number;
  daily_pnl: number;
  win_rate: number;
  roi: number;
  total_bets: number;
  active_bets: number;
  recent_performance?: Array<{
    date: string;
    pnl: number;
  }>;
}

export interface Race {
  race_id: string;
  meeting: string;
  race_number: number;
  time: string;
  race_name: string;
  class: string;
  distance: string;
  distance_meters: number;
  going: string;
  prize_money: number;
  field_size: number;
  age_restriction: string;
  race_type: string;
  surface: string;
  quality_rating: string;
  predicted_competitiveness: number;
  betting_volume: number;
  favorite: {
    horse: string;
    odds: number;
    probability: number;
  };
  race_insights: string[];
}

export interface DailyRacesData {
  total_races: number;
  total_meetings: number;
  daily_stats: {
    total_prize_money: number;
    group_races: number;
    average_field_size: number;
    handicaps: number;
    maiden_races: number;
    chase_hurdle_races: number;
    quality_distribution: Record<string, number>;
  };
  races: Race[];
}

export interface Horse {
  horse_name: string;
  jockey_name: string;
  trainer_name: string;
  age: number;
  weight_kg: number;
  win_odds: number;
  win_probability?: number;
  career_record: string;
  recent_form?: string;
  position?: number;
  silk_colors?: string;
}

export interface RaceCard {
  race_id: string;
  race_name: string;
  venue: string;
  time: string;
  distance: string;
  class: number;
  going: string;
  prize_money: number;
  field_size: number;
  horses: Horse[];
}

export interface RaceCardsData {
  total_races: number;
  total_horses: number;
  data_source: string;
  timestamp: string;
  races: RaceCard[];
}

// Error handling
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

// Generic API call function with error handling
async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    defaultOptions.headers = {
      ...defaultOptions.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  const response = await fetch(url, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new APIError(response.status, `API call failed: ${response.statusText}`);
  }

  return response.json();
}

// API Service Class
export class HorseRacingAPI {
  // Daily Races API
  static async getDailyRaces(): Promise<DailyRacesData> {
    try {
      const data = await apiCall<DailyRacesData>('/daily_races');
      return data;
    } catch (error) {
      console.error('Error fetching daily races:', error);
      // Return fallback data for development
      return this.getFallbackDailyRaces();
    }
  }

  // Real Race Cards API
  static async getRealRaceCards(): Promise<RaceCardsData> {
    try {
      const data = await apiCall<RaceCardsData>('/real_race_cards');
      return data;
    } catch (error) {
      console.error('Error fetching real race cards:', error);
      return this.getFallbackRaceCards();
    }
  }

  // Race Details API
  static async getRaceDetails(raceId: string): Promise<RaceCard> {
    try {
      const data = await apiCall<RaceCard>(`/race_details/${raceId}`);
      return data;
    } catch (error) {
      console.error('Error fetching race details:', error);
      throw error;
    }
  }

  // Betting Recommendations API
  static async getBettingRecommendations(): Promise<BettingRecommendation[]> {
    try {
      const response = await apiCall<{
        status: string;
        recommendations: BettingRecommendation[];
        timestamp: string;
      }>('/betting/recommendations');
      return response.recommendations;
    } catch (error) {
      console.error('Error fetching betting recommendations:', error);
      return this.getFallbackRecommendations();
    }
  }

  // Stage 8 Performance API
  static async getStage8Performance(): Promise<BettingPerformance> {
    try {
      const data = await apiCall<BettingPerformance>('/stage8/performance');
      return data;
    } catch (error) {
      console.error('Error fetching Stage 8 performance:', error);
      return this.getFallbackPerformance();
    }
  }

  // Live Races API
  static async getLiveRaces(): Promise<Race[]> {
    try {
      const response = await apiCall<{
        status: string;
        live_races: Race[];
        timestamp: string;
        total_live: number;
      }>('/races/live');
      return response.live_races;
    } catch (error) {
      console.error('Error fetching live races:', error);
      return [];
    }
  }

  // Fallback data methods for development/offline mode
  private static getFallbackDailyRaces(): DailyRacesData {
    return {
      total_races: 45,
      total_meetings: 8,
      daily_stats: {
        total_prize_money: 2450000,
        group_races: 3,
        average_field_size: 12.5,
        handicaps: 18,
        maiden_races: 8,
        chase_hurdle_races: 12,
        quality_distribution: {
          "A+": 3, "A": 8, "A-": 12, "B+": 15, "B": 7
        }
      },
      races: [
        {
          race_id: "daily_001",
          meeting: "Cheltenham",
          race_number: 1,
          time: "13:30",
          race_name: "Maiden Hurdle",
          class: "4",
          distance: "2m",
          distance_meters: 3200,
          going: "Good to Soft",
          prize_money: 15000,
          field_size: 12,
          age_restriction: "4yo+",
          race_type: "Hurdle",
          surface: "Turf",
          quality_rating: "B+",
          predicted_competitiveness: 85.2,
          betting_volume: 125000,
          favorite: {
            horse: "Thunder Strike",
            odds: 3.5,
            probability: 28.6
          },
          race_insights: [
            "Strong field with competitive handicap marks",
            "Weather conditions favor front runners"
          ]
        }
      ]
    };
  }

  private static getFallbackRaceCards(): RaceCardsData {
    return {
      total_races: 32,
      total_horses: 384,
      data_source: "fallback_data",
      timestamp: new Date().toISOString(),
      races: [
        {
          race_id: "real_001",
          race_name: "Class 2 Handicap",
          venue: "Newmarket",
          time: "15:30",
          distance: "1m 2f",
          class: 2,
          going: "Good",
          prize_money: 35000,
          field_size: 14,
          horses: [
            {
              horse_name: "Thunder Strike",
              jockey_name: "R. Moore",
              trainer_name: "A. O'Brien",
              age: 4,
              weight_kg: 59.0,
              win_odds: 3.5,
              win_probability: 28.6,
              career_record: "3-2-1",
              recent_form: "1-2-3",
              position: 1,
              silk_colors: "Blue, white stars"
            }
          ]
        }
      ]
    };
  }

  private static getFallbackRecommendations(): BettingRecommendation[] {
    return [
      {
        horse_name: "Thunder Strike",
        confidence: 0.85,
        current_odds: 3.5,
        value: 0.12,
        stake_recommendation: 8.5,
        recommended_action: "BACK",
        race_id: "rec_001",
        race_time: "15:30",
        venue: "Newmarket"
      },
      {
        horse_name: "Lightning Bolt",
        confidence: 0.78,
        current_odds: 4.2,
        value: 0.08,
        stake_recommendation: 6.2,
        recommended_action: "BACK",
        race_id: "rec_002",
        race_time: "16:05",
        venue: "Cheltenham"
      }
    ];
  }

  private static getFallbackPerformance(): BettingPerformance {
    return {
      account_balance: 1245.67,
      daily_pnl: 45.32,
      win_rate: 72.5,
      roi: 12.8,
      total_bets: 89,
      active_bets: 3,
      recent_performance: [
        { date: "2025-08-19", pnl: 45.32 },
        { date: "2025-08-18", pnl: -12.50 },
        { date: "2025-08-17", pnl: 67.89 }
      ]
    };
  }
}

// React hooks for API integration
export default HorseRacingAPI;
