---
project: laos-events
url: https://laos-events.shellnode.lol
vps: ghost
port: 80
stack: static HTML/CSS/JS, nginx:alpine, SWAG
standards_version: "2.0"
security: done
ux_ui: not_started
repo_cleanup: done
readme: done
last_session: "2026-03-09"
has_blockers: false
---

# Project Status — laos-events

## Last Session
Date: 2026-03-09
Agent: Claude Code

### Completed
- Fixed Dockerfile: replaced `COPY . /usr/share/nginx/html` with explicit copies of web assets only (index.html, styles.css, main.js, images/)
- Created nginx.conf with security headers, gzip, dotfile block, static caching
- Created .dockerignore (excludes .venv, *.py, requirements.txt, images/raw, .env, etc.)
- Added .env / .env.* to .gitignore
- Updated docker-compose.yml: added SWAG routing labels, added `image:` field, removed hardcoded port mapping
- Added README.md

### Incomplete
- UX/UI audit not started

### Blocked — Needs Matt
- Confirm swag_address: used `laos-events-app` (matches container_name). If subdomain should be different, update swag_url label.
- docker-compose.yml previously had port `8422:80` — removed in favor of SWAG-only routing. If direct port access is needed, add back.

## Backlog
- [P2] UX/UI audit — responsiveness, page weight, console errors
- [P3] images/thumbs and images/full in git repo (49MB) — consider .gitignore for large image dirs

## Done
- [x] Dockerfile hardened (explicit COPY, nginx.conf, proper EXPOSE) — 2026-03-09
- [x] nginx.conf created with full security/perf config — 2026-03-09
- [x] .dockerignore created — 2026-03-09
- [x] .gitignore updated (.env added) — 2026-03-09
- [x] docker-compose.yml updated with SWAG labels — 2026-03-09
- [x] README.md added — 2026-03-09

## Decisions Log
- "Dockerfile previously used COPY . . — this exposed Python scripts (crawl_images.py, fetch_replacements.py, requirements.txt) in nginx web root. Fixed to explicit COPY of web assets only." (2026-03-09)
- "Removed hardcoded port 8422:80 from docker-compose — SWAG handles routing via labels, no need for direct port exposure." (2026-03-09)
- "images/ included in git — 49MB of webp images. This is large but intentional. Left as-is, added backlog note." (2026-03-09)

## Project Notes
- Has Python pipeline scripts (crawl_images.py, fetch_replacements.py) — these are dev tools, not served
- .venv/ is in .gitignore but IS present locally — not committed
- images/ has full/, thumbs/, and raw/ subdirectories — raw/ is gitignored, others are tracked
