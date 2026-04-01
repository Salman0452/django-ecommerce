---
applyTo: "**/models.py"
---
# Rules for models.py files only

- Every model MUST inherit from CoreModel
- Never define id, created_at, updated_at manually — CoreModel provides them
- Always define __str__ method
- Always define class Meta with ordering and verbose_name
- Use PROTECT for ForeignKey on_delete unless explicitly told otherwise
- Never import from other apps directly — use string references for FK if needed