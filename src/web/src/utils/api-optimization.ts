import React from 'react';
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

interface ApiCacheEntry {
  data: any;
  timestamp: number;
  etag?: string;
  maxAge: number;
}

interface RequestQueueItem {
  config: ExtendedAxiosRequestConfig;
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
  priority: number;
  retries: number;
  timestamp: number;
}

interface RequestMetadata {
  requestId: string;
  startTime: number;
  retryCount?: number;
  skipQueue?: boolean;
}

interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  metadata?: RequestMetadata;
  priority?: number;
}

interface RateLimitConfig {
  maxRequests: number;
  windowMs: number;
  strategy: 'sliding' | 'fixed';
}

interface ApiOptimizationConfig {
  baseURL: string;
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  cacheEnabled?: boolean;
  cacheTTL?: number;
  rateLimiting?: RateLimitConfig;
  compression?: boolean;
  batchRequests?: boolean;
  maxConcurrent?: number;
  requestPriority?: boolean;
}

export class OptimizedApiClient {
  private axiosInstance: AxiosInstance;
  private cache: Map<string, ApiCacheEntry> = new Map();
  private requestQueue: RequestQueueItem[] = [];
  private activeRequests: Set<string> = new Set();
  private rateLimitWindow: number[] = [];
  private isProcessingQueue = false;
  private batchTimer: NodeJS.Timeout | null = null;
  private batchQueue: Map<string, RequestQueueItem[]> = new Map();
  
  private config: Required<ApiOptimizationConfig>;

