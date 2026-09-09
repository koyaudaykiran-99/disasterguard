import { API_BASE_URL } from "../apiConfig";
import { QueuedSOS, EmergencyUpdateItem } from './emergencyTypes';
import { sosQueueRepository } from '../../storage/repositories/sosQueueRepository';
import { locationService } from '../location/locationService';
import { communicationManager } from '../communication/communicationManager';
import { connectivityService } from '../connectivity/connectivityService';
import { emergencyQueue } from './emergencyQueue';
import { emergencyGuidanceService } from '../guidance/emergencyGuidanceService';

type QueueListener = (activeSOS: QueuedSOS | null, allItems: QueuedSOS[]) => void;

class EmergencyManager {
  private listeners: Set<QueueListener> = new Set();
  private activeSOS: QueuedSOS | null = null;
  private allSOS: QueuedSOS[] = [];
  private retryTimeout: any = null;
  private syncInterval: any = null;

  constructor() {
    this.refreshState();

    // Listen to network changes for automatic emergency retry
    connectivityService.subscribe((conn) => {
      if (conn.internet === 'ONLINE' && conn.backend === 'REACHABLE') {
        console.log('[EmergencyManager] Network restored. Triggering automatic retry of pending emergency requests...');
        this.retryPendingRequests();
      }
    });
  }

  public async refreshState(): Promise<void> {
    try {
      this.allSOS = await sosQueueRepository.getAll();
      this.activeSOS = await emergencyQueue.getActiveSOS();
      this.notify();

      if (this.activeSOS && this.activeSOS.backendSosId && this.activeSOS.status !== 'RESCUED') {
        if (!this.syncInterval) {
          this.startGuidancePoller(this.activeSOS.backendSosId);
        }
      }
    } catch (err) {
      console.warn('[EmergencyManager] Refresh warning:', err);
    }
  }

  public subscribe(listener: QueueListener): () => void {
    this.listeners.add(listener);
    listener(this.activeSOS, this.allSOS);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    this.listeners.forEach((l) => l(this.activeSOS, this.allSOS));
  }

  public async createSOS(
    message: string = 'Critical flood distress signal. Immediate evacuation or medical assistance required.',
    severity: 'CRITICAL' | 'HIGH' = 'CRITICAL'
  ): Promise<{ success: boolean; isDuplicate: boolean; sos: QueuedSOS }> {
    await this.refreshState();

    // 1. Persistent SOS: If active un-resolved SOS already exists, attach update instead of duplicating
    if (this.activeSOS && this.activeSOS.status !== 'RESCUED') {
      console.log('[EmergencyManager] Active SOS exists. Attaching update to SOS:', this.activeSOS.id);
      await this.sendEmergencyUpdate('REPEAT_SOS', message);
      return {
        success: true,
        isDuplicate: true,
        sos: this.activeSOS,
      };
    }

    // 2. Capture GPS Coordinates
    const loc = locationService.getState();
    const now = new Date().toISOString();
    const id = `sos_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;

    const initialUpdate: EmergencyUpdateItem = {
      id: `up_init_${Date.now()}`,
      updateType: 'INITIAL_SOS',
      message,
      latitude: loc.coords?.latitude ?? (loc.coords ? loc.coords.latitude : 13.0827),
      longitude: loc.coords?.longitude ?? (loc.coords ? loc.coords.longitude : 80.2707),
      accuracy: loc.coords?.accuracy ?? null,
      createdAt: now,
      status: 'LOCAL_QUEUED',
    };

    const newSOS: QueuedSOS = {
      id,
      createdAt: now,
      latitude: loc.coords?.latitude ?? (loc.coords ? loc.coords.latitude : 13.0827),
      longitude: loc.coords?.longitude ?? (loc.coords ? loc.coords.longitude : 80.2707),
      accuracy: loc.coords?.accuracy ?? null,
      locationName: loc.locationName || 'Chennai Metropolitan Area',
      message,
      severity,
      status: 'LOCAL_QUEUED',
      transport: 'NONE_AVAILABLE',
      retryCount: 0,
      lastAttemptAt: null,
      priority: severity === 'CRITICAL' ? 100 : 75,
      updates: [initialUpdate],
    };

    // 3. Immediately Persist to IndexedDB
    await sosQueueRepository.enqueue(newSOS);
    this.activeSOS = newSOS;
    this.allSOS.push(newSOS);
    this.notify();

    // 4. Attempt Immediate Transmission
    await this.attemptTransmission(newSOS);

    return {
      success: true,
      isDuplicate: false,
      sos: this.activeSOS || newSOS,
    };
  }

  public async sendEmergencyUpdate(
    updateType: string,
    message?: string,
    coordsOverride?: { latitude: number; longitude: number; accuracy?: number }
  ): Promise<EmergencyUpdateItem> {
    await this.refreshState();

    if (!this.activeSOS) {
      const res = await this.createSOS(message || 'Emergency distress signal', 'CRITICAL');
      return (res.sos.updates && res.sos.updates[0]) || {
        id: `up_${Date.now()}`,
        updateType,
        message,
        createdAt: new Date().toISOString(),
        status: 'LOCAL_QUEUED'
      };
    }

    const loc = coordsOverride || (locationService.getState().coords ? {
      latitude: locationService.getState().coords!.latitude,
      longitude: locationService.getState().coords!.longitude,
      accuracy: locationService.getState().coords!.accuracy ?? undefined
    } : undefined);

    const now = new Date().toISOString();
    const updateItem: EmergencyUpdateItem = {
      id: `up_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      sosId: this.activeSOS.backendSosId,
      updateType,
      message,
      latitude: loc?.latitude,
      longitude: loc?.longitude,
      accuracy: loc?.accuracy,
      createdAt: now,
      status: 'LOCAL_QUEUED',
    };

