from fastapi import FastAPI
from src.routes.auth import auth_router
from src.routes.user import user_router
from middleware import corsPolicy


version = "v1"
app = FastAPI(
    title= "login",
    description="A simple login page",
    version=version
)

corsPolicy(app)



limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, prefix=f"/api/{version}/auth")
app.include_router(user_router, prefix=f"/api/{version}/user")

