import React from 'react';
import { ReadinessScore } from '../../types';

interface ReadinessMeterProps {
  readiness: ReadinessScore;
  roleTitle: string;
}

export const ReadinessMeter: React.FC<ReadinessMeterProps> = ({ readiness, roleTitle }) => {
  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600 dark:text-green-400';
    if (score >= 45) return 'text-amber-600 dark:text-amber-400';
    return 'text-rose-600 dark:text-rose-400';
  };

  const getBarColor = (score: number) => {
    if (score >= 75) return 'bg-green-600 dark:bg-green-500';
    if (score >= 45) return 'bg-amber-500 dark:bg-amber-400';
    return 'bg-rose-500 dark:bg-rose-400';
  };

  return (
    <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wider font-mono text-gray-500 dark:text-dark-muted mb-1">
            Deterministic Role Readiness
          </div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
            <span>{roleTitle}</span>
          </h2>
          <p className="text-xs text-gray-500 dark:text-dark-muted mt-0.5">
            Calculated from verified code evidence. Core skills weighted 2.0x, Supporting 1.0x.
          </p>
        </div>

        <div className="flex items-baseline space-x-2 self-start sm:self-auto">
          <span className={`text-4xl font-extrabold font-mono tracking-tight ${getScoreColor(readiness.score)}`}>
            {readiness.score}%
          </span>
          <span className="text-xs text-gray-400 font-mono">
            ({readiness.earned} / {readiness.max_possible} pts)
          </span>
        </div>
      </div>

      {/* Primary Progress Bar */}
      <div className="w-full bg-gray-100 dark:bg-dark-bg h-2 rounded-full overflow-hidden mt-4">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${getBarColor(readiness.score)}`}
          style={{ width: `${Math.min(100, Math.max(0, readiness.score))}%` }}
        />
      </div>

      {/* Sub-breakdown metrics */}
      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100 dark:border-dark-border text-xs">
        <div>
          <div className="flex justify-between items-center text-gray-600 dark:text-dark-muted mb-1">
            <span className="font-medium">Core Skills Readiness (2.0x)</span>
            <span className="font-mono font-semibold text-gray-900 dark:text-white">{readiness.core_score}%</span>
          </div>
          <div className="w-full bg-gray-100 dark:bg-dark-bg h-1.5 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 dark:bg-blue-500 rounded-full"
              style={{ width: `${Math.min(100, Math.max(0, readiness.core_score))}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center text-gray-600 dark:text-dark-muted mb-1">
            <span className="font-medium">Supporting Skills (1.0x)</span>
            <span className="font-mono font-semibold text-gray-900 dark:text-white">{readiness.supporting_score}%</span>
          </div>
          <div className="w-full bg-gray-100 dark:bg-dark-bg h-1.5 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 dark:bg-indigo-500 rounded-full"
              style={{ width: `${Math.min(100, Math.max(0, readiness.supporting_score))}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
