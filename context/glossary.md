# Glossary

This document defines key terms used throughout the AI-Powered Job Finder project.

## A

**ATS (Applicant Tracking System)**
Software used by employers to manage recruitment and hiring processes. Not integrated in the MVP but noted as out of scope for direct integration.

**API (Application Programming Interface)**
A set of rules that allows different software applications to communicate with each other. The backend exposes a REST/JSON API for the frontend and internal services.

**Apify**
A platform for web scraping and automation. Used to extract job postings from various sources via pre-built actors.

## C

**CI/CD (Continuous Integration/Continuous Deployment)**
A practice of automating the integration, testing, and deployment of code changes. Implemented via GitHub Actions in this project.

**Celery**
A distributed task queue used for asynchronous job processing (e.g., scraping, embedding generation, notifications).

**Celery Beat**
A scheduler that triggers periodic tasks (e.g., triggering scraping jobs at defined intervals).

**Celery Worker**
A background process that executes tasks from the Celery queue.

**Docker**
A platform for developing, shipping, and running applications in containers. Used to containerize the frontend, backend, and worker services.

**Docker Compose**
A tool for defining and running multi-container Docker applications. Used for local development setup.

## F

**FastAPI**
A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. Used for the backend service.

## G

**GDPR (General Data Protection Regulation)**
A regulation in EU law on data protection and privacy. The project aims to be GDPR-compliant.

**JWT (JSON Web Token)**
An open standard for securely transmitting information between parties as a JSON object. Used for authentication via Supabase Auth.

**JWKS (JSON Web Key Set)**
A set of keys containing the public keys used to verify JWTs. The backend validates tokens using Supabase's published JWKS.

## M

**Microservices**
An architectural style that structures an application as a collection of loosely coupled services. The project follows a modular monolith approach with a path to migrate to microservices.

## N

**Next.js**
A React framework for building server-side rendered and static web applications. Used for the frontend.

## O

**OAuth**
An open standard for access delegation commonly used for token-based authentication. Supported via Supabase Auth (Google, GitHub, etc.).

## P

**PostgreSQL**
A powerful, open-source object-relational database system. Used via Supabase with the pgvector extension for vector storage and similarity search.

**pgvector**
A PostgreSQL extension for efficient similarity search using vector data types. Used to store and query résumé and job embeddings.

## R

**Redis**
An in-memory data structure store used as a database, cache, and message broker. Used as the Celery broker and for caching.

**REST (Representational State Transfer)**
An architectural style for designing networked applications. The backend follows REST principles for its API.

**Role-Based Access Control (RBAC)**
A method of restricting system access based on the roles of individual users. Implemented via user metadata (user/admin) in Supabase Auth.

**Row Level Security (RLS)**
A feature of PostgreSQL that enables controlling access to rows in a database. Used to enforce data access policies in Supabase.

## S

**SaaS (Software as a Service)**
A software distribution model in which applications are hosted by a provider and made available to customers over the internet. The project is a SaaS platform.

**SDK (Software Development Kit)**
A set of tools and libraries used to develop applications for a specific platform. Not explicitly called out but implied via libraries (e.g., Supabase JS client).

## T

**TypeScript**
A strongly typed programming language that builds on JavaScript, adding static type definitions. Used for the frontend.

## U

**UUID (Universally Unique Identifier)**
A 128-bit label used for information in computer systems. Used as primary keys in the database.

## W

**WebSocket**
A protocol providing full-duplex communication channels over a single TCP connection. Used optionally for real-time features via Supabase Realtime.

## Domain-Specific Terms

**Cover Letter Generation**
The process of using AI (LLM) to create a personalized cover letter based on a user's résumé and a job description.

**Deduplication**
The process of identifying and removing duplicate job postings from collected data. Uses exact hashes and fuzzy matching.

**Embedding**
A numerical representation of text (typically a vector) that captures semantic meaning. Generated via OpenAI's text-embedding-3-small model.

**Job Ingestion**
The process of fetching, normalizing, deduplicating, and storing job postings from external sources (via Apify) into the database.

**Job Matching**
The process of computing relevance scores between a user's résumé and job postings using a hybrid of vector similarity, keyword overlap, recency, and location factors.

**Normalization**
The process of cleaning and structuring raw job data into a consistent format (e.g., parsing salary, standardizing location).

**Resume Parsing**
The process of extracting text from a résumé file (PDF/DOCX) and structuring it into sections (contact, summary, experience, education, skills, certifications).

**Skill Extraction**
The process of identifying and normalizing skills from résumé text, often mapping to a standard taxonomy (e.g., ESCO, O*NET).

**Vector Similarity**
A measure of similarity between two vectors, often using cosine distance. Used to compare résumé and job embeddings.