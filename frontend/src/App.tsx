import React, { useState } from 'react';
import { Header } from './components/layout/Header';
import { Home } from './pages/Home';
import { ReadinessMeter } from './components/dashboard/ReadinessMeter';
import { NextBestActionBanner } from './components/dashboard/NextBestActionBanner';
import { SkillCard } from './components/dashboard/SkillCard';
import { AISummaryCard } from './components/dashboard/AISummaryCard';
import { EvidenceModal } from './components/evidence/EvidenceModal';
import { QuizView } from './components/quizzes/QuizView';
import { LearningPathView } from './components/learning/LearningPathView';
import { MissionView } from './components/tasks/MissionView';
import { ProgressView } from './components/progress/ProgressView';
import { api } from './services/api';
import {
  CareerAnalysisResponse,
  RoleAnalysis,
  EvidenceItem,
  NextBestAction,
} from './types';
import { Filter, AlertCircle, ArrowLeft } from 'lucide-react';

export const App: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('ml_engineer');
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [loading, setLoading] = useState<boolean>(false);
  const [analysis, setAnalysis] = useState<CareerAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Skill filter on dashboard
  const [skillFilter, setSkillFilter] = useState<'all' | 'proven' | 'partial' | 'missing'>('all');

  // Active skill context for modal / quiz / mission
  const [activeSkill, setActiveSkill] = useState<string>('Python');
  const [evidenceModal, setEvidenceModal] = useState<{ skill: string; items: EvidenceItem[] } | null>(null);

  const activeRoleAnalysis: RoleAnalysis | undefined = analysis?.analyses.find(
    (a) => a.role.id === selectedRole
  ) || analysis?.analyses[0];

  const handleAnalyze = async (user: string, roleId: string) => {
    setLoading(true);
    setError(null);
    try {
      setUsername(user);
      setSelectedRole(roleId);
      const res = await api.analyzeCareer(user, [roleId], true);
      setAnalysis(res);
      setCurrentTab('dashboard');
    } catch (err: any) {
      setError(err.message || 'Analysis failed. Please check username or network.');
      setUsername('');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setUsername('');
    setAnalysis(null);
    setCurrentTab('dashboard');
    setError(null);
  };

  // Quick navigation handlers from buttons
  const handleViewEvidence = (skill: string) => {
    if (!activeRoleAnalysis) return;
    const assessment = activeRoleAnalysis.skill_assessments.find((a) => a.skill === skill);
    const items = assessment?.top_evidence || [];
    setEvidenceModal({ skill, items });
  };

  const handleTakeQuiz = (skill: string) => {
    setActiveSkill(skill);
    setCurrentTab('quiz');
  };

  const handleLearn = (skill: string) => {
    setActiveSkill(skill);
    setCurrentTab('learning');
  };

  const handleMission = (skill: string) => {
    setActiveSkill(skill);
    setCurrentTab('mission');
  };

  const handleNextBestAction = (actionType: string, skill: string) => {
    setActiveSkill(skill);
    if (actionType === 'quiz' || actionType === 'code_challenge') {
      setCurrentTab('quiz');
    } else if (actionType === 'practical_mission') {
      setCurrentTab('mission');
    } else {
      setCurrentTab('learning');
    }
  };

  // Filter skills for dashboard
  const filteredAssessments = activeRoleAnalysis?.skill_assessments.filter((a) => {
    if (skillFilter === 'all') return true;
    return a.classification === skillFilter;
  }) || [];

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-dark-bg dark:text-dark-text transition-colors duration-200">
      {/* Navigation Header */}
      <Header
        username={username}
        roleTitle={activeRoleAnalysis?.role.title}
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onReset={handleReset}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error notification if any */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-xs text-rose-800 dark:text-rose-300 flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {/* Landing Page when no user is analyzed */}
        {!username || !analysis ? (
          <Home onAnalyze={handleAnalyze} loading={loading} />
        ) : (
          <>
            {/* VIEW 1: Dashboard */}
            {currentTab === 'dashboard' && activeRoleAnalysis && (
              <div className="space-y-6 animate-fade-in">
                {/* 1. Readiness Meter */}
                <ReadinessMeter
                  readiness={activeRoleAnalysis.readiness}
                  roleTitle={activeRoleAnalysis.role.title}
                />

                {/* 2. Next Best Action Banner */}
                <NextBestActionBanner
                  action={{
                    skill: activeRoleAnalysis.missing_skills[0] || activeRoleAnalysis.partial_skills[0] || 'Python',
                    action_type: activeRoleAnalysis.missing_skills.length > 0 ? 'quiz' : 'practical_mission',
                    title: `Bridge ${activeRoleAnalysis.missing_skills[0] || activeRoleAnalysis.partial_skills[0] || 'Python'} Gap`,
                    reason: `High-leverage core requirement for ${activeRoleAnalysis.role.title} readiness.`,
                    priority: 1,
                    target_role: selectedRole,
                  }}
                  onActionClick={handleNextBestAction}
                />

                {/* 3. Gemma 4 AI Summary Card */}
                {activeRoleAnalysis.ai_insight && (
                  <AISummaryCard insight={activeRoleAnalysis.ai_insight} />
                )}

                {/* 4. Skills Grid with Filter Bar */}
                <div className="space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-200 dark:border-dark-border pb-3">
                    <div>
                      <h3 className="text-base font-bold text-gray-900 dark:text-white">
                        Skill Competency Matrix
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-dark-muted font-mono">
                        {activeRoleAnalysis.proven_skills.length} Proven • {activeRoleAnalysis.partial_skills.length} Partial • {activeRoleAnalysis.missing_skills.length} Missing
                      </p>
                    </div>

                    {/* Filter Pills */}
                    <div className="flex items-center space-x-1.5 text-xs font-mono">
                      {(['all', 'proven', 'partial', 'missing'] as const).map((filter) => (
                        <button
                          key={filter}
                          onClick={() => setSkillFilter(filter)}
                          className={`px-2.5 py-1 rounded capitalize transition-colors ${
                            skillFilter === filter
                              ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-semibold'
                              : 'text-gray-600 dark:text-dark-muted hover:bg-gray-100 dark:hover:bg-dark-card'
                          }`}
                        >
                          {filter}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Cards Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredAssessments.map((assessment) => (
                      <SkillCard
                        key={assessment.skill}
                        assessment={assessment}
                        onViewEvidence={handleViewEvidence}
                        onTakeQuiz={handleTakeQuiz}
                        onLearn={handleLearn}
                        onMission={handleMission}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* VIEW 2: Evidence Explorer View */}
            {currentTab === 'evidence' && activeRoleAnalysis && (
              <div className="space-y-6 animate-fade-in">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      Physical Code Evidence Explorer
                    </h2>
                    <p className="text-xs text-gray-500 font-mono">
                      Every skill is linked to verified file paths and line ranges.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {activeRoleAnalysis.skill_assessments.map((a) => (
                    <div
                      key={a.skill}
                      className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-4 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-sm text-gray-900 dark:text-white">{a.skill}</span>
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded uppercase bg-gray-100 dark:bg-dark-bg text-gray-600 dark:text-dark-muted">
                          {a.classification}
                        </span>
                      </div>

                      <div className="text-xs text-gray-500 dark:text-dark-muted">
                        Evidence count: {a.evidence_count} items
                      </div>

                      <button
                        onClick={() => handleViewEvidence(a.skill)}
                        className="w-full py-1.5 rounded border border-gray-200 dark:border-dark-border text-xs font-medium hover:bg-gray-50 dark:hover:bg-dark-bg transition-colors"
                      >
                        Inspect Traces
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* VIEW 3: Learning & Roadmap */}
            {currentTab === 'learning' && (
              <div className="animate-fade-in">
                <LearningPathView
                  roleId={selectedRole}
                  missingSkills={activeRoleAnalysis?.missing_skills}
                  partialSkills={activeRoleAnalysis?.partial_skills}
                  onTakeQuiz={handleTakeQuiz}
                  onMission={handleMission}
                />
              </div>
            )}

            {/* VIEW 4: 3-Dimension Assessment (Quiz + Monaco) */}
            {currentTab === 'quiz' && (
              <div className="animate-fade-in">
                <QuizView
                  skill={activeSkill}
                  username={username}
                  onAssessmentCompleted={() => {}}
                />
              </div>
            )}

            {/* VIEW 5: Practical Mission & GitHub Verification */}
            {currentTab === 'mission' && (
              <div className="animate-fade-in">
                <MissionView
                  skill={activeSkill}
                  username={username}
                  onVerified={() => {}}
                />
              </div>
            )}

            {/* VIEW 6: Progress & Tri-Pillars Confidence */}
            {currentTab === 'progress' && (
              <div className="animate-fade-in">
                <ProgressView
                  username={username}
                  roleId={selectedRole}
                  onTakeAction={handleNextBestAction}
                />
              </div>
            )}
          </>
        )}
      </main>

      {/* Traceable Evidence Modal */}
      {evidenceModal && (
        <EvidenceModal
          skill={evidenceModal.skill}
          evidenceItems={evidenceModal.items}
          onClose={() => setEvidenceModal(null)}
        />
      )}
    </div>
  );
};
export default App;
