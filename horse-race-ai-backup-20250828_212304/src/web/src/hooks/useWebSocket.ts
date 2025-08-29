import { useEffect, useRef, useState, useCallback } from 'react';

interface UseWebSocketOptions {
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: string) => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  lastMessage: string | null;
  sendMessage: (message: string) => void;
  reconnect: () => void;
  disconnect: () => void;
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error';
}

export const useWebSocket = (
  url: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    enabled = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError,
    onMessage,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected');
  
  const websocket = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const messageQueue = useRef<string[]>([]);

  const connect = useCallback(() => {
    if (!enabled || websocket.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    setIsConnecting(true);
    setConnectionStatus('connecting');

    try {
      websocket.current = new WebSocket(url);

      websocket.current.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
        
        // Send queued messages
        while (messageQueue.current.length > 0) {
          const message = messageQueue.current.shift();
          if (message && websocket.current?.readyState === WebSocket.OPEN) {
            websocket.current.send(message);
          }
        }

        onOpen?.();
      };

      websocket.current.onclose = () => {
        setIsConnected(false);
        setIsConnecting(false);
        setConnectionStatus('disconnected');
        onClose?.();

        // Auto-reconnect if enabled and under max attempts
        if (enabled && reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      websocket.current.onerror = (error) => {
        setIsConnecting(false);
        setConnectionStatus('error');
        onError?.(error);
      };

      websocket.current.onmessage = (event) => {
        setLastMessage(event.data);
        onMessage?.(event.data);
      };
    } catch (error) {
      setIsConnecting(false);
      setConnectionStatus('error');
      console.error('WebSocket connection error:', error);
    }
  }, [url, enabled, onOpen, onClose, onError, onMessage, reconnectInterval, maxReconnectAttempts]);

  const sendMessage = useCallback((message: string) => {
    if (websocket.current?.readyState === WebSocket.OPEN) {
      websocket.current.send(message);
    } else {
      // Queue message if not connected
      messageQueue.current.push(message);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (websocket.current) {
      websocket.current.close();
      websocket.current = null;
    }
    
    setIsConnected(false);
    setIsConnecting(false);
    setConnectionStatus('disconnected');
    reconnectAttempts.current = 0;
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  // Connect on mount and when enabled changes
  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isConnecting,
    lastMessage,
    sendMessage,
    reconnect,
    disconnect,
    connectionStatus,
  };
};
