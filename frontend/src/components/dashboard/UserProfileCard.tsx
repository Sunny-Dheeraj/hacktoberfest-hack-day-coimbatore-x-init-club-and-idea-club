import React from 'react';
import { GitHubProfile } from '../../types';
import { GitBranch, FolderGit2, ShieldCheck, ExternalLink, Info } from 'lucide-react';

interface UserProfileCardProps {
  profile?: GitHubProfile;
  username: string;
  roleTitle?: string;
  repositoriesAnalyzed: number;
  totalPublicRepos: number;
  evidenceCount: number;
  coverageSummary?: string;
}

export const UserProfileCard: React.FC<UserProfileCardProps> = ({
  profile,
  username,
  roleTitle,
  repositoriesAnalyzed,
  totalPublicRepos,
  evidenceCount,
  coverageSummary,
}) => {
  const avatarUrl = profile?.avatar_url || `https://github.com/${username}.png`;
  const name = profile?.name || username;
  const bio = profile?.bio;
  const githubUrl = profile?.html_url || `https://github.com/${username}`;
  const totalRepos = profile?.public_repos || totalPublicRepos || repositoriesAnalyzed;

  return (
    <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        {/* Profile Info */}
        <div className="flex items-center space-x-4">
          <img
            src={avatarUrl}
            alt={username}
            className="w-16 h-16 rounded-full border-2 border-green-500/30 object-cover shadow-sm bg-gray-100 dark:bg-dark-bg"
            onError={(e) => {
              // Fallback placeholder if image fails
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {name}
              </h2>
              <a
                href={githubUrl}
                target="_blank"
                rel="noreferrer"
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                title="View on GitHub"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
            <p className="text-xs font-mono text-gray-500 dark:text-dark-muted">
              @{username}
            </p>
            {bio && (
              <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 max-w-xl line-clamp-2">
                {bio}
              </p>
            )}
          </div>
        </div>

        {/* Target Role & Verification State */}
        {roleTitle && (
          <div className="flex sm:flex-col items-start sm:items-end justify-between sm:justify-center border-t sm:border-t-0 pt-3 sm:pt-0 border-gray-100 dark:border-dark-border">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gray-500 dark:text-dark-muted">
              Target Career Role
            </span>
            <span className="text-sm font-semibold text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 px-2.5 py-0.5 rounded border border-green-200 dark:border-green-900/40 mt-0.5">
              {roleTitle}
            </span>
          </div>
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 border-t border-gray-100 dark:border-dark-border">
        <div className="bg-gray-50 dark:bg-dark-bg/60 p-3 rounded-lg border border-gray-200/60 dark:border-dark-border/60">
          <div className="flex items-center space-x-1.5 text-xs text-gray-500 dark:text-dark-muted">
            <FolderGit2 className="w-3.5 h-3.5" />
            <span>Public Repositories</span>
          </div>
          <div className="text-lg font-bold text-gray-900 dark:text-white mt-0.5">
            {totalRepos}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-dark-bg/60 p-3 rounded-lg border border-gray-200/60 dark:border-dark-border/60">
          <div className="flex items-center space-x-1.5 text-xs text-gray-500 dark:text-dark-muted">
            <GitBranch className="w-3.5 h-3.5 text-blue-500" />
            <span>Analyzed for Code</span>
          </div>
          <div className="text-lg font-bold text-gray-900 dark:text-white mt-0.5">
            {repositoriesAnalyzed}
          </div>
        </div>

        <div className="col-span-2 sm:col-span-1 bg-gray-50 dark:bg-dark-bg/60 p-3 rounded-lg border border-gray-200/60 dark:border-dark-border/60">
          <div className="flex items-center space-x-1.5 text-xs text-gray-500 dark:text-dark-muted">
            <ShieldCheck className="w-3.5 h-3.5 text-green-500" />
            <span>Verified Code Signals</span>
          </div>
          <div className="text-lg font-bold text-green-600 dark:text-green-400 mt-0.5">
            {evidenceCount}
          </div>
        </div>
      </div>

      {/* Coverage Transparency Banner */}
      <div className="bg-blue-50/70 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/40 rounded-lg p-3 text-xs text-blue-900 dark:text-blue-300 flex items-start space-x-2">
        <Info className="w-4 h-4 shrink-0 mt-0.5 text-blue-600 dark:text-blue-400" />
        <div>
          <span className="font-semibold">Repository Coverage Transparency: </span>
          <span>
            {coverageSummary || `Analyzed ${repositoriesAnalyzed} of ${totalRepos} public repositories (excluding forks and repositories without supported source code).`}
          </span>
        </div>
      </div>
    </div>
  );
};
