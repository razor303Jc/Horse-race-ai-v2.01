/**
 * Advanced AI & ML API Service
 * Connects to PostgreSQL database for ML model management
 */

const ML_API_BASE_URL = process.env.REACT_APP_ML_API_URL || 'http://localhost:8001/api/ml';

export interface MLModelConfig {
  id?: string;
  name: string;
  type: 'win_predictor' | 'place_predictor' | 'odds_predictor' | 'ensemble';
  status: 'active' | 'training' | 'inactive' | 'error';
  version: string;
  description: string;
  tier: 'free' | 'premium' | 'professional';
  features: string[];
  hyperparameters: Record<string, any>;
  training_config: {
    batch_size: number;
    learning_rate: number;
    epochs: number;
    validation_split: number;
    early_stopping: boolean;
  };
}

export interface ModelPerformanceMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  sharpe_ratio: number;
  roi: number;
  win_rate: number;
  total_predictions: number;
  correct_predictions: number;
  profit_loss: number;
  max_drawdown: number;
  volatility: number;
  last_updated: string;
}

export interface ABTestConfig {
  name: string;
  model_a_id: string;
  model_b_id: string;
  traffic_split: number;
  duration_days: number;
  success_metric: 'accuracy' | 'roi' | 'sharpe_ratio';
  minimum_sample_size: number;
  confidence_level: number;
}

export interface PremiumModelListing {
  id: string;
  name: string;
  description: string;
  vendor: string;
  tier: 'premium' | 'professional';
  price_per_prediction: number;
  monthly_subscription: number;
  performance_guarantee: ModelPerformanceMetrics;
  specializations: string[];
  track_compatibility: string[];
  weather_optimized: boolean;
  live_updates: boolean;
}

class MLAPIService {
  private baseURL: string;
  private authToken: string | null = null;

