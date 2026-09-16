# Crestview Estates

A one-page marketing / lead-gen landing site for "Crestview Estates," a
residential property in Los Angeles. Built with FastAPI, server-rendered
Jinja2 templates, and SQLite — no separate JS framework.

Recreated from the design handoff in
`design_handoff_crestview_estates/` (see that folder's `README.md` for the
full section-by-section spec this implementation follows).

## Stack

- **Backend:** FastAPI
- **Templates:** Jinja2 (server-rendered, no client framework)
- **Database:** SQLite via SQLAlchemy (swap `DATABASE_URL` for Postgres later)
- **Frontend interactivity:** plain CSS transforms + vanilla JS (3D carousel,
  sticky CTA, lead form submission)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real SMTP creds before launch
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/.

The SQLite database file and its `leads` table are created automatically on
startup (`app/database.py` + `app/models.py`).

## Deploying to Vercel

`vercel.json` + `api/index.py` re-export the FastAPI app as a Vercel Python
serverless function, so `vercel deploy` (or a GitHub-connected project)
should build and serve the site with no further config.

**Read this before you rely on it in production:** a serverless function's
filesystem is read-only except `/tmp`, and `/tmp` is wiped on every cold
start and isn't shared across instances. `app/config.py` detects Vercel's
`VERCEL=1` env var and points SQLite at `/tmp/crestview.db` automatically
so the app doesn't crash — but that means **leads saved through the
`/tmp` SQLite file can and will disappear** between deploys, cold starts,
and scale-out. Two ways to get real persistence:

1. **Set `DATABASE_URL` to a hosted Postgres** in the Vercel project's
   environment variables (Neon, Supabase, and Vercel Postgres all work —
   pick one, create a database, copy its connection string). Add
   `psycopg2-binary` to `requirements.txt` and nothing else needs to
   change; SQLAlchemy handles the rest.
2. **Host it somewhere with a persistent disk and a long-running process**
   instead — Render, Railway, Fly.io, or a small VPS all suit a stateful
   FastAPI app better than serverless. On any of those, `uvicorn
   app.main:app` (see Setup above) is the whole deployment.

The same caveat applies to the background lead-notification email
(`app/email_utils.py`): FastAPI's `BackgroundTasks` runs after the response
is sent, and a serverless platform can freeze the function's container
right after that response — so once you fill in real `SMTP_*` credentials,
test that the email actually lands when deployed on Vercel specifically,
not just locally.

## Project layout

```
api/
  index.py        Vercel serverless entrypoint (re-exports app/main.py's app)
vercel.json       Vercel build/route config
app/
  main.py         FastAPI app, page route, POST /api/leads
  config.py       Settings loaded from .env (DB URL, SMTP)
  database.py     SQLAlchemy engine/session
  models.py       Lead ORM model
  schemas.py      Lead request validation
  content.py      Loads data/content.json
  email_utils.py  Lead notification email (SMTP)
data/
  content.json    All page copy: stats, amenities, floor plans, gallery
                   photo slots, testimonial, location info. Edit this file
                   (or later move it into DB tables / a real CMS) instead
                   of hardcoding copy in templates.
templates/
  base.html, index.html, partials/*.html
static/
  css/styles.css  Design tokens + section layout
  js/carousel.js  3D circular gallery carousel
  js/main.js      Sticky CTA + lead form submission
```

## What's still a placeholder

- **Photos.** `static/img/design-placeholders/` holds 11 photos recovered
  from the design handoff's own screenshots (cropped out of
  `02-about.png`, `05-location.png`, `06-retreat.png` — About's 3 photos,
  Location's site photo, and Retreat's 6-photo mosaic + feature photo) and
  wired into their matching slots via `data/content.json`'s `*_src` fields,
  at the client's request, purely so the site doesn't look unfinished
  during development. **They are still the same unlicensed stock imagery
  the design handoff's own README says isn't cleared for production** —
  every slot using one still carries the `TODO: replace with real,
  licensed property photography` HTML comment (see
  `templates/partials/photo.html`), now noting it's a temporary stand-in
  specifically. Two things could *not* be recovered this way and are still
  gray placeholder plates: the **hero background photo** and all **25
  gallery carousel photos** — the handoff's screenshots folder never
  included captures of those two sections, only About/Amenities/Floor
  Plans/Location/Retreat. Swap every photo (recovered or not) for real,
  licensed photography before launch — search the templates for
  `photo_plate(` to find every slot.
- **SMTP.** `app/email_utils.py` sends a lead notification email on each
  `/api/leads` submission, but does nothing (just logs) until `SMTP_HOST` is
  set in `.env`. Leads are always saved to the database regardless of email
  delivery.
- **Testimonial.** Single hardcoded quote in `data/content.json` — same as
  the design mock.

## Lead form

`POST /api/leads` accepts `{ "name": string, "phone": string }` as JSON,
validates both fields (see `app/schemas.py`), saves the lead to the `leads`
table, and fires the email notification in a background task. The frontend
(`static/js/main.js`) submits via `fetch` and swaps the form for a
thank-you card on success, matching the design mock's behavior.
