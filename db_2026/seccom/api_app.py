import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Header, status, Request
from loguru import logger
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from db_2026.seccom.pool import create_db_pool
# Import your models and service (adjust import paths as needed)
from model import Message, Group, GroupUser, Invite, User
from service import SeccomService




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the async connection pool
    app.state.pool = await create_db_pool()
    yield
    # Shutdown: Close the pool (if applicable)
    if hasattr(app.state.pool, "close"):
        await app.state.pool.close()


app = FastAPI(title="Seccom API", lifespan=lifespan)

# Add CORS Middleware to allow your Next.js frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # The URL of your Next.js app
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],  # Allows all headers (like your custom 'token' header)
)

# --- Dependencies ---

def get_service(request: Request) -> SeccomService:
    return SeccomService(request.app.state.pool)


async def get_current_user(
    token: str = Header(..., description="User identification token"),
    service: SeccomService = Depends(get_service)
) -> User:
    user = await service.user_by_token(token)
    logger.info(f"User {user} performing request")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# --- Pydantic Schemas ---

class SignupInitRequest(BaseModel):
    pub_key: str
    invite_id: UUID

class SignupFinishRequest(BaseModel):
    pub_key: str
    invite_id: UUID
    solution: str

class LoginRequest(BaseModel):
    pub_key: str

class LoginFinishRequest(BaseModel):
    pub_key: str
    solution: str

class PostMessageRequest(BaseModel):
    content: str


# --- Public / Auth Endpoints (No Token Required) ---

@app.post("/auth/signup/init", response_model=str)
async def signup_init(req: SignupInitRequest, service: SeccomService = Depends(get_service)):
    try:
        return await service.signup_init(req.pub_key, req.invite_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signup/finish", status_code=status.HTTP_201_CREATED)
async def signup_finish(req: SignupFinishRequest, service: SeccomService = Depends(get_service)):
    try:
        await service.signup_finish(req.pub_key, req.invite_id, req.solution)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login/init", response_model=str)
async def login_init(req: LoginRequest, service: SeccomService = Depends(get_service)):
    try:
        return await service.login_user(req.pub_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login/finish", response_model=str)
async def login_finish(req: LoginFinishRequest, service: SeccomService = Depends(get_service)):
    try:
        return await service.login_finish(req.pub_key, req.solution)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Protected Endpoints (Token Required) ---

@app.post("/auth/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    try:
        await service.logout_user(current_user.pub_key)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/groups/{group_id}/messages")
async def post_message(
    group_id: UUID,
    req: PostMessageRequest,
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    await service.post_message(group_id, current_user.pub_key, req.content)
    return {"status": "success"}

@app.get("/groups/{group_id}/messages", response_model=list[Message])
async def fetch_messages(
    group_id: UUID,
    since: datetime | None = None,
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    return await service.fetch_messages(group_id, current_user.pub_key, since)

@app.get("/users/me/groups", response_model=list[UUID])
async def fetch_groups(
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    return await service.fetch_groups(current_user.pub_key)

@app.post("/groups/{group_id}/join")
async def join_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    await service.join_group(current_user.pub_key, group_id)
    return {"status": "success"}

@app.post("/groups/{group_id}/leave")
async def leave_group(
    group_id: UUID,
    current_user: User = Depends(get_current_user),
    service: SeccomService = Depends(get_service)
):
    await service.leave_group(current_user.pub_key, group_id)
    return {"status": "success"}


# --- Admin Endpoints (Admin Token Required) ---

@app.post("/admin/groups")
async def create_group(
    name: str,
    admin_user: User = Depends(get_admin_user),
    service: SeccomService = Depends(get_service)
):
    await service.create_group(name)
    return {"status": "success"}

@app.post("/admin/invites", response_model=Invite)
async def create_invite(
    admin_user: User = Depends(get_admin_user),
    service: SeccomService = Depends(get_service)
):
    return await service.create_invite()

@app.post("/admin/users/{pub_key}/elevate")
async def elevate_user_admin(
    pub_key: str,
    admin_user: User = Depends(get_admin_user),
    service: SeccomService = Depends(get_service)
):
    try:
        await service.elevate_user_admin(pub_key)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # Runs the application on http://127.0.0.1:8000
    uvicorn.run("db_2026.seccom.api_app:app", host="127.0.0.1", port=8001, reload=True)