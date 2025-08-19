/**
 * Generic API service hook for HTTP requests
 * Provides a simple interface for making API calls with error handling
 */

import { useCallback } from 'react';

interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
}

interface UseApiServiceReturn {
  get: <T = any>(url: string) => Promise<ApiResponse<T>>;
  post: <T = any>(url: string, data?: any) => Promise<ApiResponse<T>>;
  put: <T = any>(url: string, data?: any) => Promise<ApiResponse<T>>;
  delete: <T = any>(url: string) => Promise<ApiResponse<T>>;
}

export const useApiService = (): UseApiServiceReturn => {
  const baseURL = 'http://localhost:8000';

  const makeRequest = useCallback(async <T = any>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
  ): Promise<ApiResponse<T>> => {
    try {
      const config: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (data && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(data);
      }

      const response = await fetch(`${baseURL}${url}`, config);
      
      let responseData: T;
      try {
        responseData = await response.json();
      } catch {
        responseData = {} as T;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
      };
    } catch (error) {
      console.error(`API ${method} ${url} failed:`, error);
      throw error;
    }
  }, [baseURL]);

  const get = useCallback(<T = any>(url: string) => 
    makeRequest<T>('GET', url), [makeRequest]
  );

  const post = useCallback(<T = any>(url: string, data?: any) => 
    makeRequest<T>('POST', url, data), [makeRequest]
  );

  const put = useCallback(<T = any>(url: string, data?: any) => 
    makeRequest<T>('PUT', url, data), [makeRequest]
  );

  const deleteMethod = useCallback(<T = any>(url: string) => 
    makeRequest<T>('DELETE', url), [makeRequest]
  );

  return {
    get,
    post,
    put,
    delete: deleteMethod,
  };
};
