import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, RotateCcw, Send, AlertCircle, CheckCircle, Volume2, Globe } from 'lucide-react';
import { emergencyManager } from '../../services/emergency/emergencyManager';
import { locationService } from '../../services/location/locationService';

interface VoiceSOSRecorderProps {
  onSuccess?: () => void;
  className?: string;
  isInitialSOS?: boolean;
}

type RecordingState = 'IDLE' | 'RECORDING' | 'STOPPING' | 'PROCESSING' | 'REVIEW' | 'ERROR';

const LANGUAGES = [
  { code: 'te', label: 'తెలుగు', name: 'Telugu' },
  { code: 'hi', label: 'हिन्दी', name: 'Hindi' },
  { code: 'en', label: 'English', name: 'English' },
];

const MAX_RECORDING_SECONDS = 30;

export const VoiceSOSRecorder: React.FC<VoiceSOSRecorderProps> = ({
  onSuccess,
  className = '',
  isInitialSOS = false,
}) => {
  const [recordingState, setRecordingState] = useState<RecordingState>('IDLE');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('te');
  const [durationSeconds, setDurationSeconds] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<any>(null);

  // Clean up audio streams on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setErrorMessage(null);
    audioChunksRef.current = [];

    // Check browser support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setRecordingState('ERROR');
      setErrorMessage('Audio recording is not supported in this browser environment. Please use text SOS.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });
      streamRef.current = stream;

      // Select supported audio mime type
      const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4', 'audio/wav'];
      let chosenMime = 'audio/webm';
      for (const m of mimeTypes) {
        if (MediaRecorder.isTypeSupported(m)) {
          chosenMime = m;
          break;
        }
      }

      const recorder = new MediaRecorder(stream, { mimeType: chosenMime });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: chosenMime });
        setRecordedBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setRecordingState('REVIEW');
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      recorder.start(250); // Collect data chunks every 250ms
      setRecordingState('RECORDING');
      setDurationSeconds(0);

      // Duration Timer
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        setDurationSeconds(elapsed);
        if (elapsed >= MAX_RECORDING_SECONDS) {
          stopRecording();
        }
      }, 500);
    } catch (err: any) {
      console.warn('[VoiceSOSRecorder] Microphone access error:', err);
      setRecordingState('ERROR');
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMessage('Microphone permission denied. Allow microphone access in your browser or use Quick Text Updates.');
      } else {
        setErrorMessage('Microphone unavailable or audio device error. Please use manual distress buttons.');
      }
    }
  };

  const stopRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      setRecordingState('STOPPING');
      mediaRecorderRef.current.stop();
    }
  };

  const cancelRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setRecordedBlob(null);
    setDurationSeconds(0);
    setRecordingState('IDLE');
    setErrorMessage(null);
  };

  const handleSendVoice = async () => {
    if (!recordedBlob) return;
    setIsSubmitting(true);
    try {
      const loc = locationService.getState();
      const coords = loc.coords
        ? {
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
            accuracy: loc.coords.accuracy ?? undefined,
          }
        : undefined;

      await emergencyManager.sendVoiceEmergencyUpdate(
        recordedBlob,
        selectedLanguage,
        durationSeconds || 5,
        coords
      );

      setRecordingState('IDLE');
      setRecordedBlob(null);
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
        setAudioUrl(null);
      }
      setDurationSeconds(0);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setErrorMessage(`Voice transmission failed: ${err.message || 'Network error'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60)
      .toString()
      .padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className={`p-3.5 rounded-2xl border border-rose-500/30 bg-rose-950/20 font-mono text-xs space-y-3 ${className}`}>
      {/* Header & Language Selection */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rose-500/20 pb-2">
        <div className="flex items-center gap-1.5 text-rose-400 font-bold uppercase tracking-wider text-[11px]">
          <Mic className="w-3.5 h-3.5 text-rose-400" />
          <span>{isInitialSOS ? 'Multilingual Voice SOS' : 'Voice Emergency Update'}</span>
        </div>

        {/* Language Selector */}
        <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-slate-800">
          <Globe className="w-3 h-3 text-slate-400 ml-1 mr-0.5" />
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              type="button"
              onClick={() => setSelectedLanguage(lang.code)}
              disabled={recordingState === 'RECORDING'}
              className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-colors ${
                selectedLanguage === lang.code
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      {/* Accessible Live Region */}
      <div className="sr-only" aria-live="polite">
        {recordingState === 'RECORDING'
          ? `Recording audio in ${selectedLanguage}. ${durationSeconds} seconds of 30 elapsed.`
          : recordingState === 'REVIEW'
          ? 'Audio recorded and ready for review.'
          : 'Voice recorder ready.'}
      </div>

      {/* State: IDLE */}
      {recordingState === 'IDLE' && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2.5 pt-1">
          <div className="text-slate-300 text-[11px] leading-relaxed text-center sm:text-left">
            <span>Speak in </span>
            <strong className="text-rose-400">
              {LANGUAGES.find((l) => l.code === selectedLanguage)?.name || 'Telugu'}
            </strong>
            <span>: Describe location, trapped persons, or rising floodwaters.</span>
          </div>

          <button
            type="button"
            onClick={startRecording}
            className="w-full sm:w-auto px-4 py-2 bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 active:scale-95 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-rose-950/50 transition-all shrink-0"
          >
            <Mic className="w-4 h-4" />
            <span>Tap to Speak</span>
          </button>
        </div>
      )}

      {/* State: RECORDING */}
      {recordingState === 'RECORDING' && (
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between bg-black/40 p-2.5 rounded-xl border border-rose-500/40">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
              </span>
              <span className="font-bold text-rose-300 uppercase tracking-wider text-[11px]">
                Recording in {LANGUAGES.find((l) => l.code === selectedLanguage)?.name}...
              </span>
            </div>

            <div className="text-white font-black text-sm tracking-widest bg-rose-950/60 px-2.5 py-0.5 rounded-lg border border-rose-500/30">
              {formatTimer(durationSeconds)} / {formatTimer(MAX_RECORDING_SECONDS)}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={stopRecording}
              className="flex-1 py-2 bg-rose-600 hover:bg-rose-500 active:scale-95 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors"
            >
              <Square className="w-4 h-4 fill-white" />
              <span>Finish & Review</span>
            </button>
            <button
              type="button"
              onClick={cancelRecording}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* State: STOPPING / PROCESSING */}
      {recordingState === 'STOPPING' && (
        <div className="p-3 text-center text-slate-300 flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-rose-500 border-t-transparent rounded-full animate-spin" />
          <span>Finalizing audio recording...</span>
        </div>
      )}

      {/* State: REVIEW */}
      {recordingState === 'REVIEW' && (
        <div className="space-y-2.5 pt-1">
          <div className="flex items-center justify-between text-[11px] text-slate-300">
            <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <CheckCircle className="w-3.5 h-3.5" />
              Recording Complete ({durationSeconds}s)
            </span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold uppercase text-[10px]">
              Language: {LANGUAGES.find((l) => l.code === selectedLanguage)?.name}
            </span>
          </div>

          {/* Audio Player Preview */}
          {audioUrl && (
            <div className="bg-black/30 p-2 rounded-xl border border-slate-800 flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-rose-400 shrink-0" />
              <audio controls src={audioUrl} className="w-full h-8" />
            </div>
          )}

          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={handleSendVoice}
              disabled={isSubmitting}
              className="flex-1 py-2 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 disabled:opacity-50 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-md transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Transmitting...' : 'Send Voice Update'}</span>
            </button>

            <button
              type="button"
              onClick={cancelRecording}
              disabled={isSubmitting}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Re-record</span>
            </button>
          </div>
        </div>
      )}

      {/* Error state display */}
      {errorMessage && (
        <div className="p-2.5 bg-rose-950/40 border border-rose-500/50 rounded-xl text-rose-200 text-[11px] flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => setErrorMessage(null)}
              className="text-[10px] text-rose-300 underline hover:text-rose-100"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
