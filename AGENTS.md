# AGENTS.md - AI Coding Assistant Rules & Guardrails

> This repository houses the **BTL HUNRE O2O E-Commerce & AI Platform**.
> Stack: PHP Laravel + Python FastAPI + Docker Compose + MySQL 3307 + Redis 6379.

---

## 🚨 MANDATORY CONSTRAINTS FOR ALL AI CODING ASSISTANTS

Every AI Assistant (Cursor, GitHub Copilot, Claude, ChatGPT, Gemini, etc.) interacting with this workspace MUST enforce the following rules:

### 1. Git & Branching Safety
- **NEVER** push or suggest committing directly to `master`.
- **ALWAYS** instruct the developer to branch off `master`:
  ```bash
  git checkout master
  git pull origin master
  git checkout -b feature/<developer-name>-<feature-name>
  ```
- Keep pull requests small and focused.

### 2. API Contract Immutability (Backwards Compatibility)
- **NEVER** modify, rename, or delete existing JSON keys in request/response DTOs or endpoints across services.
- Inter-service communication relies on exact field mapping (e.g. `product_id`, `current_price`, `trust_score`).
- All changes must be **additive only** (new optional fields).
- When an endpoint URI is modified or added, update:
  - Gateway routing rules (`BTL/gateway/nginx.conf`).
  - Frontend API consumers (`BTL/frontend/student-portal/js/app.js`).

### 3. Port & Docker Infrastructure Protection
- **DO NOT** change port mappings in `BTL/docker-compose.yml`:
  - `8000`: BTL Nginx Gateway
  - `8001`: Auth Service
  - `8002`: Product Service
  - `8003`: Escrow Service
  - `8004`: Hub Logistics Service
  - `8005`: AI Intelligence Engine
  - `3307`: MySQL (BTL)
  - `6379`: Redis
- To restart only a modified service: `docker compose restart <service-name>`.

### 4. Zero-Downtime Safe Database Migrations
- **FORBIDDEN:** `DROP TABLE`, `TRUNCATE`, destructive `DROP COLUMN`.
- Database schema modifications must be additive migrations saved in `BTL/shared/database-init/` (e.g., `02_add_field.sql`):
  ```sql
  ALTER TABLE users ADD COLUMN phone_number VARCHAR(15) NULL;
  ```

### 5. Repository Cleanliness & Git Hygiene
- Before proposing any git commit, inspect `git status`.
- Ensure ignored files are **NEVER staged**:
  - `vendor/`, `.venv/`, `env/`
  - `__pycache__/`, `*.pyc`, `.pytest_cache/`
  - `*.log`, `out.log`
  - `.env` (contains private secrets)
- Commit messages must follow Conventional Commits: `feat(...)`, `fix(...)`, `docs(...)`.
