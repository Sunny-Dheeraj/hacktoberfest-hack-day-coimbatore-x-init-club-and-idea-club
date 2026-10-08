import {
  CareerRole,
  RoleSummary,
  CareerAnalysisResponse,
  FullSkillAssessment,
  CodeChallenge,
  QuizResultResponse,
  CodeChallengeResultResponse,
  LearningResource,
  LearningPathResponse,
  PracticalTask,
  TaskVerificationResponse,
  UserProgressResponse,
  NextBestAction,
} from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(`API Error (${res.status}): ${errorDetail}`);
  }
  return res.json();
}

export const api = {
  // Roles
  getRoles: async (): Promise<{ roles: RoleSummary[]; total: number }> => {
    const res = await fetch(`${API_BASE_URL}/api/analysis/roles`);
    return handleResponse(res);
  },

  getRole: async (roleId: string): Promise<CareerRole> => {
    const res = await fetch(`${API_BASE_URL}/api/analysis/roles/${roleId}`);
    return handleResponse(res);
  },

  // Career Analysis
  analyzeCareer: async (
    username: string,
    roleIds?: string[],
    includeAi: boolean = true
  ): Promise<CareerAnalysisResponse> => {
    const res = await fetch(`${API_BASE_URL}/api/analysis/career`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        role_ids: roleIds,
        include_ai: includeAi,
      }),
    });
    return handleResponse(res);
  },

  // 3-Dimension Assessment (Quiz & Code Challenge)
  getSkillAssessment: async (skill: string): Promise<FullSkillAssessment> => {
    const res = await fetch(`${API_BASE_URL}/api/quiz/generate?skill=${encodeURIComponent(skill)}`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  submitQuiz: async (
    username: string,
    skill: string,
    answers: Record<string, number>
  ): Promise<QuizResultResponse> => {
    const res = await fetch(`${API_BASE_URL}/api/quiz/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, skill, answers }),
    });
    return handleResponse(res);
  },

  getCodeChallenge: async (skill: string): Promise<CodeChallenge> => {
    const res = await fetch(`${API_BASE_URL}/api/code-challenges/generate?skill=${encodeURIComponent(skill)}`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  submitCodeChallenge: async (
    username: string,
    challengeId: string,
    skill: string,
    language: string,
    code: string
  ): Promise<CodeChallengeResultResponse> => {
    const res = await fetch(`${API_BASE_URL}/api/code-challenges/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        challenge_id: challengeId,
        skill,
        language,
        code,
      }),
    });
    return handleResponse(res);
  },

  // Learning & Roadmaps
  getLearningResources: async (skill: string): Promise<LearningResource[]> => {
    const res = await fetch(`${API_BASE_URL}/api/learning/${encodeURIComponent(skill)}`);
    return handleResponse(res);
  },

  getLearningPath: async (
    roleId: string,
    missing?: string[],
    partial?: string[]
  ): Promise<LearningPathResponse> => {
    const params = new URLSearchParams();
    if (missing) missing.forEach(m => params.append('missing', m));
    if (partial) partial.forEach(p => params.append('partial', p));
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE_URL}/api/learning-path/${roleId}${qs}`);
    return handleResponse(res);
  },

  // Practical Tasks & Static Verification
  getMission: async (skill: string): Promise<PracticalTask> => {
    const res = await fetch(`${API_BASE_URL}/api/tasks/generate?skill=${encodeURIComponent(skill)}`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  verifyMission: async (
    username: string,
    taskId: string,
    skill: string,
    repoUrl: string,
    branch: string = 'main'
  ): Promise<TaskVerificationResponse> => {
    const res = await fetch(`${API_BASE_URL}/api/tasks/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        task_id: taskId,
        skill,
        repo_url: repoUrl,
        branch,
      }),
    });
    return handleResponse(res);
  },

  // Progress & Recommendations
  getProgress: async (username: string, role?: string): Promise<UserProgressResponse> => {
    const qs = role ? `?role=${encodeURIComponent(role)}` : '';
    const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(username)}${qs}`);
    return handleResponse(res);
  },

  getRecommendations: async (username: string, role?: string): Promise<NextBestAction> => {
    const qs = role ? `?role=${encodeURIComponent(role)}` : '';
    const res = await fetch(`${API_BASE_URL}/api/progress/${encodeURIComponent(username)}/recommendations${qs}`);
    return handleResponse(res);
  },

  // Adaptive 100+ Question Bank Assessment
  startAdaptiveAssessment: async (
    username: string,
    skill: string,
    mode: 'quick' | 'standard' | 'full' | 'comprehensive' = 'quick',
    roleId?: string
  ): Promise<any> => {
    const res = await fetch(`${API_BASE_URL}/api/assessment/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, skill, mode, role_id: roleId }),
    });
    return handleResponse(res);
  },

  submitAdaptiveAnswer: async (
    sessionId: string,
    questionId: string,
    selectedAnswer: string,
    timeTakenSeconds?: number
  ): Promise<any> => {
    const res = await fetch(`${API_BASE_URL}/api/assessment/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        selected_answer: selectedAnswer,
        time_taken_seconds: timeTakenSeconds,
      }),
    });
    return handleResponse(res);
  },

  getQuestionBankSummary: async (skill: string): Promise<any> => {
    const res = await fetch(`${API_BASE_URL}/api/assessment/summary/${encodeURIComponent(skill)}`);
    return handleResponse(res);
  },
};
