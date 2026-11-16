"""Offline evidence manifest adjudication for source versions and mailing dates.

No network I/O; no legal certification or claims of real vote counts.
"""
from __future__ import annotations
from datetime import date
from hashlib import sha256
import re

HASH=re.compile(r"^[a-f0-9]{64}$")
REQUIRED=("source_id","source_epoch","bytes","sha256","authority")

def verify_manifestation(record):
    if not isinstance(record,dict) or any(k not in record for k in REQUIRED):
        raise ValueError("missing manifestation fields")
    if any(not isinstance(record[k],str) or not record[k].strip() for k in ("source_id","source_epoch","authority")):
        raise ValueError("invalid manifestation identity metadata")
    if not isinstance(record["bytes"],bytes):raise ValueError("actual bytes required")
    digest=record["sha256"]
    if not isinstance(digest,str) or not HASH.fullmatch(digest):raise ValueError("invalid digest")
    if sha256(record["bytes"]).hexdigest()!=digest:raise ValueError("byte mismatch")
    return {"source_id":record["source_id"],"source_epoch":record["source_epoch"],"sha256":digest,"authority":record["authority"],"byte_length":len(record["bytes"])}

def compare_report_versions(left,right,*,authoritative_relation=None):
    a=verify_manifestation(left)
    b=verify_manifestation(right)
    if a["source_epoch"]==b["source_epoch"]:raise ValueError("distinct source epochs required")
    if a["source_id"]==b["source_id"] and a["sha256"]!=b["sha256"]:raise ValueError("source ID reused for nonidentical bytes")
    same_bytes=a["sha256"]==b["sha256"]
    relation="BYTE_IDENTICAL" if same_bytes else "DISTINCT_BYTES_LOGICAL_IDENTITY_UNRESOLVED"
    # A claim about linkage requires documentary evidence, not merely an operator assertion.
    if authoritative_relation is not None and (not isinstance(authoritative_relation,dict) or authoritative_relation.get("status")!="UNVERIFIED"):
        raise ValueError("unsupported authority promotion")
    return {"left":a,"right":b,"byte_relation":relation,"logical_relation":"UNRESOLVED",
            "schema_relation":"UNTESTED","row_reconciliation":"BLOCKED",
            "certification":"AUDIT_ONLY"}

def mailing_scenario(*,first_mail_date,last_mail_date,resolution_binding):
    if resolution_binding!="CEE-RS-26-010":raise ValueError("unbound calendar authority")
    try:
        first=date.fromisoformat(first_mail_date)
        last=date.fromisoformat(last_mail_date)
    except (TypeError,ValueError) as exc:raise ValueError("invalid mailing date") from exc
    start_limit=date(2028,9,20)
    end_limit=date(2028,10,3)
    errors=[]
    if first>start_limit:errors.append("START_AFTER_RESOLUTION_DEADLINE")
    if last>end_limit:errors.append("END_AFTER_RESOLUTION_DEADLINE")
    if last<first:errors.append("END_BEFORE_START")
    return {"first_mail_date":str(first),"last_mail_date":str(last),
            "source":"CEE-RS-26-010","status":"SYNTHETIC_COMPLIANT" if not errors else "SYNTHETIC_NONCOMPLIANT",
            "findings":errors,"certification":"TEST_ONLY"}
