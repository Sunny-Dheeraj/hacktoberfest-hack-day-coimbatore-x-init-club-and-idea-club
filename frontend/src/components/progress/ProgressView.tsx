import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { UserProgressResponse, SkillConfidence } from '../../types';
import { BarChart2, ShieldCheck, HelpCircle, GitBranch, Loader2, ArrowRight } from 'lucide-react';

interface ProgressViewProps {
  username: string;
  roleId: string;
  onTakeAction: (actionType: string, skill: string) => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({ username, roleId, onTakeAction }) => {
  const [progress, setProgress] = useState<UserProgressResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, [username, roleId]);

  const loadProgress = async () => {
    setLoading(true);
    try {
      const data = await api.getProgress(username, roleId);
      setProgress(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin text-green-600 mb-2" />
        <p className="text-sm font-mono">Loading skill confidence records...</p>
      </div>
    );
  }

  if (!progress) return null;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header with Composite Formula Callout */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-green-600 dark:text-green-400 font-semibold">
              ProofPath Tri-Pillar Engine
            </span>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Composite Skill Confidence Tracking
            </h2>
            <p className="text-xs text-gray-500 dark:text-dark-muted mt-0.5">
              Confidence = (Code Evidence × 40%) + (Knowledge Quiz × 30%) + (Practical Ability × 30%)
            </p>
          </div>

          <div className="flex items-baseline space-x-2 self-start sm:self-auto">
            <span className="text-3xl font-extrabold font-mono text-green-600 dark:text-green-400">
              {progress.overall_confidence}%
            </span>
            <span className="text-xs font-mono text-gray-400">Overall Confidence</span>
          </div>
        </div>

        {/* 3 Pillars Explanatory Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-gray-100 dark:border-dark-border text-xs">
          <div className="flex items-center space-x-2.5 p-2 rounded bg-gray-50 dark:bg-dark-bg/60">
            <ShieldCheck className="w-4 h-4 text-green-600 shrink-0" />
            <div>
              <span className="font-semibold text-gray-900 dark:text-white block font-mono">1. Code Evidence (40%)</span>
              <span className="text-[11px] text-gray-500">Deterministic AST repository proof</span>
            </div>
          </div>
          <div className="flex items-center space-x-2.5 p-2 rounded bg-gray-50 dark:bg-dark-bg/60">
            <HelpCircle className="w-4 h-4 text-blue-600 shrink-0" />
            <div>
              <span className="font-semibold text-gray-900 dark:text-white block font-mono">2. Knowledge Quiz (30%)</span>
              <span className="text-[11px] text-gray-500">Conceptual & code reasoning questions</span>
            </div>
          </div>
          <div className="flex items-center space-x-2.5 p-2 rounded bg-gray-50 dark:bg-dark-bg/60">
            <GitBranch className="w-4 h-4 text-purple-600 shrink-0" />
            <div>
              <span className="font-semibold text-gray-900 dark:text-white block font-mono">3. Practical Ability (30%)</span>
              <span className="text-[11px] text-gray-500">Monaco code challenge & GitHub missions</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tracked Skills Table */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 dark:border-dark-border flex items-center justify-between">
          <h3 className="text-sm font-bold text-gray-900 dark:text-white">
            Skill Confidence Breakdown ({progress.skills.length} tracked)
          </h3>
          <span className="text-xs font-mono text-gray-400">Candidate: @{username}</span>
        </div>

        {progress.skills.length === 0 ? (
          <div className="p-8 text-center text-xs text-gray-500">
            No skill progress records saved yet. Complete an assessment or repository analysis to track skills.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-50 dark:bg-dark-bg/60 font-mono text-gray-500 uppercase text-[10px] border-b border-gray-100 dark:border-dark-border">
                <tr>
                  <th className="px-5 py-3">Skill</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Code (40%)</th>
                  <th className="px-4 py-3">Quiz (30%)</th>
                  <th className="px-4 py-3">Practical (30%)</th>
                  <th className="px-4 py-3">Confidence</th>
                  <th className="px-5 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-dark-border font-mono">
                {progress.skills.map((s) => (
                  <tr key={s.skill} className="hover:bg-gray-50/50 dark:hover:bg-dark-bg/30 transition-colors">
                    <td className="px-5 py-3 font-semibold text-gray-900 dark:text-white font-sans text-xs">
                      {s.skill}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-[10px] px-2 py-0.5 rounded font-medium capitalize bg-gray-100 dark:bg-dark-bg text-gray-700 dark:text-dark-muted border border-gray-200 dark:border-dark-border">
                        {s.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-dark-text">
                      {s.code_score}%
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-dark-text">
                      {s.quiz_score}%
                    </td>
                    <td className="px-4 py-3 text-gray-700 dark:text-dark-text">
                      {s.practical_score}%
                    </td>
                    <td className="px-4 py-3 font-bold text-green-600 dark:text-green-400">
                      {s.confidence}%
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => onTakeAction('quiz', s.skill)}
                        className="px-2.5 py-1 rounded bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-[11px] font-sans font-medium hover:bg-gray-800 transition-colors inline-flex items-center space-x-1"
                      >
                        <span>Reinforce</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
