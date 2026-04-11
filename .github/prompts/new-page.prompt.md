---
mode: agent
description: "Scaffold a new authenticated page: view + URL + template following BOA conventions"
---

Create a new page called **${input:pageName}** with title **${input:pageTitle}** and URL path **${input:urlPath}**.

Follow these steps in order:

1. **Add the view** to `boaapp/views.py`:
   - Function-based view
   - Add `@login_required` decorator if ${input:requiresLogin:true}
   - Use `return render(request, 'boaapp/${input:templateName}.html')`

2. **Add the URL** to `boa/urls.py`:
   - Pattern: `path('${input:urlPath}/', boaapp_views.${input:viewName}, name='${input:urlName}')`

3. **Create the template** at `boaapp/templates/boaapp/${input:templateName}.html`:
   - Extend `boaapp/base_generic.html`
   - Include `{% load static %}`
   - Add `{% block title %}thenumerix | ${input:pageTitle}{% endblock %}`
   - Put ALL page CSS inside `{% block content %}` as a `<style>` block (never in index.css)
   - Use the `pt-hero` hero pattern with a `pt-tag` label chip
   - Use `pt-card` / `pt-stack` layout for content
   - Reference CSS variables: `--c-blue`, `--c-card`, `--c-border`, `--c-muted`, `--c-shadow`, `--c-shadow-lg`, `--c-radius`, `--c-text`
   - Pair every light-mode rule with a `[data-theme="dark"]` rule

4. **Add sidebar nav item** (if this is a main section) in `base_generic.html`:
   - `<a href="{% url '${input:urlName}' %}" class="sidebar-link">` in the correct group

5. Run `python manage.py check` and confirm 0 issues.
