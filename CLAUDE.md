# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Backend for [hackernewsalerts.com](https://hackernewsalerts.com): emails users when someone replies to their Hacker News comments or posts. Two Django services share one database:

- **Web** (`alerts/views.py`): a [Django Ninja](https://django-ninja.dev/) REST API mounted at `/api/` handling signup, email verification, and unsubscribe.
- **Tasks** (`alerts/tasks.py`): a [Django Q2](https://django-q2.readthedocs.io/) `qcluster` worker that periodically scans HN for new activity and sends alert emails.

Django project package is `socialalerts`; the single app is `alerts`.

## Commands

```bash
make run-web          # runserver (web API)
make run-tasks        # qcluster (scheduled worker)
make migrate          # apply migrations
make makemigrations
make test             # python manage.py test
make create-superuser # admin user; also used as the failure-alert recipient
```

Run a single test: `python manage.py test alerts.tests_hn.HnGetNewCommentReplies`

Tests live in `alerts/tests_hn.py` and `alerts/tests_tasks.py` (NOT the empty default `tests.py`). `tests_tasks.py` is an opt-in integration test that hits the live proxy and sends a real email — it only runs when `TEST_RUN_TASK=1` and reads `TEST_HN_USERNAME` / `TEST_USER_EMAIL` from the environment.

## Environment & configuration

`settings.py` decides local vs. production by the presence of `SECRET_KEY`:
- **No `SECRET_KEY`** → LOCAL mode: `DEBUG=True`, SQLite (`db.sqlite3`), and `.env` is loaded via `python-dotenv`.
- **`SECRET_KEY` set** → production: Postgres from `DB_*` env vars.

Other required env vars: `UI_URL`, `API_URL`, `PROXY_HOSTNAME`, and AWS creds (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) for SES. `make` includes `.env` and exports it for the deploy targets.

## How the alert flow works

1. **Signup** (`POST /api/signup`) creates an unverified `User` (HN username + email, unique on username) and emails a verification link containing a `django.core.signing` token.
2. **Verify** (`POST /api/verify/{code}`) unsigns the token and sets `is_verified=True`.
3. **Worker** (`check_for_alerts` → `process_user`) runs over verified users only. For each user it fetches new post comments and comment replies since `user.last_checked`, composes one email, then advances `last_checked`. Any per-user exception is caught, counted, and a summary failure email is sent to the superuser — so a single user's bad data never stops the batch. Missing/`None` upstream data is expected and treated as "no items".
4. **Unsubscribe**: alert emails embed a signed token (separate `UnsubscribeSigner` salt). `GET /api/unsubscribe/` shows an HTML confirm page; `POST /api/unsubscribe/confirm/` (CSRF-exempt) deletes the user.

`check_for_alerts` is not scheduled in code — the Django Q2 schedule is configured at runtime (via the Django admin / Schedule table), not in this repo.

## HN data source (`alerts/hn.py`)

All HN data comes from a self-hosted JSON Feed proxy at `PROXY_HOSTNAME` (`/replies.jsonfeed`, `/submitted.jsonfeed`, `/item.jsonfeed`), not the official HN API. Post-comment scanning only considers posts from the last 14 days ("open for discussion"), and the user's own activity is filtered out of results.

## Deployment

Deployed to [CapRover](https://caprover.com/) as two apps from one repo, each with its own Dockerfile and `captain-definition` file:
- Web: `Dockerfile-web` → `run-web.sh` (runs `migrate` then gunicorn). Deploy with `make deploy-web`.
- Tasks: `Dockerfile-tasks` → `python manage.py qcluster`. Deploy with `make deploy-tasks`.

Email is sent through AWS SES (`alerts/mail.py`, region `eu-west-2`, hardcoded sender `alerts@hackernewsalerts.com`).
