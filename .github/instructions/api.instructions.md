---
applyTo: "**/api/**"
---
# Rules for DRF API files (chatbot only)

- All responses use camelCase field names
- Always version endpoints: /api/v1/
- Always use serializers — never return raw model data
- Authentication: SessionAuthentication for logged-in users, allow anonymous with session_key