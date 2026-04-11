---
mode: agent
description: "Create a new Django model with migration, admin registration, and optional view wiring"
---

Create a new Django model called **${input:modelName}** in `boaapp/models.py`.

Fields: ${input:fields}

Steps:
1. **Add the model** to `boaapp/models.py` with:
   - `__str__` method returning a meaningful string
   - `class Meta` with `ordering` and `verbose_name_plural` if appropriate
   - No unused imports

2. **Register in admin** (`boaapp/admin.py`):
   - `@admin.register(${input:modelName})` decorator
   - `list_display` showing the most useful fields

3. **Create migration**: run `python manage.py makemigrations` and confirm it's clean.

4. **Wire to a view** (if ${input:needsView:false}):
   - Add a function-based view in `boaapp/views.py`
   - Add URL in `boa/urls.py`

Run `python manage.py check` before finishing.
