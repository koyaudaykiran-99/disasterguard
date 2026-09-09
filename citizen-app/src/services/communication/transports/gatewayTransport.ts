import { CommunicationTransport, TransportResult, TransportStatus } from '../communicationTypes';
import { QueuedSOS } from '../../emergency/emergencyTypes';

export class GatewayTransport implements CommunicationTransport {
  public type = 'GATEWAY' as const;
  public name = 'Civil Defense Emergency Gateway (LoRa / RF)';
  public description = 'Long-range sub-gigahertz radio link to municipal civil defense towers';

  public async isAvailable(): Promise<boolean> {
    return false;
  }

  public getStatus(): TransportStatus {
    return 'STANDBY';
  }

  public async sendEmergencyMessage(_sos: QueuedSOS): Promise<TransportResult> {
    return {
      success: false,
      transport: 'GATEWAY',
      timestamp: new Date().toISOString(),
      error: 'Civil Defense RF/LoRa gateway transceiver adapter is in standby mode.',
    };
  }
}

export const gatewayTransport = new GatewayTransport();
