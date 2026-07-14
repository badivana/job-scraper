# Prompt Library

## Purpose

To centralize the prompt templates used by the AI Service for generating cover letters, cold emails, and skill‑gap analyses. This ensures consistency, facilitates A/B testing, and simplifies updates.

## Contents

- Cover Letter Prompt
- Cold Email Prompt
- Skill‑Gap Analysis Prompt
- Prompt Versioning
- Safety and Moderation
- Customization and Variables

## Cover Letter Prompt

Used when a user requests a cover letter for a specific job.

**System Message**  
"You are a professional cover letter writer with expertise in tailoring letters to job descriptions."

**User Message**  
"Write a concise, one‑page cover letter for the following resume and job description. Use a formal yet engaging tone, highlight relevant skills and experiences, and include a greeting and closing."

```
Resume Summary:
{resume_summary}

Job Description:
{job_description}
```

**Parameters**  
- `temperature`: 0.7 (balanced creativity)  
- `max_tokens`: 500  

## Cold Email Prompt

Used when a user wants a short outreach message to a recruiter or hiring manager.

**System Message**  
"You are a skilled business communicator who writes short, impactful outreach emails."

**User Message**  
"Write a brief (150‑200 word) email to a recruiter introducing the candidate, expressing interest in the role, and requesting a conversation or next steps."

```
Candidate Summary:
{resume_summary}

Job Title: {job_title}
Company: {company}
```

**Parameters**  
- `temperature`: 0.7  
- `max_tokens`: 200  

## Skill‑Gap Analysis Prompt

Used to identify missing skills and suggest learning resources.

**System Message**  
"You are an HR analyst specializing in skill gap analysis and career development."

**User Message**  
"Compare the candidate’s skill set with the job’s required skills. List the missing skills, estimate their importance (high/medium/low), and suggest one learning resource (course, tutorial, or certification) for each missing high‑importance skill."

```
Candidate Skills (normalized):
{candidate_skills}

Job Skills (normalized):
{job_skills}
```

**Parameters**  
- `temperature`: 0.2 (more factual)  
- `max_tokens`: 300  

## Prompt Versioning

Each prompt is stored as a Jinja2 template in the `prompts/ai.md` file (or separate files) with a version comment (e.g., `# v1.0`). Changes to prompts are tracked via Git, and backward compatibility is maintained by keeping old versions until a feature flag rollout is complete.

## Safety and Moderation

All prompts are designed to avoid requesting disallowed content. Additionally:
- The OpenAI Moderation API is called on both the prompt and the generated text.
- A profanity filter is applied to the output before storage or display.
- If the moderation API flags content, the request is rejected and an error is returned to the user.

## Customization and Variables

The following variables are injected into the templates at runtime:
- `resume_summary`: a brief summary of the user’s resume (experience, skills, education).
- `job_description`: the full text of the job posting.
- `job_title`, `company`: extracted fields from the job posting.
- `candidate_skills`, `job_skills`: arrays of normalized skill names (from the skill normalization pipeline).

These variables are prepared by the Resume Service and Job Service before calling the AI Service.
