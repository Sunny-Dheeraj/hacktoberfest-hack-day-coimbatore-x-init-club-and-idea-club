import React from 'react';
import { SkillAssessment } from '../../types';
import { ShieldCheck, BookOpen, CheckSquare, GitBranch } from 'lucide-react';

interface SkillCardProps {
  assessment: SkillAssessment;
  onViewEvidence: (skill: string) => void;
  onTakeQuiz: (skill: string) => void;
  onLearn: (skill: string) => void;
  onMission: (skill: string) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({
  assessment,
  onViewEvidence,
  onTakeQuiz,
  onLearn,
  onMission,
}) => {
  const getBadgeStyle = () => {
    switch (assessment.classification) {
      case 'proven':
        return 'bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/60';
      case 'partial':
        return 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/60';
      default:
        return 'bg-gray-50 dark:bg-dark-card text-gray-500 dark:text-dark-muted border-gray-200 dark:border-dark-border';
    }
  };

  return (
    <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-4 transition-all hover:border-gray-300 dark:hover:border-gray-600 flex flex-col justify-between">
      <div>
        {/* Top Header: Skill Name & Core Tag */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
              {assessment.skill}
            </h4>
            {assessment.is_core ? (
              <span className="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/40">
                Core (2.0x)
              </span>
            ) : (
              <span className="text-[10px] font-mono text-gray-400 px-1 py-0.5">
                Supporting (1.0x)
              </span>
            )}
          </div>

          {/* Status Badge */}
          <span
            className={`text-[11px] font-mono uppercase font-semibold px-2 py-0.5 rounded border ${getBadgeStyle()}`}
          >
            {assessment.classification}
          </span>
        </div>

        {/* Evidence Strength Meter (5-dots) */}
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-dark-muted my-3">
          <span className="font-mono text-[11px]">
            Strength Level {assessment.evidence_strength}/5
          </span>
          <div className="flex space-x-1">
            {[1, 2, 3, 4, 5].map((lvl) => (
              <span
                key={lvl}
                className={`inline-block w-2.5 h-2.5 rounded-full ${
                  lvl <= assessment.evidence_strength
                    ? assessment.classification === 'proven'
                      ? 'bg-green-600 dark:bg-green-500'
                      : 'bg-amber-500 dark:bg-amber-400'
                    : 'bg-gray-200 dark:bg-dark-border'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Evidence details preview if available */}
        {assessment.top_evidence && assessment.top_evidence.length > 0 ? (
          <div className="bg-gray-50 dark:bg-dark-bg/60 rounded p-2 text-xs font-mono text-gray-600 dark:text-dark-muted truncate border border-gray-100 dark:border-dark-border mb-3">
            <span className="text-gray-400">file:</span> {assessment.top_evidence[0].file || 'repo'}
          </div>
        ) : (
          <div className="text-[11px] text-gray-400 italic mb-3">
            No source code evidence detected in repositories.
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-1.5 pt-2 border-t border-gray-100 dark:border-dark-border text-xs">
        {assessment.evidence_count > 0 ? (
          <button
            onClick={() => onViewEvidence(assessment.skill)}
            className="px-2.5 py-1.5 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-700 dark:text-dark-text transition-colors flex items-center justify-center space-x-1"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
            <span>Trace ({assessment.evidence_count})</span>
          </button>
        ) : (
          <button
            onClick={() => onLearn(assessment.skill)}
            className="px-2.5 py-1.5 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-700 dark:text-dark-text transition-colors flex items-center justify-center space-x-1"
          >
            <BookOpen className="w-3.5 h-3.5 text-blue-500" />
            <span>Learn</span>
          </button>
        )}

        <button
          onClick={() => onTakeQuiz(assessment.skill)}
          className="px-2.5 py-1.5 rounded border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-700 dark:text-dark-text transition-colors flex items-center justify-center space-x-1"
        >
          <CheckSquare className="w-3.5 h-3.5 text-emerald-500" />
          <span>Assess</span>
        </button>

        <button
          onClick={() => onMission(assessment.skill)}
          className="col-span-2 px-2.5 py-1.5 rounded bg-gray-100 dark:bg-dark-border hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-800 dark:text-white transition-colors flex items-center justify-center space-x-1 font-medium"
        >
          <GitBranch className="w-3.5 h-3.5 text-purple-500" />
          <span>Practical Mission & Verification</span>
        </button>
      </div>
    </div>
  );
};
