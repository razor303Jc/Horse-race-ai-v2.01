import React, { memo, useMemo, useCallback, Suspense, lazy, useState, useEffect } from 'react';
import { CircularProgress, Box } from '@mui/material';
import { debounce, sampleData, PerformanceMonitor } from './performanceUtils';

// Lazy load heavy components for code splitting
const AdvancedBettingDashboard = lazy(() => import('../components/betting/AdvancedBettingDashboard'));
const AdvancedAnalyticsDashboard = lazy(() => import('../components/analytics/AdvancedAnalyticsDashboard'));
const UserManagementDashboard = lazy(() => import('../components/user/UserManagementDashboard'));
const PersonalizationEngine = lazy(() => import('../components/user/PersonalizationEngine'));

// Performance optimized loading component
const LoadingFallback = memo(() => (
  <Box 
    display="flex" 
    justifyContent="center" 
    alignItems="center" 
    minHeight="400px"
  >
    <CircularProgress size={40} />
  </Box>
));

LoadingFallback.displayName = 'LoadingFallback';

// HOC for lazy loading with performance optimizations
export const LazyComponentWrapper: React.FC<{ 
  component: React.ComponentType;
  fallback?: React.ComponentType;
}> = ({ component: Component, fallback: Fallback }) => {
  return (
    <Suspense fallback={Fallback ? <Fallback /> : <LoadingFallback />}>
      <Component />
    </Suspense>
  );
};// Performance optimized components
// Export optimized components directly
export const OptimizedBettingDashboard = AdvancedBettingDashboard;
export const OptimizedAnalyticsDashboard = AdvancedAnalyticsDashboard;
export const OptimizedUserDashboard = UserManagementDashboard;
export const OptimizedPersonalizationEngine = PersonalizationEngine;

// Memoized data processors for heavy calculations
export const useOptimizedCalculations = () => {
  // Memoize expensive calculations
  const calculatePortfolioMetrics = useCallback((data: any[]) => {
    return useMemo(() => {
      if (!data?.length) return { totalValue: 0, totalPL: 0, roi: 0 };
      
      const totalValue = data.reduce((sum, item) => sum + (item.value || 0), 0);
      const totalPL = data.reduce((sum, item) => sum + (item.pl || 0), 0);
      const roi = totalValue > 0 ? (totalPL / totalValue) * 100 : 0;
      
      return { totalValue, totalPL, roi };
    }, [data]);
  }, []);

  const calculateRiskMetrics = useCallback((positions: any[]) => {
    return useMemo(() => {
      if (!positions?.length) return { var: 0, sharpeRatio: 0, maxDrawdown: 0 };
      
      // VaR calculation (simplified)
      const returns = positions.map(p => p.return || 0).sort((a, b) => a - b);
      const var95 = returns[Math.floor(returns.length * 0.05)] || 0;
      
      // Sharpe ratio calculation
      const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
      const sharpeRatio = variance > 0 ? avgReturn / Math.sqrt(variance) : 0;
      
      // Max drawdown
      let peak = 0;
      let maxDrawdown = 0;
      positions.forEach(pos => {
        const value = pos.cumulativeValue || 0;
        if (value > peak) peak = value;
        const drawdown = (peak - value) / peak;
        if (drawdown > maxDrawdown) maxDrawdown = drawdown;
      });
      
      return { var: var95, sharpeRatio, maxDrawdown: maxDrawdown * 100 };
    }, [positions]);
  }, []);

  return { calculatePortfolioMetrics, calculateRiskMetrics };
};

// Virtual scrolling for large datasets
export const VirtualizedList = memo<{
  items: any[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: any, index: number) => React.ReactNode;
}>(({ items, itemHeight, containerHeight, renderItem }) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );
    
    return items.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight
    }));
  }, [items, scrollTop, itemHeight, containerHeight]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, top }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top,
              left: 0,
              right: 0,
              height: itemHeight
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
});

VirtualizedList.displayName = 'VirtualizedList';

// Debounced input for performance
export function useDebouncedValue<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Performance monitoring hook
export const usePerformanceMonitor = (componentName: string) => {
  React.useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      if (renderTime > 16) { // More than one frame (60fps)
        console.warn(`${componentName} render took ${renderTime.toFixed(2)}ms`);
      }
      
      // Send to analytics in production
      if (process.env.NODE_ENV === 'production') {
        // analytics.track('component_performance', {
        //   component: componentName,
        //   renderTime
        // });
      }
    };
  });
};

// Memory efficient data cache
class LRUCache<K, V> {
  private cache = new Map<K, V>();
  private maxSize: number;

  constructor(maxSize = 100) {
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
      // Update existing
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
}

// Global data cache instance
export const dataCache = new LRUCache<string, any>(200);

// Cached API service wrapper
export function useCachedApiCall<T>(
  apiCall: () => Promise<T>,
  cacheKey: string,
  dependencies: any[] = [],
  cacheTTL = 5 * 60 * 1000 // 5 minutes
): { data: T | null; loading: boolean; error: Error | null; refetch: () => void; invalidateCache: () => void } {
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    // Check cache first
    const cacheEntry = dataCache.get(cacheKey);
    if (cacheEntry && Date.now() - cacheEntry.timestamp < cacheTTL) {
      setData(cacheEntry.data);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      
      // Cache the result
      dataCache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });
      
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [apiCall, cacheKey, cacheTTL]);

  React.useEffect(() => {
    fetchData();
  }, [fetchData, ...dependencies]);

  const invalidateCache = useCallback(() => {
    dataCache.set(cacheKey, null);
    fetchData();
  }, [cacheKey, fetchData]);

  return { data, loading, error, refetch: fetchData, invalidateCache };
};

// Optimized chart data processor
export const useOptimizedChartData = (rawData: any[], sampleSize = 100) => {
  return useMemo(() => {
    if (!rawData?.length) return [];
    
    if (rawData.length <= sampleSize) {
      return rawData;
    }
    
    // Downsample data for performance
    const step = Math.floor(rawData.length / sampleSize);
    return rawData.filter((_, index) => index % step === 0);
  }, [rawData, sampleSize]);
};

export default {
  useOptimizedCalculations,
  VirtualizedList,
  useDebouncedValue,
  usePerformanceMonitor,
  dataCache,
  useCachedApiCall,
  useOptimizedChartData
};
