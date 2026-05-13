# Aegis — Phase 1 Architecture

Overview

Aegis is structured as a modular monorepo with separate frontend and backend services and an infrastructure composition for local development.

Core services
- `frontend`: Next.js 15 (App Router) TypeScript app. Handles UI, Auth.js (NextAuth) integration, and developer workflows.
- `backend`: FastAPI (Python 3.12) async service exposing REST APIs for auth, repo onboarding, ingestion orchestration, and integrations.
- `docker`: Docker Compose manifest for local dev: Postgres, Redis, Neo4j, Qdrant, frontend, backend.

Data model
- PostgreSQL: users, repositories, analyses, runs, github_connections
- Neo4j: code & architecture graph (nodes/edges), ingested later
- Qdrant: vector store for embeddings (future)

Ingestion flow (Phase 1 foundation)
1. User authenticates via GitHub OAuth.
2. User selects repositories to import via secure backend endpoints.
3. Backend validates repository metadata and enqueues an ingestion job.
4. Ingestion worker (future) will create an isolated workspace, clone, validate, and run language parsers.
5. Parsed AST/artifacts will be stored as graph nodes in Neo4j and vectors in Qdrant.

Security considerations
- Short-lived tokens, encrypted storage, strict scopes.
- Repository clone sandboxing (ephemeral workspaces) with network restrictions.
- Input sanitization, size/time limits, rate limiting.
