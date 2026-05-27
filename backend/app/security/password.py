"""Password hashing and verification using bcrypt directly.

passlib[bcrypt] is listed in the spec but is incompatible with bcrypt 5.x,
which is already installed.  We use the bcrypt library's native API instead,
which provides identical security and the same cost factor.
"""
import bcrypt


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches the stored *hashed* password."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
