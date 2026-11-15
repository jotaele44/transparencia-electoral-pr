"""Offline synthetic identity and public-safe case security gates. NOT a production IdP."""
from __future__ import annotations
import hashlib, hmac, json, re
from dataclasses import dataclass
from datetime import datetime, timezone

AUDIENCE = "transparencia-electoral-pr-rc6-offline"
ROLES = frozenset({"analyst", "reviewer", "release_officer"})
PUBLIC_FIELDS = frozenset({"case_id", "domain", "status", "source_count", "review_state", "synthetic", "classification"})
DOMAINS = frozenset({"ELECTORAL_ADMINISTRATION", "RESULT_DISCREPANCY", "EQUIPMENT_PROCUREMENT", "CAMPAIGN_FINANCE", "BOUNDARY_CHANGE", "OTHER"})
STATUSES = frozenset({"DETECTED", "TRIAGED", "EVIDENCE_VERIFIED", "HUMAN_REVIEWED", "REFERRAL_READY", "WITHDRAWN"})
CASE_ID = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

@dataclass(frozen=True)
class VerifiedPrincipal:
    subject: str
    role: str
    issuer: str
    expires_at: int

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False).encode("utf-8")

def synthetic_token(claims, secret):
    """Creates only a test fixture token; never deploy as an authentication endpoint."""
    if not isinstance(secret, bytes) or len(secret)<32: raise ValueError("insecure test key")
    data=canonical(claims)
    return {"claims":claims,"mac":hmac.new(secret,data,hashlib.sha256).hexdigest()}

def verify_token(token, secret, *, now, expected_issuer="synthetic-rc6-idp"):
    if not isinstance(secret,bytes) or len(secret)<32: raise ValueError("insecure test key")
    if not isinstance(token,dict) or set(token)!={"claims","mac"}: raise PermissionError("invalid signed fixture")
    claims=token["claims"]
    if not isinstance(claims,dict) or set(claims)!={"sub","role","iss","aud","exp","iat"}: raise PermissionError("invalid fixture claims")
    expected=hmac.new(secret,canonical(claims),hashlib.sha256).hexdigest()
    mac=token["mac"]
    if not isinstance(mac,str) or not hmac.compare_digest(expected,mac): raise PermissionError("signature mismatch")
    if claims["iss"]!=expected_issuer or claims["aud"]!=AUDIENCE: raise PermissionError("untrusted issuer or audience")
    if not isinstance(claims["sub"],str) or not CASE_ID.fullmatch(claims["sub"]): raise PermissionError("invalid subject")
    if claims["role"] not in ROLES: raise PermissionError("invalid role")
    if type(claims["exp"]) is not int or type(claims["iat"]) is not int or type(now) is not int: raise PermissionError("invalid time")
    if not (claims["iat"]<=now<claims["exp"]) or claims["exp"]-claims["iat"]>900: raise PermissionError("expired or overlong assertion")
    return VerifiedPrincipal(claims["sub"],claims["role"],claims["iss"],claims["exp"])

def require_distinct_principals(analyst, reviewer, officer):
    if not all(isinstance(p,VerifiedPrincipal) for p in (analyst,reviewer,officer)): raise PermissionError("identity verification required")
    if (analyst.role,reviewer.role,officer.role)!=("analyst","reviewer","release_officer"): raise PermissionError("invalid role separation")
    if len({analyst.subject,reviewer.subject,officer.subject})!=3: raise PermissionError("separation of duties failed")
    if len({analyst.issuer,reviewer.issuer,officer.issuer})!=1: raise PermissionError("issuer mismatch")
    return True

def route(domain):
    if domain not in DOMAINS: raise ValueError("unsupported case domain")
    return {"RESULT_DISCREPANCY":"CEE","ELECTORAL_ADMINISTRATION":"CEE","CAMPAIGN_FINANCE":"OCE"}.get(domain,"JURISDICTION_REVIEW_REQUIRED")

def public_envelope(payload):
    """Fail-closed allowlist. No summarization or raw-text leakage."""
    if not isinstance(payload,dict) or set(payload)!=PUBLIC_FIELDS: raise ValueError("unrecognized or missing fields")
    if payload["synthetic"] is not True: raise PermissionError("real cases disabled")
    if not isinstance(payload["case_id"],str) or not CASE_ID.fullmatch(payload["case_id"]): raise ValueError("invalid id")
    if payload["domain"] not in DOMAINS or payload["status"] not in STATUSES: raise ValueError("invalid domain/status")
    if type(payload["source_count"]) is not int or payload["source_count"]<0: raise ValueError("bad source count")
    if payload["review_state"] not in ("OPEN","REVIEWED","UNRESOLVED"): raise ValueError("bad review state")
    if payload["classification"] not in ("DOCUMENT_VERSION","ARITHMETIC","DATE_CONTRADICTION","UNKNOWN"): raise ValueError("bad class")
    return dict(payload)

def verified_evidence_manifest(records):
    """Manifest of byte hashes, not proof of source provenance or WORM storage."""
    if not isinstance(records,list): raise ValueError("records list required")
    seen=set()
    for r in records:
        if not isinstance(r,dict) or set(r)!={"source_id","sha256","synthetic"}: raise ValueError("unexpected evidence fields")
        if r["synthetic"] is not True: raise PermissionError("real evidence disabled")
        if not isinstance(r["source_id"],str) or not CASE_ID.fullmatch(r["source_id"]): raise ValueError("invalid source id")
        if not isinstance(r["sha256"],str) or not HEX64.fullmatch(r["sha256"]): raise ValueError("bad hash")
        if r["source_id"] in seen: raise ValueError("duplicate source")
        seen.add(r["source_id"])
    return {"source_count":len(records),"manifest_sha256":hashlib.sha256(canonical(sorted(records,key=lambda r:r["source_id"]))).hexdigest(),"source_ids":sorted(seen),"certification":"SYNTHETIC_UNVERIFIED"}
