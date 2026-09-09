import React from 'react';
import { Check } from 'lucide-react';

interface ProgressStepIndicatorProps {
  currentStep: 1 | 2 | 3;
}

export const ProgressStepIndicator: React.FC<ProgressStepIndicatorProps> = ({ currentStep }) => {
  const steps = [
    { num: 1, label: 'Account' },
    { num: 2, label: 'Safety Profile' },
    { num: 3, label: 'Complete' },
  ];

  return (
    <div className="w-full mb-6">
      <div className="flex items-center justify-between relative">
        {/* Connecting Progress Track */}
        <div className="absolute left-6 right-6 top-4 h-[2px] bg-slate-200 -z-0" />
        <div
          className="absolute left-6 top-4 h-[2px] bg-red-600 transition-all duration-500 ease-out -z-0"
          style={{
            width: currentStep === 1 ? '0%' : currentStep === 2 ? '50%' : '100%',
          }}
        />

        {steps.map((step) => {
          const isCompleted = step.num < currentStep;
          const isCurrent = step.num === currentStep;

          return (
            <div key={step.num} className="flex flex-col items-center relative z-10">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 shadow-sm ${
                  isCompleted
                    ? 'bg-red-600 text-white shadow-red-500/20'
                    : isCurrent
                    ? 'bg-white text-red-600 border-2 border-red-600 shadow-md ring-4 ring-red-50'
                    : 'bg-slate-100 text-slate-400 border border-slate-200'
                }`}
              >
                {isCompleted ? <Check className="w-4 h-4 stroke-[3]" /> : `0${step.num}`}
              </div>
              <span
                className={`text-[11px] font-medium mt-1.5 transition-colors ${
                  isCurrent ? 'text-slate-900 font-bold' : isCompleted ? 'text-slate-700' : 'text-slate-400'
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
