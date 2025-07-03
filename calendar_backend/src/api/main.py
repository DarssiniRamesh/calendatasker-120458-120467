from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .auth import router as auth_router, clerk_jwt_required
from .notifications import router as notifications_router
from .gmail import router as gmail_router
from .schedulers import router as schedulers_router

from fastapi import Depends

from .events import router as events_router
from .tasks import router as tasks_router
from .reminders import router as reminders_router

app = FastAPI()

# Validate Clerk.dev env at startup
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"message": "Healthy"}

# Register API routers (auth public, others protected)
app.include_router(auth_router)  # /auth endpoints: login/logout/register info, /me (JWT protected in route)

# Secure all other routers with Clerk JWT dependency.
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
