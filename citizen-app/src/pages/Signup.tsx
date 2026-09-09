import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AuthNetworkBackground } from '../components/auth/AuthNetworkBackground';
import { AuthCard } from '../components/auth/AuthCard';
import { ProgressStepIndicator } from '../components/auth/ProgressStepIndicator';
import { StepAccount } from '../components/auth/StepAccount';
import { StepSafetyProfile } from '../components/auth/StepSafetyProfile';
import { StepProtectedSuccess } from '../components/auth/StepProtectedSuccess';
import { SafetyProfileData } from '../services/auth/authService';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();

  const [currentStep, setCurrentStep] = useState<1 | 2 | 3>(1);
  const [accountData, setAccountData] = useState({
    name: '',
    emailOrPhone: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  React.useEffect(() => {
    if (isAuthenticated && currentStep !== 3) {
      navigate('/');
    }
  }, [isAuthenticated, currentStep, navigate]);

  const handleStep1Continue = (data: { name: string; emailOrPhone: string; password: string }) => {
    setAccountData(data);
    setErrorMessage(null);
    setCurrentStep(2);
  };

  const handleStep2Submit = async (safetyProfile: SafetyProfileData) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      await register(accountData.name, accountData.emailOrPhone, accountData.password, safetyProfile);
      setCurrentStep(3);
    } catch (err: any) {
      setErrorMessage(
        err.message || 'Unable to complete emergency registration. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-center items-center px-4 py-8 relative bg-[#FAFAFA] text-slate-900 selection:bg-red-500 selection:text-white">
      <AuthNetworkBackground />

      <AuthCard>
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center mb-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-b from-red-500 to-red-600 text-white flex items-center justify-center shadow-lg shadow-red-500/25 mb-2 border border-red-400/40">
            <Shield className="w-6 h-6 stroke-[2.2]" />
          </div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-red-600 font-mono">
            Citizen Registration
          </span>
        </div>

        {/* 3-Step Progress Indicator */}
        <ProgressStepIndicator currentStep={currentStep} />

        {/* Step 1: Account Credentials */}
        {currentStep === 1 && (
          <StepAccount onContinue={handleStep1Continue} initialData={accountData} />
        )}

        {/* Step 2: Safety Profile */}
        {currentStep === 2 && (
          <StepSafetyProfile
            onBack={() => setCurrentStep(1)}
            onSubmit={handleStep2Submit}
            isLoading={isLoading}
            errorMessage={errorMessage}
          />
        )}

        {/* Step 3: Complete Success Screen */}
        {currentStep === 3 && (
          <StepProtectedSuccess
            userName={accountData.name}
            onEnterDashboard={() => navigate('/')}
          />
        )}

        {/* Bottom Switcher (Only visible in step 1 & 2) */}
        {currentStep !== 3 && (
          <div className="mt-6 pt-4 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="font-bold text-red-600 hover:text-red-700 transition-colors">
                Sign In
              </Link>
            </p>
          </div>
        )}
      </AuthCard>
    </div>
  );
};
