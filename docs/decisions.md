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

## ADR-006 — Payments app: Payment model, service layer, and views
**Date**: 2026-04-04
**Decision**: Implement the payments app with a `Payment` model (OneToOne → Order, amount, status: pending/completed/failed), a service layer (`create_payment`, `get_payment_by_order`, `update_payment_status`, `get_user_payments`, `get_payment_by_id`), and three CBVs (`PaymentHistoryView`, `PaymentDetailView`, `PaymentConfirmView`) routed under `/payments/`.
**Reason**: Separates payment tracking from order management, allows independent status transitions, and follows the existing service-backed CBV pattern.
**Trade-off**: Payment processing is simulated (no real payment gateway). A real gateway integration would replace `update_payment_status` in the confirm view.

## ADR-007 — Products URL include moved to last in ROOT_URLCONF
**Date**: 2026-04-04
**Decision**: Move `path('', include('apps.products.urls'))` to the end of `urlpatterns` in `config/urls.py`.
**Reason**: The products app uses an empty prefix (`''`) with a `<slug:slug>/` wildcard pattern. When registered first it shadowed `/payments/`, `/orders/`, and `/account/` routes — Django's URL resolver matched 'payments', 'orders', and 'account' as slugs before the dedicated includes could be tried. Registering the products include last ensures fixed-prefix apps are resolved first.
