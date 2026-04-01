# Conventions

## Python & Django
- Style: PEP8, enforced by black + flake8
- All names: snake_case
- Models: PascalCase singular → User, Product, Order, OrderItem
- Model fields: snake_case → user_id, product_name, created_at, is_active
- Foreign keys: <model_name>_id → user_id, product_id, order_id
- App names: lowercase plural → users, products, orders, payments
- Service functions: verb_noun → get_user_cart, create_order, process_payment
- URL names: app_namespace:action → users:login, products:detail, orders:checkout

## Database
- All columns: snake_case
- Primary keys: id (auto, BigAutoField)
- Foreign keys: <model>_id → user_id, product_id
- Boolean fields: is_<state> or has_<thing> → is_active, is_staff, has_paid
- Timestamps: created_at, updated_at (on every table via CoreModel)
- Soft delete field: is_deleted (on every table via CoreModel)

## JavaScript (templates)
- Variables: camelCase → userId, productId, cartTotal
- Data attributes: kebab-case → data-product-id, data-user-id
- JS files: snake_case → cart_manager.js, product_filter.js

## API (DRF — chatbot only)
- JSON responses: camelCase → userId, sessionId, botResponse
- URL pattern: /api/v1/<resource>/
- Endpoints are versioned from day one

## Templates
- Template names: snake_case → product_detail.html, order_summary.html
- Template folders mirror app names → templates/products/product_detail.html
- Component templates: templates/components/<name>.html

## CSS Classes
- BEM methodology → .product-card, .product-card__title, .product-card--featured
- Utility prefix: u- → u-hidden, u-text-center
- JS hooks prefix: js- → js-add-to-cart (never style these classes)

## Testing
- Test files: tests/test_<module>.py → tests/test_models.py, tests/test_views.py
- Test classes: Test<ModelOrView> → TestProductModel, TestCartView
- Test methods: test_<scenario> → test_user_can_add_to_cart

## Git
- Branches: <type>/<description> → feature/product-catalog, fix/cart-quantity-bug
- Commits: conventional commits → feat:, fix:, docs:, test:, refactor: