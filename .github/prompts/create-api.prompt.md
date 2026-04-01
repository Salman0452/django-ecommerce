---
agent: 'agent'
description: 'Create a DRF API endpoint (chatbot only)'
---

Create a Django REST Framework endpoint.

Rules to follow — read these first:
- #file:../../docs/conventions.md
- #file:../../docs/architecture.md

Requirements:
1. This is for the chatbot app only — /api/v1/chatbot/
2. All serializer fields use camelCase in JSON output (use source= parameter)
3. Always use explicit serializers — never return raw model data
4. Authentication: SessionAuthentication + allow anonymous via session_key
5. Version the URL: /api/v1/
6. Add the URL to config/urls.py under api/v1/ prefix

Endpoint to create: [DESCRIBE YOUR ENDPOINT HERE]