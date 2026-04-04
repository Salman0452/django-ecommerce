# Architecture Decision Records (ADR)

## ADR-001 — Django monolith with DRF only for chatbot
**Date**: 2026-04-01
**Decision**: Use Django Templates for all frontend. DRF only for chatbot API.
**Reason**: Simplicity, single deployment, no CORS complexity.
**Trade-off**: Less interactive UI. Acceptable for this project scope.

## ADR-002 — PostgreSQL as primary database
**Date**: 2026-04-01
**Decision**: PostgreSQL from day one, including development.
**Reason**: Avoid SQLite-to-Postgres migration bugs. Consistency across environments.

## ADR-003 — CoreModel as base for all models
**Date**: 2026-04-01
**Decision**: All models inherit CoreModel with id, created_at, updated_at, is_deleted.
**Reason**: Consistency, soft delete support, audit trail.

## ADR-004 — snake_case for all DB fields, Python code
**Date**: 2026-04-01
**Decision**: snake_case everywhere in Python and DB. camelCase only in JS and DRF JSON.
**Reason**: Prevents naming conflicts between agents.

## ADR-005 — Products app uses service-backed CBVs
**Date**: 2026-04-04
**Decision**: Implement product listing and detail pages using class-based views that delegate data access to `apps.products.services`.
**Reason**: Keeps business/query logic out of views and follows project service-layer conventions.

## ADR-005 — Stock field index deferred
**Date**: 2026-04-04
**Decision**: No index on products_product.stock for now.
**Reason**: No query patterns established yet. Add when inventory 
filtering queries are identified and data volume justifies it.