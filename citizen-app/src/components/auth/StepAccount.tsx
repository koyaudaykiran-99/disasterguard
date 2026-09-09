import React, { useState } from 'react';
import { User, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react';

interface StepAccountProps {
  onContinue: (data: { name: string; emailOrPhone: string; password: string }) => void;
  initialData: { name: string; emailOrPhone: string; password: string };
}

export const StepAccount: React.FC<StepAccountProps> = ({ onContinue, initialData }) => {
  const [name, setName] = useState(initialData.name);
  const [emailOrPhone, setEmailOrPhone] = useState(initialData.emailOrPhone);
  const [password, setPassword] = useState(initialData.password);
  const [confirmPassword, setConfirmPassword] = useState(initialData.password);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Password strength calculation
  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return 0;
    let score = 0;
    if (pwd.length >= 6) score += 1;
    if (pwd.length >= 8) score += 1;
    if (/[A-Z]/.test(pwd) || /[0-9]/.test(pwd)) score += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
    return score;
  };

  const strength = getPasswordStrength(password);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Please enter your full name.');
      return;
    }

    if (!emailOrPhone.trim()) {
      setError('Please enter a valid email address or phone number.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please verify and try again.');
      return;
    }

    onContinue({ name: name.trim(), emailOrPhone: emailOrPhone.trim(), password });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 text-left">
      <div className="text-center mb-5">
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">Create Safety Account</h2>
        <p className="text-xs text-slate-500 mt-0.5">Enter your basic credentials to register for protection.</p>
      </div>

      {error && (
        <div
          role="alert"
          className="flex items-start gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium animate-fadeIn"
        >
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Full Name */}
      <div>
        <label htmlFor="reg-name" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Full Name
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <User className="w-4 h-4" />
          </div>
          <input
            id="reg-name"
            type="text"
            required
            autoComplete="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Ramesh Reddy"
            className="w-full pl-9 pr-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
        </div>
      </div>

      {/* Email or Phone */}
      <div>
        <label htmlFor="reg-identifier" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Email or Phone
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Mail className="w-4 h-4" />
          </div>
          <input
            id="reg-identifier"
            type="text"
            required
            autoComplete="email"
            value={emailOrPhone}
            onChange={(e) => setEmailOrPhone(e.target.value)}
            placeholder="name@example.com or 9876543210"
            className="w-full pl-9 pr-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
        </div>
      </div>

      {/* Password */}
      <div>
        <label htmlFor="reg-password" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Password
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Lock className="w-4 h-4" />
          </div>
          <input
            id="reg-password"
            type={showPassword ? 'text' : 'password'}
            required
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 6 characters"
            className="w-full pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>

        {/* Strength Meter */}
        {password.length > 0 && (
          <div className="mt-1.5 flex items-center gap-1">
            {[1, 2, 3, 4].map((level) => (
              <div
                key={level}
                className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                  strength >= level
                    ? strength <= 1
                      ? 'bg-amber-500'
                      : strength <= 3
                      ? 'bg-emerald-500'
                      : 'bg-emerald-600'
                    : 'bg-slate-200'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Confirm Password */}
      <div>
        <label htmlFor="reg-confirm" className="block text-xs font-semibold text-slate-700 mb-1.5">
          Confirm Password
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Lock className="w-4 h-4" />
          </div>
          <input
            id="reg-confirm"
            type={showConfirm ? 'text' : 'password'}
            required
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter password"
            className="w-full pl-9 pr-10 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
          />
          <button
            type="button"
            onClick={() => setShowConfirm(!showConfirm)}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
            aria-label={showConfirm ? 'Hide confirm password' : 'Show confirm password'}
          >
            {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <button
        type="submit"
        className="w-full mt-2 py-3 px-4 rounded-xl bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold text-xs shadow-md shadow-red-600/20 hover:shadow-lg transition-all focus:outline-none focus:ring-2 focus:ring-red-500/50"
      >
        Continue to Safety Profile &rarr;
      </button>
    </form>
  );
};
