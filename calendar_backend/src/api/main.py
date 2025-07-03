from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .notifications import router as notifications_router
from .gmail import router as gmail_router
from .schedulers import router as schedulers_router

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

# Register API routers
app.include_router(auth_router)
# Placeholder event/tasks endpoints - to be implemented in their own routers in future steps
app.include_router(notifications_router)
app.include_router(gmail_router)
app.include_router(schedulers_router)
