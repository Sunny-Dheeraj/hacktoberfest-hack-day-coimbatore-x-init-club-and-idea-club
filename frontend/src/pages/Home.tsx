import React, { useState, useEffect } from 'react';
import { RoleSummary } from '../types';
import { api } from '../services/api';
import { Shield, ArrowRight, Loader2, GitBranch, Terminal, Award } from 'lucide-react';

interface HomeProps {
  onAnalyze: (username: string, roleId: string) => void;
  loading: boolean;
}

export const Home: React.FC<HomeProps> = ({ onAnalyze, loading }) => {
  const [username, setUsername] = useState('torvalds');
  const [roles, setRoles] = useState<RoleSummary[]>([]);
  const [selectedRole, setSelectedRole] = useState('ml_engineer');
  const [fetchingRoles, setFetchingRoles] = useState(true);

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      const data = await api.getRoles();
      setRoles(data.roles);
      if (data.roles.length > 0) {
        setSelectedRole(data.roles[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setFetchingRoles(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim()) {
      onAnalyze(username.trim(), selectedRole);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:py-20 space-y-12 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-900/40 text-xs font-mono font-medium text-green-700 dark:text-green-300">
          <Shield className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
          <span>Core Principle: NO EVIDENCE → NO CLAIM</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight">
          Prove your skills through your code.
        </h1>

        <p className="max-w-xl mx-auto text-sm sm:text-base text-gray-600 dark:text-dark-muted leading-relaxed">
          ProofPath deterministically analyzes your public GitHub repositories, uncovers verified code evidence, benchmarks your readiness against industry career roles, and tests missing skills.
        </p>
      </div>

      {/* Main Analysis Input Box */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-6 sm:p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-gray-700 dark:text-dark-text mb-1.5">
                GitHub Username
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-gray-400 font-mono text-sm">@</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. torvalds"
                  required
                  disabled={loading}
                  className="w-full pl-8 pr-3 py-2.5 text-sm font-mono bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-md text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-gray-700 dark:text-dark-text mb-1.5">
                Target Career Role
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                disabled={loading || fetchingRoles}
                className="w-full px-3 py-2.5 text-sm bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-md text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title} ({r.core_skill_count} core skills)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Quick Demo Pre-fills */}
          <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-dark-muted pt-1">
            <span className="font-mono text-[11px]">Quick samples:</span>
            {['torvalds', 'tiangolo', 'octocat'].map((u) => (
              <button
                key={u}
                type="button"
                onClick={() => setUsername(u)}
                className="font-mono text-xs text-blue-600 dark:text-blue-400 hover:underline"
              >
                @{u}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading || !username.trim()}
            className="w-full mt-2 py-3 px-4 rounded-md bg-green-600 hover:bg-green-700 text-white font-medium text-sm transition-colors flex items-center justify-center space-x-2 shadow-sm disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Extracting Deterministic Evidence & Calculating Readiness...</span>
              </>
            ) : (
              <>
                <span>Analyze with ProofPath</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* 4 Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 text-left">
        <div className="p-4 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-card space-y-2">
          <div className="p-2 rounded bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400 w-fit">
            <Shield className="w-4 h-4" />
          </div>
          <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
            Deterministic Evidence
          </h3>
          <p className="text-xs text-gray-500 dark:text-dark-muted leading-relaxed">
            Parses AST trees, decorators, and imports without code execution. Exact file and line traceability.
          </p>
        </div>

        <div className="p-4 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-card space-y-2">
          <div className="p-2 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 w-fit">
            <Terminal className="w-4 h-4" />
          </div>
          <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
            Monaco Code Challenges
          </h3>
          <p className="text-xs text-gray-500 dark:text-dark-muted leading-relaxed">
            Test missing skills in real interactive editor. Graded statically through AST syntax inspection.
          </p>
        </div>

        <div className="p-4 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-card space-y-2">
          <div className="p-2 rounded bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-400 w-fit">
            <GitBranch className="w-4 h-4" />
          </div>
          <h3 className="font-semibold text-sm text-gray-900 dark:text-white">
            GitHub Static Verification
          </h3>
          <p className="text-xs text-gray-500 dark:text-dark-muted leading-relaxed">
            Complete practical missions in real repositories. Automatic static verification awards verified proof.
          </p>
        </div>
      </div>
    </div>
  );
};
