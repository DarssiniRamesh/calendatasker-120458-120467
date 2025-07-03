from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
import os

from .auth import router as auth_router, clerk_jwt_required
from .notifications import router as notifications_router
from .gmail import router as gmail_router
from .schedulers import router as schedulers_router
from .email_integrations import router as email_router
from .events import router as events_router
from .tasks import router as tasks_router
from .reminders import router as reminders_router

# -- OpenAPI Tag Metadata for docs UI organization --
openapi_tags = [
    {
        "name": "auth",
        "description": "Endpoints for authentication (Clerk.dev integration, login info, JWT validation, user info)",
    },
    {
        "name": "email",
        "description": "Email integrations: Outgoing reminders (via Resend) and Gmail OAuth connection/disconnect/help.",
    },
    {
        "name": "gmail",
        "description": "Legacy/stub Gmail API endpoints (see /email for real OAuth/gmail integration; may be deprecated).",
    },
    {
        "name": "schedulers",
        "description": "Endpoints for background job status and periodic tasks (reminders, Gmail sync).",
    },
    {
        "name": "events",
        "description": "CRUD endpoints for calendar events (protected, user-scoped)",
    },
    {
        "name": "tasks",
        "description": "CRUD endpoints for tasks/to-dos (protected, user-scoped)",
    },
    {
        "name": "reminders",
        "description": "Endpoints for reminders/notifications (protected, demo & stub).",
    },
]

description = """
## CalendarTasker Backend API

This API powers the CalendarTasker application.

**Features:**
- Robust authentication (JWT/Clerk.dev)
- Secure CRUD for events and tasks
- Email reminders (send via Resend)
- Integrate your Gmail account (OAuth)
- Background scheduling (reminders, Gmail sync)
- OpenAPI and Swagger documentation

**API Security:**  
All endpoints **except `/auth/*`** require Clerk.dev JWT in the `Authorization: Bearer ...` header.

**Frontend Integration:**  
CORS settings are permissive in development (see source); adjust in production.

**See [README](../../README.md) for credential setup instructions.**
"""

app = FastAPI(
    title="CalendarTasker Backend API",
    version="1.0.0",
    description=description,
    openapi_tags=openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Validate Clerk.dev config at startup
def validate_clerk_env():
    missing_keys = []
    for key in ["CLERK_PEM_PUBLIC_KEY", "CLERK_JWT_ISSUER", "CLERK_AUDIENCE"]:
        value = os.getenv(key, "")
        if not value or not value.strip():
            missing_keys.append(key)
    if missing_keys:
        raise RuntimeError(
            f"Missing Clerk.dev config vars: {', '.join(missing_keys)}. Please fill in your .env file."
        )

validate_clerk_env()

# -- CORS: allow frontend dev URLs and prod (see .env for allowed origins) --
origins = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
if not any(o.strip() for o in origins):
    # Default for development: allow all
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # May be useful for file downloads
)

@app.get("/", tags=["meta"], summary="Health check endpoint")
def health_check():
    """Simple health check endpoint."""
    return {"message": "Healthy - CalendarTasker API up!"}

@app.get("/docs/openapi", include_in_schema=False)
def get_openapi_schema():
    """
    Returns the OpenAPI schema with docs on authentication and CORS requirements.
    Useful for frontend integration tooling, codegen, or IDE plugins.
    """
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=openapi_tags,
    )
    # Augment with custom security info
    schema["info"]["x-authentication"] = {
        "method": "Clerk.dev JWT Bearer Token",
        "description": "Provide `Authorization: Bearer <JWT>` header on all user routes. See /auth/me for user info or /auth/login for info.",
        "login_url": "/auth/login",
        "how_to_get_jwt": "Login via frontend (Clerk.dev), or see Clerk.dev docs."
    }
    schema["info"]["x-cors"] = {
        "allow_origins": origins,
        "note": "Default is '*' for development, but set CORS_ALLOW_ORIGINS in env for production."
    }
    return JSONResponse(schema)

@app.get("/openapi.json", include_in_schema=False)
def openapi_json_redirect():
    """Redirect /openapi.json to /docs/openapi for enhanced doc features."""
    return RedirectResponse(url="/docs/openapi")

# -- Register Routers --
app.include_router(auth_router)  # /auth endpoints (login/logout/register info, /me)
app.include_router(
    notifications_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    gmail_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    schedulers_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    email_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    events_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    tasks_router,
    dependencies=[Depends(clerk_jwt_required)]
)
app.include_router(
    reminders_router,
    dependencies=[Depends(clerk_jwt_required)]
)

# -- Optional: Self-test endpoint --
@app.get("/self-test", tags=["meta"], summary="Backend self-test for CI and service readiness")
async def self_test():
    """
    Quick backend self-test for CI/deployment: Validates config & core routes.
    """
    try:
        validate_clerk_env()
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}
    return {"status": "ok", "auth": True, "routes": [r.path for r in app.routes if r.include_in_schema]}
