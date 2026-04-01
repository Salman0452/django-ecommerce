# Architecture

## System Overview
Django monolith. One codebase, one deployment unit.
DRF is used only for the /api/v1/chatbot/ endpoint.

## Apps and Responsibilities

| App       | Responsibility                                      |
|-----------|-----------------------------------------------------|
| core      | Abstract base model, shared utilities, mixins       |
| users     | Auth, registration, profiles, addresses             |
| products  | Catalog, categories, inventory, images              |
| orders    | Cart, order creation, order history                 |
| payments  | Payment records, status tracking                    |
| chatbot   | DRF API endpoint, LLM integration, session history  |

## Base Model (CoreModel) — Every model inherits this
```python
# apps/core/models.py
class CoreModel(models.Model):
    id         = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
```

## Database Schema

### users_user
| Field          | Type         | Notes                    |
|----------------|--------------|--------------------------|
| id             | BigInt PK    |                          |
| email          | varchar      | unique, used as username |
| first_name     | varchar      |                          |
| last_name      | varchar      |                          |
| is_active      | boolean      |                          |
| is_staff       | boolean      |                          |
| created_at     | timestamptz  | from CoreModel           |
| updated_at     | timestamptz  | from CoreModel           |
| is_deleted     | boolean      | from CoreModel           |

### products_category
| Field       | Type      | Notes        |
|-------------|-----------|--------------|
| id          | BigInt PK |              |
| name        | varchar   | unique       |
| slug        | slug      | unique       |
| is_active   | boolean   |              |
| created_at  | timestamptz |            |
| updated_at  | timestamptz |            |

### products_product
| Field        | Type        | Notes                    |
|--------------|-------------|--------------------------|
| id           | BigInt PK   |                          |
| category_id  | FK          | → products_category      |
| name         | varchar     |                          |
| slug         | slug        | unique                   |
| description  | text        |                          |
| price        | decimal     | max_digits=10, places=2  |
| stock        | integer     |                          |
| is_active    | boolean     |                          |
| created_at   | timestamptz |                          |
| updated_at   | timestamptz |                          |

### orders_cart / orders_cartitem
| Field        | Type      | Notes               |
|--------------|-----------|---------------------|
| cart.id      | BigInt PK |                     |
| cart.user_id | FK        | → users_user        |
| cartitem.cart_id   | FK  | → orders_cart       |
| cartitem.product_id| FK  | → products_product  |
| cartitem.quantity  | int |                     |

### orders_order / orders_orderitem
| Field           | Type        | Notes                    |
|-----------------|-------------|--------------------------|
| order.id        | BigInt PK   |                          |
| order.user_id   | FK          | → users_user             |
| order.status    | varchar     | pending/paid/shipped/done|
| order.total     | decimal     |                          |
| orderitem.order_id   | FK   | → orders_order           |
| orderitem.product_id | FK   | → products_product       |
| orderitem.quantity   | int  |                          |
| orderitem.unit_price | decimal | price at time of order|

### payments_payment
| Field        | Type      | Notes                        |
|--------------|-----------|------------------------------|
| id           | BigInt PK |                              |
| order_id     | FK        | → orders_order (OneToOne)    |
| amount       | decimal   |                              |
| status       | varchar   | pending/completed/failed     |
| created_at   | timestamptz |                            |

### chatbot_session / chatbot_message
| Field              | Type      | Notes               |
|--------------------|-----------|---------------------|
| session.id         | BigInt PK |                     |
| session.user_id    | FK        | nullable (guests)   |
| session.session_key| varchar   | for anonymous users |
| message.session_id | FK        | → chatbot_session   |
| message.role       | varchar   | user / assistant    |
| message.content    | text      |                     |
| message.created_at | timestamptz |                   |

## URL Structure
/                          → products:home
/products/                 → products:list
/products/<slug>/          → products:detail
/cart/                     → orders:cart
/checkout/                 → orders:checkout
/orders/                   → orders:list
/orders/<id>/              → orders:detail
/account/                  → users:profile
/account/login/            → users:login
/account/register/         → users:register
/admin/                    → Django admin
/api/v1/chatbot/           → chatbot:chat (DRF)
/api/v1/chatbot/history/   → chatbot:history (DRF)