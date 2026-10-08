export type EvidenceStatus = 'proven' | 'partial' | 'missing';
export type EvidenceType = 'none' | 'mentioned' | 'dependency' | 'implementation' | 'applied' | 'production';

export interface EvidenceItem {
  skill: string;
  status: EvidenceStatus;
  repository?: string;
  file?: string;
  line_start?: number;
  line_end?: number;
  signals: string[];
  evidence_type: EvidenceType;
  strength: number;
  explanation: string;
}

export interface SkillSummary {
  skill: string;
  category: string;
  status: EvidenceStatus;
  strength: number;
  evidence: EvidenceItem[];
}

export interface RoleSkillRequirement {
  skill: string;
  weight: number;
  is_core: boolean;
}

export interface CareerRole {
  id: string;
  title: string;
  description: string;
  core_skills: RoleSkillRequirement[];
  supporting_skills: RoleSkillRequirement[];
}

export interface RoleSummary {
  id: string;
  title: string;
  description: string;
  core_skill_count: number;
  supporting_skill_count: number;
}

export interface ReadinessScore {
  score: number;
  max_possible: number;
  earned: number;
  core_score: number;
  supporting_score: number;
}

export interface SkillAssessment {
  skill: string;
  classification: EvidenceStatus;
  is_core: boolean;
  weight: number;
  evidence_strength: number;
  evidence_count: number;
  top_evidence: EvidenceItem[];
}

export interface AIInsight {
  summary: string;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  confidence: number;
  grounded: boolean;
  model_used?: string;
  fallback_used: boolean;
}

export interface RoleAnalysis {
  role: CareerRole;
  readiness: ReadinessScore;
  skill_assessments: SkillAssessment[];
  proven_skills: string[];
  partial_skills: string[];
  missing_skills: string[];
  ai_insight?: AIInsight;
}

export interface CareerAnalysisResponse {
  username: string;
  roles_analyzed: number;
  primary_role?: string;
  analyses: RoleAnalysis[];
  overall_strengths: string[];
  phase1_evidence_count: number;
  ai_available: boolean;
  metadata: Record<string, any>;
}

// Phase 3 Assessment & Progress Types
export interface KnowledgeQuestion {
  id: string;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface CodeReasoningQuestion {
  id: string;
  language: string;
  snippet: string;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface ChallengeCriterion {
  name: string;
  description: string;
}

export interface ChallengeCriterionResult {
  name: string;
  description: string;
  passed: boolean;
  feedback?: string;
}

export interface CodeChallenge {
  id: string;
  skill: string;
  language: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  description: string;
  starter_code: string;
  expected_behavior: string[];
  criteria: ChallengeCriterion[];
}

export interface FullSkillAssessment {
  skill: string;
  knowledge_questions: KnowledgeQuestion[];
  code_reasoning_questions: CodeReasoningQuestion[];
  code_challenge?: CodeChallenge;
}

export interface QuizQuestionResult {
  question_id: string;
  selected_index: number;
  correct_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface QuizResultResponse {
  username: string;
  skill: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  question_results: QuizQuestionResult[];
  updated_confidence: number;
  feedback: string;
}

export interface CodeChallengeResultResponse {
  challenge_id: string;
  skill: string;
  language: string;
  status: 'passed' | 'partially_passed' | 'failed';
  score: number;
  criteria: ChallengeCriterionResult[];
  feedback: string;
  updated_confidence: number;
}

export interface PracticalTask {
  id: string;
  skill: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  description: string;
  requirements: string[];
  expected_artifacts: string[];
  verification_rules: Record<string, any>;
}

export interface TaskCriterionResult {
  name: string;
  description: string;
  passed: boolean;
  details?: string;
}

export interface TaskVerificationResponse {
  username: string;
  task_id: string;
  skill: string;
  repo_url: string;
  status: 'verified' | 'partially_verified' | 'not_verified';
  score: number;
  criteria: TaskCriterionResult[];
  signals_detected: string[];
  files_checked: string[];
  updated_confidence: number;
  feedback: string;
}

export interface LearningResource {
  id: string;
  skill: string;
  title: string;
  description: string;
  type: 'documentation' | 'tutorial' | 'course' | 'guide' | 'example';
  url: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_time: string;
}

export interface LearningPathResponse {
  role_id: string;
  role_title: string;
  readiness_score: number;
  ordered_skills: {
    step: number;
    skill: string;
    is_core: boolean;
    status: string;
    priority_label: string;
    resources_count: number;
    primary_resource?: LearningResource;
  }[];
  total_estimated_time: string;
}

export interface SkillConfidence {
  skill: string;
  code_score: number;
  quiz_score: number;
  practical_score: number;
  confidence: number;
  status: string;
}

export interface NextBestAction {
  skill: string;
  action_type: 'learn' | 'quiz' | 'code_challenge' | 'practical_mission';
  title: string;
  reason: string;
  priority: number;
  target_role?: string;
}

export interface UserProgressResponse {
  username: string;
  target_role?: string;
  overall_confidence: number;
  skills: SkillConfidence[];
  next_best_action?: NextBestAction;
}
