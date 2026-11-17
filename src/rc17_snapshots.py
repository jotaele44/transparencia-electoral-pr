"""META-2028 RC17: deterministic *offline* source publication snapshot comparison.

Only caller-supplied bytes and strict UTC timestamps. This tool cannot fetch,
publish, adjudicate legal validity, or establish source authority.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlsplit
from collections import Counter

def _utc(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("UTC ISO-8601 Z required")
    try:
        result=datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if result.tzinfo is None or result.utcoffset().total_seconds()!=0:
        raise ValueError("UTC must have zero offset")
    return result

def freeze_fixture(*,source_id,authority,url,received_utc,bytes_value,source_date=None):
    """Generate inspectable byte provenance; no claim of authenticated official origin."""
    if not isinstance(source_id,str) or not source_id.strip():raise ValueError("source ID missing")
    if not isinstance(authority,str) or not authority.strip():raise ValueError("authority label missing")
    if not isinstance(url,str) or urlsplit(url).scheme!="https" or not urlsplit(url).netloc:
        raise ValueError("exact HTTPS source locator required")
    _utc(received_utc)
    if not isinstance(bytes_value,bytes) or not bytes_value:raise ValueError("nonempty source bytes required")
    if source_date is not None and not isinstance(source_date,str):raise ValueError("source date invalid")
    return {"source_id":source_id,"authority_claim":authority,"url":url,"received_utc":received_utc,
            "source_date":source_date,"sha256":sha256(bytes_value).hexdigest(),"byte_length":len(bytes_value),
            "scope":"CALLER_SUPPLIED_FIXTURE_ONLY","original_authority_verified":False}

def compare_snapshots(old,new):
    fields=("source_id","url","received_utc","sha256","byte_length","scope","original_authority_verified")
    for r in (old,new):
        if not isinstance(r,dict) or any(k not in r for k in fields):
            raise ValueError("malformed snapshot")
        _utc(r["received_utc"])
        if r["scope"]!="CALLER_SUPPLIED_FIXTURE_ONLY" or r["original_authority_verified"] is not False:
            raise PermissionError("unreviewed source claim")
        if not isinstance(r["sha256"],str) or len(r["sha256"])!=64 or any(c not in "0123456789abcdef" for c in r["sha256"]):
            raise ValueError("bad sha256")
    if old["source_id"]!=new["source_id"]:
        raise ValueError("source ID conflicts; preserve separate manifestations")
    if _utc(new["received_utc"])<_utc(old["received_utc"]):
        raise ValueError("out-of-order capture")
    same=old["sha256"]==new["sha256"]
    same_url=old["url"]==new["url"]
    return {"classification":("BYTE_IDENTICAL" if same else
            "REISSUED_AT_SAME_URL_CANDIDATE" if same_url else
            "MOVED_AND_BYTE_CHANGED_CANDIDATE"),
            "url_changed":not same_url,"bytes_changed":not same,
            "schema_relation":"UNTESTED","logical_relation":"UNRESOLVED",
            "source_authenticity":"UNVERIFIED","human_review_required":not same,
            "automated_publication":False}

def classify_source_visibility(before,after,*,searched_coverage):
    """Missing observation != deleted record, unless exhaustive scope is independently proved."""
    if not isinstance(searched_coverage,dict) or searched_coverage.get("exhaustive") is not True:
        return {"state":"SEARCH_COVERAGE_INCOMPLETE","deletion_proven":False,
                "search_false_negative":"OPEN"}
    if before is None:
        return {"state":"NO_PRIOR_SOURCE","deletion_proven":False}
    if after is None:
        return {"state":"UNOBSERVED_IN_CERTIFIED_SEARCH_SCOPE","deletion_proven":False}
    return {"state":"OBSERVED","deletion_proven":False}

def source_identity_coverage(registry):
    """Close the *discovered registry* denominator, not the unknown total expected events."""
    if not isinstance(registry,dict):raise ValueError("registry required")
    events=registry.get("events",[]);sources=registry.get("source_registry",[])
    if not isinstance(events,list) or not isinstance(sources,list):raise ValueError("lists required")
    ids=[s.get("source_id") for s in sources if isinstance(s,dict)]
    if len(ids)!=len(sources) or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
        raise ValueError("source namespace incomplete/duplicate")
    unresolved=sorted({e.get("source_id") for e in events if isinstance(e,dict) and e.get("source_id") not in ids},key=str)
    bad_rows=len(events)-sum(isinstance(e,dict) and isinstance(e.get("source_id"),str) for e in events)
    return {"discovered_source_count":len(ids),"discovered_event_count":len(events),
            "unbound_event_source_ids":unresolved,"invalid_event_rows":bad_rows,
            "complete_authoritative_event_denominator":None,"full_catalogue_certification":"OPEN"}
