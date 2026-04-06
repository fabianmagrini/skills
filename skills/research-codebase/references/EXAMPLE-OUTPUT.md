# example-project — Documentation

> A minimal Express.js REST API for managing to-do items, backed by PostgreSQL.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Infrastructure](#infrastructure)
- [Data Model](#data-model)
- [Development Setup](#development-setup)
- [Available Commands](#available-commands)
- [Tech Stack](#tech-stack)

## Overview

`example-project` is a simple CRUD API for to-do items. It exposes a REST interface over HTTP, stores data in PostgreSQL, and is designed to be deployed as a single Docker container.

## How It Works

Incoming HTTP requests are handled by Express route handlers in `src/routes/`. Each handler validates input, calls a service function in `src/services/`, which in turn runs a query via the repository layer in `src/repositories/`. Responses are JSON.

## Architecture

```
Client
  │
  ▼
Express (src/app.ts)
  │
  ├── src/routes/todos.ts       ← HTTP layer
  │       │
  │       ▼
  ├── src/services/todoService.ts  ← Business logic
  │       │
  │       ▼
  └── src/repositories/todoRepo.ts ← DB queries (pg)
          │
          ▼
      PostgreSQL
```

## Repository Structure

```
example-project/
├── src/
│   ├── app.ts              # Express app setup, middleware
│   ├── routes/
│   │   └── todos.ts        # GET /todos, POST /todos, DELETE /todos/:id
│   ├── services/
│   │   └── todoService.ts  # Validation and business rules
│   └── repositories/
│       └── todoRepo.ts     # Raw SQL via node-postgres
├── migrations/
│   └── 001_create_todos.sql
├── tests/
│   └── todos.test.ts       # Jest integration tests
├── docker-compose.yml
├── Dockerfile
└── package.json
```

## Infrastructure

| Name | Technology | Port | Purpose |
|------|-----------|------|---------|
| db | PostgreSQL 15 | 5432 | Primary data store |

## Data Model

### `todos`

Defined in `migrations/001_create_todos.sql`.

| Column | Type | Notes |
|--------|------|-------|
| `id` | `uuid` | Primary key, default `gen_random_uuid()` |
| `title` | `text` | Required |
| `done` | `boolean` | Default `false` |
| `created_at` | `timestamptz` | Default `now()` |

## Development Setup

**Prerequisites:** Node.js 20+, Docker

```bash
# 1. Install dependencies
npm install

# 2. Start the database
docker compose up -d db

# 3. Run migrations
npm run migrate

# 4. Copy and configure environment
cp .env.example .env

# 5. Start the dev server
npm run dev
```

**Environment variables:**

| Variable | Example | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgres://user:pass@localhost:5432/todos` | PostgreSQL connection string |
| `PORT` | `3000` | HTTP port |

## Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with hot reload |
| `npm run build` | Compile TypeScript to `dist/` |
| `npm start` | Run compiled app |
| `npm test` | Run Jest test suite |
| `npm run migrate` | Apply pending migrations |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Node.js 20 |
| Framework | Express 4 |
| Language | TypeScript 5 |
| Database | PostgreSQL 15 |
| DB client | node-postgres (pg) |
| Testing | Jest |
| Containerisation | Docker / Docker Compose |
