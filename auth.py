import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from database import get_db
import models
import jwt as pyjwt
import bcrypt

logger = logging.getLogger("kanbanflow.auth")

SECRET_KEY  = os.environ.get("SECRET_KEY", "kanbanflow-secret-key-2024-change-in-prod")
ALGORITHM   = "HS256"
COOKIE_NAME = "kf_session"
TOKEN_EXPIRE_DAYS = 7

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception as e:
        logger.error(f"verify_password error: {e}")
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=TOKEN_EXPIRE_DAYS))
    payload["exp"] = int(expire.timestamp())   # integer Unix ts — works with any JWT lib
    return pyjwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def _decode_token(token: str) -> Optional[dict]:
    """Try HS256 first; also accept RS256 / no-alg tokens from older lib versions."""
    for alg in ("HS256", "HS384", "HS512"):
        try:
            return pyjwt.decode(
                token, SECRET_KEY,
                algorithms=[alg],
                options={"verify_exp": True},
            )
        except pyjwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except pyjwt.InvalidAlgorithmError:
            continue
        except pyjwt.InvalidTokenError:
            continue
    logger.warning("Token invalid with all attempted algorithms")
    return None

def get_token_from_request(request: Request) -> Optional[str]:
    """Cookie → X-Token header → Authorization header."""
    t = request.cookies.get(COOKIE_NAME)
    if t:
        return t
    t = request.headers.get("x-token", "")
    if t:
        return t
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None

def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    exc = HTTPException(status_code=401, detail="Could not validate credentials")

    token = get_token_from_request(request)
    if not token:
        logger.warning("No token found in any source")
        raise exc

    payload = _decode_token(token)
    if payload is None:
        raise exc

    user_id: str = payload.get("sub")
    if not user_id:
        logger.warning("JWT has no sub claim")
        raise exc

    user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise exc
    if not user.is_active:
        raise exc

    return user

def require_role(*roles):
    def checker(user: models.User = Depends(get_current_user)):
        if user.global_role not in roles:
            raise HTTPException(403, detail=f"Required: {roles}")
        return user
    return checker
