import React from 'react';
import { EvidenceItem } from '../../types';
import { X, FileCode, CheckCircle, Shield } from 'lucide-react';

interface EvidenceModalProps {
  skill: string;
  evidenceItems: EvidenceItem[];
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ skill, evidenceItems, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 dark:border-dark-border">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded bg-green-100 dark:bg-green-950/60 text-green-700 dark:text-green-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-gray-900 dark:text-white">
                Traceable Evidence: {skill}
              </h3>
              <p className="text-xs text-gray-500 dark:text-dark-muted font-mono">
                Verified repository code traces proving competence
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-gray-400 hover:text-gray-700 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-dark-bg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Scrollable Evidence Items */}
        <div className="p-6 overflow-y-auto space-y-4">
          {evidenceItems.length === 0 ? (
            <div className="text-center py-8 text-sm text-gray-500 dark:text-dark-muted">
              No direct code evidence items found for this skill.
            </div>
          ) : (
            evidenceItems.map((item, idx) => (
              <div
                key={idx}
                className="border border-gray-200 dark:border-dark-border rounded-lg p-4 bg-gray-50/50 dark:bg-dark-bg/40 space-y-2.5"
              >
                {/* File Location & Strength Badge */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs font-mono font-medium text-gray-800 dark:text-dark-text truncate">
                    <FileCode className="w-4 h-4 text-gray-400 shrink-0" />
                    <span className="text-blue-600 dark:text-blue-400 font-semibold">{item.repository}</span>
                    <span className="text-gray-400">/</span>
                    <span className="truncate">{item.file || 'repository root'}</span>
                    {item.line_start !== undefined && item.line_start !== null && (
                      <span className="text-gray-400 text-[11px]">
                        #L{item.line_start}
                        {item.line_end ? `-L${item.line_end}` : ''}
                      </span>
                    )}
                  </div>

                  <span className="shrink-0 text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-dark-card border border-gray-200 dark:border-dark-border font-medium text-gray-700 dark:text-dark-muted">
                    Strength Level {item.strength}/5 ({item.evidence_type})
                  </span>
                </div>

                {/* Technical Finding / Explanation */}
                <p className="text-xs text-gray-700 dark:text-dark-text leading-relaxed">
                  {item.explanation}
                </p>

                {/* Signals Tags */}
                {item.signals && item.signals.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="text-[10px] font-mono text-gray-400 py-0.5">Signals:</span>
                    {item.signals.map((sig, sIdx) => (
                      <span
                        key={sIdx}
                        className="text-[11px] font-mono bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border px-1.5 py-0.5 rounded text-gray-800 dark:text-dark-text"
                      >
                        {sig}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-gray-100 dark:border-dark-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
          >
            Close Explorer
          </button>
        </div>
      </div>
    </div>
  );
};
