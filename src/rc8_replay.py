"""SQLite transactional replay register for synthetic test identities only.

This module does not authenticate users. The caller must supply a separately
verified principal. SQLite state survives process restart on the same volume,
but it is not a distributed multi-writer authorization service.
"""
import re
import sqlite3
from pathlib import Path
from rc6_security import VerifiedPrincipal

_ALLOWED = {"triage": "analyst", "review": "reviewer", "approve_draft": "release_officer"}
_SAFE = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
_NONCE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
_SCHEMA = """CREATE TABLE IF NOT EXISTS used_nonces (
 issuer TEXT NOT NULL,
 subject TEXT NOT NULL,
 case_id TEXT NOT NULL,
 nonce TEXT NOT NULL,
 action TEXT NOT NULL,
 expires_at INTEGER NOT NULL,
 PRIMARY KEY(issuer, subject, nonce)
) WITHOUT ROWID"""

def consume(db_path, principal, *, action, case_id, nonce, now):
    if not isinstance(principal, VerifiedPrincipal):
        raise PermissionError("trusted verified principal required")
    if action not in _ALLOWED or principal.role != _ALLOWED[action]:
        raise PermissionError("action role denied")
    if principal.issuer != "synthetic-rc6-idp":
        raise PermissionError("untrusted test issuer")
    if type(now) is not int or type(principal.expires_at) is not int or now >= principal.expires_at:
        raise PermissionError("assertion expired")
    if not isinstance(case_id, str) or not _SAFE.fullmatch(case_id):
        raise ValueError("case id malformed")
    if not isinstance(nonce, str) or not _NONCE.fullmatch(nonce):
        raise ValueError("nonce malformed")
    db_path = Path(db_path)
    if not db_path.parent.is_dir():
        raise ValueError("database parent missing")
    # Isolation against concurrent consumers sharing a single local SQLite file.
    with sqlite3.connect(db_path, timeout=5, isolation_level=None) as conn:
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute(_SCHEMA)
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute(
                "INSERT INTO used_nonces VALUES (?,?,?,?,?,?)",
                (principal.issuer,principal.subject,case_id,nonce,action,principal.expires_at)
            )
            conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            conn.execute("ROLLBACK")
            raise PermissionError("replayed nonce") from exc
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    return {"result": "SYNTHETIC_NONCE_CONSUMED", "action": action, "case_id": case_id}

def count(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT count(*) FROM used_nonces").fetchone()[0]
