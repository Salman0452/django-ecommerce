---
agent: 'agent'
description: 'Create a Django CBV view with template following project conventions'
---

Create a Django class-based view and its template.

Rules to follow — read these first:
- #file:../../docs/conventions.md
- #file:../../docs/architecture.md

Requirements:
1. Use class-based views (CBV) only
2. Never put business logic in views — create a services.py function and call it
3. Authenticated views must use LoginRequiredMixin
4. Template path: templates/<app>/<model>_<action>.html
5. URL name: <app>:<action> format
6. View must handle only one responsibility — no fat views
7. Always add the URL to apps/<app_name>/urls.py
8. Template must extend base.html

View to create: [DESCRIBE YOUR VIEW HERE]