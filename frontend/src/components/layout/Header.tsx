import React from 'react';
import { ThemeToggle } from '../common/ThemeToggle';
import { GitBranch, ShieldCheck, Compass, BookOpen, CheckSquare, BarChart2, RefreshCw, FolderGit2 } from 'lucide-react';

interface HeaderProps {
  username?: string;
  roleTitle?: string;
  currentTab: string;
  onSelectTab: (tab: string) => void;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  username,
  roleTitle,
  currentTab,
  onSelectTab,
  onReset,
}) => {
  return (
    <header className="border-b border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg sticky top-0 z-30 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
            <div className="flex items-center justify-center w-7 h-7 rounded bg-green-600 text-white font-mono font-bold text-sm">
              P
            </div>
            <div className="flex items-baseline space-x-2">
              <span className="font-semibold tracking-tight text-gray-900 dark:text-white text-base">ProofPath</span>
              <span className="text-[11px] font-mono text-gray-500 dark:text-dark-muted hidden sm:inline">NO EVIDENCE → NO CLAIM</span>
            </div>
          </div>

          {/* Navigation Links */}
          {username && (
            <nav className="hidden md:flex items-center space-x-1">
              <button
                onClick={() => onSelectTab('dashboard')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'dashboard'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white font-semibold'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <Compass className="w-3.5 h-3.5" />
                <span>Dashboard</span>
              </button>
              <button
                onClick={() => onSelectTab('repos')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'repos'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white font-semibold'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <FolderGit2 className="w-3.5 h-3.5" />
                <span>Repositories</span>
              </button>
              <button
                onClick={() => onSelectTab('evidence')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'evidence'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white font-semibold'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Evidence</span>
              </button>
              <button
                onClick={() => onSelectTab('learning')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'learning'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Roadmap</span>
              </button>
              <button
                onClick={() => onSelectTab('quiz')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'quiz'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <CheckSquare className="w-3.5 h-3.5" />
                <span>Assessment</span>
              </button>
              <button
                onClick={() => onSelectTab('mission')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'mission'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <GitBranch className="w-3.5 h-3.5" />
                <span>Mission</span>
              </button>
              <button
                onClick={() => onSelectTab('progress')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  currentTab === 'progress'
                    ? 'bg-gray-100 dark:bg-dark-card text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-dark-muted hover:text-gray-900 dark:hover:text-dark-text'
                }`}
              >
                <BarChart2 className="w-3.5 h-3.5" />
                <span>Progress</span>
              </button>
            </nav>
          )}

          {/* Right Side: Active Candidate Badge, ThemeToggle, Reset */}
          <div className="flex items-center space-x-3">
            {username && (
              <div className="hidden sm:flex items-center space-x-2 text-xs border border-gray-200 dark:border-dark-border px-2.5 py-1 rounded-md bg-gray-50 dark:bg-dark-card">
                <span className="font-mono text-gray-500 dark:text-dark-muted">@{username}</span>
                {roleTitle && (
                  <span className="text-gray-400 dark:text-dark-border">/</span>
                )}
                {roleTitle && (
                  <span className="font-medium text-gray-700 dark:text-dark-text">{roleTitle}</span>
                )}
              </div>
            )}

            {username && (
              <button
                onClick={onReset}
                className="p-1.5 rounded-md border border-gray-200 dark:border-dark-border text-gray-500 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-dark-card transition-colors text-xs flex items-center space-x-1"
                title="Analyze Another Profile"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span className="hidden lg:inline">Switch</span>
              </button>
            )}

            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
};
