---
agent: 'agent'
description: 'Create tests for a Django model, view, or service'
---

Create tests for the code I describe.

Rules to follow:
- #file:../../docs/conventions.md

Requirements:
1. Use Django's TestCase for model/view tests
2. Use APITestCase for DRF endpoint tests
3. File location: apps/<app_name>/tests/test_<module>.py
4. Class name: Test<WhatYouAreTesting>
5. Method names: test_<scenario_in_plain_english>
6. Always create test fixtures inline — no external fixture files
7. Test both happy path and failure cases
8. For views: test authenticated and unauthenticated access separately

What to test: [DESCRIBE WHAT YOU WANT TESTED HERE]