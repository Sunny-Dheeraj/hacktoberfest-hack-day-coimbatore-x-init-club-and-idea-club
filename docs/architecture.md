# ProofPath — Architecture & Engineering Specification

> **Core Principle:** `NO EVIDENCE → NO CLAIM`

---

## 1. Phase 1 Purpose & Product Vision

ProofPath determines which technical skills of a software engineer can **actually be substantiated by evidence found in their public source code**.

Traditional resumes and GitHub profile summaries rely on unverified self-assertions or shallow README mentions. ProofPath replaces subjective claims with **deterministic, traceable code-level evidence**.

Phase 1 implements the complete **Proof Extraction Engine**:
- Ingests public GitHub profiles and repositories.
- Discovers file trees and filters out binaries, dependencies, and irrelevant artifacts.
- Deterministically parses source code ASTs, manifests, and framework patterns.
- Evaluates code signals against an extensible, data-driven skill taxonomy.
- Computes calibrated evidence strengths (Level 0 through Level 5) with source-location traceability.
- Emits structured Evidence JSON ready for Phase 2 career reasoning and role evaluation.

---

## 2. High-Level Architecture

```text
               ┌───────────────────────┐
               │    GitHub Username    │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │    GitHub Service     │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │  Repository Collector │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   File Prioritizer    │
               └───────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Python AST        JS / TS Parser      Dependency
    Analyzer            Analyzer          Analyzer
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   Framework Engine    │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │    Skill Detector     │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │    Evidence Engine    │
               │ (Strength & Location) │
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Structured Evidence   │
               │         JSON          │
               └───────────────────────┘
```

---

## 3. GitHub API Flow & Repository Collection

The `GitHubService` communicates with the GitHub REST API (`api.github.com`):
1. **Profile Fetch:** `GET /users/{username}` retrieves account metadata (`login`, `name`, `bio`, `avatar_url`, `public_repos`, `html_url`).
2. **Repository Fetch:** `GET /users/{username}/repos` fetches public, non-fork repositories sorted by recent updates.
3. **Git Trees API:** `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1` retrieves repository directory hierarchies in a single HTTP request without downloading entire archives.
4. **File Content:** Raw file contents are fetched selectively via the GitHub Contents API / Raw endpoints with strict size cutoffs.

### Resiliency & Limits
- **Authentication:** Reads `GITHUB_TOKEN` from environment variables if configured (elevates rate limits from 60 to 5,000 requests/hour).
- **HTTP Timeouts:** Enforces configurable HTTP timeouts (default: 15.0s).
- **Graceful Error Handling:** Translates 404 into `GitHubUserNotFoundError`, 403 into `GitHubRateLimitError`, and network issues into `GitHubAPIError`.

---

## 4. File Filtering & Security Model

Repository code is **untrusted external input**.

### Strict Security Rules
- **NEVER EXECUTE:** ProofPath never executes repository code, shell scripts, Python files, or package install commands (`pip install`, `npm install`).
- **READ-ONLY PARSING:** Analysis is strictly static (AST traversal, lexical tokenization, and JSON/TOML parsing).

### Ignored Directories
The following directories are pruned before content fetching:
- Version control: `.git/`, `.github/`
- Dependencies: `node_modules/`, `venv/`, `.venv/`, `env/`, `vendor/`
- Build outputs: `dist/`, `build/`, `.next/`, `target/`, `out/`, `bin/`, `obj/`
- Cache & metadata: `__pycache__/`, `coverage/`, `.idea/`, `.vscode/`, `.pytest_cache/`, `.mypy_cache/`

