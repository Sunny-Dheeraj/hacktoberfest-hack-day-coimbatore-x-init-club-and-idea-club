# ProofPath

> Career advice backed by your own code.

## Team

**Team Name:** Rebels


| Member | Contribution   |
| ------ | -------------- |
| Varun Shankar | Team Leader |
| Dheeraj Kumar Reddy | Member |
| Vishnu Vardhan Reddy | Member |
| Mohith Kumar Naidu | Member |


## Problem Statement

### The Problem

Students and early-career developers frequently list technical skills on their resumes that are difficult to verify from their actual work.

A developer may claim:

Python
Machine Learning
PyTorch
Docker
AWS
MLOps

However, their GitHub repositories may contain only partial evidence, tutorial projects, unused dependencies, incomplete implementations, or projects without deployment and testing.

This creates a gap between:

What a developer claims
        ≠
What their code demonstrates

Existing career platforms often depend on resumes, questionnaires, self-reported skills, or generic AI recommendations. These approaches can produce advice that is disconnected from the candidate's actual technical experience.

Students therefore need a way to answer:

What skills does my code actually demonstrate?

Which of my claimed skills can I prove?

What evidence supports each skill?

What skills am I missing for my target role?

What should I build next to become more career-ready?

### Why We Chose This Problem

**Why We Chose This Problem**

Students often have projects but struggle to communicate the technical value of those projects.

A GitHub repository contains much more information than a resume:

Source code

Dependencies

Project structure

APIs

Tests

Configuration

Documentation

CI/CD workflows

Deployment configuration

Development patterns

We wanted to turn this existing technical evidence into meaningful career guidance.

Instead of asking an AI:

"What should this student learn?"

ProofPath asks:

"What does this student's code prove, and what evidence is still missing?"

This makes career advice more transparent, personalized, and actionable.

## **Solution**

ProofPath analyzes a user's GitHub repositories against a selected target role and creates an evidence-backed career readiness profile.

The system follows this workflow:

GitHub Profile
      ↓
Repository Collection
      ↓
Code & Dependency Analysis
      ↓
Evidence Extraction
      ↓
Skill Verification
      ↓
AI Evidence Reasoning
      ↓
Role Readiness Analysis
      ↓
Skill Gaps
      ↓
Proof Missions

For example, if a user claims to know PyTorch, ProofPath does not automatically accept the claim.

It searches for evidence such as:

torch imports
nn.Module
DataLoader
optimizers
training loops
model implementation

If these are found in meaningful implementation contexts, ProofPath can classify the skill as strongly demonstrated.

If the repository only mentions PyTorch in a README, the skill may be classified as weak or unverified.


### Key Features

1. **GitHub Code Analysis**

Analyze public repositories and identify technologies, programming languages, frameworks, dependencies, implementation patterns, and engineering practices.

2. **Evidence-Based Skill Detection**

Determine whether a skill is:

Not demonstrated

Claimed only

Supported by dependency evidence

Supported by implementation evidence

Strongly demonstrated

Supported by production/engineering evidence

3. **Claim vs Proof**

Compare user-claimed skills with evidence found in their GitHub repositories.

Example:

Skill

Claim

Evidence

Status

Python

Yes

Strong implementation

🟢 Proven

PyTorch

Yes

Training pipeline

🟢 Proven

Docker

Yes

README only

🟡 Weak

AWS

Yes

No evidence

🔴 Unverified

SQL

Yes

Multiple projects

🟢 Proven

4. **Evidence Explorer**

Every skill assessment can be traced back to the repository and file that produced the evidence.

Skill
 ↓
Repository
 ↓
File
 ↓
Implementation
 ↓
Evidence

5. **Role Readiness Analysis**

Compare demonstrated skills against the requirements of a target role such as:

Full-Stack Developer

ML Engineer

Data Analyst

Data Scientist

Backend Developer

Frontend Developer

AI Engineer

DevOps Engineer

Data Engineer

6. **Skill Gap Detection**

Identify the skills that are missing or insufficiently demonstrated for the selected career path.

7. **Proof Missions**

Instead of giving generic advice such as "learn Docker", ProofPath generates practical tasks that use the user's existing projects to create new evidence.

Example:

Proof Mission: Prove Docker proficiency

1. Add a Dockerfile
2. Containerize the existing application
3. Add a health endpoint
4. Add basic tests
5. Document container execution

