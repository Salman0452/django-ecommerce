# ShopAI

**AI-powered e-commerce platform built with Django**

![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django 5.1](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-Django%20REST%20Framework-ff1709?logo=django&logoColor=white)
![Groq AI](https://img.shields.io/badge/Groq-AI-000000)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

ShopAI is a production-oriented Django e-commerce application that combines a full storefront experience (catalog, cart, checkout, orders, payments) with an AI shopping assistant powered by Groq. The platform follows a clean service-layer architecture so business logic remains testable and maintainable.

## Features

- Product catalog with categories
- Shopping cart and checkout flow
- Order management and order history
- Payment tracking and history
- AI shopping assistant powered by Groq
- Custom Django admin panel (Jazzmin)
- Responsive UI built with vanilla CSS (no CSS framework)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1, Python 3.12 |
| API | Django REST Framework |
| AI | Groq API (`llama-3.3-70b-versatile`) |
| Database | PostgreSQL (production), SQLite (development) |
| Admin | django-jazzmin |
| Testing | pytest, pytest-django |

## Project Structure

```text
e-commerce/
├── apps/
│   ├── chatbot/      # DRF chatbot API + Groq integration
│   ├── core/         # CoreModel and shared abstractions
│   ├── orders/       # Cart, checkout, order lifecycle
│   ├── payments/     # Payment records and status tracking
│   ├── products/     # Catalog, categories, product views/services
│   └── users/        # Authentication, registration, profile flows
├── config/           # Django settings and root URL configuration
├── docs/             # Architecture, conventions, and decisions
├── requirements/     # Base/dev/prod dependency sets
├── static/           # CSS, JS, and static assets
├── templates/        # Django templates by app
├── docker/           # Dockerfile and entrypoint scripts
└── manage.py
```

### App Responsibilities

| App | Responsibility |
|---|---|
| `core` | Abstract base model (`CoreModel`) and shared utilities |
| `users` | Authentication, registration, and profile management |
| `products` | Product catalog, categories, and product discovery |
| `orders` | Cart operations, checkout flow, order creation/history |
| `payments` | Payment tracking, payment statuses, payment history |
| `chatbot` | DRF endpoints, conversation session management, Groq LLM integration |

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- PostgreSQL (optional for development; SQLite works out-of-the-box)
- Git
- Groq API key

### Installation

1. Clone the repository.

```bash
git clone <your-repo-url>
cd e-commerce
```

2. Create and activate a virtual environment.

```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

3. Install development dependencies.

```bash
pip install -r requirements/development.txt
```

4. Create environment file from template.

```bash
cp .env.example .env
# On Windows CMD: copy .env.example .env
```

5. Apply migrations.

```bash
python manage.py migrate
```

6. Create an admin user.

```bash
python manage.py createsuperuser
```

7. Start development server.

```bash
python manage.py runserver
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DEBUG` | Yes | Enables debug mode in development |
| `SECRET_KEY` | Yes | Django secret key |
| `DATABASE_URL` | Recommended | Database connection URL (PostgreSQL in production) |
| `GROQ_API_KEY` | Yes (chatbot) | API key for Groq LLM requests |
| `GROQ_MODEL` | Yes (chatbot) | LLM model name (default: `llama-3.3-70b-versatile`) |

## Architecture

ShopAI uses a layered architecture:

```text
URLs -> Views -> Services -> Models
```

- URL modules define route contracts.
- Views orchestrate request/response handling only.
- Services contain business logic and external integrations.
- Models represent persistence and domain state.

### Architectural Rules

- Views contain no business logic; business rules live in `services.py`.
- Models follow the shared `CoreModel` pattern for common fields (`id`, `created_at`, `updated_at`, `is_deleted`).
- Project exception: `users.User` extends `AbstractUser` and includes compatible lifecycle fields.

## GitHub Copilot Development

This project was built using GitHub Copilot as a first-class engineering assistant across architecture, implementation, testing, and documentation.

### Copilot Features Used

1. Custom Instructions
2. Prompt Files
3. Slash Commands and Context Variables
4. Agent Mode
5. Model Selection
6. Code Review
7. Copilot CLI
8. Copilot Coding Agent

Conventions defined in `.github/copilot-instructions.md` enforce naming standards, service-layer boundaries, and app-level responsibilities. This guardrail prevented naming inconsistencies across all AI agents involved in development.

## Testing

### Run Tests

```bash
pytest
```

```bash
python manage.py test
```

### Current Test Coverage by App

Snapshot date: 2026-04-06

| App | Current Test Status | Line Coverage |
|---|---|---|
| `chatbot` | 4 passed, 0 failed | Not measured (`pytest-cov` not installed) |
| `orders` | 53 passed, 1 failed | Not measured (`pytest-cov` not installed) |
| `payments` | 39 passed, 1 failed | Not measured (`pytest-cov` not installed) |
| `products` | 8 passed, 1 failed | Not measured (`pytest-cov` not installed) |
| `users` | 23 passed, 0 failed | Not measured (`pytest-cov` not installed) |
| `core` | No test module detected | Not measured (`pytest-cov` not installed) |

Overall latest suite result: **127 passed, 3 failed**.

## API Documentation

### Chat Endpoint

- **Method**: `POST`
- **URL**: `/api/v1/chatbot/`

Request body:

```json
{
  "message": "I need a laptop under $1200"
}
```

Response body:

```json
{
  "response": "Here are some options that match your budget...",
  "sessionId": "1"
}
```

### Chat History Endpoint

- **Method**: `GET`
- **URL**: `/api/v1/chatbot/history/`

Response body:

```json
{
  "sessionId": "1",
  "messages": [
    {
      "role": "user",
      "content": "I need a laptop under $1200",
      "createdAt": "2026-04-06T09:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Here are some options that match your budget...",
      "createdAt": "2026-04-06T09:30:03Z"
    }
  ]
}
```

Notes:

- Session continuity uses Django session authentication.
- Authenticated and anonymous users are both supported.

## Contributing

1. Fork the repository.
2. Create a feature branch (`feature/your-change`).
3. Commit using conventional commit style (`feat:`, `fix:`, `docs:`, etc.).
4. Open a pull request with clear context and testing notes.

Before contributing, read `docs/conventions.md` to follow naming, architecture, and testing standards.

## License

MIT License.