### Ignored Files & Binaries
- Images & Media: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.mp3`, `.mp4`, `.mov`, `.wav`
- Compiled Binaries & Archives: `.zip`, `.tar`, `.gz`, `.exe`, `.dll`, `.so`, `.bin`, `.pyc`
- Minified Code: `*.min.js`, `*.min.css`, `bundle.js`, `*.map`
- Documents & Fonts: `.pdf`, `.docx`, `.woff`, `.woff2`, `.ttf`

### Prioritization Hierarchy
1. **Manifests & Dependencies:** `requirements.txt`, `pyproject.toml`, `Pipfile`, `package.json`, `Dockerfile`
2. **Key Source Code:** `.py`, `.ipynb`, `.ts`, `.tsx`, `.js`, `.jsx`, `.sql`
3. **Documentation:** `README.md`
4. **Config:** `.yaml`, `.yml`

---

## 5. Analyzers

### 5.1 Python Analyzer (`PythonAnalyzer`)
- Uses Python's native `ast` module (no crude regex keyword guessing).
- Handles standard `.py` files and Jupyter notebooks (`.ipynb`) by extracting code cells.
- Extracts:
  - Import statements (`import torch`, `from torch import nn`)
  - Class definitions and base class inheritance (`class Model(nn.Module)`)
  - Function and async function definitions
  - Decorators (FastAPI `@app.get`, `@router.post`, Flask `@app.route`)
  - Method calls (`loss.backward()`, `optimizer.step()`, `DataLoader()`, `model.fit()`, `pd.read_csv()`)
  - Composite patterns (e.g., PyTorch training loops matching forward + backward + optimizer steps)
- Captures exact start and end line numbers (`line_start`, `line_end`).
- Catches syntax errors gracefully without failing overall analysis.

### 5.2 JavaScript / TypeScript Analyzer (`JavaScriptAnalyzer`)
- Analyzes `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`.
- Detects:
  - React imports and components (`React.FC`, function components, class components)
  - React hooks (`useState`, `useEffect`, `useContext`, `useMemo`, `useCallback`)
  - JSX syntax elements (`<div`, `<Component`)
  - Express.js route handlers (`app.get`, `router.post`)
  - Node.js APIs (`require('fs')`, `process.env`, `http.createServer`)
  - TypeScript constructs (`interface`, `type`, `enum`, generics, type annotations)
  - `async/await`, `fetch`, and `axios` HTTP calls

### 5.3 Dependency Analyzer (`DependencyAnalyzer`)
- Parses dependency manifests (`requirements.txt`, `pyproject.toml`, `Pipfile`, `package.json`, `package-lock.json`, `yarn.lock`, `Dockerfile`).
- Normalizes package names to canonical technologies (e.g., `torch` → `PyTorch`, `fastapi` → `FastAPI`).
- Classifies signals with type `dependency` (strength 2).

### 5.4 Framework Analyzer (`FrameworkAnalyzer`)
- Parses `.sql` files to extract relational statements (`SELECT`, `INSERT`, `CREATE TABLE`, `JOIN`).
- Scans `README.md` files to extract declared mentions (strength 1).

---

## 6. Skill Taxonomy (`data/skills.json`)

The skill catalog is **data-driven and externalized**:
```json
{
  "skills": [
    {
      "name": "PyTorch",
      "category": "Machine Learning",
      "signals": ["torch", "torch.nn", "torch.nn.Module", "torch.optim", "DataLoader", "loss.backward", "optimizer.step"],
      "dependencies": ["torch", "torchvision", "torchaudio"],
      "file_extensions": [".py", ".ipynb"],
      "parent_skills": ["Python", "Deep Learning", "Machine Learning"]
    }
  ]
}
```

Includes baseline definitions for:
`Python`, `JavaScript`, `TypeScript`, `React`, `Node.js`, `FastAPI`, `Flask`, `Django`, `PyTorch`, `TensorFlow`, `Scikit-learn`, `Pandas`, `NumPy`, `SQL`, `Git`, `Docker`, `OpenCV`, `Transformers`, `Machine Learning`, `Deep Learning`, `REST API`, `Data Analysis`.

---

## 7. Evidence Levels & Scoring Model

ProofPath measures **substantiated ability**, not repository popularity:
- Stars, forks, repository age, and commit frequency are **never** used as skill proof.

| Level | Evidence Type | Description | Example |
| :---: | :--- | :--- | :--- |
| **0** | None | No evidence detected in source code or metadata | Technology not present in repo |
| **1** | Mentioned | Technology claimed in documentation only | `README.md: "Built with PyTorch"` |
| **2** | Dependency | Technology declared in dependencies, but not in code | `requirements.txt: torch>=2.0.0` |
| **3** | Implementation | Direct source code usage (imports, simple calls) | `import torch; x = torch.tensor(...)` |
| **4** | Applied | Meaningful integration across components | `nn.Module` + `DataLoader` + training loop |
| **5** | Production | Applied integration + tests, CI/CD, or containerization | Applied code + `pytest` suite + `Dockerfile` |

### Status Classification
- **Proven:** Strength 4 to 5
- **Partial:** Strength 2 to 3
- **Missing:** Strength 0 to 1

---

## 8. Evidence Traceability & Schema

Every skill claim in ProofPath is accountable:
```text
Skill (e.g. PyTorch)
  └── Repository (e.g. vision-model)
        └── File (e.g. train.py)
              └── Lines (e.g. 5–32)
                    └── Signals (e.g. torch.nn.Module, DataLoader, optimizer.step)
                          └── Strength: 4 (Proven)
