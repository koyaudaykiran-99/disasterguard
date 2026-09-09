import { API_BASE_URL } from "../../apiConfig";
import { CommunicationTransport, TransportResult, TransportStatus } from '../communicationTypes';
import { QueuedSOS } from '../../emergency/emergencyTypes';
import { connectivityService } from '../../connectivity/connectivityService';

export class InternetTransport implements CommunicationTransport {
  public type = 'INTERNET' as const;
  public name = 'Broadband / Cellular Internet';
  public description = 'Direct HTTPS API transmission to DisasterGuard FastAPI Command Backend';

  public async isAvailable(): Promise<boolean> {
    const conn = connectivityService.getState();
    if (conn.internet === 'OFFLINE' || conn.isDemoOffline) return false;
    return await connectivityService.checkBackendReachability();
  }

  public getStatus(): TransportStatus {
    const conn = connectivityService.getState();
    if (conn.internet === 'OFFLINE' || conn.isDemoOffline) return 'UNAVAILABLE';
    return conn.backend === 'REACHABLE' ? 'AVAILABLE' : 'STANDBY';
  }

  public async sendEmergencyMessage(sos: QueuedSOS): Promise<TransportResult> {
    const isAvail = await this.isAvailable();
    if (!isAvail) {
      return {
        success: false,
        transport: 'INTERNET',
        timestamp: new Date().toISOString(),
        error: 'Internet or backend server currently unreachable.',
      };
    }

    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 6000);

      const response = await fetch(`${API_BASE_URL}/api/v1/sos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          client_id: sos.id,
          latitude: sos.latitude !== null && !isNaN(sos.latitude) ? sos.latitude : 13.0827,
          longitude: sos.longitude !== null && !isNaN(sos.longitude) ? sos.longitude : 80.2707,
          accuracy: sos.accuracy ?? undefined,
          message: sos.message || 'Critical flood distress signal. Immediate evacuation required.',
          severity: sos.severity || 'CRITICAL',
          transport: 'INTERNET',
          device_timestamp: sos.createdAt,
        }),
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (!response.ok) {
        let errMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          if (errData?.error?.message) errMessage = errData.error.message;
        } catch (_) {}
        throw new Error(errMessage);
      }

      const data = await response.json();
      const serverSosId = data.id || data.sos_id;

      return {
        success: true,
        transport: 'INTERNET',
        messageId: String(serverSosId || sos.id),
        backendSosId: serverSosId ? Number(serverSosId) : undefined,
        serverAck: data,
        timestamp: data.received_at || data.created_at || new Date().toISOString(),
      };
    } catch (err: any) {
      return {
        success: false,
        transport: 'INTERNET',
        timestamp: new Date().toISOString(),
        error: err.message || 'Network request failed during SOS dispatch.',
      };
    }
  }
}

export const internetTransport = new InternetTransport();
