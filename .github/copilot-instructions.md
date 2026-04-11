# thenumerix / BOA — Copilot Instructions

## Stack at a Glance

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.1 (ASGI via Daphne) |
| Database | PostgreSQL (psycopg2-binary) |
| Task queue | Celery + Redis |
| WebSockets | Django Channels + channels-redis |
| CSS framework | Bootstrap 5.3.2 |
| Icons | Font Awesome 6.5.0 |
| Font | Inter (Google Fonts) |
| Deployment | Render (render.yaml) — push to `main` triggers auto-deploy |
| Auth | Django built-in + `@login_required` |

## Project Layout

```
boa/               # Django project root (settings, urls, wsgi, asgi, celery)
boaapp/            # Single app: models, views, tasks, consumers, templates
  templates/boaapp/ # All HTML templates
  static/          # CSS and JS source files
staticfiles/       # Collected statics (never edit manually)
```

## Template Conventions

- All templates extend `boaapp/base_generic.html`.
- **CSS belongs inside `{% block content %}`** as a `<style>` block — this ensures styles survive panel innerHTML injection and dark-mode resets. Do NOT add page CSS to `static/css/index.css` unless it's truly site-wide.
- Dark mode uses `[data-theme="dark"]` on `<html>`. Always pair light and dark rules.
- CSS variables: `--c-blue`, `--c-violet`, `--c-emerald`, `--c-amber`, `--c-card`, `--c-border`, `--c-muted`, `--c-shadow`, `--c-shadow-lg`, `--c-radius`, `--c-text`.
- Reference images with `{% static 'css/img/<filename>' %}` — all logos live in `boaapp/static/css/img/`.
- Use `{% url 'name' %}` for all internal links, never hardcode paths.

## UI Design Patterns — Use These Consistently

### Cards
```html
<div class="pt-card"> <!-- rounded-24, shadow, hover lift -->
  <div class="pt-card-head"> ... </div>
  <div class="pt-content"> ... </div>
</div>
```

### Accordion (Bootstrap collapse)
```html
<div class="pt-accordion" id="<groupId>">
  <div class="pt-acc-item">
    <button class="pt-acc-header" type="button"
            data-bs-toggle="collapse" data-bs-target="#<collapseId>"
            aria-expanded="false" aria-controls="<collapseId>">
      <span>🔧</span> Title
      <i class="fas fa-chevron-down pt-acc-chevron"></i>
    </button>
    <div id="<collapseId>" class="collapse" data-bs-parent="#<groupId>">
      <div class="pt-acc-body">
        <p>Content here.</p>
      </div>
    </div>
  </div>
</div>
```

### Badges / Chips
```html
<span class="pt-badge">Default blue</span>
<span class="pt-badge pt-badge--amber">Amber</span>
<span class="pt-badge pt-badge--green">Green</span>
<span class="pt-badge pt-badge--violet">Violet</span>
<span class="pt-badge pt-badge--rose">Rose</span>
```

### Hero Section
```html
<div class="pt-hero">
  <div class="pt-tag"><i class="fas fa-icon me-1"></i> Label</div>
  <h1>Page Title</h1>
  <p class="lead">Subtitle text. Max ~560px.</p>
</div>
```

## Key Named URLs

| Name | Template | Notes |
|------|----------|-------|
| `home` | `home.html` | Dashboard — requires login |
| `portfolio_showcase` | `portfolio_showcase.html` | Company tab cards + detail panels |
| `education_details` | `education.html` | 4 institution cards |
| `process_flows` | `process_flows.html` | AI demo page |
| `uploadit` | `uploadit.html` | File upload |
| `dashboard` | (part of uploadit flow) | Login required |
| `course_list` | courses list | Requires login |
| `analytics` | analytics page | Requires login |
| `code_playground` | playground | Requires login |
| `etl_pipeline` | demo page | |
| `mlops_lifecycle` | demo page | |
| `streaming_architecture` | demo page | |
| `api_orchestration` | demo page | |
| `idp_demo` | document processing demo | |
| `login` / `logout` / `register` | auth pages | |

## Views — Rules

- All views are **function-based** in `boaapp/views.py`.
- Use `@login_required` for anything inside the authenticated dashboard.
- For new pages, add view → url → template in that order.
- Views that only render a template need no context: `return render(request, 'boaapp/page.html')`.

## Models to Know

| Model | Purpose |
|-------|---------|
| `AudioFile` | Processed notebook audio |
| `Document` | Uploaded Jupyter notebook |
| `Course`, `CourseSection`, `Enrollment` | LMS |
| `PortfolioItem`, `DevopsItem` | Portfolio showcase |
| `ChatConversation`, `ChatMessage` | RAG chatbot |
| `ResumeDocument`, `ScrollingImage` | Legacy — largely unused |

## Celery Tasks (`boaapp/tasks.py`)

- `create_audio_files_task(document_pk, user_pk)` — triggered after notebook upload.
- Always use `apply_async` — never call tasks synchronously in production views.

## Sidebar Navigation (base_generic.html)

Sidebar groups: **Profile** (Portfolio, Education) → **Demos** (AI Process Flows, UploadIt!, ETL, MLOps, CI/CD, Streaming, API Orchestration, Document Processing) → **Tools** (Courses, Analytics, Playground).

To add a nav item: add a `<a href="{% url 'name' %}" class="sidebar-link">` in the appropriate group in `base_generic.html`.

## Dark Mode

- Toggle via `#theme-toggle-btn` button in sidebar footer.
- State stored in `localStorage` key `"theme"`.
- Applied as `data-theme="dark"` on `<html>` by `static/js/index.js`.
- Always test new CSS rules against both `data-theme="light"` (default) and `[data-theme="dark"]`.

## Working with Static Files

- Dev: `python manage.py runserver` — whitenoise serves statics.
- After editing `index.css` or `index.js`: run `python manage.py collectstatic --no-input` before commit.
- Logo images referenced as: `{% static 'css/img/<name>.png' %}`

## Deployment Notes

- **Push to `main` → Render auto-deploys** — no manual steps.
- `render.yaml` configures the web service, Redis, and PostgreSQL.
- `start.sh` runs migrations + `daphne boa.asgi:application`.
- Environment variables set in Render dashboard (never commit secrets).
- `DJANGO_DEBUG=False` in production — whitenoise handles static serving.

## Coding Standards

- HTML: 2-space indent. Inline styles only for one-off overrides (`style="width:80px"`).
- Python: PEP 8. Use f-strings. No unused imports.
- Never hardcode URLs — always `{% url 'name' %}` in templates.
- Never use `!important` in CSS unless absolutely necessary.
- When adding a new company logo: place PNG in `boaapp/static/css/img/`, reference via `{% static %}`.
- Prefer editing existing files over creating new ones.
- `django check` must pass with 0 issues before committing.
