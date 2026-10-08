import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  Award,
  Zap,
  RotateCcw,
  BookOpen,
  ArrowRight,
  Loader2,
  Code2,
} from 'lucide-react';

interface AdaptiveQuizViewProps {
  skill: string;
  username: string;
}

export const AdaptiveQuizView: React.FC<AdaptiveQuizViewProps> = ({ skill, username }) => {
  const [mode, setMode] = useState<'quick' | 'standard' | 'full' | 'comprehensive'>('quick');
  const [summary, setSummary] = useState<any>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);

  // Active Session State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<any>(null);
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [startingSession, setStartingSession] = useState(false);
  const [completedSession, setCompletedSession] = useState<any>(null);

  useEffect(() => {
    loadBankSummary();
  }, [skill]);

  const loadBankSummary = async () => {
    setLoadingSummary(true);
    try {
      const data = await api.getQuestionBankSummary(skill);
      setSummary(data);
    } catch (err) {
      console.error('Failed to load question bank summary:', err);
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleStartSession = async () => {
    setStartingSession(true);
    setFeedback(null);
    setCompletedSession(null);
    setSelectedOption(null);
    try {
      const data = await api.startAdaptiveAssessment(username, skill, mode);
      setSessionId(data.session_id);
      setCurrentQuestion(data.first_question);
    } catch (err) {
      console.error('Failed to start adaptive session:', err);
    } finally {
      setStartingSession(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!sessionId || !currentQuestion || !selectedOption) return;

    setSubmittingAnswer(true);
    try {
      const res = await api.submitAdaptiveAnswer(
        sessionId,
        currentQuestion.question_id,
        selectedOption
      );
      setFeedback(res);

      if (res.session_completed) {
        setCompletedSession(res.session_summary);
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
    } finally {
      setSubmittingAnswer(false);
    }
  };

  const handleNextQuestion = () => {
    if (feedback?.next_question) {
      setCurrentQuestion(feedback.next_question);
      setSelectedOption(null);
      setFeedback(null);
    }
  };

  const getDifficultyBadge = (diff: string) => {
    switch (diff?.toLowerCase()) {
      case 'beginner':
        return 'bg-green-100 dark:bg-green-950/60 text-green-800 dark:text-green-300 border-green-300 dark:border-green-800';
      case 'intermediate':
        return 'bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-800';
      case 'advanced':
        return 'bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300 border-purple-300 dark:border-purple-800';
      case 'expert':
        return 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800';
      default:
        return 'bg-gray-100 dark:bg-dark-bg text-gray-700 dark:text-gray-300 border-gray-200 dark:border-dark-border';
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration & Bank Stats Header */}
      {!sessionId || completedSession ? (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/40 text-[11px] font-mono text-blue-700 dark:text-blue-300 mb-2">
                <Zap className="w-3.5 h-3.5" />
                <span>Adaptive Difficulty Scaling</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Adaptive Skill Assessment: {skill}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 max-w-xl">
                The assessment begins at your verified level and dynamically scales up or down based on your performance. Strong answers level up to Advanced & Expert challenge tiers.
              </p>
            </div>

            {summary && (
              <div className="bg-gray-50 dark:bg-dark-bg/60 p-3.5 rounded-lg border border-gray-200/80 dark:border-dark-border text-center shrink-0">
                <div className="text-2xl font-black text-gray-900 dark:text-white font-mono">
                  {summary.total_questions}+
                </div>
                <div className="text-[11px] font-mono uppercase text-gray-500 dark:text-dark-muted">
                  Questions in Bank
                </div>
              </div>
            )}
          </div>

          {/* Mode Selector */}
          <div className="space-y-3 pt-2 border-t border-gray-100 dark:border-dark-border">
            <label className="block text-xs font-mono font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">
              Select Assessment Depth
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { id: 'quick', title: 'Quick', count: 20, desc: 'Rapid check (20 Qs)' },
                { id: 'standard', title: 'Standard', count: 40, desc: 'Balanced audit (40 Qs)' },
                { id: 'full', title: 'Full', count: 75, desc: 'Deep evaluation (75 Qs)' },
                { id: 'comprehensive', title: 'Comprehensive', count: '100+', desc: 'Complete bank (105 Qs)' },
              ].map((m) => (
                <button
                  key={m.id}
                  onClick={() => setMode(m.id as any)}
                  className={`p-3.5 rounded-xl border text-left transition-all ${
                    mode === m.id
                      ? 'bg-green-50 dark:bg-green-950/40 border-green-500 text-green-900 dark:text-green-200 shadow-sm'
                      : 'bg-white dark:bg-dark-bg/40 border-gray-200 dark:border-dark-border text-gray-700 dark:text-gray-300 hover:border-gray-300'
                  }`}
                >
                  <div className="font-bold text-sm">{m.title}</div>
                  <div className="text-xs font-mono text-gray-500 dark:text-dark-muted mt-0.5">
                    {m.count} Questions
                  </div>
                  <div className="text-[11px] text-gray-400 mt-1">{m.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleStartSession}
            disabled={startingSession}
            className="w-full py-3 px-4 rounded-xl bg-green-600 hover:bg-green-700 text-white font-medium text-sm transition-colors flex items-center justify-center space-x-2 shadow-sm disabled:opacity-50"
          >
            {startingSession ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Calibrating Question Bank...</span>
              </>
            ) : (
              <>
                <span>Begin Adaptive Assessment</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      ) : null}

      {/* Active Question View */}
      {sessionId && !completedSession && currentQuestion && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-6 shadow-sm space-y-6 animate-fade-in">
          {/* Question Header & Stepper */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 dark:border-dark-border pb-4">
            <div className="flex items-center space-x-2.5">
              <span className="font-mono text-xs font-bold text-gray-500 dark:text-dark-muted">
                Question {currentQuestion.question_number} of {currentQuestion.total_questions}
              </span>
              <span
                className={`text-[11px] font-mono uppercase font-bold px-2 py-0.5 rounded border ${getDifficultyBadge(
                  currentQuestion.difficulty
                )}`}
              >
                {currentQuestion.difficulty} Tier
              </span>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-dark-bg text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-dark-border">
                {currentQuestion.question_type?.replace('_', ' ')}
              </span>
            </div>

            <div className="text-xs font-mono text-gray-500 dark:text-dark-muted">
              Topic: <span className="font-semibold text-gray-700 dark:text-gray-200">{currentQuestion.topic}</span>
            </div>
          </div>

          {/* Question Text */}
          <div className="space-y-4">
            <h4 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white leading-relaxed">
              {currentQuestion.question_text}
            </h4>

            {/* Code Snippet if applicable */}
            {currentQuestion.code_snippet && (
              <div className="bg-slate-900 text-slate-100 rounded-lg p-4 font-mono text-xs overflow-x-auto border border-slate-800 shadow-inner">
                <pre>{currentQuestion.code_snippet}</pre>
              </div>
            )}
          </div>

          {/* Options List */}
          <div className="space-y-2.5">
            {currentQuestion.options.map((option: string, idx: number) => {
              const isSelected = selectedOption === option;
              return (
                <button
                  key={idx}
                  disabled={feedback !== null}
                  onClick={() => setSelectedOption(option)}
                  className={`w-full p-4 rounded-xl border text-left text-sm transition-all flex items-start space-x-3 ${
                    isSelected
                      ? 'bg-blue-50/80 dark:bg-blue-950/40 border-blue-500 text-blue-900 dark:text-blue-100 font-semibold shadow-sm'
                      : 'bg-white dark:bg-dark-bg/60 border-gray-200 dark:border-dark-border text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-dark-bg'
                  }`}
                >
                  <span className="w-6 h-6 rounded-full border border-gray-300 dark:border-gray-600 flex items-center justify-center font-mono text-xs shrink-0 mt-0.5">
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span className="flex-1 leading-relaxed">{option}</span>
                </button>
              );
            })}
          </div>

          {/* Immediate Feedback Card */}
          {feedback && (
            <div
              className={`p-4 rounded-xl border text-sm space-y-2 animate-fade-in ${
                feedback.is_correct
                  ? 'bg-green-50 dark:bg-green-950/40 border-green-200 dark:border-green-900/60 text-green-900 dark:text-green-200'
                  : 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900/60 text-rose-900 dark:text-rose-200'
              }`}
            >
              <div className="flex items-center space-x-2 font-bold">
                {feedback.is_correct ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                    <span>Correct!</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                    <span>Incorrect — Correct Answer: {feedback.correct_answer}</span>
                  </>
                )}
              </div>
              <p className="text-xs leading-relaxed text-gray-700 dark:text-gray-300">
                {feedback.explanation}
              </p>

              {/* Adaptive leveling indicator */}
              <div className="pt-2 flex items-center space-x-2 text-xs font-mono">
                {feedback.is_correct ? (
                  <span className="flex items-center space-x-1 text-green-700 dark:text-green-400">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Targeting next question at: {feedback.next_difficulty} tier</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 text-amber-700 dark:text-amber-400">
                    <TrendingDown className="w-3.5 h-3.5" />
                    <span>Calibrating difficulty: {feedback.next_difficulty} tier</span>
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-dark-border">
            <span className="text-xs font-mono text-gray-500 dark:text-dark-muted">
              Current accuracy: {feedback?.current_score ?? 0}%
            </span>

            {!feedback ? (
              <button
                onClick={handleSubmitAnswer}
                disabled={!selectedOption || submittingAnswer}
                className="py-2.5 px-6 rounded-lg bg-green-600 hover:bg-green-700 text-white font-medium text-xs transition-colors disabled:opacity-50 flex items-center space-x-1.5 shadow-sm"
              >
                {submittingAnswer ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Submit Answer</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={handleNextQuestion}
                className="py-2.5 px-6 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs transition-colors flex items-center space-x-1.5 shadow-sm"
              >
                <span>Proceed to Next Question</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Completed Session Diagnostic Summary */}
      {completedSession && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-xl p-6 shadow-sm space-y-6 animate-fade-in">
          <div className="flex items-center space-x-3">
            <div className="p-3 rounded-full bg-green-50 dark:bg-green-950/40 text-green-600 dark:text-green-400">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                Assessment Complete: {skill}
              </h3>
              <p className="text-xs text-gray-500 dark:text-dark-muted font-mono">
                Knowledge verified across {completedSession.records?.length} adaptive challenges.
              </p>
            </div>
          </div>

          {/* High level stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3.5 rounded-lg bg-gray-50 dark:bg-dark-bg border border-gray-200/80 dark:border-dark-border">
              <div className="text-xs text-gray-500 font-mono">Accuracy Score</div>
              <div className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
                {completedSession.score}%
              </div>
            </div>
            <div className="p-3.5 rounded-lg bg-gray-50 dark:bg-dark-bg border border-gray-200/80 dark:border-dark-border">
              <div className="text-xs text-gray-500 font-mono">Knowledge Level</div>
              <div className="text-base font-bold text-gray-900 dark:text-white mt-1">
                {completedSession.estimated_knowledge_level}
              </div>
            </div>
            <div className="p-3.5 rounded-lg bg-gray-50 dark:bg-dark-bg border border-gray-200/80 dark:border-dark-border">
              <div className="text-xs text-gray-500 font-mono">Confidence Level</div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
                {completedSession.confidence_score}%
              </div>
            </div>
            <div className="p-3.5 rounded-lg bg-gray-50 dark:bg-dark-bg border border-gray-200/80 dark:border-dark-border">
              <div className="text-xs text-gray-500 font-mono">Next Target</div>
              <div className="text-xs font-semibold text-purple-600 dark:text-purple-400 mt-1">
                {completedSession.recommended_next_level}
              </div>
            </div>
          </div>

          {/* Topics Breakdown */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Strong Topics */}
            <div className="p-4 rounded-xl border border-green-200 dark:border-green-900/60 bg-green-50/40 dark:bg-green-950/20 space-y-2">
              <span className="text-xs font-mono font-bold uppercase text-green-800 dark:text-green-300">
                Strong Topics Identified
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {completedSession.strong_topics?.length > 0 ? (
                  completedSession.strong_topics.map((t: string, i: number) => (
                    <span
                      key={i}
                      className="text-xs font-mono px-2 py-0.5 rounded bg-white dark:bg-dark-bg text-green-700 dark:text-green-300 border border-green-200 dark:border-green-900"
                    >
                      ✓ {t}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-gray-400 italic">None recorded</span>
                )}
              </div>
            </div>

            {/* Weak Topics */}
            <div className="p-4 rounded-xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 space-y-2">
              <span className="text-xs font-mono font-bold uppercase text-amber-800 dark:text-amber-300">
                Areas for Growth & Learning
              </span>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {completedSession.weak_topics?.length > 0 ? (
                  completedSession.weak_topics.map((t: string, i: number) => (
                    <span
                      key={i}
                      className="text-xs font-mono px-2 py-0.5 rounded bg-white dark:bg-dark-bg text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-900"
                    >
                      ! {t}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-green-600 font-mono">No major weaknesses detected!</span>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={() => {
              setSessionId(null);
              setCompletedSession(null);
            }}
            className="w-full py-3 px-4 rounded-xl border border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-900 dark:text-white font-medium text-xs transition-colors flex items-center justify-center space-x-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Take Another Assessment</span>
          </button>
        </div>
      )}
    </div>
  );
};
