from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router, clerk_jwt_required
from .notifications import router as notifications_router
from .gmail import router as gmail_router
from .schedulers import router as schedulers_router

from fastapi import Depends

app = FastAPI()

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
