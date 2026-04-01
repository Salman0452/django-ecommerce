---
agent: 'agent'
description: 'Create a Django model following project conventions'
---

Create a Django model based on the description I provide.

Rules to follow — read these first:
- #file:../../docs/conventions.md
- #file:../../docs/architecture.md

Requirements:
1. Model must inherit from CoreModel (apps/core/models.py)
2. Never define id, created_at, updated_at — CoreModel provides them
3. All field names: snake_case
4. ForeignKey: use string reference format 'app.Model', on_delete=models.PROTECT
5. Always add __str__ returning the most human-readable field
6. Always add class Meta with ordering = ['-created_at'] and verbose_name
7. Add indexes for slug, is_active, and any FK fields
8. Place the file in apps/<app_name>/models.py

After creating the model, also create:
- The migration: remind me to run makemigrations
- apps/<app_name>/admin.py registration with list_display

Model to create: [DESCRIBE YOUR MODEL HERE]