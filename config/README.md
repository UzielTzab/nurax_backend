# Configuration Files

This directory contains environment-specific configuration files.

## Files

### `postgres.env`
**Database connection configuration** - Used by Docker Compose for both `db` and `api` services.

Only contains PostgreSQL/Database-related variables:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_SSLMODE`, `DB_PORT`

**Never commit to Git** (has database credentials)
**Template:** `postgres.env.example`

### `postgres.env.example`
Template for `postgres.env`. Safe to commit to Git.

---

## How to Set Up

1. **Database Configuration:**
   ```bash
   cp postgres.env.example postgres.env
   # Edit postgres.env with your database credentials
   ```

2. **Application Configuration:**
   ```bash
   # From root of project (not from config/)
   cp .env.example .env
   # Edit .env with Cloudinary, Pusher, Admin credentials
   ```

3. **Run Docker:**
   ```bash
   docker-compose up --build
   ```

---

## Environment Variable Distribution

| File | Scope | Contains |
|------|-------|----------|
| `config/postgres.env` | Database only | PostgreSQL connection (DB_HOST, DB_NAME, etc.) |
| `.env` (root) | Application | Django settings, Cloudinary, Pusher, Admin creds |
| `docker-compose.yml` | Both | Loads both files via `env_file` |

---

## For Developers

- ✅ Commit: `postgres.env.example` and `.env.example`
- ❌ Never commit: `postgres.env` and `.env`
- ⚠️  Both are in `.gitignore` for safety