```

### JSON Schema Output (`AnalyzeResponse`)
```json
{
  "username": "coder",
  "profile": {
    "login": "coder",
    "name": "Alex Coder",
    "bio": "ML Engineer",
    "avatar_url": "https://avatars.githubusercontent.com/u/123",
    "public_repositories": 12,
    "html_url": "https://github.com/coder"
  },
  "repositories_analyzed": 5,
  "repositories": [
    {
      "name": "vision-model",
      "full_name": "coder/vision-model",
      "description": "Image classifier",
      "html_url": "https://github.com/coder/vision-model",
      "language": "Python",
      "stars": 15,
      "forks": 2,
      "default_branch": "main",
      "files_analyzed": 14
    }
  ],
  "skills": [
    {
      "skill": "PyTorch",
      "category": "Machine Learning",
      "status": "proven",
      "strength": 4,
      "evidence": [
        {
          "skill": "PyTorch",
          "status": "proven",
          "repository": "vision-model",
          "file": "train.py",
          "line_start": 5,
          "line_end": 32,
          "signals": ["torch.nn.Module", "DataLoader", "loss.backward", "optimizer.step"],
          "evidence_type": "applied",
          "strength": 4,
          "explanation": "PyTorch is applied meaningfully in train.py via torch.nn.Module, DataLoader, loss.backward, optimizer.step."
        }
      ]
    }
  ],
  "proven": ["Python", "PyTorch", "Deep Learning", "Machine Learning"],
  "partial": ["SQL"],
  "missing": ["Docker", "FastAPI"],
  "evidence": [...]
}
```

---

## 9. API Specifications

### `POST /api/github/analyze`
- **Request Body:**
  ```json
  {
    "username": "octocat",
    "max_repos": 5
  }
  ```
- **Response:** `200 OK` with full `AnalyzeResponse` JSON.
- **Errors:**
  - `404 Not Found`: GitHub user does not exist.
  - `429 Too Many Requests`: GitHub API rate limit reached.
  - `502 Bad Gateway`: GitHub connection error.

### `GET /api/github/profile/{username}`
- **Response:** `200 OK` with user profile and repository listing.

### `GET /health`
- **Response:** `200 OK` with service health status.

---

## 10. Phase 2 Integration Contract

In Phase 2, the **Evidence JSON** generated by Phase 1 will be fed directly to the Gemma reasoning model.

```text
┌───────────────────────┐
│     Phase 1 Output    │
│  (Evidence JSON)      │
└───────────┬───────────┘
            │  (No re-scraping of GitHub needed)
            ▼
┌───────────────────────┐
│     Phase 2 Gemma     │
│   Reasoning Engine    │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ • Role Readiness Gap  │
│ • Custom Tech Quizzes │
│ • Targeted Missions   │
└───────────────────────┘
```

The Phase 1 output guarantees complete traceability: Gemma will refer to verified physical files and line numbers rather than hallucinating skill claims.

---

## 11. Phase 2: Career Intelligence & Gemma 4 Architecture

Phase 2 builds directly upon the Phase 1 Proof Extraction Engine, introducing deterministic career role mapping and evidence-grounded AI interpretation powered by **Google Cloud Managed Gemma 4** (`gemma-4-26b-a4b-it-maas`).

### Architectural Pipeline

```text
GitHub Profile & Code
          │
          ▼
