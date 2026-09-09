import { CommunicationTransport, TransportResult, TransportStatus } from '../communicationTypes';
import { QueuedSOS } from '../../emergency/emergencyTypes';

export class RelayTransport implements CommunicationTransport {
  public type = 'RELAY' as const;
  public name = 'Local Emergency Mesh Relay';
  public description = 'Short-range peer-to-peer relay over localized Wi-Fi Direct / BLE beacons';

  public async isAvailable(): Promise<boolean> {
    return false;
  }

  public getStatus(): TransportStatus {
    return 'STANDBY';
  }

  public async sendEmergencyMessage(_sos: QueuedSOS): Promise<TransportResult> {
    return {
      success: false,
      transport: 'RELAY',
      timestamp: new Date().toISOString(),
      error: 'Local peer-to-peer mesh relay transport adapter is in standby mode.',
    };
  }
}

export const relayTransport = new RelayTransport();
