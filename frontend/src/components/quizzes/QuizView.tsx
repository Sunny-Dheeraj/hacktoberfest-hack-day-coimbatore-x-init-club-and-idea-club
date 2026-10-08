import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { api } from '../../services/api';
import {
  FullSkillAssessment,
  QuizResultResponse,
  CodeChallengeResultResponse,
} from '../../types';
import {
  CheckCircle,
  XCircle,
  Terminal,
  HelpCircle,
  Code2,
  RotateCcw,
  Play,
  ArrowRight,
  Loader2,
  Award,
} from 'lucide-react';

interface QuizViewProps {
  skill: string;
  username: string;
  onAssessmentCompleted?: (updatedConfidence: number) => void;
}

export const QuizView: React.FC<QuizViewProps> = ({ skill, username, onAssessmentCompleted }) => {
  const [assessment, setAssessment] = useState<FullSkillAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Stepper state: 1 = Knowledge, 2 = Code Reasoning, 3 = Implementation, 4 = Results
  const [currentStep, setCurrentStep] = useState<number>(1);

  // User selections
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({});
  const [codeValue, setCodeValue] = useState<string>('');

  // Evaluation results
  const [quizResult, setQuizResult] = useState<QuizResultResponse | null>(null);
  const [challengeResult, setChallengeResult] = useState<CodeChallengeResultResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadAssessment();
  }, [skill]);

  const loadAssessment = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getSkillAssessment(skill);
      setAssessment(data);
      if (data.code_challenge) {
        setCodeValue(data.code_challenge.starter_code);
      }
      setSelectedAnswers({});
      setCurrentStep(1);
    } catch (err: any) {
      setError(err.message || 'Failed to load skill assessment.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId: string, optionIndex: number) => {
    setSelectedAnswers((prev) => ({ ...prev, [questionId]: optionIndex }));
  };

  const handleResetCode = () => {
    if (assessment?.code_challenge) {
      setCodeValue(assessment.code_challenge.starter_code);
    }
  };

  const handleFinishQuiz = async () => {
    setSubmitting(true);
    try {
      // 1. Submit multiple-choice answers
      const qRes = await api.submitQuiz(username, skill, selectedAnswers);
      setQuizResult(qRes);

      // 2. Submit Monaco code challenge if available
      if (assessment?.code_challenge) {
        const cRes = await api.submitCodeChallenge(
          username,
          assessment.code_challenge.id,
          skill,
          assessment.code_challenge.language,
          codeValue
        );
        setChallengeResult(cRes);
        if (onAssessmentCompleted) {
          onAssessmentCompleted(cRes.updated_confidence);
        }
      } else if (onAssessmentCompleted) {
        onAssessmentCompleted(qRes.updated_confidence);
      }

      setCurrentStep(4); // Move to results step
    } catch (err: any) {
      setError(err.message || 'Error scoring assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-500 dark:text-dark-muted">
        <Loader2 className="w-8 h-8 animate-spin text-green-600 mb-2" />
        <p className="text-sm font-mono">Generating 3-dimension assessment for {skill}...</p>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 rounded-lg p-5 text-center">
        <p className="text-sm text-rose-700 dark:text-rose-400 font-medium mb-3">{error || 'Assessment not available.'}</p>
        <button
          onClick={loadAssessment}
          className="px-4 py-1.5 rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Assessment Header & 3-Step Breadcrumb */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-green-600 dark:text-green-400 font-semibold">
              3-Dimension Skill Assessment
            </span>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {skill} Competency Evaluation
            </h2>
          </div>
          <span className="text-xs font-mono text-gray-400 self-start sm:self-auto">
            Candidate: @{username}
          </span>
        </div>

        {/* Step indicator */}
        <div className="grid grid-cols-4 gap-2 pt-2 border-t border-gray-100 dark:border-dark-border text-xs">
          <button
            onClick={() => setCurrentStep(1)}
            className={`flex items-center space-x-1.5 p-2 rounded text-left transition-colors ${
              currentStep === 1
                ? 'bg-green-50 dark:bg-green-950/40 text-green-800 dark:text-green-300 font-semibold border border-green-200 dark:border-green-800/60'
                : 'text-gray-500 hover:text-gray-800 dark:hover:text-dark-text'
            }`}
          >
            <HelpCircle className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">1. Knowledge</span>
          </button>

          <button
            onClick={() => setCurrentStep(2)}
            className={`flex items-center space-x-1.5 p-2 rounded text-left transition-colors ${
              currentStep === 2
                ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-800 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-800/60'
                : 'text-gray-500 hover:text-gray-800 dark:hover:text-dark-text'
            }`}
          >
            <Code2 className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">2. Reasoning</span>
          </button>

          <button
            onClick={() => setCurrentStep(3)}
            className={`flex items-center space-x-1.5 p-2 rounded text-left transition-colors ${
              currentStep === 3
                ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-800 dark:text-purple-300 font-semibold border border-purple-200 dark:border-purple-800/60'
                : 'text-gray-500 hover:text-gray-800 dark:hover:text-dark-text'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">3. Monaco Code</span>
          </button>

          <button
            onClick={() => currentStep === 4 && setCurrentStep(4)}
            disabled={currentStep !== 4}
            className={`flex items-center space-x-1.5 p-2 rounded text-left transition-colors ${
              currentStep === 4
                ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 font-semibold border border-amber-200 dark:border-amber-800/60'
                : 'text-gray-400 opacity-60 cursor-not-allowed'
            }`}
          >
            <Award className="w-3.5 h-3.5 shrink-0" />
            <span className="truncate">4. Results</span>
          </button>
        </div>
      </div>

      {/* STEP 1: Conceptual Knowledge */}
      {currentStep === 1 && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-6">
          <div className="border-b border-gray-100 dark:border-dark-border pb-3">
            <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center space-x-2">
              <span>Dimension 1: Conceptual Knowledge</span>
            </h3>
            <p className="text-xs text-gray-500 dark:text-dark-muted mt-0.5">
              Tests core theoretical foundations without guessing.
            </p>
          </div>

          <div className="space-y-6">
            {assessment.knowledge_questions.map((q, idx) => (
              <div key={q.id} className="space-y-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {idx + 1}. {q.question}
                </p>
                <div className="space-y-2">
                  {q.options.map((opt, optIdx) => (
                    <label
                      key={optIdx}
                      onClick={() => handleSelectOption(q.id, optIdx)}
                      className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer text-xs transition-colors ${
                        selectedAnswers[q.id] === optIdx
                          ? 'border-green-600 bg-green-50/50 dark:bg-green-950/30 text-gray-900 dark:text-white'
                          : 'border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-700 dark:text-dark-text'
                      }`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        checked={selectedAnswers[q.id] === optIdx}
                        onChange={() => handleSelectOption(q.id, optIdx)}
                        className="mt-0.5 text-green-600 focus:ring-green-500"
                      />
                      <span className="leading-relaxed">{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4 border-t border-gray-100 dark:border-dark-border">
            <button
              onClick={() => setCurrentStep(2)}
              className="px-4 py-2 rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium flex items-center space-x-1.5 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              <span>Next: Code Reasoning</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Code Reasoning */}
      {currentStep === 2 && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-6">
          <div className="border-b border-gray-100 dark:border-dark-border pb-3">
            <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center space-x-2">
              <span>Dimension 2: Code Reasoning</span>
            </h3>
            <p className="text-xs text-gray-500 dark:text-dark-muted mt-0.5">
              Inspect realistic code snippets and predict their execution behavior.
            </p>
          </div>

          <div className="space-y-6">
            {assessment.code_reasoning_questions.map((q, idx) => (
              <div key={q.id} className="space-y-3">
                <div className="bg-gray-900 rounded-lg p-4 font-mono text-xs text-gray-200 overflow-x-auto border border-gray-800 shadow-inner">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2 font-semibold">
                    Snippet ({q.language})
                  </div>
                  <pre>{q.snippet}</pre>
                </div>

                <p className="text-sm font-medium text-gray-900 dark:text-white pt-2">
                  {idx + 1}. {q.question}
                </p>

                <div className="space-y-2">
                  {q.options.map((opt, optIdx) => (
                    <label
                      key={optIdx}
                      onClick={() => handleSelectOption(q.id, optIdx)}
                      className={`flex items-start space-x-3 p-3 rounded-lg border cursor-pointer text-xs transition-colors ${
                        selectedAnswers[q.id] === optIdx
                          ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-950/30 text-gray-900 dark:text-white'
                          : 'border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-bg text-gray-700 dark:text-dark-text'
                      }`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        checked={selectedAnswers[q.id] === optIdx}
                        onChange={() => handleSelectOption(q.id, optIdx)}
                        className="mt-0.5 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="leading-relaxed">{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between pt-4 border-t border-gray-100 dark:border-dark-border">
            <button
              onClick={() => setCurrentStep(1)}
              className="px-3 py-1.5 rounded border border-gray-200 dark:border-dark-border text-xs text-gray-600 dark:text-dark-muted hover:bg-gray-50"
            >
              Back to Knowledge
            </button>
            <button
              onClick={() => setCurrentStep(3)}
              className="px-4 py-2 rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium flex items-center space-x-1.5 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              <span>Next: Monaco Code Challenge</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Monaco Editor Code Implementation */}
      {currentStep === 3 && assessment.code_challenge && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-5">
          <div className="border-b border-gray-100 dark:border-dark-border pb-3 flex justify-between items-start">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-purple-600 dark:text-purple-400 font-semibold">
                Dimension 3: Code Implementation
              </span>
              <h3 className="text-base font-bold text-gray-900 dark:text-white mt-0.5">
                {assessment.code_challenge.title}
              </h3>
              <p className="text-xs text-gray-600 dark:text-dark-muted mt-1">
                {assessment.code_challenge.description}
              </p>
            </div>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/60 uppercase">
              {assessment.code_challenge.difficulty}
            </span>
          </div>

          {/* Expected Behavior List */}
          {assessment.code_challenge.expected_behavior.length > 0 && (
            <div className="bg-gray-50 dark:bg-dark-bg/60 border border-gray-200 dark:border-dark-border rounded p-3 text-xs space-y-1">
              <span className="font-semibold text-gray-700 dark:text-dark-text">Expected Behavior:</span>
              <ul className="list-disc list-inside font-mono text-[11px] text-gray-600 dark:text-dark-muted">
                {assessment.code_challenge.expected_behavior.map((b, idx) => (
                  <li key={idx}>{b}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Monaco Editor Container */}
          <div className="border border-gray-200 dark:border-dark-border rounded-lg overflow-hidden shadow-sm">
            <div className="bg-gray-100 dark:bg-dark-bg px-4 py-2 border-b border-gray-200 dark:border-dark-border flex items-center justify-between text-xs font-mono">
              <span className="text-gray-600 dark:text-dark-muted flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5" />
                <span>editor.{assessment.code_challenge.language}</span>
              </span>
              <button
                onClick={handleResetCode}
                className="text-gray-500 hover:text-gray-800 dark:hover:text-white flex items-center space-x-1"
                title="Reset to starter code"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset</span>
              </button>
            </div>
            <div className="h-64 sm:h-72">
              <Editor
                height="100%"
                language={assessment.code_challenge.language === 'dockerfile' ? 'dockerfile' : assessment.code_challenge.language}
                theme="vs-dark"
                value={codeValue}
                onChange={(val) => setCodeValue(val || '')}
                options={{
                  fontSize: 13,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  lineNumbers: 'on',
                  automaticLayout: true,
                }}
              />
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex justify-between items-center pt-3 border-t border-gray-100 dark:border-dark-border">
            <button
              onClick={() => setCurrentStep(2)}
              className="px-3 py-1.5 rounded border border-gray-200 dark:border-dark-border text-xs text-gray-600 dark:text-dark-muted hover:bg-gray-50"
            >
              Back to Reasoning
            </button>
            <button
              onClick={handleFinishQuiz}
              disabled={submitting}
              className="px-5 py-2 rounded-md bg-green-600 hover:bg-green-700 text-white text-xs font-semibold flex items-center space-x-2 shadow-sm transition-colors disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Statically Evaluating AST & Criteria...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  <span>Submit & Verify All 3 Dimensions</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Results Display */}
      {currentStep === 4 && (
        <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-6 space-y-6 animate-fade-in">
          <div className="text-center py-4 border-b border-gray-100 dark:border-dark-border">
            <div className="inline-flex p-3 rounded-full bg-green-100 dark:bg-green-950/60 text-green-700 dark:text-green-400 mb-2">
              <Award className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Assessment Results for {skill}
            </h3>
            <p className="text-xs text-gray-500 dark:text-dark-muted font-mono mt-0.5">
              Deterministic scoring verified. Skill confidence updated in database.
            </p>
          </div>

          {/* Score Summary Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {quizResult && (
              <div className="border border-gray-200 dark:border-dark-border rounded-lg p-4 bg-gray-50/50 dark:bg-dark-bg/40">
                <span className="text-xs uppercase font-mono tracking-wider text-gray-500">
                  Dimensions 1 & 2 (Knowledge & Reasoning)
                </span>
                <div className="text-3xl font-extrabold font-mono text-gray-900 dark:text-white mt-1">
                  {quizResult.score}%
                </div>
                <p className="text-xs text-gray-600 dark:text-dark-muted mt-1">
                  {quizResult.correct_answers} of {quizResult.total_questions} questions answered correctly.
                </p>
              </div>
            )}

            {challengeResult && (
              <div className="border border-gray-200 dark:border-dark-border rounded-lg p-4 bg-gray-50/50 dark:bg-dark-bg/40">
                <span className="text-xs uppercase font-mono tracking-wider text-gray-500">
                  Dimension 3 (Monaco Code Challenge)
                </span>
                <div className="text-3xl font-extrabold font-mono text-gray-900 dark:text-white mt-1 flex items-center space-x-2">
                  <span>{challengeResult.score}%</span>
                  <span className="text-xs uppercase font-normal font-sans px-2 py-0.5 rounded bg-green-100 dark:bg-green-950 text-green-700 dark:text-green-400">
                    {challengeResult.status}
                  </span>
                </div>
                <p className="text-xs text-gray-600 dark:text-dark-muted mt-1">
                  {challengeResult.feedback}
                </p>
              </div>
            )}
          </div>

          {/* Code Challenge Criteria Breakdown */}
          {challengeResult && challengeResult.criteria.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-gray-700 dark:text-dark-text uppercase font-mono">
                Code Static Criteria Breakdown
              </h4>
              <div className="space-y-1.5">
                {challengeResult.criteria.map((crit, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded border border-gray-100 dark:border-dark-border text-xs"
                  >
                    <div className="flex items-center space-x-2">
                      {crit.passed ? (
                        <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
                      ) : (
                        <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
                      )}
                      <span className="text-gray-800 dark:text-dark-text font-medium">{crit.description}</span>
                    </div>
                    <span className="text-[11px] font-mono text-gray-500">{crit.feedback}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reset / Retake Button */}
          <div className="flex justify-center pt-4">
            <button
              onClick={loadAssessment}
              className="px-4 py-2 rounded-md bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              Retake Assessment
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
