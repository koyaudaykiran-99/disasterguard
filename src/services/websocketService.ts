import { DomainEvent, RealTimeEventType, ConnectionStatus } from '../types/realtime';

type EventHandler<T = any> = (event: DomainEvent<T>) => void;
type StatusHandler = (status: ConnectionStatus) => void;
type ReconnectHandler = () => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private status: ConnectionStatus = 'OFFLINE';
  private eventHandlers: Map<string, Set<EventHandler>> = new Map();
  private statusHandlers: Set<StatusHandler> = new Set();
  private reconnectHandlers: Set<ReconnectHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectDelay = 16000;
  private reconnectTimer: any = null;
  private pingTimer: any = null;
  private explicitDisconnect = false;

  constructor() {
    // Lazy initialized when connect() is called
  }

  private getWsUrl(): string {
    const wsUrl = import.meta.env.VITE_WS_URL;
    if (wsUrl) {
      return wsUrl;
    }
    const envUrl = import.meta.env.VITE_API_URL;
    if (envUrl) {
      const clean = envUrl.replace(/\/$/, '').replace(/^http/, 'ws');
      return `${clean}/api/v1/ws`;
    }
    const loc = window.location;
    const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = loc.hostname || 'localhost';
    // Default to port 8000 for direct local development, or proxy through current host for tunnels & remote access
    if (loc.port === '3000' && (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1')) {
      return `${proto}//${host}:8000/api/v1/ws`;
    }
    return `${proto}//${loc.host}/api/v1/ws`;
  }

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.explicitDisconnect = false;
    this.updateStatus(this.reconnectAttempts === 0 ? 'RECONNECTING' : 'RECONNECTING');

    try {
      const url = this.getWsUrl();
      console.log(`[WebSocket] Connecting to: ${url}`);
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('[WebSocket] Real-time connection established');
        const wasReconnecting = this.reconnectAttempts > 0;
        this.reconnectAttempts = 0;
        this.updateStatus('LIVE');
        this.startHeartbeat();

        if (wasReconnecting) {
          this.reconnectHandlers.forEach((handler) => {
            try {
              handler();
            } catch (err) {
              console.warn('[WebSocket] Error in reconnect handler:', err);
            }
          });
        }
      };

      this.ws.onmessage = (messageEvent) => {
        try {
          if (messageEvent.data === 'pong') return;
          const domainEvent: DomainEvent = JSON.parse(messageEvent.data);
          this.dispatch(domainEvent);
        } catch (err) {
          console.warn('[WebSocket] Failed to parse message:', messageEvent.data, err);
        }
      };

      this.ws.onerror = (error) => {
        console.warn('[WebSocket] Connection error:', error);
      };

      this.ws.onclose = (closeEvent) => {
        console.warn(`[WebSocket] Closed (code: ${closeEvent.code}). Explicit: ${this.explicitDisconnect}`);
        this.stopHeartbeat();
        this.ws = null;

        if (!this.explicitDisconnect) {
          this.scheduleReconnect();
        } else {
          this.updateStatus('OFFLINE');
        }
      };
    } catch (err) {
      console.warn('[WebSocket] Connection exception:', err);
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.explicitDisconnect = true;
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.updateStatus('OFFLINE');
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s (max)
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
    this.updateStatus(this.reconnectAttempts >= 5 ? 'OFFLINE' : 'RECONNECTING');

    console.log(`[WebSocket] Scheduling reconnect in ${delay}ms (attempt #${this.reconnectAttempts})`);
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, 25000);
  }

  private stopHeartbeat(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private updateStatus(newStatus: ConnectionStatus): void {
    if (this.status !== newStatus) {
      this.status = newStatus;
      this.statusHandlers.forEach((handler) => {
        try {
          handler(newStatus);
        } catch (err) {
          console.warn('[WebSocket] Error in status handler:', err);
        }
      });
    }
  }

  public getStatus(): ConnectionStatus {
    return this.status;
  }

  public on(event: RealTimeEventType | '*', handler: EventHandler): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
    return () => this.off(event, handler);
  }

  public off(event: RealTimeEventType | '*', handler: EventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  public onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    handler(this.status);
    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  public onReconnect(handler: ReconnectHandler): () => void {
    this.reconnectHandlers.add(handler);
    return () => {
      this.reconnectHandlers.delete(handler);
    };
  }

  private dispatch(event: DomainEvent): void {
    // Specific handlers
    const specific = this.eventHandlers.get(event.event);
    if (specific) {
      specific.forEach((h) => {
        try {
          h(event);
        } catch (err) {
          console.error(`[WebSocket] Error in ${event.event} handler:`, err);
        }
      });
    }

    // Wildcard handlers
    const wildcard = this.eventHandlers.get('*');
    if (wildcard) {
      wildcard.forEach((h) => {
        try {
          h(event);
        } catch (err) {
          console.error('[WebSocket] Error in wildcard handler:', err);
        }
      });
    }
  }
}

export const websocketService = new WebSocketService();
