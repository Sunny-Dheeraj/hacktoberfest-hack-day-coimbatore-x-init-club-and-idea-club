import React from 'react';
import { SkillAssessment } from '../../types';
import { ShieldCheck, BookOpen, CheckSquare, GitBranch, Check, X, MapPin } from 'lucide-react';

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
        return 'bg-green-100 dark:bg-green-950/60 text-green-800 dark:text-green-300 border-green-300 dark:border-green-800';
      case 'partial':
        return 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800';
      default:
        return 'bg-gray-100 dark:bg-dark-card text-gray-700 dark:text-gray-400 border-gray-300 dark:border-dark-border';
    }
  };

  const evidenceFound = assessment.evidence_found || [];
  const missingEvidence = assessment.missing_evidence || [];
  const locations = assessment.evidence_locations || [];

  return (
    <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-5 transition-all hover:shadow-sm hover:border-gray-300 dark:hover:border-gray-600 flex flex-col justify-between space-y-4">
      <div>
        {/* Top Header: Skill Name & Core Tag */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <h4 className="font-bold text-gray-900 dark:text-white text-base">
              {assessment.skill}
            </h4>
            {assessment.is_core ? (
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-950/50 text-blue-800 dark:text-blue-300 border border-blue-300 dark:border-blue-900/60">
                Core (2.0x)
              </span>
            ) : (
              <span className="text-[10px] font-mono font-medium text-gray-500 dark:text-gray-400 px-1.5 py-0.5 rounded bg-gray-100 dark:bg-dark-bg border border-gray-200 dark:border-dark-border">
                Supporting (1.0x)
              </span>
            )}
          </div>

          {/* Status Badge */}
          <span
            className={`text-xs font-mono uppercase font-bold px-2.5 py-0.5 rounded border ${getBadgeStyle()}`}
          >
            {assessment.classification}
          </span>
        </div>

        {/* Evidence Strength Meter (5-dots) */}
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 my-2.5">
          <span className="font-mono text-xs font-semibold">
            Evidence Level {assessment.evidence_strength}/5
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

        {/* Section 17 Detailed Explanation: Evidence Found & Missing */}
        <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-dark-border text-xs">
          {evidenceFound.length > 0 && (
            <div className="space-y-1">
              <span className="font-mono text-[10px] uppercase font-bold text-green-700 dark:text-green-400 flex items-center space-x-1">
                <span>Evidence Verified:</span>
              </span>
              <ul className="space-y-0.5">
                {evidenceFound.slice(0, 2).map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-1.5 text-gray-700 dark:text-gray-300">
                    <Check className="w-3.5 h-3.5 text-green-600 dark:text-green-400 shrink-0 mt-0.5" />
                    <span className="line-clamp-1">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {missingEvidence.length > 0 && assessment.classification !== 'proven' && (
            <div className="space-y-1 pt-1">
              <span className="font-mono text-[10px] uppercase font-bold text-amber-700 dark:text-amber-400 flex items-center space-x-1">
                <span>Missing for Next Tier:</span>
              </span>
              <ul className="space-y-0.5">
                {missingEvidence.slice(0, 2).map((item, idx) => (
                  <li key={idx} className="flex items-start space-x-1.5 text-gray-600 dark:text-gray-400">
                    <X className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                    <span className="line-clamp-1">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Locations if present */}
          {locations.length > 0 && (
            <div className="flex items-center space-x-1 text-[11px] font-mono text-gray-500 dark:text-gray-400 pt-1 truncate">
              <MapPin className="w-3 h-3 text-gray-400 shrink-0" />
              <span className="truncate">{locations[0]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-3 border-t border-gray-100 dark:border-dark-border text-xs">
        {assessment.evidence_count > 0 ? (
          <button
            onClick={() => onViewEvidence(assessment.skill)}
            className="px-2.5 py-2 rounded-lg border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-800 dark:text-gray-200 font-medium transition-colors flex items-center justify-center space-x-1.5"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
            <span>Trace ({assessment.evidence_count})</span>
          </button>
        ) : (
          <button
            onClick={() => onLearn(assessment.skill)}
            className="px-2.5 py-2 rounded-lg border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-800 dark:text-gray-200 font-medium transition-colors flex items-center justify-center space-x-1.5"
          >
            <BookOpen className="w-3.5 h-3.5 text-blue-500" />
            <span>Learn</span>
          </button>
        )}

        <button
          onClick={() => onTakeQuiz(assessment.skill)}
          className="px-2.5 py-2 rounded-lg border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-800 dark:text-gray-200 font-medium transition-colors flex items-center justify-center space-x-1.5"
        >
          <CheckSquare className="w-3.5 h-3.5 text-emerald-500" />
          <span>Assess</span>
        </button>

        <button
          onClick={() => onMission(assessment.skill)}
          className="col-span-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-dark-bg hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-900 dark:text-white font-medium border border-gray-200 dark:border-dark-border transition-colors flex items-center justify-center space-x-1.5"
        >
          <GitBranch className="w-3.5 h-3.5 text-purple-500" />
          <span>Practical Mission & Verification</span>
        </button>
      </div>
    </div>
  );
};
