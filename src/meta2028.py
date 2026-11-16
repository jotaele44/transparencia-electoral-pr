"""META-2028 offline, synthetic-only public evidence monitoring candidate.

Does not call remote sites, record real voter data, send alerts, or adjudicate
election integrity. External providers require separate review and authorization.
"""
from __future__ import annotations
from datetime import date
from hashlib import sha256
from rc6_security import VerifiedPrincipal,require_distinct_principals,canonical
from rc14_reporting_units import can_compare_result_pair
from rc15_custody_gates import custody_relation

ALLOWED_EVENT_TYPES=frozenset(("PRIMARY","ELECTION_DAY","ADVANCE_MAIL","CEE_DECISION","SOURCE_REVISION","RESULT_PUBLICATION","CUSTODY_ACTION"))
KNOWN_STATES=frozenset(("OFFICIAL_SOURCE_STATED","STATUTORY_DATE_VERIFIED_WITH_CONTRADICTORY_RFP","SIGNED_RESOLUTION","UNRESOLVED"))
ALLOWED_SOURCE_STATES=frozenset(("VISUALLY_REVIEWED_NOT_BYTES_FROZEN","IDENTIFIED_BYTES_UNAVAILABLE","COMPLETION_EVENT_CONFIRMED_ATTACHMENT_UNKNOWN","IDENTIFIED_NOT_BYTES_FROZEN"))
HEX=frozenset("0123456789abcdef")

def validate_registry(registry):
    """Schema gate, not a live monitor or a claim of source authenticity."""
    if not isinstance(registry,dict) or registry.get("schema_version")!="meta2028_event_registry_v1":
        raise ValueError("unrecognized registry contract")
    if registry.get("production_monitor_enabled") is not False:raise PermissionError("live monitoring not authorized")
    if registry.get("source_evidence_has_original_bytes") is not False:raise PermissionError("unverified byte claims")
    events=registry.get("events"); sources=registry.get("source_registry")
    if not isinstance(events,list) or not isinstance(sources,list):raise ValueError("lists required")
    event_ids=set();source_ids=set()
    for s in sources:
        if not isinstance(s,dict) or not isinstance(s.get("source_id"),str) or not s["source_id"]:
            raise ValueError("bad source id")
        if s["source_id"] in source_ids:raise ValueError("duplicate source")
        source_ids.add(s["source_id"])
        if s.get("state") not in ALLOWED_SOURCE_STATES or s.get("original_sha256") is not None:
            raise ValueError("unfrozen source cannot be promoted")
        if not isinstance(s.get("url"),str) or not s["url"].startswith("https://"):
            raise ValueError("invalid source url")
    for e in events:
        if not isinstance(e,dict) or not isinstance(e.get("id"),str) or not e["id"]:
            raise ValueError("bad event id")
        if e["id"] in event_ids:raise ValueError("duplicate event")
        event_ids.add(e["id"])
        if e.get("event_type") not in ALLOWED_EVENT_TYPES or e.get("legal_state") not in KNOWN_STATES:
            raise ValueError("invalid event type or authority state")
        if e.get("monitor_state")!="NOT_ENABLED" or e.get("source_sha256") is not None:
            raise PermissionError("monitor or source bytes unexpectedly enabled")
        if not isinstance(e.get("source_url"),str) or not e["source_url"].startswith("https://"):
            raise ValueError("event url missing")
        try:date.fromisoformat(e["date"])
        except (TypeError,ValueError,KeyError) as exc:raise ValueError("invalid event date") from exc
    return {"events":len(events),"sources":len(sources),"monitor":"OFF","certification":"AUDIT_ONLY"}

def observe_snapshot(old,new,*,source_id,now_utc):
    """Compare actual synthetic bytes. No external source claim or autonomous alert."""
    if not isinstance(source_id,str) or not source_id.strip():raise ValueError("source ID required")
    if not isinstance(now_utc,str) or not now_utc.endswith("Z"):raise ValueError("UTC provenance required")
    if not isinstance(old,bytes) or not isinstance(new,bytes):raise ValueError("original bytes missing")
    before=sha256(old).hexdigest();after=sha256(new).hexdigest()
    return {"source_id":source_id,"observation_utc":now_utc,"before_sha256":before,"after_sha256":after,
            "byte_change":"BYTE_IDENTICAL" if before==after else "BYTE_DIFFERENT",
            "logical_schema_change":"UNRESOLVED","alert":"PROVISIONAL_REVIEW_REQUIRED" if before!=after else "NONE",
            "source":"SYNTHETIC_FIXTURE_NOT_OFFICIAL"}

