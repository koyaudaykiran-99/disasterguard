/**
 * Centralized API & WebSocket Configuration for Citizen App
 * Supports both direct production URLs via VITE_API_URL / VITE_WS_URL
 * and local reverse proxy fallbacks.
 */

export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    return envUrl.replace(/\/$/, '');
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
  const loc = window.location;
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = loc.hostname || 'localhost';
  if (loc.port === '3001' && (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1')) {
    return `${proto}//${host}:8000/api/v1/ws`;
  }
  return `${proto}//${loc.host}/api/v1/ws`;
};
