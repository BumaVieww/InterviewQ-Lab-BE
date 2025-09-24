import jwt
from clerk_backend_api import Clerk
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from sqlalchemy.orm import Session
from core.database import get_db
from app.domain.user.model.user import User
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

if not CLERK_SECRET_KEY:
    raise ValueError("CLERK_SECRET_KEY environment variable is required")

clerk = Clerk(bearer_auth=CLERK_SECRET_KEY)

app_id = os.getenv("APP_ID")
CLERK_ISSUER = f"https://{app_id}.clerk.accounts.dev"
JWKS_URL = f"{CLERK_ISSUER}/.well-known/jwks.json"
_jwks = PyJWKClient(JWKS_URL)

def decode_clerk_token(token: str) -> dict:
    signing_key = _jwks.get_signing_key_from_jwt(token).key
    return jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        issuer=CLERK_ISSUER,
        options={"verify_aud": False},
    )


async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    print(token)
    try:
        # 1) 로컬에서 토큰 검증
        claims = decode_clerk_token(token)

        # 2) user_id(sub)로 Clerk API에서 유저 조회
        user_info = clerk.users.get(user_id=claims["sub"])
        return user_info

    except Exception as e:
        print(str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )


async def get_current_user(
    clerk_user = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Clerk에서 검증된 사용자 정보로 데이터베이스의 사용자를 조회하거나 생성합니다.
    """
    primary_email = None
    if clerk_user.email_addresses:
        primary_email = next((email.email_address for email in clerk_user.email_addresses if email.id == clerk_user.primary_email_address_id), None)

    if not primary_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No email address found for user"
        )

    # email로 사용자 조회
    user = db.query(User).filter(User.email == primary_email).first()

    if not user:
        # 사용자가 없으면 새로 생성
        user = User(
            email=primary_email,
            nickname=clerk_user.first_name or primary_email.split("@")[0],  # 기본 닉네임
            role="user",  # 기본 역할
            is_onboarding=True  # 온보딩 필요
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    선택적 인증 - 토큰이 있으면 사용자를 반환하고, 없으면 None을 반환합니다.
    """
    if not credentials:
        return None

    try:
        clerk_user = await verify_clerk_token(credentials)
        return await get_current_user(clerk_user, db)
    except HTTPException:
        return None