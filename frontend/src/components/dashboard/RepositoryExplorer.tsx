import React from 'react';
import { RepositorySummary } from '../../types';
import { FolderGit2, Star, GitFork, FileCode, ExternalLink, Code2 } from 'lucide-react';

interface RepositoryExplorerProps {
  repositories: RepositorySummary[];
  username: string;
  onSelectSkill?: (skill: string) => void;
}

export const RepositoryExplorer: React.FC<RepositoryExplorerProps> = ({
  repositories,
  username,
  onSelectSkill,
}) => {
  if (!repositories || repositories.length === 0) {
    return (
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-8 text-center text-gray-500 dark:text-dark-muted">
        No public repositories were analyzed.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
            <FolderGit2 className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span>Public Repository Explorer</span>
          </h2>
          <p className="text-xs text-gray-500 dark:text-dark-muted font-mono mt-0.5">
            Inspected source files and detected signals from {repositories.length} public repositories.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {repositories.map((repo) => {
          const repoUrl = `https://github.com/${username}/${repo.name}`;
          return (
            <div
              key={repo.name}
              className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-5 shadow-sm hover:border-gray-300 dark:hover:border-gray-700 transition-all space-y-3"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <a
                    href={repoUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="font-bold text-base text-gray-900 dark:text-white hover:text-green-600 dark:hover:text-green-400 flex items-center space-x-1.5 transition-colors"
                  >
                    <span>{repo.name}</span>
                    <ExternalLink className="w-3.5 h-3.5 opacity-60" />
                  </a>
                  {repo.description ? (
                    <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                      {repo.description}
                    </p>
                  ) : (
                    <p className="text-xs text-gray-400 italic mt-1">
                      No description provided
                    </p>
                  )}
                </div>

                {repo.language && (
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-dark-bg text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-dark-border shrink-0">
                    {repo.language}
                  </span>
                )}
              </div>

              {/* Repo Stats */}
              <div className="flex items-center space-x-4 text-xs font-mono text-gray-500 dark:text-dark-muted pt-1">
                <span className="flex items-center space-x-1">
                  <Star className="w-3.5 h-3.5 text-amber-500" />
                  <span>{repo.stars}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <GitFork className="w-3.5 h-3.5 text-blue-500" />
                  <span>{repo.forks}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <FileCode className="w-3.5 h-3.5 text-purple-500" />
                  <span>{repo.files_analyzed} files analyzed</span>
                </span>
              </div>

              {/* Detected Skills in this repo */}
              {repo.detected_skills && repo.detected_skills.length > 0 && (
                <div className="pt-2 border-t border-gray-100 dark:border-dark-border">
                  <div className="text-[11px] font-mono uppercase tracking-wider text-gray-400 dark:text-dark-muted mb-1.5 flex items-center space-x-1">
                    <Code2 className="w-3 h-3" />
                    <span>Evidence Contributed:</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {repo.detected_skills.map((skill) => (
                      <button
                        key={skill}
                        onClick={() => onSelectSkill && onSelectSkill(skill)}
                        className="text-xs font-mono px-2 py-0.5 rounded bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-900/40 hover:bg-green-100 dark:hover:bg-green-900/60 transition-colors"
                      >
                        {skill}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
