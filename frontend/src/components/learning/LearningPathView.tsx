import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { LearningPathResponse, LearningResource } from '../../types';
import { BookOpen, ExternalLink, Clock, CheckSquare, GitBranch, Loader2, ArrowRight } from 'lucide-react';

interface LearningPathViewProps {
  roleId: string;
  missingSkills?: string[];
  partialSkills?: string[];
  onTakeQuiz: (skill: string) => void;
  onMission: (skill: string) => void;
}

export const LearningPathView: React.FC<LearningPathViewProps> = ({
  roleId,
  missingSkills = [],
  partialSkills = [],
  onTakeQuiz,
  onMission,
}) => {
  const [learningPath, setLearningPath] = useState<LearningPathResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [resources, setResources] = useState<LearningResource[]>([]);

  useEffect(() => {
    loadLearningPath();
  }, [roleId]);

  const loadLearningPath = async () => {
    setLoading(true);
    try {
      const data = await api.getLearningPath(roleId, missingSkills, partialSkills);
      setLearningPath(data);
      if (data.ordered_skills.length > 0) {
        loadSkillResources(data.ordered_skills[0].skill);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadSkillResources = async (skill: string) => {
    setSelectedSkill(skill);
    try {
      const res = await api.getLearningResources(skill);
      setResources(res);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin text-green-600 mb-2" />
        <p className="text-sm font-mono">Building prioritized learning roadmap...</p>
      </div>
    );
  }

  if (!learningPath) return null;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[11px] font-mono uppercase tracking-wider text-blue-600 dark:text-blue-400 font-semibold">
              Gap-Prioritized Learning Roadmap
            </span>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              {learningPath.role_title} Mastery Path
            </h2>
            <p className="text-xs text-gray-500 dark:text-dark-muted mt-0.5">
              Ordered by career gap severity: Missing core skills are prioritized first.
            </p>
          </div>
          <div className="flex items-center space-x-2 text-xs font-mono text-gray-600 dark:text-dark-muted border border-gray-200 dark:border-dark-border px-3 py-1.5 rounded-md bg-gray-50 dark:bg-dark-bg self-start sm:self-auto">
            <Clock className="w-3.5 h-3.5" />
            <span>Estimated: {learningPath.total_estimated_time}</span>
          </div>
        </div>
      </div>

      {/* Grid: Roadmap Timeline on left, Selected Skill Resources on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Ordered Skill List */}
        <div className="lg:col-span-1 space-y-2">
          <h3 className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-dark-muted font-semibold px-1">
            Curriculum Sequence ({learningPath.ordered_skills.length} Skills)
          </h3>
          <div className="space-y-1.5">
            {learningPath.ordered_skills.map((item) => (
              <div
                key={item.skill}
                onClick={() => loadSkillResources(item.skill)}
                className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between text-xs ${
                  selectedSkill === item.skill
                    ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-950/30 text-gray-900 dark:text-white font-medium shadow-sm'
                    : 'border-gray-200 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-card text-gray-700 dark:text-dark-text'
                }`}
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <span className="font-mono text-gray-400 text-[11px] w-4">
                    #{item.step}
                  </span>
                  <div className="truncate">
                    <span className="font-semibold block truncate">{item.skill}</span>
                    <span className="text-[10px] text-gray-400 capitalize">{item.status}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-1 shrink-0">
                  {item.is_core && (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300">
                      Core
                    </span>
                  )}
                  <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Detailed Resources for Selected Skill */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-dark-card border border-gray-200 dark:border-dark-border rounded-lg p-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 dark:border-dark-border pb-3 mb-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-gray-400">Selected Module</span>
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  {selectedSkill} Technical Learning Resources
                </h3>
              </div>

              {selectedSkill && (
                <div className="flex space-x-2">
                  <button
                    onClick={() => onTakeQuiz(selectedSkill)}
                    className="px-3 py-1.5 rounded border border-gray-200 dark:border-dark-border text-xs font-medium text-gray-700 dark:text-dark-text hover:bg-gray-50 flex items-center space-x-1"
                  >
                    <CheckSquare className="w-3.5 h-3.5 text-green-600" />
                    <span>Assess</span>
                  </button>
                  <button
                    onClick={() => onMission(selectedSkill)}
                    className="px-3 py-1.5 rounded bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium flex items-center space-x-1"
                  >
                    <GitBranch className="w-3.5 h-3.5" />
                    <span>Start Mission</span>
                  </button>
                </div>
              )}
            </div>

            {/* List of Verified Public Resources */}
            <div className="space-y-3">
              {resources.length === 0 ? (
                <p className="text-xs text-gray-500 py-6 text-center">No curated links loaded.</p>
              ) : (
                resources.map((res) => (
                  <div
                    key={res.id}
                    className="border border-gray-200 dark:border-dark-border rounded-lg p-3.5 hover:border-gray-300 dark:hover:border-gray-600 transition-colors bg-gray-50/50 dark:bg-dark-bg/40 flex flex-col justify-between space-y-2"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-dark-card text-gray-700 dark:text-dark-muted capitalize font-medium">
                          {res.type} • {res.difficulty}
                        </span>
                        <span className="text-[11px] text-gray-400 font-mono flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{res.estimated_time}</span>
                        </span>
                      </div>
                      <h4 className="font-semibold text-sm text-gray-900 dark:text-white mt-1.5">
                        {res.title}
                      </h4>
                      <p className="text-xs text-gray-600 dark:text-dark-muted mt-1 leading-relaxed">
                        {res.description}
                      </p>
                    </div>

                    <a
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="self-start text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center space-x-1 pt-1"
                    >
                      <span>Open Verified Public Resource</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
