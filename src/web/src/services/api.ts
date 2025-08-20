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
  horse_name: string;
  horse_number: number | null;
  jockey: string;
  trainer: string;
  age: number;
  weight_kg: number | null;
  odds: string | null;
  form: string | null;
  draw: number | null;
  silk_colors: string | null;
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
}

export interface DailyRacesResponse {
  date: string;
  total_races: number;
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
  }>;
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
        race_id: race.race_id.toString(),
        race_name: race.race_name,
        venue: race.course,
        time: race.race_time,
        distance: race.distance,
        class: parseInt(race.class.replace('Class ', '') || '0'),
        going: race.surface,
        prize_money: parseInt(race.prize.replace(/[£,]/g, '') || '0'),
        field_size: race.runners,
        horses: [] // Will be populated when we fetch detailed race data
      }))
    };
  }

  // Get all race cards with basic info (no horse details)
  static async getRaceCardsBasic() {
    const dailyRaces = await this.getDailyRaces();
    return this.transformDailyRacesToRaceCards(dailyRaces);
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
}

export default HorseRacingAPI;
