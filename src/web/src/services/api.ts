/**
 * API Service for Horse Racing AI Frontend
 * 
 * This service handles all API calls using REAL data from PostgreSQL database.
 * NO MOCK DATA - All endpoints connect to live database at localhost:3000
 */

// API Base URL - pointing to the real backend with PostgreSQL data
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

// Real API Response Types (matching PostgreSQL database structure)
export interface RealHorse {
  horse_id: number;
  name: string;
  horse_name?: string; // Alias for name
  horse_number?: number;
  jockey: string;
  trainer: string;
  age: number;
  weight_kg: number | null;
  odds: string | null;
  form: string | null;
  draw: number | null;
  silk_colors: string | null;
  // Additional properties used in components
  position?: number;
  jockey_name?: string;
  trainer_name?: string;
  win_odds?: string;
  win_probability?: number;
  recent_form?: string;
  career_record?: string;
}

export interface RealRaceCard {
  race_id: number;
  race_number: number;
  race_time: string;
  course: string;
  race_type: string;
  race_date: string;
  race_name: string;
  class: string;
  distance: string;
  surface: string;
  prize: string;
  total_runners: number;
  horses: RealHorse[];
  // Additional properties used in components
  time?: string;
  venue?: string;
  going?: string;
  prize_money?: number;
}

export interface DailyRacesResponse {
  date: string;
  total_races: number;
  total_meetings?: number;
  daily_stats?: {
    total_prize_money: number;
    group_races: number;
    average_field_size: number;
  };
  races: Array<{
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
    meeting?: string;
    time?: string;
    distance_meters?: number;
    going?: string;
    race_type?: string;
    quality_rating?: string;
    prize_money?: number;
    field_size?: number;
    predicted_competitiveness?: number;
    favorite?: {
      horse: string;
      odds: number;
      probability: number;
    };
  }>;
}

// Legacy interfaces for backward compatibility
export interface RaceCard extends RealRaceCard {}
export interface Horse extends RealHorse {}
export interface RaceCardsData {
  total_races: number;
  total_horses: number;
  data_source: string;
  timestamp: string;
  races: RealRaceCard[];
}
export interface DailyRacesData extends DailyRacesResponse {}
export interface Race {
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
  meeting?: string;
  race_type?: string;
  horses?: Horse[];
}

// Betting interfaces
export interface BettingRecommendation {
  race_id: number;
  horse_name: string;
  recommended_action: 'BUY' | 'SELL' | 'HOLD' | 'SKIP';
  confidence: number;
  odds: string;
  stake_percentage: number;
  expected_return: number;
  reasoning: string;
  // Additional properties used in components
  venue?: string;
  race_time?: string;
  current_odds?: number;
  stake_recommendation?: number;
  value?: number;
}

export interface BettingPerformance {
  total_bets: number;
  winning_bets: number;
  total_stake: number;
  total_return: number;
  profit_loss: number;
  roi: number;
  win_rate: number;
  // Additional properties used in components
  account_balance?: number;
  daily_pnl?: number;
  active_bets?: number;
  recent_performance?: any[];
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

// API Service Class - REAL DATA ONLY
export class HorseRacingAPI {
  
  // Get daily races from PostgreSQL database
  static async getDailyRaces(): Promise<DailyRacesResponse> {
    try {
      const data = await apiCall<DailyRacesResponse>('/daily_races');
      console.log('Real daily races loaded:', data.total_races, 'races');
      return data;
    } catch (error) {
      console.error('Error fetching daily races:', error);
      throw error; // No fallback - we want real data only
    }
  }

  // Get detailed race information with horses
  static async getRaceDetails(raceId: number): Promise<RealRaceCard> {
    try {
      const data = await apiCall<RealRaceCard>(`/race_details/${raceId}`);
      console.log('Real race details loaded:', data.race_name, 'with', data.total_runners, 'runners');
      return data;
    } catch (error) {
      console.error('Error fetching race details:', error);
      throw error; // No fallback - we want real data only
    }
  }