    if (!this.activeSOS.updates) {
      this.activeSOS.updates = [];
    }
    this.activeSOS.updates.push(updateItem);

    if (loc?.latitude && loc?.longitude) {
      this.activeSOS.latitude = loc.latitude;
      this.activeSOS.longitude = loc.longitude;
      if (loc.accuracy) this.activeSOS.accuracy = loc.accuracy;
    }

    await sosQueueRepository.update(this.activeSOS);
    this.notify();

    await this.attemptUpdateTransmission(this.activeSOS, updateItem);
    return updateItem;
  }

  public async sendVoiceEmergencyUpdate(
    audioBlob: Blob,
    language: string = 'te',
    durationSeconds?: number,
    coordsOverride?: { latitude: number; longitude: number; accuracy?: number }
  ): Promise<EmergencyUpdateItem> {
    await this.refreshState();

    if (!this.activeSOS) {
      const res = await this.createSOS(
        language === 'te'
          ? 'మా ఇంట్లోకి నీళ్లు వచ్చాయి, సహాయం కావాలి'
          : language === 'hi'
          ? 'घर में पानी भर गया है, तुरंत मदद चाहिए'
          : 'Water entering premises, urgent rescue required',
        'CRITICAL'
      );
      if (res.sos.backendSosId) {
        // Connected and active
      }
    }

    const loc = coordsOverride || (locationService.getState().coords ? {
      latitude: locationService.getState().coords!.latitude,
      longitude: locationService.getState().coords!.longitude,
      accuracy: locationService.getState().coords!.accuracy ?? undefined
    } : undefined);

    const now = new Date().toISOString();
    const updateItem: EmergencyUpdateItem = {
      id: `up_voice_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      sosId: this.activeSOS?.backendSosId,
      updateType: 'VOICE_UPDATE',
      message: `Voice emergency update (${language.toUpperCase()}) recorded.`,
      original_language: language,
      audioBlob,
      audioDuration: durationSeconds,
      audioMimeType: audioBlob.type || 'audio/webm',
      audioSize: audioBlob.size,
      latitude: loc?.latitude,
      longitude: loc?.longitude,
      accuracy: loc?.accuracy,
      createdAt: now,
      status: 'LOCAL_QUEUED',
    };

    if (this.activeSOS) {
      if (!this.activeSOS.updates) {
        this.activeSOS.updates = [];
      }
      this.activeSOS.updates.push(updateItem);
      await sosQueueRepository.update(this.activeSOS);
      this.notify();

      await this.attemptVoiceTransmission(this.activeSOS, updateItem, audioBlob, language, durationSeconds);
    }

    return updateItem;
  }

  private async attemptVoiceTransmission(
    sos: QueuedSOS,
    updateItem: EmergencyUpdateItem,
    audioBlob: Blob,
    language: string,
    durationSeconds?: number
  ): Promise<void> {
    if (!sos.backendSosId) {
      console.log('[EmergencyManager] Backend SOS ID not yet assigned. Voice update queued in IndexedDB:', updateItem.id);
      return;
    }

    updateItem.status = 'SENDING';
    await sosQueueRepository.update(sos);
    this.notify();

    try {
      const formData = new FormData();
      const ext = audioBlob.type && audioBlob.type.includes('wav') ? 'wav' : (audioBlob.type && audioBlob.type.includes('ogg')) ? 'ogg' : 'webm';
      formData.append('file', audioBlob, `voice_sos_${updateItem.id}.${ext}`);
      formData.append('language', language);
      formData.append('client_update_id', updateItem.id);
      if (updateItem.latitude != null) formData.append('latitude', String(updateItem.latitude));
      if (updateItem.longitude != null) formData.append('longitude', String(updateItem.longitude));
      if (updateItem.accuracy != null) formData.append('accuracy', String(updateItem.accuracy));
      if (durationSeconds != null) formData.append('duration_seconds', String(durationSeconds));

      const res = await fetch(`${API_BASE_URL}/api/v1/sos/${sos.backendSosId}/voice`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        updateItem.status = 'RECEIVED';
        updateItem.message = data.message;
        updateItem.audioId = data.audio_id;
        updateItem.transcriptionProvider = data.transcription_provider;
        updateItem.transcriptionModel = data.transcription_model;
        updateItem.deliveredAt = new Date().toISOString();
        updateItem.failureReason = undefined;
        console.log(`[EmergencyManager] Voice update ${updateItem.id} delivered and transcribed: "${data.message}"`);
      } else {
        updateItem.status = 'LOCAL_QUEUED';
        updateItem.failureReason = `HTTP ${res.status}`;
      }
    } catch (err: any) {
      updateItem.status = 'LOCAL_QUEUED';
      updateItem.failureReason = err.message || 'Network unavailable';
    }

    await sosQueueRepository.update(sos);
    this.notify();
  }

  private async attemptUpdateTransmission(sos: QueuedSOS, updateItem: EmergencyUpdateItem): Promise<void> {
    if (!sos.backendSosId) {
      console.log('[EmergencyManager] Backend SOS ID not yet assigned. Update stored in IndexedDB:', updateItem.id);
      return;
    }

    updateItem.status = 'SENDING';
    await sosQueueRepository.update(sos);
    this.notify();

    try {
      const payload = {
        client_update_id: updateItem.id,
        update_type: updateItem.updateType,
        message: updateItem.message || undefined,
        latitude: updateItem.latitude || undefined,
        longitude: updateItem.longitude || undefined,
        accuracy: updateItem.accuracy || undefined,
        location_timestamp: updateItem.createdAt,
        source: 'CITIZEN_APP'
      };

      const res = await fetch(`${API_BASE_URL}/api/v1/sos/${sos.backendSosId}/updates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        updateItem.status = 'RECEIVED';
        updateItem.deliveredAt = new Date().toISOString();
        updateItem.failureReason = undefined;
        console.log(`[EmergencyManager] Emergency update ${updateItem.id} delivered to Command Centre.`);
      } else {
        updateItem.status = 'LOCAL_QUEUED';
        updateItem.failureReason = `HTTP ${res.status}`;
      }
    } catch (err: any) {
      updateItem.status = 'LOCAL_QUEUED';
      updateItem.failureReason = err.message || 'Network unavailable';
    }

    await sosQueueRepository.update(sos);
    this.notify();
  }

  private async attemptTransmission(sos: QueuedSOS): Promise<void> {
    sos.status = 'SENDING';
    sos.lastAttemptAt = new Date().toISOString();
    await sosQueueRepository.update(sos);
    this.activeSOS = { ...sos };
    this.notify();

    const result = await communicationManager.dispatchEmergencyMessage(sos);

    if (result.success) {
      sos.status = 'RECEIVED';
      sos.transport = result.transport;
      sos.deliveredAt = result.timestamp;
      sos.backendSosId = result.backendSosId;
      sos.serverAck = result.serverAck;
      sos.failureReason = undefined;

      if (sos.updates && sos.updates.length > 0) {
        sos.updates[0].status = 'RECEIVED';
        sos.updates[0].deliveredAt = result.timestamp;
      }

      await sosQueueRepository.update(sos);
      this.activeSOS = { ...sos };
      this.notify();
      console.log(`[EmergencyManager] SOS ${sos.id} successfully received by Command Centre as #DG-${sos.backendSosId || sos.id}.`);

      if (result.backendSosId) {
        this.startGuidancePoller(result.backendSosId);
      }

      await this.flushQueuedUpdates(sos);
    } else {
      sos.status = 'WAITING_FOR_TRANSPORT';
      sos.transport = result.transport;
      sos.retryCount += 1;
      sos.failureReason = result.error;
      await sosQueueRepository.update(sos);
      this.activeSOS = { ...sos };
      this.notify();

      this.scheduleRetry(sos);
    }
  }

  private async flushQueuedUpdates(sos: QueuedSOS): Promise<void> {
    if (!sos.updates || sos.updates.length === 0 || !sos.backendSosId) return;
    for (const up of sos.updates) {
      if (up.status === 'LOCAL_QUEUED' || up.status === 'FAILED') {
        if (up.updateType === 'VOICE_UPDATE' && up.audioBlob) {
          await this.attemptVoiceTransmission(sos, up, up.audioBlob, up.original_language || 'en', up.audioDuration);
        } else {
          await this.attemptUpdateTransmission(sos, up);
        }
      }
    }
  }

  private async scheduleRetry(sos: QueuedSOS): Promise<void> {
    if (this.retryTimeout) clearTimeout(this.retryTimeout);

    const delay = await emergencyQueue.getNextRetryDelay(sos.retryCount);
    console.log(`[EmergencyManager] Next retry in ${delay / 1000}s (Attempt #${sos.retryCount + 1})...`);

    this.retryTimeout = setTimeout(async () => {
      const current = await sosQueueRepository.getActive();
      if (current && current.status !== 'SENT' && current.status !== 'RECEIVED') {
        await this.attemptTransmission(current);
      }
    }, delay);
  }

  public async retryPendingRequests(): Promise<void> {
    if (this.retryTimeout) clearTimeout(this.retryTimeout);

    const pending = await emergencyQueue.getPendingRequests();
    for (const sos of pending) {
      await this.attemptTransmission(sos);
      if (sos.status !== 'SENT' && sos.status !== 'RECEIVED') break;
    }

    if (this.activeSOS && this.activeSOS.backendSosId) {
      await this.flushQueuedUpdates(this.activeSOS);
    }
  }

  public async cancelActiveSOS(): Promise<void> {
    if (!this.activeSOS) return;
    await sosQueueRepository.delete(this.activeSOS.id);
    if (this.retryTimeout) clearTimeout(this.retryTimeout);
    this.stopGuidancePoller();
    this.activeSOS = null;
    await this.refreshState();
  }

  public async dismissActiveSOS(): Promise<void> {
    this.stopGuidancePoller();
    this.activeSOS = null;
    this.notify();
  }

  public startGuidancePoller(backendSosId: number): void {
    if (this.syncInterval) clearInterval(this.syncInterval);
    this.pollGuidance(backendSosId);
    this.syncInterval = setInterval(() => {
      if (!this.activeSOS || this.activeSOS.status === 'RESCUED') {
        this.stopGuidancePoller();
        return;
      }
      this.pollGuidance(backendSosId);
    }, 5000);
  }

  public stopGuidancePoller(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  public async pollGuidance(backendSosId: number): Promise<void> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/sos/${backendSosId}/guidance`);
      if (res.ok) {
        const data = await res.json();
        if (this.activeSOS && (this.activeSOS.backendSosId === backendSosId || !this.activeSOS.backendSosId)) {
          let hasChanges = false;
          if (data.status && data.status !== this.activeSOS.status) {
            this.activeSOS.status = data.status;
            hasChanges = true;
          } else if (data.dispatch_status === 'DISPATCHED' || data.dispatch_status === 'EN_ROUTE') {
            if (this.activeSOS.status !== 'DISPATCHED') {
              this.activeSOS.status = 'DISPATCHED';
              hasChanges = true;
            }
          } else if (data.dispatch_status === 'ON_SCENE') {
            if (this.activeSOS.status !== ('ON_SCENE' as any)) {
              this.activeSOS.status = 'ON_SCENE' as any;
              hasChanges = true;
            }
          } else if (data.dispatch_status === 'RESOLVED' || data.status === 'RESCUED') {
            if (this.activeSOS.status !== 'RESCUED') {
              this.activeSOS.status = 'RESCUED';
              hasChanges = true;
            }
          } else if (data.triage_summary && this.activeSOS.status === 'RECEIVED') {
            this.activeSOS.status = 'TRIAGED';
            hasChanges = true;
          }

          if (data.assigned_team_name && data.assigned_team_name !== this.activeSOS.assignedTeamName) {
            this.activeSOS.assignedTeamName = data.assigned_team_name;
            hasChanges = true;
          }

          emergencyGuidanceService.cacheRemoteGuidance(backendSosId, data);
          this.activeSOS.guidance = data;

          await sosQueueRepository.update(this.activeSOS);
          this.notify();
        }
      }
    } catch (err) {
      console.warn('[EmergencyManager] Guidance poll warning:', err);
    }
  }

  public getActiveSOS(): QueuedSOS | null {
    return this.activeSOS;
  }
}

export const emergencyManager = new EmergencyManager();
