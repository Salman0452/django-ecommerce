# GitHub Copilot Instructions

## Project Overview
This is a Django e-commerce platform with an AI chatbot.
Monolithic architecture: Django handles both backend and frontend (Django Templates).
The only exception is the chatbot, which is served via Django REST Framework.

## Stack
- Backend: Django 5.x, Python 3.12
- Frontend: Django Templates, vanilla JS, CSS
- Database: PostgreSQL
- API layer: Django REST Framework (chatbot only)
- Containerization: Docker + Docker Compose
- AI Chatbot: DRF endpoint consuming an LLM API

## Agent Roles — Always Respect Boundaries
- **Architect**: Defines models, DB schema, URL structure. No other agent creates
  models without architect approval.
- **Backend**: Implements views, models, serializers, business logic.
  Follows architect's schema exactly.
- **Frontend**: Works inside templates/ only. Never modifies models or views logic.
- **Designer**: Works inside static/css/ and template structure only.
  Never touches Python files.
- **QA**: Writes tests in tests/ inside each app. Never modifies source logic.
- **DevOps**: Manages docker/, requirements/, config/settings/ only.

## Non-Negotiable Rules
1. Read docs/conventions.md before writing any code.
2. Read docs/architecture.md before creating any model or URL.
3. Never invent field names — use exactly what is defined in architecture.md.
4. Never use userId, ProductID, or any camelCase in Python or database fields.
5. Every model must inherit from CoreModel (apps/core/models.py).
6. Never put business logic in views — use service functions in services.py.
7. Never put raw SQL unless explicitly asked.
8. All secrets come from environment variables via django-environ. Never hardcode.
9. Every new decision must be logged in docs/decisions.md.
10. When uncertain about a field name or relationship — stop and check architecture.md.

## Concrete Examples — Right vs Wrong

### Model fields
# WRONG
class Product(models.Model):
    productName = models.CharField()
    categoryId = models.ForeignKey()
    isActive = models.BooleanField()

# RIGHT
class Product(CoreModel):
    name = models.CharField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

### Service layer
# WRONG — business logic in view
def cart_view(request):
    cart = Cart.objects.get(user=request.user)
    cart.total = sum(item.price * item.quantity for item in cart.items.all())
    cart.save()

# RIGHT — view calls service
def cart_view(request):
    cart = get_user_cart(request.user)
    return render(request, 'orders/cart.html', {'cart': cart})

### URL naming
# WRONG
path('product-detail/<slug>/', views.detail)

# RIGHT
path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='detail')

### Template context variables
# WRONG — passing raw querysets without pagination
context = {'products': Product.objects.all()}

# RIGHT
context = {'products': get_active_products(page=request.GET.get('page', 1))}