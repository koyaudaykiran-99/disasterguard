import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Mail, Lock, Eye, EyeOff, AlertCircle, Loader2, LifeBuoy } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AuthNetworkBackground } from '../components/auth/AuthNetworkBackground';
import { AuthCard } from '../components/auth/AuthCard';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showForgotModal, setShowForgotModal] = useState(false);

  // If already authenticated, redirect to dashboard
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!identifier.trim()) {
      setErrorMessage('Please enter your email or registered phone number.');
      return;
    }

    if (!password) {
      setErrorMessage('Please enter your password.');
      return;
    }

    setIsLoading(true);
    try {
      await login(identifier.trim(), password, rememberMe);
      navigate('/');
    } catch (err: any) {
      setErrorMessage(
        err.message || 'Unable to connect to the emergency service. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-center items-center px-4 py-8 relative bg-[#FAFAFA] text-slate-900 selection:bg-red-500 selection:text-white">
      <AuthNetworkBackground />

      <AuthCard>
        {/* Emblem & Brand Header */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-b from-red-500 to-red-600 text-white flex items-center justify-center shadow-lg shadow-red-500/25 mb-3 border border-red-400/40">
            <Shield className="w-7 h-7 stroke-[2.2]" />
          </div>

          <span className="text-[11px] font-bold uppercase tracking-widest text-red-600 font-mono mb-1">
            Civil Emergency Protection
          </span>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Welcome Back</h1>
          <p className="text-xs text-slate-500 mt-1 font-medium">Stay protected. Stay connected.</p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div
            role="alert"
            className="mb-5 flex items-start gap-2.5 p-3.5 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium animate-fadeIn text-left"
          >
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-600" />
            <div className="flex-1 leading-relaxed">{errorMessage}</div>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-left">
          {/* Email or Phone Input */}
          <div>
            <label htmlFor="login-identifier" className="block text-xs font-semibold text-slate-700 mb-1.5">
              Email or Phone Number
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Mail className="w-4 h-4" />
              </div>
              <input
                id="login-identifier"
                type="text"
                required
                autoComplete="username"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="name@example.com or 9876543210"
                className="w-full pl-10 pr-3.5 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="login-password" className="block text-xs font-semibold text-slate-700">
                Password
              </label>
              <button
                type="button"
                onClick={() => setShowForgotModal(true)}
                className="text-[11px] font-bold text-red-600 hover:text-red-700 transition-colors focus:outline-none"
              >
                Forgot password?
              </button>
            </div>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full pl-10 pr-10 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500/30 focus:border-red-500 focus:bg-white transition-all shadow-sm"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember Me Checkbox */}
          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded-md border-slate-300 text-red-600 focus:ring-red-500/30 cursor-pointer accent-red-600"
              />
              <span className="text-xs font-medium text-slate-600">Remember this device</span>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-3.5 px-4 rounded-2xl bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold text-xs shadow-lg shadow-red-600/25 hover:shadow-red-600/35 transition-all flex items-center justify-center gap-2 disabled:opacity-60 focus:outline-none focus:ring-2 focus:ring-red-500/50"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating with Emergency Command...</span>
              </>
            ) : (
              <span>Sign In &rarr;</span>
            )}
          </button>
        </form>

        {/* Bottom Switcher */}
        <div className="mt-6 pt-5 border-t border-slate-100 text-center">
          <p className="text-xs text-slate-500">
            Don't have an account?{' '}
            <Link to="/signup" className="font-bold text-red-600 hover:text-red-700 transition-colors">
              Create Account
            </Link>
          </p>
        </div>

        {/* Emergency First-Bypass Direct Link */}
        <div className="mt-4 pt-3 text-center">
          <Link
            to="/emergency"
            className="inline-flex items-center gap-1.5 text-[11px] font-bold text-slate-500 hover:text-red-600 bg-slate-100 hover:bg-red-50 px-3 py-1.5 rounded-full transition-all border border-slate-200 hover:border-red-200"
          >
            <LifeBuoy className="w-3.5 h-3.5 text-red-600" />
            <span>Immediate Life Distress? Tap for Offline SOS</span>
          </Link>
        </div>
      </AuthCard>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl border border-slate-200 text-left space-y-3">
            <h3 className="text-sm font-bold text-slate-900">Emergency Account Recovery</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              If you have forgotten your password, your account can be verified directly via emergency SMS or
              by contacting your local Disaster Command Center officer at helpline{' '}
              <strong className="text-slate-900">1077</strong>.
            </p>
            <p className="text-[11px] text-slate-500">
              In an active flood or hazard scenario, use the <strong>Offline SOS</strong> button below to
              signal rescue teams immediately without password verification.
            </p>
            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setShowForgotModal(false)}
                className="py-2 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
