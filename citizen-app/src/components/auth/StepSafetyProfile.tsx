import React, { useState } from 'react';
import { UserCheck, PhoneCall, Languages, MapPin, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { SafetyProfileData } from '../../services/auth/authService';

interface StepSafetyProfileProps {
  onBack: () => void;
  onSubmit: (profile: SafetyProfileData) => Promise<void>;
  isLoading: boolean;
  errorMessage?: string | null;
}

export const StepSafetyProfile: React.FC<StepSafetyProfileProps> = ({
  onBack,
  onSubmit,
  isLoading,
  errorMessage,
}) => {
  const [contactName, setContactName] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [language, setLanguage] = useState<'te' | 'en' | 'hi'>('te');
  const [locGranted, setLocGranted] = useState(false);
  const [isRequestingLoc, setIsRequestingLoc] = useState(false);
  const [locError, setLocError] = useState<string | null>(null);

  const handleRequestLocation = () => {
    if (!navigator.geolocation) {
      setLocError('Geolocation is not supported by your device.');
      return;
    }
    setIsRequestingLoc(true);
    setLocError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsRequestingLoc(false);
        setLocGranted(true);
      },
      (error) => {
        setIsRequestingLoc(false);
        setLocError('Location access was not enabled. You can still proceed.');
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      emergencyContactName: contactName.trim() || 'Next of Kin',
      emergencyContactPhone: contactPhone.trim(),
      preferredLanguage: language,
      locationGranted: locGranted,
    });
  };

  return (
    <form onSubmit={handleFormSubmit} className="space-y-4 text-left">
      <div className="text-center mb-4">
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Safety & Triage Profile</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Equip the emergency dispatch system to protect your household.
        </p>
      </div>

      {errorMessage && (
        <div
          role="alert"
          className="flex items-start gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium"
        >
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Emergency Contact Name */}
      <div>
        <label htmlFor="sec-contact-name" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Emergency Contact Name (Optional)
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <UserCheck className="w-4 h-4" />
          </div>
          <input
            id="sec-contact-name"
            type="text"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
            placeholder="e.g. Family member or guardian"
            className="w-full pl-9 pr-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
        </div>
      </div>

      {/* Emergency Contact Phone */}
      <div>
        <label htmlFor="sec-contact-phone" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Emergency Contact Phone
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <PhoneCall className="w-4 h-4" />
          </div>
          <input
            id="sec-contact-phone"
            type="tel"
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
            placeholder="+91 98765 43210"
            className="w-full pl-9 pr-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
        </div>
      </div>

      {/* Preferred Language */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
          <Languages className="w-3.5 h-3.5 text-slate-500" />
          Preferred Emergency Directive Language
        </label>
        <div className="grid grid-cols-3 gap-2">
          {[
            { id: 'te', label: 'తెలుగు (Telugu)' },
            { id: 'en', label: 'English' },
            { id: 'hi', label: 'हिंदी (Hindi)' },
          ].map((lang) => (
            <button
              key={lang.id}
              type="button"
              onClick={() => setLanguage(lang.id as any)}
              className={`py-2 px-2 rounded-xl text-xs font-bold border transition-all text-center ${
                language === lang.id
                  ? 'bg-red-50 text-red-700 border-red-500 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      {/* Location Permission Section */}
      <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
        <div className="flex items-start gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-red-100 text-red-600 flex items-center justify-center shrink-0 mt-0.5">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900">Emergency Location Telemetry</h4>
            <p className="text-[11px] text-slate-600 leading-relaxed mt-0.5">
              Your location helps us provide nearby emergency alerts, shelters and rescue assistance.
            </p>
          </div>
        </div>

        <div className="pt-1">
          {locGranted ? (
            <div className="flex items-center gap-1.5 text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-2 rounded-xl text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Location Telemetry Active (Ready for Rescue Dispatch)</span>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleRequestLocation}
              disabled={isRequestingLoc}
              className="w-full py-2 px-3 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-sm"
            >
              {isRequestingLoc ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-red-600" />
                  <span>Acquiring GPS Signal...</span>
                </>
              ) : (
                <>
                  <MapPin className="w-3.5 h-3.5 text-red-600" />
                  <span>Enable Emergency GPS Precision</span>
                </>
              )}
            </button>
          )}
          {locError && <p className="text-[10px] text-slate-500 mt-1">{locError}</p>}
        </div>
      </div>

      <div className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={onBack}
          disabled={isLoading}
          className="w-1/3 py-3 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition-colors"
        >
          &larr; Back
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="w-2/3 py-3 px-4 rounded-xl bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold text-xs shadow-md shadow-red-600/20 hover:shadow-lg transition-all flex items-center justify-center gap-1.5 disabled:opacity-60"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Activating Protection...</span>
            </>
          ) : (
            <span>Complete Registration &rarr;</span>
          )}
        </button>
      </div>
    </form>
  );
};
