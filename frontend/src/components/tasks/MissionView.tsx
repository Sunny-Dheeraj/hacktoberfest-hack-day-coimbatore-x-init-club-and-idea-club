import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { PracticalTask, TaskVerificationResponse } from '../../types';
import { GitBranch, CheckCircle2, XCircle, AlertCircle, Loader2, ArrowRight, ShieldCheck, FileCheck } from 'lucide-react';

interface MissionViewProps {
  skill: string;
  username: string;
  onVerified?: (newConfidence: number) => void;
}

export const MissionView: React.FC<MissionViewProps> = ({ skill, username, onVerified }) => {
  const [mission, setMission] = useState<PracticalTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState<TaskVerificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMission();
  }, [skill]);

  const loadMission = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.getMission(skill);
      setMission(data);
      // Pre-fill default repo pattern for ease of demonstration
      setRepoUrl(`${username}/${skill.toLowerCase()}-project`);
    } catch (err: any) {
      setError(err.message || 'Failed to load mission.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mission || !repoUrl.trim()) return;

    setVerifying(true);
    setError(null);
    try {
      const res = await api.verifyMission(username, mission.id, skill, repoUrl.trim(), branch.trim() || 'main');
      setResult(res);
      if (onVerified) {
        onVerified(res.updated_confidence);
      }
    } catch (err: any) {
      setError(err.message || 'Static verification failed.');
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600 mb-2" />
        <p className="text-sm font-mono">Loading mission for {skill}...</p>
      </div>
    );
  }

  if (!mission) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Mission Briefing Card */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 dark:border-dark-border pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-purple-600 dark:text-purple-400 font-semibold">
                Practical Mission
              </span>
              <span className="text-gray-300 dark:text-dark-border">•</span>
              <span className="text-xs font-mono text-gray-500 capitalize">{mission.difficulty}</span>
            </div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">
              {mission.title}
            </h2>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-900/40 self-start sm:self-auto font-medium">
            Target Skill: {skill}
          </span>
        </div>

        <p className="text-sm text-gray-700 dark:text-dark-text leading-relaxed">
          {mission.description}
        </p>

        {/* Requirements & Artifacts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
          <div className="border border-gray-200 dark:border-dark-border rounded-lg p-4 bg-gray-50/50 dark:bg-dark-bg/40 space-y-2">
            <span className="font-semibold text-gray-900 dark:text-white flex items-center space-x-1.5 font-mono uppercase text-[11px]">
              <FileCheck className="w-3.5 h-3.5 text-blue-500" />
              <span>Project Requirements</span>
            </span>
            <ul className="space-y-1.5 text-gray-600 dark:text-dark-muted">
              {mission.requirements.map((req, idx) => (
                <li key={idx} className="flex items-start space-x-1.5">
                  <span className="text-blue-500 font-mono">•</span>
                  <span>{req}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="border border-gray-200 dark:border-dark-border rounded-lg p-4 bg-gray-50/50 dark:bg-dark-bg/40 space-y-2">
            <span className="font-semibold text-gray-900 dark:text-white flex items-center space-x-1.5 font-mono uppercase text-[11px]">
              <ShieldCheck className="w-3.5 h-3.5 text-purple-500" />
              <span>Expected Artifacts</span>
            </span>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {mission.expected_artifacts.map((art, idx) => (
                <span
                  key={idx}
                  className="font-mono text-[11px] bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border px-2 py-1 rounded text-gray-800 dark:text-dark-text"
                >
                  {art}
                </span>
              ))}
            </div>
            <p className="text-[11px] text-gray-400 dark:text-dark-muted pt-2 leading-relaxed">
              Static inspection will parse the repository tree and source code AST for verified presence.
            </p>
          </div>
        </div>

        {/* GitHub Verification Form */}
        <div className="border-t border-gray-100 dark:border-dark-border pt-5">
          <form onSubmit={handleVerify} className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1">
                <label className="block text-xs font-mono text-gray-600 dark:text-dark-muted mb-1">
                  GitHub Repository (owner/repo or full URL)
                </label>
                <div className="relative">
                  <GitBranch className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="username/repository-name"
                    required
                    className="w-full pl-9 pr-3 py-2 text-xs font-mono bg-white dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-md text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                  />
                </div>
              </div>

              <div className="w-full sm:w-32">
                <label className="block text-xs font-mono text-gray-600 dark:text-dark-muted mb-1">
                  Branch
                </label>
                <input
                  type="text"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  className="w-full px-3 py-2 text-xs font-mono bg-white dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-md text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <div className="self-end w-full sm:w-auto">
                <button
                  type="submit"
                  disabled={verifying}
                  className="w-full sm:w-auto px-5 py-2 rounded-md bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
                >
                  {verifying ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Inspecting Repository Tree...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4 h-4" />
                      <span>Verify Code via GitHub</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>

          {error && (
            <p className="text-xs text-rose-600 dark:text-rose-400 mt-2 font-mono">{error}</p>
          )}
        </div>
      </div>

      {/* Verification Result Card */}
      {result && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-5 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 dark:border-dark-border pb-3">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400">
                Static Verification Result
              </span>
              <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center space-x-2 mt-0.5">
                <span>Repository: {result.repo_url}</span>
              </h3>
            </div>

            <span
              className={`text-xs font-mono px-3 py-1 rounded font-bold uppercase ${
                result.status === 'verified'
                  ? 'bg-green-100 dark:bg-green-950/60 text-green-700 dark:text-green-400 border border-green-300 dark:border-green-800'
                  : result.status === 'partially_verified'
                  ? 'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800'
                  : 'bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border border-rose-300 dark:border-rose-800'
              }`}
            >
              {result.status.replace('_', ' ')} ({result.score}%)
            </span>
          </div>

          <p className="text-xs text-gray-700 dark:text-dark-text leading-relaxed">
            {result.feedback}
          </p>

          {/* Criteria Checklist */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold font-mono text-gray-700 dark:text-dark-text uppercase">
              Verification Criteria Checklist
            </h4>
            <div className="space-y-1.5">
              {result.criteria.map((crit, idx) => (
                <div
                  key={idx}
                  className="flex items-start justify-between p-2.5 rounded border border-gray-100 dark:border-dark-border text-xs"
                >
                  <div className="flex items-start space-x-2">
                    {crit.passed ? (
                      <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                    )}
                    <div>
                      <span className="font-medium text-gray-900 dark:text-white block">{crit.description}</span>
                      {crit.details && <span className="text-[11px] font-mono text-gray-400">{crit.details}</span>}
                    </div>
                  </div>
                  <span className="font-mono text-[10px] text-gray-400 shrink-0 capitalize">{crit.passed ? 'PASSED' : 'MISSING'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Detected Signals Preview */}
          {result.signals_detected && result.signals_detected.length > 0 && (
            <div className="pt-2">
              <span className="text-[11px] font-mono text-gray-500 block mb-1">Signals verified in repo:</span>
              <div className="flex flex-wrap gap-1.5">
                {result.signals_detected.map((sig, idx) => (
                  <span
                    key={idx}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-dark-bg text-gray-700 dark:text-dark-text border border-gray-200 dark:border-dark-border"
                  >
                    {sig}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
