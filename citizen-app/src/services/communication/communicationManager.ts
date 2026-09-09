import { CommunicationTransport, TransportResult, TransportStatus } from './communicationTypes';
import { QueuedSOS, TransportType } from '../emergency/emergencyTypes';
import { internetTransport } from './transports/internetTransport';
import { smsTransport } from './transports/smsTransport';
import { relayTransport } from './transports/relayTransport';
import { gatewayTransport } from './transports/gatewayTransport';

class CommunicationManager {
  private transports: CommunicationTransport[] = [
    internetTransport,
    gatewayTransport,
    relayTransport,
    smsTransport,
  ];

  public getTransports(): CommunicationTransport[] {
    return this.transports;
  }

  public getStatusOverview(): Record<TransportType, TransportStatus> {
    return {
      INTERNET: internetTransport.getStatus(),
      GATEWAY: gatewayTransport.getStatus(),
      RELAY: relayTransport.getStatus(),
      SMS: smsTransport.getStatus(),
      NONE_AVAILABLE: 'UNAVAILABLE',
    };
  }

  public async hasAnyAvailableTransport(): Promise<boolean> {
    for (const transport of this.transports) {
      if (await transport.isAvailable()) {
        return true;
      }
    }
    return false;
  }

  public async dispatchEmergencyMessage(sos: QueuedSOS): Promise<TransportResult> {
    for (const transport of this.transports) {
      const isAvailable = await transport.isAvailable();
      if (isAvailable) {
        console.log(`[CommunicationManager] Dispatching SOS ${sos.id} via ${transport.name}...`);
        const result = await transport.sendEmergencyMessage(sos);
        if (result.success) {
          return result;
        }
      }
    }

    return {
      success: false,
      transport: 'NONE_AVAILABLE',
      timestamp: new Date().toISOString(),
      error: 'No active emergency communication path available. Request is securely queued on this device.',
    };
  }
}

export const communicationManager = new CommunicationManager();
