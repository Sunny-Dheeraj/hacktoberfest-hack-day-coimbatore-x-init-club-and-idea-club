"""Google Cloud Managed Gemma 4 Service for ProofPath."""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.models.career import (
    CareerRole,
    ReadinessScore,
    SkillAssessment,
    AIInsight,
    SkillClassification,
)
from app.ai.prompt_builder import build_role_assessment_prompt

logger = logging.getLogger(__name__)


class GemmaService:
    """
    Client for Google Cloud Managed Gemma 4 (gemma-4-26b-a4b-it-maas).
    Interprets deterministic code evidence to provide structured career insights.
    Falls back gracefully to deterministic synthesis if AI is unavailable.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.location = location or os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        self.model_name = model_name or os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it-maas")
        self.api_key = api_key or os.getenv("GEMMA_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY") or os.getenv("GOOGLE_CLOUD_API_KEY", "")
        self.timeout = float(os.getenv("GEMMA_TIMEOUT", str(timeout)))

    def is_configured(self) -> bool:
        """Check if minimum Google Cloud or API credentials are provided."""
        return bool(self.api_key or self.project_id)

    async def generate_role_insight(
        self,
        username: str,
        role: CareerRole,
        readiness: ReadinessScore,
        assessments: List[SkillAssessment],
        proven_skills: List[str],
        partial_skills: List[str],
        missing_skills: List[str],
    ) -> AIInsight:
        """
        Generate evidence-grounded role insights using Gemma 4,
        with automatic fallback to deterministic synthesis if AI is unconfigured or fails.
        """
        if not self.is_configured():
            logger.info("Gemma 4 credentials not configured; using deterministic fallback.")
            return self._generate_deterministic_fallback(
                role, readiness, assessments, proven_skills, partial_skills, missing_skills
            )

        prompt = build_role_assessment_prompt(
            username=username,
            role=role,
            readiness=readiness,
            assessments=assessments,
            proven_skills=proven_skills,
            partial_skills=partial_skills,
            missing_skills=missing_skills,
        )

        try:
            raw_response = await self._call_gemma_api(prompt)
            parsed_insight = self._parse_and_validate_response(raw_response)
            if parsed_insight:
                return parsed_insight
            else:
                logger.warning("Gemma 4 response parsing failed; using fallback.")
                return self._generate_deterministic_fallback(
                    role, readiness, assessments, proven_skills, partial_skills, missing_skills
                )
        except Exception as e:
            logger.warning(f"Gemma 4 API request encountered error: {e}; using fallback.")
            return self._generate_deterministic_fallback(
                role, readiness, assessments, proven_skills, partial_skills, missing_skills
            )

    async def _call_gemma_api(self, prompt: str) -> str:
        """Execute async HTTP request to Google Cloud Gemma endpoint."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 1. API Key based access (Vertex AI MaaS / Generative AI gateway)
            if self.api_key:
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.model_name}:generateContent?key={self.api_key}"
                )
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "response_mime_type": "application/json",
                    },
                }
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                # Extract text from response structure
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                raise ValueError("Empty or invalid candidate content received from Gemma API")

            # 2. Google Cloud Vertex AI MaaS endpoint via project/location
            else:
                loc_prefix = f"{self.location}-" if self.location and self.location != "global" else ""
                url = (
                    f"https://{loc_prefix}aiplatform.googleapis.com/v1beta1/projects/"
                    f"{self.project_id}/locations/{self.location}/publishers/google/models/"
                    f"{self.model_name}:generateContent"
                )
                headers = {}
                token = os.getenv("GOOGLE_OAUTH_TOKEN")
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                payload = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                    },
                }
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                raise ValueError("Empty or invalid response from Vertex AI Gemma endpoint")

    def _parse_and_validate_response(self, text: str) -> Optional[AIInsight]:
        """Parse raw response text, strip markdown backticks if any, and validate schema."""
        if not text:
            return None

        clean_text = text.strip()
        # Remove markdown code fences if model wrapped response in ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
        if fence_match:
            clean_text = fence_match.group(1).strip()

        # If still not valid, try finding outermost JSON object
        json_obj_match = re.search(r"\{[\s\S]*\}", clean_text)
        if json_obj_match:
            clean_text = json_obj_match.group(0)

        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode Gemma JSON: {e}")
            return None

        # Validate required fields
        summary = data.get("summary")
        if not summary or not isinstance(summary, str):
            return None

        strengths = data.get("strengths")
        if not isinstance(strengths, list):
            strengths = [str(strengths)] if strengths else []

        gaps = data.get("gaps")
        if not isinstance(gaps, list):
            gaps = [str(gaps)] if gaps else []

        recommendations = data.get("recommendations")
        if not isinstance(recommendations, list):
            recommendations = [str(recommendations)] if recommendations else []

        confidence = float(data.get("confidence", 0.90))
        confidence = max(0.0, min(1.0, confidence))

        return AIInsight(
            summary=summary,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
            confidence=confidence,
            grounded=True,
            model_used=self.model_name,
            fallback_used=False,
        )

    def _generate_deterministic_fallback(
        self,
        role: CareerRole,
        readiness: ReadinessScore,
        assessments: List[SkillAssessment],
        proven_skills: List[str],
        partial_skills: List[str],
        missing_skills: List[str],
    ) -> AIInsight:
        """
        Deterministic, evidence-grounded fallback generator.
        Produces high-quality, traceable insights without requiring an active LLM call.
        """
        # Summary synthesis
        if readiness.score >= 75.0:
            readiness_desc = "strongly aligned with demonstrable production and applied evidence"
        elif readiness.score >= 45.0:
            readiness_desc = "partially aligned with key foundational competencies demonstrated"
        else:
            readiness_desc = "early-stage alignment with significant skill gaps requiring implementation proof"

        summary = (
            f"Candidate displays a deterministic {readiness.score}% readiness for the {role.title} role. "
            f"Core skills evaluated at {readiness.core_score}%, with {readiness_desc}. "
            f"{len(proven_skills)} skills proven through repository code."
        )

        # Grounded strengths
        strengths = []
        for a in assessments:
            if a.classification == SkillClassification.PROVEN and a.top_evidence:
                top_ev = a.top_evidence[0]
                strengths.append(
                    f"Verified {a.skill} implementation in {top_ev.file or top_ev.repository} "
                    f"(strength {a.evidence_strength}/5, {top_ev.evidence_type.value} tier)."
                )
            elif a.classification == SkillClassification.PROVEN:
                strengths.append(f"Demonstrated proficiency in {a.skill} with verified code traces.")

        if not strengths and proven_skills:
            strengths = [f"Demonstrated competence in {s}" for s in proven_skills[:5]]
        elif not strengths:
            strengths = ["Foundational repository structure and version control workflow."]

        # Identified gaps
        gaps = []
        for a in assessments:
            if a.is_core and a.classification == SkillClassification.MISSING:
                gaps.append(f"Critical core requirement '{a.skill}' has no source code implementation evidence.")
            elif a.is_core and a.classification == SkillClassification.PARTIAL:
                gaps.append(f"Core requirement '{a.skill}' is only partially evidenced (e.g. dependency manifest only).")

        for a in assessments:
            if not a.is_core and a.classification == SkillClassification.MISSING and len(gaps) < 4:
                gaps.append(f"Supporting skill '{a.skill}' is not currently evidenced in repositories.")

        if not gaps:
            gaps = ["No significant skill gaps identified for this role profile."]

        # Actionable recommendations
        recommendations = []
        for a in assessments:
            if a.is_core and a.classification == SkillClassification.MISSING:
                recommendations.append(
                    f"Build an end-to-end project applying {a.skill} with robust test coverage and configuration."
                )
            elif a.is_core and a.classification == SkillClassification.PARTIAL:
                recommendations.append(
                    f"Expand {a.skill} beyond package manifests into active architectural usage and handlers."
                )

        if len(recommendations) < 3:
            recommendations.append(
                f"Add automated tests and Docker/CI workflows to elevate applied skills to production strength."
            )
            recommendations.append(
                f"Document architecture and create full functional showcases for {role.title} competencies."
            )

        return AIInsight(
            summary=summary,
            strengths=strengths[:4],
            gaps=gaps[:4],
            recommendations=recommendations[:4],
            confidence=0.85,
            grounded=True,
            model_used=f"{self.model_name} (deterministic fallback)",
            fallback_used=True,
        )