8. **Evidence Graph**

Visualize the relationship between:

Target Role
    ↓
Required Skill
    ↓
Repository
    ↓
File
    ↓
Code Evidence

9. **AI-Powered Evidence Reasoning**

An open-source/open-weight AI model such as Gemma reasons over structured evidence to explain:

Why a skill is supported

How strong the evidence is

What limitations exist

What evidence is missing

What the developer should build next

The AI interprets evidence rather than inventing it.

10. **Interview Defense Mode**

Generate interview questions based on the user's actual repositories and implementations, helping developers prepare to explain the work they claim on their resumes.

## Innovation and Differentiation

Most AI career tools follow a model similar to:

Resume
  ↓
AI
  ↓
Generic Career Advice

ProofPath uses an evidence-first approach:

Actual Code
    ↓
Evidence
    ↓
Skill Verification
    ↓
AI Reasoning
    ↓
Role Analysis
    ↓
Skill Gaps
    ↓
Proof Missions
    ↓
New Evidence

The central innovation is the Proof Loop.

A missing skill does not simply become a recommendation.

It becomes a practical project mission designed to generate evidence for that skill.

For example:

Docker
  ↓
No implementation evidence
  ↓
Proof Mission
  ↓
Dockerize existing project
  ↓
New Docker evidence
  ↓
Improved career profile

Core Differentiator

ProofPath doesn't evaluate what you claim. It evaluates what you can prove.

Another important design principle is:

Code proves. AI interprets.

Static analysis and deterministic rules establish factual evidence, while the AI is used for reasoning and personalized recommendations.


## Technical Implementation

### Architecture
flowchart TD

    A[GitHub Username] --> B[GitHub API / Repository Collector]

    B --> C[Repository Analyzer]

    C --> D[Source Code Analysis]
    C --> E[Dependency Analysis]
    C --> F[Project Metadata]
    C --> G[Engineering Analysis]

    D --> H[Evidence Engine]
    E --> H
    F --> H
    G --> H

    H --> I[Skill Detection]

    I --> J[Gemma Evidence Reasoner]

    J --> K[Role Matching Engine]

    K --> L[Role Readiness Score]
    K --> M[Skill Gap Analysis]
    K --> N[Claim Verification]

    M --> O[Proof Mission Generator]

    L --> P[Career Report]
    N --> P
    O --> P

    P --> Q[Evidence Explorer]
    P --> R[Evidence Graph]

### Technology Stack


| Category        | Technologies                |
| --------------- | --------------------------- |
| Frontend        | [Technologies / N/A]        |
| Backend         | [Technologies / N/A]        |
| Database        | [Technologies / N/A]        |
| AI / ML         | [Models / frameworks / N/A] |
| Infrastructure  | [Technologies / N/A]        |
| APIs / Services | [Services / N/A]            |


### How It Works

1. GitHub Collection

The user provides a GitHub username.

ProofPath collects publicly accessible repository information and identifies the most relevant repositories for analysis.

2. Repository Analysis

Each repository is analyzed for:

Programming languages

Frameworks

Libraries

Dependencies

Source code

Project structure

Tests

Documentation

Docker configuration

CI/CD configuration

API implementation

Deployment-related configuration

3. Evidence Extraction

The system converts technical signals into structured evidence.

For example:

{
  "skill": "PyTorch",
  "repository": "image-classifier",
  "file": "train.py",
  "evidence_type": "implementation",
  "signals": [
    "torch.nn.Module",
    "DataLoader",
    "optimizer",
    "training loop"
  ]
}

4. Skill Verification

ProofPath determines how strongly the available evidence supports each skill.

A dependency alone is not treated as equivalent to meaningful implementation.

For example:

requirements.txt
      ↓
torch
      ↓
Dependency Evidence

is weaker than:

model.py
      ↓
torch.nn.Module
      ↓
training pipeline
      ↓
Implementation Evidence

5. AI Evidence Reasoning

Structured evidence is passed to the AI reasoning layer.

The model helps answer:

Does this evidence support the skill?

How strong is the evidence?

What limitations should be communicated?

What additional evidence would strengthen the claim?

What practical project should the developer build next?

The AI is constrained by the evidence collected from the repository.

6. Role Matching

The selected target role contains a set of expected skills and capabilities.

