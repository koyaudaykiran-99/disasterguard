/**
 * Centralized API & WebSocket Configuration for Citizen App
 * Supports direct production URLs via VITE_API_URL / VITE_WS_URL
 * with automatic fallback to permanent Render backend in production.
 */

export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://ai-disasterguard-backend.onrender.com';
  }
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const getWsUrl = (): string => {
  const wsUrl = import.meta.env.VITE_WS_URL;
  if (wsUrl) return wsUrl;
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    const clean = apiUrl.replace(/\/$/, '').replace(/^http/, 'ws');
    return `${clean}/api/v1/ws`;
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'wss://ai-disasterguard-backend.onrender.com/api/v1/ws';
  }
  const loc = window.location;
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = loc.hostname || 'localhost';
  if (loc.port === '3001' && (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1')) {
    return `${proto}//${host}:8000/api/v1/ws`;
  }
  return `${proto}//${loc.host}/api/v1/ws`;
};