def deadline_check(*,deadline_kind,legal_bound,observed,synthetic=True):
    if synthetic is not True:raise PermissionError("real electoral enforcement disabled")
    if deadline_kind not in ("LATEST_START","LATEST_END"):raise ValueError("unsupported legal deadline kind")
    try:expected=date.fromisoformat(legal_bound);actual=date.fromisoformat(observed)
    except (ValueError,TypeError) as exc:raise ValueError("invalid ISO date") from exc
    if deadline_kind=="LATEST_START" and expected!=date(2028,9,20):raise ValueError("unknown start bound")
    if deadline_kind=="LATEST_END" and expected!=date(2028,10,3):raise ValueError("unknown end bound")
    return {"status":"SYNTHETIC_LATE_OBSERVATION" if actual>expected else "SYNTHETIC_WITHIN_BOUND",
            "source_id":"cee_rs_26_010","official_compliance_finding":False,"human_review_required":True}

def unit_match(a,b):
    """Exact epoch scoped key match is discovery only; no canonical identity."""
    fields=("source_epoch","municipality_raw","precinct_raw","unit_raw","college_raw","ballot_type")
    if not isinstance(a,dict) or not isinstance(b,dict):raise ValueError("record object required")
    if any(not isinstance(r.get(f),str) or not r[f] for r in (a,b) for f in fields):
        return {"state":"UNRESOLVED","match":None}
    matching=all(a[f]==b[f] for f in fields)
    return {"state":"CANDIDATE_NOT_IDENTITY","match":matching,"canonical_identity_proven":False}

def compare_result_manifests(a,b):
    """Reuse RC14 source-grain and byte-hash gates; never compute real votes."""
    return can_compare_result_pair(a,b)

def custody_overlap(agreement,manifest):
    return custody_relation(agreement,manifest)

def review_case(*,case,analyst,reviewer,officer):
    if not isinstance(case,dict) or set(case)!={
        "case_id","synthetic","source_ids","finding_state","release_requested"}:
        raise ValueError("fail-closed case fields")
    if case["synthetic"] is not True:raise PermissionError("real case review disabled")
    if not isinstance(case["case_id"],str) or not case["case_id"].strip():raise ValueError("invalid case id")
    if not isinstance(case["source_ids"],list) or any(not isinstance(x,str) or not x for x in case["source_ids"]) or len(case["source_ids"])!=len(set(case["source_ids"])):
        raise ValueError("source IDs required, unique")
    if case["finding_state"] not in ("UNRESOLVED","DOCUMENTED_PROCESS","SYNTHETIC_DETECTED","WITHDRAWN"):
        raise ValueError("finding cannot imply guilt")
    if case["release_requested"] is not False:raise PermissionError("real/public release not enabled")
    require_distinct_principals(analyst,reviewer,officer)
    return {"case_id":case["case_id"],"synthetic":True,"status":"REVIEWED_FIXTURE_ONLY",
            "public_release_authorized":False,"automated_referral_authorized":False}

def public_preview(payload):
    """No free text, names, evidence bytes, contacts or true real-case data."""
    fields={"case_id","synthetic","status","source_count","classification"}
    if not isinstance(payload,dict) or set(payload)!=fields:raise ValueError("unexpected public fields")
    if payload["synthetic"] is not True:raise PermissionError("real data cannot enter preview")
    if not isinstance(payload["case_id"],str) or not payload["case_id"].startswith("synthetic-") or len(payload["case_id"])>80:
        raise ValueError("case id invalid")
    if payload["status"] not in ("OPEN","REVIEWED","WITHDRAWN"):raise ValueError("invalid status")
    if type(payload["source_count"]) is not int or not 0<=payload["source_count"]<=10000:raise ValueError("invalid count")
    if payload["classification"] not in ("UNRESOLVED","SOURCE_VERSION","DATE_CONFLICT","CUSTODY_GAP"):
        raise ValueError("invalid classification")
    return dict(payload)