ProofPath compares those requirements with the user's demonstrated evidence.

For example:

Target Role: ML Engineer

Python              ✓ Strong
Machine Learning    ✓ Strong
PyTorch             ✓ Strong
API Development     ◐ Partial
Docker              ◐ Partial
Testing             ◐ Partial
MLOps               ✕ Missing
Cloud               ✕ Missing

7. Proof Mission Generation

The system converts important gaps into practical tasks.

Example:

Gap:
Deployment

Existing Evidence:
ML model + Python project

Proof Mission:

Build a FastAPI inference endpoint,
containerize it using Docker,
add automated tests,
and document deployment.

### Technical Decisions

Evidence Before AI

We intentionally separate factual analysis from AI reasoning.

Static Analysis
      ↓
Facts
      ↓
Evidence
      ↓
AI Reasoning

This reduces the risk of hallucinated career claims.

Evidence-Based Scoring

Skills are not treated as simple yes/no values.

The system considers different levels of evidence, ranging from claims and dependency signals to implementation and production-level evidence.

Repository-Level Traceability

Every major assessment should be traceable back to a repository and file whenever possible.

This makes the system explainable and allows users to verify the result themselves.

Role-Specific Analysis

Career readiness is contextual.

A repository may demonstrate strong frontend skills but provide little evidence for an ML Engineer role.

Therefore, ProofPath evaluates skills relative to the user's selected target role.


## Implementation During the Hackathon

During the Hack Day, the team will build the core ProofPath workflow from GitHub analysis to evidence-backed career recommendations.

The main implementation will focus on:

GitHub repository collection

Source-code and dependency analysis

Evidence extraction

Skill detection

Role matching

AI-powered evidence reasoning

Evidence-backed career report

Skill gap analysis

Proof Mission generation

Interactive user interface

The MVP will prioritize a complete working flow over supporting a very large number of programming languages or career roles.


### Team Contributions

- **Varun Shankar:** [Contribution]
- **Dheeraj Kumar Reddy:** [Contribution]
- **Vishnu Vardhan Reddy:** [Contribution]
- **Mohith Kumar Naidu:** [Contribution]

## Working Application

**Live Application:** [Live URL]


The application should allow users to:

Enter a GitHub username.

Select a target career role.

Start the repository analysis.

View the detected skills.

Inspect evidence behind each skill.

View their role readiness profile.

Identify missing or weak skills.

Receive personalized Proof Missions.

## Demo Video

**Demo Video:** [Video URL]

[Provide a short demonstration of the working project, covering the main user flow and important functionality.]

## Open Source and AI Usage

### AI / Models

- **[Model]:** [How it is used]

### Open Source Components

- **[Library / Framework]:** [Purpose]
- **[Dataset]:** [Purpose]
- **[API / Service]:** [Purpose]

[Include relevant licenses, attribution, and acknowledgements for external components.]

## Setup and Usage

### Prerequisites

- [Requirement]
- [Requirement]

### Installation

```bash
git clone [repository-url]
cd [project-directory]
[installation-command]
```

### Environment Variables

```env
[VARIABLE_NAME]=[value]
```



### Running the Project

```bash
[run-command]
```

### Usage

[Explain the basic steps required to use the project.]

## Devpost Submission

**Devpost Project:** [Devpost Project URL]

[Add the link to the team's Devpost submission. Ensure the Devpost project page is complete and contains the required project information, links, media, and team details.]

## Credits and License

### Credits

[Credit libraries, frameworks, datasets, models, APIs, contributors, and other external resources used.]

### License

[License name and/or link.]

## Submission Checklist

- [ ] Project title and description added
- [ ] All team members listed
- [ ] Problem clearly explained
- [ ] Reason for choosing the problem explained
- [ ] Solution and key features documented
- [ ] Innovation and differentiation explained
- [ ] Architecture included
- [ ] Technical implementation documented
- [ ] Work completed during the hackathon documented
- [ ] Team contributions documented
- [ ] Working application is functional
- [ ] Live application link added where applicable
- [ ] Demo video added
- [ ] AI and open-source components documented
- [ ] Setup and usage instructions tested
- [ ] Challenges and learnings documented
- [ ] Devpost submission completed
- [ ] Devpost link added
- [ ] Credits added
- [ ] License added
- [ ] Repository is organized and complete