Phase 1 Proof Extraction (Deterministic)
          │
          ▼
Structured Skill Evidence & Strengths (0-5)
          │
          ▼
Career Role Matching (data/roles.json)
          │
          ├─────────────────────────────────────────┐
          ▼                                         ▼
Core Skills (2.0x Weight)             Supporting Skills (1.0x Weight)
          │                                         │
          └───────────────────┬─────────────────────┘
                              ▼
        Deterministic Readiness Score (0-100%)
                              │
          ┌───────────────────┴─────────────────────┐
          ▼                                         ▼
Proven / Partial / Missing              Dense Grounded Prompt
   Classifications                                  │
          │                                         ▼
          │                            Google Cloud Gemma 4
          │                            (gemma-4-26b-a4b-it-maas)
          │                                         │
          │                            ┌────────────┴────────────┐
          │                            ▼                         ▼
          │                     Raw JSON Output          Failure / Unconfigured
          │                            │                         │
          │                            ▼                         ▼
          │                     Schema Validation       Deterministic Fallback
          │                            │                         │
          └───────────────────┬────────┴─────────────────────────┘
                              ▼
                Unified Career Analysis JSON
```

### Deterministic Readiness Scoring

ProofPath maintains that **Code proves; AI interprets**. Gemma is strictly forbidden from altering technical evidence or readiness scores.

Readiness scoring is purely mathematical:
$$\text{Earned Score} = \sum (\text{weight}_i \times \text{strength}_i)$$
$$\text{Max Possible} = \sum (\text{weight}_i \times 5)$$
$$\text{Readiness Percentage} = \frac{\text{Earned Score}}{\text{Max Possible}} \times 100$$

- **Core Skills:** Weighted at **2.0**
- **Supporting Skills:** Weighted at **1.0**
- **Skill Classification:**
  - $\text{Strength} \ge 3 \implies \textbf{Proven}$
  - $\text{Strength} = 2 \implies \textbf{Partial}$
  - $\text{Strength} \le 1 \implies \textbf{Missing}$

### Google Cloud Managed Gemma 4 Integration

- **Model:** `gemma-4-26b-a4b-it-maas`
- **Location:** `global`
- **Vertex AI Model Garden / MaaS:** Access via Vertex AI endpoint or Google Cloud Generative AI gateway.
- **Strict Grounding:** The prompt embeds verified code signals, file paths, repositories, and deterministic metric scores. Gemma is instructed that `NO EVIDENCE -> NO CLAIM`.
- **Structured JSON Schema:** Output conforms strictly to `summary`, `strengths`, `gaps`, `recommendations`, and `confidence`.

### Deterministic AI Failure Fallback

If Gemma 4 credentials are unconfigured, network timeouts occur, or rate limits are met, the `GemmaService` automatically synthesizes a high-quality deterministic fallback `AIInsight`:
- `fallback_used = True`
- Grounded strengths derived from verified physical files.
- Gaps prioritized by core role requirements.
- Actionable engineering recommendations to bridge identified gaps.
- **The system never crashes or errors due to external AI unavailability.**

### Phase 2 API Endpoints

- **`POST /api/analysis/career`**: Executes Phase 1 proof extraction, deterministic career role matching, and Gemma 4 interpretation.
- **`GET /api/analysis/roles`**: Lists all available roles with requirement counts.
- **`GET /api/analysis/roles/{role_id}`**: Retrieves complete role definition with skill weights.

---

## 12. Phase 3: Proof & Progress Architecture

Phase 3 introduces the learning and verification loop, moving beyond passive evaluation to active skill progression and verified mastery.

### Tri-Pillar Skill Confidence Model

ProofPath measures true technical confidence through three calibrated pillars:
$$\text{Skill Confidence} = (\text{Code Evidence} \times 0.40) + (\text{Knowledge Quiz} \times 0.30) + (\text{Practical Ability} \times 0.30)$$

1. **Code Evidence (40%):** Derived deterministically from Phase 1 source code traces and calibrated strength levels (0–5).
2. **Knowledge Quiz (30%):** Tested via conceptual multiple-choice and snippet-based code reasoning questions.
3. **Practical Ability (30%):** Proved through Monaco Editor static coding challenges and GitHub repository practical missions.

### Three Dimensions of Quizzes

To distinguish shallow memorization from true engineering capability, ProofPath quizzes evaluate across three dimensions:
1. **Conceptual Knowledge:** "Do you know the principle?" (Multiple-choice conceptual questions).
2. **Code Reasoning:** "Can you read and reason about code using it?" (Snippet analysis and output prediction).
3. **Code Implementation:** "Can you actually write working code?" (Monaco Editor implementation challenge).

### Static Code Evaluation & Security Model

- **Zero Arbitrary Execution:** ProofPath strictly avoids `eval()`, `exec()`, or subshell execution.
- **Deterministic Static Evaluation:**
  - **Python:** AST tree traversal checks function definitions, inheritance, return statements, and syntax validity.
  - **JavaScript/TypeScript:** Regex and lexical token checks for components, JSX, array transformations, and event bindings.
  - **SQL:** Structural query verification for SELECT, GROUP BY, HAVING, and JOINs.
  - **Dockerfile:** Instruction inspection for FROM, WORKDIR, COPY, and CMD.

### Practical Missions & Static GitHub Verification

Practical tasks require students to create actual GitHub repositories:
- Evaluated via `VerificationService` reusing Phase 1's `GitHubService` and AST analyzers.
- Statically verifies directory structure, required artifact files (`Dockerfile`, `App.tsx`, `train.py`), and technical code signals.
- Returns deterministic statuses: `verified` (100%), `partially_verified` (50%), or `not_verified` (0%).

### Data Persistence Layer

Lightweight SQLite + SQLAlchemy storage tracks:
- `UserProfileRecord`: Target roles and settings.
- `SkillProgressRecord`: Composite confidence metrics (40/30/30).
- `QuizAttemptRecord`: Knowledge and reasoning answers.
- `CodeChallengeAttemptRecord`: Monaco editor submissions.
- `TaskAttemptRecord`: GitHub mission verification results.

---

## 13. Phase 4: Career Readiness Platform (Frontend)

Phase 4 provides a responsive web application built with **React, Vite, Tailwind CSS, Lucide icons, and Monaco Editor**.

### UI Aesthetic & Principles

- **Flat, Minimal, Clean:** Inspired by Linear and GitHub developer tools.
- **No Gimmicks:** Avoids bloated gradients, glassmorphism, or gaming visuals.
- **Dark & Light Mode:** Accessible theme toggle persisting user preference in `localStorage`.
- **Monaco Code Editor:** Interactive code editing with syntax highlighting, line numbers, and instant static evaluation.

### End-to-End User Journey

```text
Landing / Input GitHub Username (@torvalds) & Role (ML Engineer)
                    │
                    ▼
Deterministic Proof Extraction & Career Matching
                    │
                    ▼
Interactive Dashboard (Readiness Score & 0-5 Skill Cards)
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
Evidence Explorer       Next Best Action
(Exact File/Lines)      (e.g., Docker Quiz)
          │                   │
          │                   ▼
          │         3-Dimension Assessment
          │         (Knowledge -> Reasoning -> Monaco Editor)
          │                   │
          │                   ▼
          │         Deterministic Evaluation (AST Criteria)
          │                   │
          │                   ▼
          │         Practical Mission Briefing
          │                   │
          │                   ▼
          │         Submit GitHub Repo (e.g., user/docker-api)
          │                   │
          │                   ▼
          │         Static Verification (100% Verified)
          │                   │
          └───────────────────┼───────────────────┐
                              ▼                   ▼
                  Updated Tri-Pillar Progress   Next Action
```