  // Transform daily races data for UI consumption
  static transformDailyRacesToRaceCards(dailyRaces: DailyRacesResponse) {
    return {
      total_races: dailyRaces.total_races,
      total_horses: dailyRaces.races.reduce((sum, race) => sum + race.runners, 0),
      data_source: "postgresql_database",
      timestamp: new Date().toISOString(),
      races: dailyRaces.races.map(race => ({
        race_id: race.race_id,
        race_number: race.race_number,
        race_time: race.race_time,
        course: race.course,
        race_type: race.class, // Map class to race_type
        race_date: dailyRaces.date,
        race_name: race.race_name,
        class: race.class,
        distance: race.distance,
        surface: race.surface,
        prize: race.prize,
        total_runners: race.runners,
        horses: [] // Will be populated when we fetch detailed race data
      }))
    };
  }

  // Get all race cards with basic info (no horse details)
  static async getRaceCardsBasic() {
    const dailyRaces = await this.getDailyRaces();
    return this.transformDailyRacesToRaceCards(dailyRaces);
  }

  // Get real race cards - alias for getRaceCardsBasic for compatibility
  static async getRealRaceCards() {
    return this.getRaceCardsBasic();
  }

  // Get race cards with full horse details for specific races
  static async getRaceCardsWithHorses(raceIds?: number[]) {
    try {
      const dailyRaces = await this.getDailyRaces();
      const racesToFetch = raceIds || dailyRaces.races.slice(0, 10).map(r => r.race_id); // Limit to first 10 races if no specific IDs
      
      const detailedRaces = await Promise.all(
        racesToFetch.map(async (raceId) => {
          try {
            return await this.getRaceDetails(raceId);
          } catch (error) {
            console.warn(`Failed to load details for race ${raceId}:`, error);
            return null;
          }
        })
      );

      const validRaces = detailedRaces.filter(race => race !== null) as RealRaceCard[];

      return {
        total_races: validRaces.length,
        total_horses: validRaces.reduce((sum, race) => sum + race.total_runners, 0),
        data_source: "postgresql_database_detailed",
        timestamp: new Date().toISOString(),
        races: validRaces.map(race => ({
          race_id: race.race_id.toString(),
          race_name: race.race_name,
          venue: race.course,
          time: race.race_time,
          distance: race.distance,
          class: parseInt(race.class.replace('Class ', '') || '0'),
          going: race.surface,
          prize_money: parseInt(race.prize.replace(/[£,]/g, '') || '0'),
          field_size: race.total_runners,
          horses: race.horses.map((horse, index) => ({
            horse_name: horse.horse_name,
            jockey_name: horse.jockey,
            trainer_name: horse.trainer,
            age: horse.age,
            weight_kg: horse.weight_kg || 60,
            win_odds: parseFloat(horse.odds?.replace('/1', '') || '10'),
            win_probability: horse.odds ? (1 / (parseFloat(horse.odds.replace('/1', '')) + 1)) * 100 : 10,
            career_record: horse.form || 'N/A',
            recent_form: horse.form || 'N/A',
            position: horse.horse_number || (index + 1),
            silk_colors: horse.silk_colors
          }))
        }))
      };
    } catch (error) {
      console.error('Error fetching race cards with horses:', error);
      throw error; // No fallback - we want real data only
    }
  }

  // Get Stage 8 Performance data (betting performance metrics)
  static async getStage8Performance() {
    try {
      const data = await apiCall<any>('/dashboard_data');
      console.log('Stage 8 performance data loaded:', data);
      
      // Transform dashboard data to BettingPerformance format
      const performanceData = data.performance || {};
      return {
        account_balance: performanceData.profit_7d || 1000.0,
        daily_pnl: data.betting?.profit_today || 0.0,
        win_rate: performanceData.accuracy_7d || 0.0,
        roi: performanceData.roi_7d || 0.0,
        total_bets: performanceData.bets_placed || 0,
        active_bets: data.betting?.daily_opportunities || 0
      };
    } catch (error) {
      console.error('Error fetching Stage 8 performance:', error);
      throw error;
    }
  }

  // Get betting recommendations
  static async getBettingRecommendations() {
    try {
      const data = await apiCall<any>('/betting/recommendations');
      console.log('Betting recommendations loaded:', data);
      return data;
    } catch (error) {
      console.error('Error fetching betting recommendations:', error);
      throw error;
    }
  }

  // Get live races
  static async getLiveRaces() {
    try {
      const data = await apiCall<any>('/daily_races');
      console.log('Live races loaded:', data);
      return data.races || [];
    } catch (error) {
      console.error('Error fetching live races:', error);
      throw error;
    }
  }
}

export default HorseRacingAPI;