  constructor() {
    this.baseURL = ML_API_BASE_URL;
    this.authToken = localStorage.getItem('auth_token');
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`ML API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // ============================================================================
  // MODEL MANAGEMENT
  // ============================================================================

  /**
   * Get all ML models with optional filtering
   */
  async getModels(filters?: {
    status?: string;
    type?: string;
    tier?: string;
    active_only?: boolean;
  }): Promise<MLModelConfig[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/models${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<MLModelConfig[]>(endpoint);
  }

  /**
   * Get detailed information about a specific model
   */
  async getModel(modelId: string): Promise<MLModelConfig> {
    return this.makeRequest<MLModelConfig>(`/models/${modelId}`);
  }

  /**
   * Create a new ML model
   */
  async createModel(config: Omit<MLModelConfig, 'id'>): Promise<MLModelConfig> {
    return this.makeRequest<MLModelConfig>('/models', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  /**
   * Update an existing model configuration
   */
  async updateModel(modelId: string, updates: Partial<MLModelConfig>): Promise<MLModelConfig> {
    return this.makeRequest<MLModelConfig>(`/models/${modelId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a model
   */
  async deleteModel(modelId: string): Promise<void> {
    return this.makeRequest<void>(`/models/${modelId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Start training a model
   */
  async startTraining(modelId: string, config?: {
    force_retrain?: boolean;
    use_latest_data?: boolean;
    notification_email?: string;
  }): Promise<{ task_id: string; estimated_duration: number }> {
    return this.makeRequest<{ task_id: string; estimated_duration: number }>(`/models/${modelId}/train`, {
      method: 'POST',
      body: JSON.stringify(config || {}),
    });
  }

  /**
   * Stop training a model
   */
  async stopTraining(modelId: string): Promise<void> {
    return this.makeRequest<void>(`/models/${modelId}/train`, {
      method: 'DELETE',
    });
  }

  /**
   * Get training status and progress
   */
  async getTrainingStatus(modelId: string): Promise<{
    status: 'training' | 'completed' | 'failed' | 'stopped';
    progress: number;
    current_epoch: number;
    total_epochs: number;
    current_loss: number;
    best_accuracy: number;
    estimated_time_remaining: number;
    logs: string[];
  }> {
    return this.makeRequest(`/models/${modelId}/training-status`);
  }

  // ============================================================================
  // PERFORMANCE MONITORING
  // ============================================================================

  /**
   * Get performance metrics for a model
   */
  async getModelPerformance(
    modelId: string,
    timeRange?: {
      start_date: string;
      end_date: string;
    }
  ): Promise<ModelPerformanceMetrics> {
    const params = new URLSearchParams();
    if (timeRange) {
      params.append('start_date', timeRange.start_date);
      params.append('end_date', timeRange.end_date);
    }
    
    const endpoint = `/models/${modelId}/performance${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<ModelPerformanceMetrics>(endpoint);
  }

  /**
   * Get historical performance data for charts
   */
  async getPerformanceHistory(
    modelId: string,
    metric: 'accuracy' | 'roi' | 'sharpe_ratio' | 'win_rate',
    timeRange: {
      start_date: string;
      end_date: string;
      granularity: 'daily' | 'weekly' | 'monthly';
    }
  ): Promise<Array<{
    date: string;
    value: number;
    predictions_count: number;
  }>> {
    const params = new URLSearchParams({
      metric,
      start_date: timeRange.start_date,
      end_date: timeRange.end_date,
      granularity: timeRange.granularity,
    });
    
    return this.makeRequest(`/models/${modelId}/performance/history?${params.toString()}`);
  }

  /**
   * Compare performance between multiple models
   */
  async compareModels(
    modelIds: string[],
    metrics: string[] = ['accuracy', 'roi', 'sharpe_ratio'],
    timeRange?: {
      start_date: string;
      end_date: string;
    }
  ): Promise<{
    [modelId: string]: {
      [metric: string]: number;
    };
  }> {
    const params = new URLSearchParams();
    modelIds.forEach(id => params.append('model_ids', id));
    metrics.forEach(metric => params.append('metrics', metric));
    
    if (timeRange) {
      params.append('start_date', timeRange.start_date);
      params.append('end_date', timeRange.end_date);
    }
    
    return this.makeRequest(`/models/compare?${params.toString()}`);
  }

  // ============================================================================
  // A/B TESTING
  // ============================================================================

  /**
   * Create a new A/B test
   */
  async createABTest(config: ABTestConfig): Promise<{
    id: string;
    start_date: string;
    end_date: string;
    status: 'scheduled' | 'running' | 'completed';
  }> {
    return this.makeRequest('/ab-tests', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  /**
   * Get all A/B tests
   */
  async getABTests(status?: 'running' | 'completed' | 'scheduled'): Promise<Array<{
    id: string;
    name: string;
    model_a: MLModelConfig;
    model_b: MLModelConfig;
    status: string;
    start_date: string;
    end_date: string;
    current_results: {
      model_a_performance: ModelPerformanceMetrics;
      model_b_performance: ModelPerformanceMetrics;
      statistical_significance: number;
      confidence_level: number;
      recommended_winner: string | null;
    };
  }>> {
    const params = status ? `?status=${status}` : '';
    return this.makeRequest(`/ab-tests${params}`);
  }

  /**
   * Get detailed A/B test results
   */
  async getABTestResults(testId: string): Promise<{
    test_config: ABTestConfig;
    results: {
      model_a: {
        predictions: number;
        performance: ModelPerformanceMetrics;
        daily_metrics: Array<{ date: string; value: number }>;
      };
      model_b: {
        predictions: number;
        performance: ModelPerformanceMetrics;
        daily_metrics: Array<{ date: string; value: number }>;
      };
      statistical_analysis: {
        p_value: number;
        confidence_interval: [number, number];
        effect_size: number;
        power: number;
        recommendation: 'model_a' | 'model_b' | 'no_significant_difference';
      };
    };
  }> {
    return this.makeRequest(`/ab-tests/${testId}/results`);
  }

  /**
   * Stop an A/B test early
   */
  async stopABTest(testId: string): Promise<void> {
    return this.makeRequest(`/ab-tests/${testId}/stop`, {
      method: 'POST',
    });
  }

  // ============================================================================
  // PREMIUM MODEL MARKETPLACE
  // ============================================================================

  /**
   * Get available premium models
   */
  async getPremiumModels(filters?: {
    tier?: 'premium' | 'professional';
    specialization?: string;
    max_price?: number;
    vendor?: string;
  }): Promise<PremiumModelListing[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/marketplace${params.toString() ? `?${params.toString()}` : ''}`;
    return this.makeRequest<PremiumModelListing[]>(endpoint);
  }

  /**
   * Purchase access to a premium model
   */
  async purchasePremiumModel(
    modelId: string,
    plan: 'monthly' | 'yearly' | 'per_prediction'
  ): Promise<{
    subscription_id: string;
    access_expires: string;
    api_key: string;
  }> {
    return this.makeRequest(`/marketplace/${modelId}/purchase`, {
      method: 'POST',
      body: JSON.stringify({ plan }),
    });
  }

  /**
   * Get user's premium model subscriptions
   */
  async getPremiumSubscriptions(): Promise<Array<{
    model: PremiumModelListing;
    subscription_id: string;
    plan: string;
    access_expires: string;
    usage_this_month: number;
    usage_limit: number;
    cost_this_month: number;
  }>> {
    return this.makeRequest('/marketplace/subscriptions');
  }

  // ============================================================================
  // LIVE PREDICTIONS
  // ============================================================================

  /**
   * Get live in-race predictions
   */
  async getLivePredictions(raceId: string): Promise<{
    race_id: string;
    last_updated: string;
    predictions: Array<{
      horse_id: string;
      horse_name: string;
      current_position: number;
      win_probability: number;
      place_probability: number;
      model_confidence: number;
      predicted_finish_time: number;
      model_used: string;
    }>;
    market_analysis: {
      efficiency_score: number;
      arbitrage_opportunities: Array<{
        type: string;
        expected_profit: number;
        confidence: number;
      }>;
    };
  }> {
    return this.makeRequest(`/live-predictions/${raceId}`);
  }

  /**
   * Subscribe to live prediction updates via WebSocket
   */
  subscribeLivePredictions(
    raceId: string,
    onUpdate: (predictions: any) => void,
    onError?: (error: Error) => void
  ): () => void {
    const wsUrl = this.baseURL.replace('http', 'ws') + `/live-predictions/${raceId}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        onError?.(error as Error);
      }
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      onError?.(new Error('WebSocket connection error'));
    };

    ws.onclose = (event) => {
      if (event.code !== 1000) {
        console.warn('WebSocket closed unexpectedly:', event.code, event.reason);
      }
    };

    return () => {
      ws.close();
    };
  }

  // ============================================================================
  // MODEL OPTIMIZATION
  // ============================================================================

  /**
   * Run automated hyperparameter optimization
   */
  async optimizeHyperparameters(
    modelId: string,
    config: {
      optimization_method: 'grid_search' | 'random_search' | 'bayesian';
      parameter_space: Record<string, any>;
      max_trials: number;
      timeout_hours: number;
      objective_metric: 'accuracy' | 'f1_score' | 'roi';
    }
  ): Promise<{
    task_id: string;
    estimated_duration: number;
  }> {
    return this.makeRequest(`/models/${modelId}/optimize`, {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  /**
   * Get optimization results
   */
  async getOptimizationResults(taskId: string): Promise<{
    status: 'running' | 'completed' | 'failed';
    progress: number;
    best_parameters: Record<string, any>;
    best_score: number;
    trial_history: Array<{
      trial_number: number;
      parameters: Record<string, any>;
      score: number;
      duration: number;
    }>;
  }> {
    return this.makeRequest(`/optimization/${taskId}/results`);
  }
}

// Export singleton instance
export const mlAPIService = new MLAPIService();
