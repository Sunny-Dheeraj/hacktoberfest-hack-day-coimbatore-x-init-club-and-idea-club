import React from 'react';
import { NextBestAction } from '../../types';
import { ArrowRight, AlertCircle, BookOpen, CheckSquare, GitBranch, Terminal } from 'lucide-react';

interface NextBestActionBannerProps {
  action?: NextBestAction;
  onActionClick: (actionType: string, skill: string) => void;
}

export const NextBestActionBanner: React.FC<NextBestActionBannerProps> = ({ action, onActionClick }) => {
  if (!action) return null;

  const getActionIcon = () => {
    switch (action.action_type) {
      case 'quiz':
        return <CheckSquare className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
      case 'code_challenge':
        return <Terminal className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
      case 'practical_mission':
        return <GitBranch className="w-4 h-4 text-purple-600 dark:text-purple-400" />;
      default:
        return <BookOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />;
    }
  };

  const getButtonLabel = () => {
    switch (action.action_type) {
      case 'quiz':
        return `Start ${action.skill} Assessment`;
      case 'code_challenge':
        return `Implement ${action.skill} Challenge`;
      case 'practical_mission':
        return `Deploy & Verify Mission`;
      default:
        return `Learn ${action.skill}`;
    }
  };

  return (
    <div className="bg-amber-50/70 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/40 rounded-lg p-4 transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start space-x-3">
          <div className="p-1.5 bg-amber-100 dark:bg-amber-900/40 rounded mt-0.5">
            {getActionIcon()}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono uppercase tracking-wider font-semibold text-amber-800 dark:text-amber-400">
                Next Best Action
              </span>
              <span className="inline-block w-1 h-1 rounded-full bg-amber-400"></span>
              <span className="text-[11px] text-amber-700 dark:text-amber-300 font-medium">Priority #{action.priority}</span>
            </div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mt-0.5">
              {action.title}
            </h3>
            <p className="text-xs text-gray-600 dark:text-dark-muted mt-0.5">
              {action.reason}
            </p>
          </div>
        </div>

        <button
          onClick={() => onActionClick(action.action_type, action.skill)}
          className="self-start sm:self-auto px-3.5 py-1.5 rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors flex items-center space-x-1.5 whitespace-nowrap shadow-sm"
        >
          <span>{getButtonLabel()}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
