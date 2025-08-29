// Utility functions for performance optimization
// Non-React utilities that can be used across the application

// LRU Cache implementation for data caching
export class LRUCache<K, V> {
  private cache = new Map<K, V>();
  private maxSize: number;

  constructor(maxSize: number) {
    this.maxSize = maxSize;
  }

  get(key: K): V | undefined {
    const value = this.cache.get(key);
    if (value !== undefined) {
      // Move to end (most recently used)
      this.cache.delete(key);
      this.cache.set(key, value);
    }
    return value;
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      // Update existing key
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Remove least recently used
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, value);
  }

  clear(): void {
    this.cache.clear();
  }

  size(): number {
    return this.cache.size;
  }
}

// Global data cache instance
export const dataCache = new LRUCache<string, any>(200);

// Debounce utility function
export function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

// Throttle utility function
export function throttle<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func(...args);
    }
  };
}

// Performance monitoring utilities
export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number[]> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  startTiming(name: string): void {
    const start = performance.now();
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(start);
  }

  endTiming(name: string): number {
    const end = performance.now();
    const starts = this.metrics.get(name);
    if (starts && starts.length > 0) {
      const start = starts.pop()!;
      const duration = end - start;
      console.log(`${name}: ${duration.toFixed(2)}ms`);
      return duration;
    }
    return 0;
  }

  getAverageTime(name: string): number {
    const times = this.metrics.get(name);
    if (!times || times.length === 0) return 0;
    
    const sum = times.reduce((a, b) => a + b, 0);
    return sum / times.length;
  }

  clearMetrics(name?: string): void {
    if (name) {
      this.metrics.delete(name);
    } else {
      this.metrics.clear();
    }
  }
}

// Data sampling for large datasets
export function sampleData<T>(data: T[], sampleSize: number): T[] {
  if (!data?.length) return [];
  
  if (data.length <= sampleSize) {
    return data;
  }
  
  const step = Math.floor(data.length / sampleSize);
  return data.filter((_, index) => index % step === 0);
}

// Memory usage monitoring
export function getMemoryUsage(): {
  used: number;
  total: number;
  percentage: number;
} {
  if ('memory' in performance) {
    const memory = (performance as any).memory;
    return {
      used: memory.usedJSHeapSize,
      total: memory.totalJSHeapSize,
      percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100
    };
  }
  return { used: 0, total: 0, percentage: 0 };
}

// Batch processing utility
export async function batchProcess<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  batchSize = 10,
  delay = 100
): Promise<R[]> {
  const results: R[] = [];
  
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
    
    // Add delay between batches to prevent overwhelming
    if (i + batchSize < items.length && delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  return results;
}

// Request optimization utilities
export interface RequestConfig {
  retries?: number;
  retryDelay?: number;
  timeout?: number;
  cache?: boolean;
  cacheTTL?: number;
}

export class RequestOptimizer {
  private cache = new LRUCache<string, { data: any; timestamp: number }>(100);
  
  async optimizedFetch(
    url: string, 
    options: RequestInit & RequestConfig = {}
  ): Promise<any> {
    const {
      retries = 3,
      retryDelay = 1000,
      timeout = 10000,
      cache = true,
      cacheTTL = 300000, // 5 minutes
      ...fetchOptions
    } = options;

    // Check cache first
    if (cache) {
      const cached = this.cache.get(url);
      if (cached && Date.now() - cached.timestamp < cacheTTL) {
        return cached.data;
      }
    }

    let lastError: Error;
    
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(url, {
          ...fetchOptions,
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Cache successful response
        if (cache) {
          this.cache.set(url, { data, timestamp: Date.now() });
        }
        
        return data;
        
      } catch (error) {
        lastError = error as Error;
        
        // Don't retry on final attempt
        if (attempt < retries) {
          await new Promise(resolve => 
            setTimeout(resolve, retryDelay * Math.pow(2, attempt))
          );
        }
      }
    }
    
    throw lastError!;
  }
  
  clearCache(): void {
    this.cache.clear();
  }
}

export const requestOptimizer = new RequestOptimizer();
