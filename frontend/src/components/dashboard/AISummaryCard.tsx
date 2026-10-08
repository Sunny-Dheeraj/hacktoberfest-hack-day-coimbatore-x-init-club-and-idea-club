import React from 'react';
import { AIInsight } from '../../types';
import { Cpu, CheckCircle2, AlertTriangle, Lightbulb } from 'lucide-react';

interface AISummaryCardProps {
  insight?: AIInsight;
}

export const AISummaryCard: React.FC<AISummaryCardProps> = ({ insight }) => {
  if (!insight) return null;

  return (
    <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5 transition-colors">
      <div className="flex items-center justify-between border-b border-gray-100 dark:border-dark-border pb-3 mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-1 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-900 dark:text-white">
              Gemma 4 Career Intelligence Interpretation
            </h3>
            <span className="text-[11px] font-mono text-gray-400">
              Code proves. AI interprets. Model: {insight.model_used || 'gemma-4-26b-a4b-it-maas'}
            </span>
          </div>
        </div>

        {insight.fallback_used ? (
          <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900/60">
            Deterministic Synthesis Fallback
          </span>
        ) : (
          <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-900/60">
            Gemma 4 Grounded Inference
          </span>
        )}
      </div>

      {/* Summary Narrative */}
      <p className="text-xs sm:text-sm text-gray-700 dark:text-dark-text leading-relaxed mb-4">
        {insight.summary}
      </p>

      {/* Strengths, Gaps, Recommendations in 3 clean columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-3 border-t border-gray-100 dark:border-dark-border text-xs">
        {/* Grounded Strengths */}
        <div>
          <div className="flex items-center space-x-1.5 font-semibold text-green-700 dark:text-green-400 mb-2">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Verified Strengths</span>
          </div>
          <ul className="space-y-1.5 text-gray-600 dark:text-dark-muted">
            {insight.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start space-x-1.5">
                <span className="text-green-500 font-mono">•</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Identified Gaps */}
        <div>
          <div className="flex items-center space-x-1.5 font-semibold text-amber-700 dark:text-amber-400 mb-2">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Target Role Gaps</span>
          </div>
          <ul className="space-y-1.5 text-gray-600 dark:text-dark-muted">
            {insight.gaps.map((gap, idx) => (
              <li key={idx} className="flex items-start space-x-1.5">
                <span className="text-amber-500 font-mono">•</span>
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actionable Recommendations */}
        <div>
          <div className="flex items-center space-x-1.5 font-semibold text-blue-700 dark:text-blue-400 mb-2">
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Next Action Recommendations</span>
          </div>
          <ul className="space-y-1.5 text-gray-600 dark:text-dark-muted">
            {insight.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start space-x-1.5">
                <span className="text-blue-500 font-mono">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