  constructor(config: ApiOptimizationConfig) {
    this.config = {
      timeout: 10000,
      retryAttempts: 3,
      retryDelay: 1000,
      cacheEnabled: true,
      cacheTTL: 300000, // 5 minutes
      rateLimiting: {
        maxRequests: 100,
        windowMs: 60000, // 1 minute
        strategy: 'sliding'
      },
      compression: true,
      batchRequests: true,
      maxConcurrent: 10,
      requestPriority: true,
      ...config
    };

    this.axiosInstance = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.compression && { 'Accept-Encoding': 'gzip, deflate, br' })
      }
    });

    this.setupInterceptors();
    this.startCacheCleanup();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config: any) => {
        // Add request ID for tracking
        config.metadata = {
          requestId: Date.now().toString(36) + Math.random().toString(36).substr(2),
          startTime: Date.now()
        };

        // Add ETag for cache validation
        const cacheKey = this.getCacheKey(config);
        const cacheEntry = this.cache.get(cacheKey);
        if (cacheEntry?.etag) {
          config.headers['If-None-Match'] = cacheEntry.etag;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => {
        const config = response.config as any;
        const duration = Date.now() - config.metadata.startTime;
        
        console.log(`API Request ${config.metadata.requestId}: ${config.method?.toUpperCase()} ${config.url} - ${response.status} (${duration}ms)`);

        // Cache successful responses
        if (this.config.cacheEnabled && this.shouldCache(response)) {
          this.cacheResponse(response);
        }

        // Remove from active requests
        this.activeRequests.delete(config.metadata.requestId);

        return response;
      },
      async (error: AxiosError) => {
        const config = error.config as any;
        if (config?.metadata) {
          const duration = Date.now() - config.metadata.startTime;
          console.error(`API Request ${config.metadata.requestId} failed: ${error.response?.status} (${duration}ms)`);
          
          // Remove from active requests
          this.activeRequests.delete(config.metadata.requestId);
        }

        // Handle 304 Not Modified
        if (error.response?.status === 304) {
          const cacheKey = this.getCacheKey(config!);
          const cachedResponse = this.cache.get(cacheKey);
          if (cachedResponse) {
            return Promise.resolve({
              ...error.response,
              data: cachedResponse.data,
              status: 200
            });
          }
        }

        // Retry logic
        if (this.shouldRetry(error)) {
          return this.retryRequest(config!);
        }

        return Promise.reject(error);
      }
    );
  }

  private getCacheKey(config: AxiosRequestConfig): string {
    const url = config.url || '';
    const method = config.method || 'GET';
    const params = JSON.stringify(config.params || {});
    const data = config.method === 'GET' ? '' : JSON.stringify(config.data || {});
    
    return `${method}:${url}:${params}:${data}`;
  }

  private shouldCache(response: AxiosResponse): boolean {
    // Only cache GET requests with successful responses
    if (response.config.method !== 'GET' || response.status < 200 || response.status >= 300) {
      return false;
    }

    // Check Cache-Control headers
    const cacheControl = response.headers['cache-control'];
    if (cacheControl?.includes('no-cache') || cacheControl?.includes('no-store')) {
      return false;
    }

    return true;
  }

  private cacheResponse(response: AxiosResponse): void {
    const cacheKey = this.getCacheKey(response.config);
    const etag = response.headers.etag;
    
    // Determine cache TTL from headers or use default
    let maxAge = this.config.cacheTTL;
    const cacheControl = response.headers['cache-control'];
    if (cacheControl) {
      const maxAgeMatch = cacheControl.match(/max-age=(\d+)/);
      if (maxAgeMatch) {
        maxAge = parseInt(maxAgeMatch[1]) * 1000;
      }
    }

    this.cache.set(cacheKey, {
      data: response.data,
      timestamp: Date.now(),
      etag,
      maxAge
    });
  }

  private getCachedResponse(config: AxiosRequestConfig): any | null {
    if (!this.config.cacheEnabled || config.method !== 'GET') {
      return null;
    }

    const cacheKey = this.getCacheKey(config);
    const cacheEntry = this.cache.get(cacheKey);
    
    if (!cacheEntry) {
      return null;
    }

    // Check if cache entry is still valid
    if (Date.now() - cacheEntry.timestamp > cacheEntry.maxAge) {
      this.cache.delete(cacheKey);
      return null;
    }

    return cacheEntry.data;
  }

  private shouldRetry(error: AxiosError): boolean {
    const config = error.config as any;
    if (!config?.metadata) return false;
    
    const retryCount = config.metadata.retryCount || 0;
    if (retryCount >= this.config.retryAttempts) return false;

    // Retry on network errors or 5xx status codes
    return !error.response || (error.response.status >= 500 && error.response.status < 600);
  }

  private async retryRequest(config: any): Promise<AxiosResponse> {
    const retryCount = (config.metadata.retryCount || 0) + 1;
    const delay = this.config.retryDelay * Math.pow(2, retryCount - 1); // Exponential backoff

    console.log(`Retrying request ${config.metadata.requestId} (attempt ${retryCount}/${this.config.retryAttempts}) in ${delay}ms`);

    await new Promise(resolve => setTimeout(resolve, delay));

    config.metadata.retryCount = retryCount;
    return this.axiosInstance.request(config);
  }

  private checkRateLimit(): boolean {
    const now = Date.now();
    const windowStart = now - this.config.rateLimiting.windowMs;

    if (this.config.rateLimiting.strategy === 'sliding') {
      // Remove old entries
      this.rateLimitWindow = this.rateLimitWindow.filter(timestamp => timestamp > windowStart);
    } else {
      // Fixed window - reset if window expired
      if (this.rateLimitWindow.length > 0 && this.rateLimitWindow[0] <= windowStart) {
        this.rateLimitWindow = [];
      }
    }

    return this.rateLimitWindow.length < this.config.rateLimiting.maxRequests;
  }

  private addToRateLimit(): void {
    this.rateLimitWindow.push(Date.now());
  }

  private async processRequestQueue(): Promise<void> {
    if (this.isProcessingQueue) return;
    this.isProcessingQueue = true;

    while (this.requestQueue.length > 0 && this.activeRequests.size < this.config.maxConcurrent) {
      if (!this.checkRateLimit()) {
        // Wait before checking again
        await new Promise(resolve => setTimeout(resolve, 100));
        continue;
      }

      // Sort queue by priority (higher number = higher priority)
      this.requestQueue.sort((a, b) => b.priority - a.priority);
      
      const item = this.requestQueue.shift()!;
      
      // Check if request has expired
      if (Date.now() - item.timestamp > 30000) { // 30 second timeout
        item.reject(new Error('Request timeout in queue'));
        continue;
      }

      this.addToRateLimit();
      if (item.config.metadata) {
        this.activeRequests.add(item.config.metadata.requestId);
      }

      try {
        const response = await this.axiosInstance.request(item.config);
        item.resolve(response);
      } catch (error) {
        item.reject(error);
      }
    }

    this.isProcessingQueue = false;
  }

  private startCacheCleanup(): void {
    setInterval(() => {
      const now = Date.now();
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp > entry.maxAge) {
          this.cache.delete(key);
        }
      }
    }, 60000); // Cleanup every minute
  }

  public async request<T = any>(config: ExtendedAxiosRequestConfig): Promise<AxiosResponse<T>> {
    // Check cache first
    const cachedData = this.getCachedResponse(config);
    if (cachedData) {
      console.log(`Cache hit for ${config.method?.toUpperCase()} ${config.url}`);
      return Promise.resolve({
        data: cachedData,
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      } as AxiosResponse<T>);
    }

    // Add metadata
    const extendedConfig: any = { ...config };
    extendedConfig.metadata = {
      requestId: Date.now().toString(36) + Math.random().toString(36).substr(2),
      startTime: Date.now(),
      retryCount: 0
    };

    // Check if we can make immediate request
    if (this.activeRequests.size < this.config.maxConcurrent && this.checkRateLimit()) {
      this.addToRateLimit();
      this.activeRequests.add(extendedConfig.metadata.requestId);
      
      try {
        return await this.axiosInstance.request<T>(extendedConfig);
      } catch (error) {
        this.activeRequests.delete(extendedConfig.metadata.requestId);
        throw error;
      }
    }

    // Queue the request
    return new Promise<AxiosResponse<T>>((resolve, reject) => {
      this.requestQueue.push({
        config: extendedConfig,
        resolve,
        reject,
        priority: config.priority || 1,
        retries: 0,
        timestamp: Date.now()
      });

      // Start processing queue
      this.processRequestQueue();
    });
  }

  // Convenience methods
  public get<T = any>(url: string, config?: ExtendedAxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  public post<T = any>(url: string, data?: any, config?: ExtendedAxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  public put<T = any>(url: string, data?: any, config?: ExtendedAxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  public delete<T = any>(url: string, config?: ExtendedAxiosRequestConfig): Promise<AxiosResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }

  // Batch requests
  public async batchRequests<T = any>(requests: Array<ExtendedAxiosRequestConfig>): Promise<AxiosResponse<T>[]> {
    const promises = requests.map(config => this.request<T>(config));
    return Promise.all(promises);
  }

  // Clear cache
  public clearCache(pattern?: string): void {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  // Get stats
  public getStats() {
    return {
      cacheSize: this.cache.size,
      queueLength: this.requestQueue.length,
      activeRequests: this.activeRequests.size,
      rateLimitWindow: this.rateLimitWindow.length,
      maxConcurrent: this.config.maxConcurrent
    };
  }

  // Health check
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.axiosInstance.get('/health', { 
        timeout: 5000
      } as any);
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

// React hook for optimized API client
export function useOptimizedApi(config: ApiOptimizationConfig) {
  const [client] = React.useState(() => new OptimizedApiClient(config));
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  const request = React.useCallback(async <T = any>(
    config: ExtendedAxiosRequestConfig
  ): Promise<T> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await client.request<T>(config);
      return response.data;
    } catch (err) {
      const error = err as Error;
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [client]);

  const get = React.useCallback(<T = any>(
    url: string, 
    config?: ExtendedAxiosRequestConfig
  ) => request<T>({ ...config, method: 'GET', url }), [request]);

  const post = React.useCallback(<T = any>(
    url: string, 
    data?: any, 
    config?: ExtendedAxiosRequestConfig
  ) => request<T>({ ...config, method: 'POST', url, data }), [request]);

  return {
    client,
    loading,
    error,
    request,
    get,
    post,
    put: React.useCallback(<T = any>(
      url: string, 
      data?: any, 
      config?: ExtendedAxiosRequestConfig
    ) => request<T>({ ...config, method: 'PUT', url, data }), [request]),
    
    delete: React.useCallback(<T = any>(
      url: string, 
      config?: ExtendedAxiosRequestConfig
    ) => request<T>({ ...config, method: 'DELETE', url }), [request])
  };
}

export default OptimizedApiClient;
