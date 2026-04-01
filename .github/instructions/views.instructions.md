---
applyTo: "**/views.py"
---
# Rules for views.py files only

- Use class-based views (CBV) by default
- Never put business logic in views — call services.py functions only
- Always use LoginRequiredMixin for authenticated views
- Template names follow: <app>/<model>_<action>.html
- Always handle GET and POST explicitly — no implicit assumptions