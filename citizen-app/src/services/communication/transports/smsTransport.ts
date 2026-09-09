import { CommunicationTransport, TransportResult, TransportStatus } from '../communicationTypes';
import { QueuedSOS } from '../../emergency/emergencyTypes';

export class SMSTransport implements CommunicationTransport {
  public type = 'SMS' as const;
  public name = 'Cellular Emergency SMS Bridge';
  public description = 'Compact formatted SMS emergency transmission over telecom carrier networks';

  public async isAvailable(): Promise<boolean> {
    // In standard web browser environments without native GSM modem access, returns false
    return false;
  }

  public getStatus(): TransportStatus {
    return 'STANDBY';
  }

  public async sendEmergencyMessage(sos: QueuedSOS): Promise<TransportResult> {
    // Generates formatted standard emergency SMS payload for future native wrapper
    const payload = `DISASTERGUARD SOS [${sos.severity}] LOC:${sos.latitude?.toFixed(4)},${sos.longitude?.toFixed(4)} ID:${sos.id.slice(0, 8)} MSG:${sos.message}`;
    
    console.info('[SMSTransport] Prepared payload for carrier SMS gateway:', payload);

    return {
      success: false,
      transport: 'SMS',
      timestamp: new Date().toISOString(),
      error: 'Cellular SMS hardware transport adapter is in standby mode. Awaiting native carrier gateway bridge.',
    };
  }
}

export const smsTransport = new SMSTransport();
