from jose import jwt, JWTError
from jose import jwt
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "1f1e92bade502438c1789b443955912dfbc19a1cfde28fdf4612acf13a194f87"
ALGORITHM = "HS256"


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        first_name: str = payload.get("first_name")
        last_name: str = payload.get("last_name")
        is_admin: bool = payload.get("is_admin")
        expire = payload.get("exp")
        if first_name is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token expired!"
            )

        return {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": is_admin,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )
