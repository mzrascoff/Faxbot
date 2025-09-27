"""
Admin Users API (list/create/patch minimal)

Notes:
- No PHI; do not return password hashes.
- Uses DBUser from identity_models; creates tables if not already present when called.
- Stores disabled state in traits_json: {"is_active": false}
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import json
import os
import secrets
import hashlib

from ..main import require_admin
from ..db import SessionLocal, Base, init_db

# Ensure identity models are registered with SQLAlchemy Base
try:
    from .. import identity_models as _idm  # noqa: F401
except Exception:
    _idm = None  # type: ignore

from ..identity_models import DBUser  # type: ignore


router = APIRouter(prefix="/admin/users", tags=["Admin Users"], dependencies=[Depends(require_admin)])


class UserOut(BaseModel):
    id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


class CreateUserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: Optional[str] = None
    email: Optional[str] = None


class PatchUserIn(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


def _pepper() -> str:
    p = os.getenv("FAXBOT_SESSION_PEPPER", "")
    if not p:
        # Avoid throwing in production listing paths; enforce on create only
        return ""
    return p


def _hash_password(password: str, salt: str, rounds: int = 200_000) -> str:
    data = ( _pepper() + password ).encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", data, salt.encode("utf-8"), rounds)
    return dk.hex()


@router.get("")
def list_users() -> dict:
    # Ensure tables exist (best-effort)
    init_db()
    users: List[UserOut] = []
    try:
        with SessionLocal() as db:
            rows = db.query(DBUser).all()
            for r in rows:
                is_active = True
                try:
                    if r.traits_json:
                        tj = json.loads(r.traits_json)
                        if isinstance(tj, dict) and "is_active" in tj:
                            is_active = bool(tj.get("is_active"))
                except Exception:
                    is_active = True
                users.append(UserOut(
                    id=r.id,
                    username=r.username,
                    display_name=r.display_name,
                    email=r.email,
                    is_active=is_active,
                    created_at=r.created_at.isoformat() if getattr(r, 'created_at', None) else None,
                ))
    except Exception:
        users = []
    return {"users": [u.model_dump() for u in users]}


@router.post("")
def create_user(payload: CreateUserIn) -> UserOut:
    init_db()
    if not _pepper():
        raise HTTPException(500, detail="FAXBOT_SESSION_PEPPER missing (required to create users)")
    salt = secrets.token_hex(16)
    pwd_hex = _hash_password(payload.password, salt)
    uid = secrets.token_hex(16)
    try:
        with SessionLocal() as db:
            u = DBUser(
                id=uid,
                username=payload.username,
                display_name=payload.display_name,
                email=payload.email,
                pwd_hash=pwd_hex,
                pwd_salt=salt,
                pwd_algo="pbkdf2_sha256:200000",
                traits_json=json.dumps({"is_active": True}),
            )
            db.add(u)
            db.commit()
            return UserOut(
                id=u.id,
                username=u.username,
                display_name=u.display_name,
                email=u.email,
                is_active=True,
                created_at=u.created_at.isoformat() if getattr(u, 'created_at', None) else None,
            )
    except Exception as e:
        raise HTTPException(500, detail=f"create user failed: {e}")


@router.patch("/{user_id}")
def patch_user(user_id: str, payload: PatchUserIn) -> UserOut:
    init_db()
    with SessionLocal() as db:
        row = db.get(DBUser, user_id)
        if not row:
            raise HTTPException(404, detail="user not found")
        if payload.display_name is not None:
            row.display_name = payload.display_name
        if payload.email is not None:
            row.email = payload.email
        if payload.is_active is not None:
            try:
                tj = json.loads(row.traits_json) if row.traits_json else {}
            except Exception:
                tj = {}
            if not isinstance(tj, dict):
                tj = {}
            tj["is_active"] = bool(payload.is_active)
            row.traits_json = json.dumps(tj)
        db.add(row)
        db.commit()
        is_active = True
        try:
            if row.traits_json:
                tj = json.loads(row.traits_json)
                is_active = bool(tj.get("is_active", True))
        except Exception:
            is_active = True
        return UserOut(
            id=row.id,
            username=row.username,
            display_name=row.display_name,
            email=row.email,
            is_active=is_active,
            created_at=row.created_at.isoformat() if getattr(row, 'created_at', None) else None,
        )

