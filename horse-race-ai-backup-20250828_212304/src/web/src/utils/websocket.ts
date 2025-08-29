import React from 'react';

// WebSocket optimization and management utility
interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  messageQueueSize?: number;
  compression?: boolean;
}

interface WebSocketMessage {
  id: string;
  type: string;
  payload: any;
  timestamp: number;
  priority: 'high' | 'medium' | 'low';
}

export class OptimizedWebSocket {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketConfig>;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatTimeout: NodeJS.Timeout | null = null;
  private messageQueue: WebSocketMessage[] = [];
  private listeners: Map<string, Set<Function>> = new Map();
  private isConnecting = false;
  private lastHeartbeat = 0;
  private connectionId = '';
  
  // Message compression for large payloads
  private compressionEnabled = false;
  private compressionThreshold = 1024; // bytes

  constructor(config: WebSocketConfig) {
    this.config = {
      protocols: [],
      reconnectInterval: 5000,
      maxReconnectAttempts: 10,
      heartbeatInterval: 30000,
      messageQueueSize: 100,
      compression: true,
      ...config
    };
    
    this.compressionEnabled = this.config.compression && 'CompressionStream' in window;
    this.connect();
  }

  private connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    this.connectionId = Date.now().toString(36) + Math.random().toString(36).substr(2);
    
    try {
      // Add connection metadata to URL
      const url = new URL(this.config.url);
      url.searchParams.set('client_id', this.connectionId);
      url.searchParams.set('compression', this.compressionEnabled.toString());
      
      this.ws = new WebSocket(url.toString(), this.config.protocols);
      
      this.ws.addEventListener('open', this.onOpen.bind(this));
      this.ws.addEventListener('message', this.onMessage.bind(this));
      this.ws.addEventListener('close', this.onClose.bind(this));
      this.ws.addEventListener('error', this.onError.bind(this));
      
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  private onOpen(): void {
    console.log('WebSocket connected:', this.connectionId);
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Send queued messages
    this.flushMessageQueue();
    
    // Notify listeners
    this.emit('connected', { connectionId: this.connectionId });
  }

  private async onMessage(event: MessageEvent): Promise<void> {
    try {
      let data = event.data;
      
      // Handle compressed messages
      if (typeof data === 'string' && data.startsWith('compressed:')) {
        data = await this.decompress(data.slice(11));
      }
      
      const message = JSON.parse(data);
      
      // Handle heartbeat responses
      if (message.type === 'heartbeat') {
        this.lastHeartbeat = Date.now();
        return;
      }
      
      // Handle control messages
      if (message.type === 'control') {
        this.handleControlMessage(message);
        return;
      }
      
      // Emit message to listeners
      this.emit(message.type, message.payload);
      this.emit('message', message);
      
    } catch (error) {
      console.error('Failed to process WebSocket message:', error);
    }
  }

  private onClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.ws = null;
    this.isConnecting = false;
    
    // Stop heartbeat
    this.stopHeartbeat();
    
    // Attempt reconnection if not intentional
    if (event.code !== 1000) { // Normal closure
      this.scheduleReconnect();
    }
    
    // Notify listeners
    this.emit('disconnected', { code: event.code, reason: event.reason });
  }

  private onError(error: Event): void {
    console.error('WebSocket error:', error);
    this.emit('error', error);
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('max_reconnects_reached');
      return;
    }
    
    const delay = Math.min(
      this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts),
      30000 // Max 30 seconds
    );
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`);
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.lastHeartbeat = Date.now();
    
    this.heartbeatTimeout = setInterval(() => {
      if (Date.now() - this.lastHeartbeat > this.config.heartbeatInterval * 2) {
        console.warn('Heartbeat timeout, reconnecting...');
        this.disconnect();
        this.connect();
        return;
      }
      
      this.send({
        type: 'heartbeat',
        timestamp: Date.now()
      }, 'high');
      
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimeout) {
      clearInterval(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  private handleControlMessage(message: any): void {
    switch (message.subtype) {
      case 'rate_limit':
        console.warn('Rate limited, reducing message frequency');
        this.emit('rate_limited', message.payload);
        break;
        
      case 'server_overload':
        console.warn('Server overloaded, switching to essential updates only');
        this.emit('server_overload', message.payload);
        break;
        
      case 'maintenance':
        console.info('Server maintenance scheduled');
        this.emit('maintenance', message.payload);
        break;
    }
  }

  private async compress(data: string): Promise<string> {
    if (!this.compressionEnabled || data.length < this.compressionThreshold) {
      return data;
    }
    
    try {
      const stream = new CompressionStream('gzip');
      const writer = stream.writable.getWriter();
      const reader = stream.readable.getReader();
      
      writer.write(new TextEncoder().encode(data));
      writer.close();
      
      const chunks: Uint8Array[] = [];
      let done = false;
      
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) chunks.push(value);
      }
      
      const compressed = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0));
      let offset = 0;
      for (const chunk of chunks) {
        compressed.set(chunk, offset);
        offset += chunk.length;
      }
      
      return 'compressed:' + btoa(String.fromCharCode(...compressed));
    } catch (error) {
      console.warn('Compression failed, sending uncompressed:', error);
      return data;
    }
  }

  private async decompress(data: string): Promise<string> {
    try {
      const compressed = Uint8Array.from(atob(data), c => c.charCodeAt(0));
      const stream = new DecompressionStream('gzip');
      const writer = stream.writable.getWriter();
      const reader = stream.readable.getReader();
      
      writer.write(compressed);
      writer.close();
      
      const chunks: Uint8Array[] = [];
      let done = false;
      
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) chunks.push(value);
      }
      
      const decompressed = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0));
      let offset = 0;
      for (const chunk of chunks) {
        decompressed.set(chunk, offset);
        offset += chunk.length;
      }
      
      return new TextDecoder().decode(decompressed);
    } catch (error) {
      console.error('Decompression failed:', error);
      throw error;
    }
  }

  private flushMessageQueue(): void {
    // Sort by priority: high -> medium -> low
    this.messageQueue.sort((a, b) => {
      const priorities = { high: 3, medium: 2, low: 1 };
      return priorities[b.priority] - priorities[a.priority];
    });
    
    while (this.messageQueue.length > 0 && this.isConnected()) {
      const message = this.messageQueue.shift()!;
      this.sendDirect(message);
    }
  }

  public send(data: any, priority: 'high' | 'medium' | 'low' = 'medium'): void {
    const message: WebSocketMessage = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2),
      type: data.type || 'message',
      payload: data,
      timestamp: Date.now(),
      priority
    };
    
    if (this.isConnected()) {
      this.sendDirect(message);
    } else {
      this.queueMessage(message);
    }
  }

  private async sendDirect(message: WebSocketMessage): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.queueMessage(message);
      return;
    }
    
    try {
      const data = JSON.stringify(message.payload);
      const compressedData = await this.compress(data);
      this.ws.send(compressedData);
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      this.queueMessage(message);
    }
  }

  private queueMessage(message: WebSocketMessage): void {
    // Remove oldest low-priority messages if queue is full
    while (this.messageQueue.length >= this.config.messageQueueSize) {
      const lowPriorityIndex = this.messageQueue.findIndex(m => m.priority === 'low');
      if (lowPriorityIndex !== -1) {
        this.messageQueue.splice(lowPriorityIndex, 1);
      } else {
        this.messageQueue.shift(); // Remove oldest
      }
    }
    
    this.messageQueue.push(message);
  }

  public subscribe(event: string, callback: Function): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    this.listeners.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const eventListeners = this.listeners.get(event);
      if (eventListeners) {
        eventListeners.delete(callback);
        if (eventListeners.size === 0) {
          this.listeners.delete(event);
        }
      }
    };
  }

  private emit(event: string, data?: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }

  public getStats() {
    return {
      connectionId: this.connectionId,
      state: this.getConnectionState(),
      reconnectAttempts: this.reconnectAttempts,
      queuedMessages: this.messageQueue.length,
      lastHeartbeat: this.lastHeartbeat,
      compressionEnabled: this.compressionEnabled
    };
  }

  public disconnect(): void {
    // Clear timeouts
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.stopHeartbeat();
    
    // Close connection
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    // Clear listeners
    this.listeners.clear();
    
    // Clear message queue
    this.messageQueue = [];
    
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }
}

// WebSocket connection pool for managing multiple connections
export class WebSocketPool {
  private connections: Map<string, OptimizedWebSocket> = new Map();
  private defaultConfig: Partial<WebSocketConfig> = {};

  constructor(defaultConfig?: Partial<WebSocketConfig>) {
    this.defaultConfig = defaultConfig || {};
  }

  public createConnection(id: string, config: WebSocketConfig): OptimizedWebSocket {
    if (this.connections.has(id)) {
      console.warn(`Connection ${id} already exists, closing existing connection`);
      this.connections.get(id)!.disconnect();
    }

    const fullConfig = { ...this.defaultConfig, ...config };
    const connection = new OptimizedWebSocket(fullConfig);
    this.connections.set(id, connection);

    return connection;
  }

  public getConnection(id: string): OptimizedWebSocket | undefined {
    return this.connections.get(id);
  }

  public removeConnection(id: string): void {
    const connection = this.connections.get(id);
    if (connection) {
      connection.disconnect();
      this.connections.delete(id);
    }
  }

  public broadcast(message: any, priority?: 'high' | 'medium' | 'low'): void {
    this.connections.forEach(connection => {
      if (connection.isConnected()) {
        connection.send(message, priority);
      }
    });
  }

  public getStats() {
    const stats: any = {};
    this.connections.forEach((connection, id) => {
      stats[id] = connection.getStats();
    });
    return stats;
  }

  public disconnectAll(): void {
    this.connections.forEach(connection => connection.disconnect());
    this.connections.clear();
  }
}

// React hook for optimized WebSocket usage
export function useOptimizedWebSocket(
  url: string, 
  config?: Partial<WebSocketConfig>
) {
  const [socket, setSocket] = React.useState<OptimizedWebSocket | null>(null);
  const [connectionState, setConnectionState] = React.useState<string>('disconnected');
  const [lastMessage, setLastMessage] = React.useState<any>(null);

  React.useEffect(() => {
    const ws = new OptimizedWebSocket({ url, ...config });
    setSocket(ws);

    const unsubscribeConnected = ws.subscribe('connected', () => {
      setConnectionState('connected');
    });

    const unsubscribeDisconnected = ws.subscribe('disconnected', () => {
      setConnectionState('disconnected');
    });

    const unsubscribeMessage = ws.subscribe('message', (message: any) => {
      setLastMessage(message);
    });

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeMessage();
      ws.disconnect();
    };
  }, [url]);

  const sendMessage = React.useCallback((message: any, priority?: 'high' | 'medium' | 'low') => {
    socket?.send(message, priority);
  }, [socket]);

  const subscribe = React.useCallback((event: string, callback: Function) => {
    return socket?.subscribe(event, callback) || (() => {});
  }, [socket]);

  return {
    socket,
    connectionState,
    lastMessage,
    sendMessage,
    subscribe,
    isConnected: connectionState === 'connected'
  };
}

export default OptimizedWebSocket;
