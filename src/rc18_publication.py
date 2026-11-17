"""RC18: pure read-only publication intake and legal-scope observation.

Offline function library. Caller supplies bytes; this module never contacts
official websites, writes to disk, sends alerts or emits real legal conclusions.
"""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
from urllib.parse import urlsplit
from rc17_snapshots import compare_snapshots

MAX_BYTES=40_000_000
ALLOWED_TYPES={"application/pdf","text/html","application/json","text/plain"}
def _timestamp(v):
    if not isinstance(v,str) or not v.endswith("Z"):raise ValueError("UTC Z timestamp required")
    try:t=datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError as exc:raise ValueError("invalid timestamp") from exc
    if t.utcoffset().total_seconds()!=0:raise ValueError("nonzero UTC")
    return t

def intake(*,source_id,url,observed_utc,payload,content_type,declared_sha256=None):
    """Bounded original-byte observation; does not certify source authority."""
    if not isinstance(source_id,str) or not source_id.strip():raise ValueError("source id required")
    if not isinstance(url,str):raise ValueError("url required")
    u=urlsplit(url)
    if u.scheme!="https" or not u.hostname or u.username or u.password:
        raise ValueError("only exact HTTPS public URLs")
    _timestamp(observed_utc)
    if not isinstance(payload,bytes) or not payload or len(payload)>MAX_BYTES:
        raise ValueError("missing, empty or oversize original bytes")
    if content_type not in ALLOWED_TYPES:raise ValueError("unsupported content type")
    if content_type=="application/pdf" and not payload.startswith(b"%PDF-"):
        raise ValueError("payload is not a PDF")
    digest=sha256(payload).hexdigest()
    if declared_sha256 is not None and declared_sha256!=digest:
        raise ValueError("declared payload hash mismatch")
    return {"source_id":source_id,"url":url,"received_utc":observed_utc,
            "sha256":digest,"byte_length":len(payload),"content_type":content_type,
            "scope":"CALLER_SUPPLIED_FIXTURE_ONLY","original_authority_verified":False,
            "publication_date":None,"effective_date":None,"legal_conclusion":"UNRESOLVED"}

def classify_incremental(old,new):
    """Reuse RC17 strict ordering and byte/URL differences."""
    result=compare_snapshots(old,new)
    return {"source_id":new["source_id"],"state":result["classification"],
            "logical_relation":result["logical_relation"],
            "publication_date_verified":False,
            "legal_change_verified":False,
            "requires_independent_review":result["human_review_required"],
            "public_alert_allowed":False}

def compare_public_information_with_law(*,web_claim_days,law_claim_days,web_source,law_source,modality,law_effective_verified=False):
    """Treat mismatched stated deadlines as review candidates, never violations."""
    if type(web_claim_days) is not int or type(law_claim_days) is not int:
        raise ValueError("integer day windows required")
    if not (0<=web_claim_days<=365 and 0<=law_claim_days<=365):
        raise ValueError("day window invalid")
    if not all(isinstance(v,str) and v for v in (web_source,law_source,modality)):
        raise ValueError("binding metadata required")
    if modality not in ("ABSENTEE_APPLICATION","ADVANCE_APPLICATION","ABSENTEE_BALLOT_TRANSMISSION","ADVANCE_MAILING"):
        raise ValueError("modality unresolved")
    return {"web_source":web_source,"law_source":law_source,"modality":modality,
            "stated_deadlines_differ":web_claim_days!=law_claim_days,
            "law_effective_verified":law_effective_verified is True,
            "actual_deadline_administered":None,"affected_voters":None,
            "legal_violation_proven":False,
            "classification":"PUBLIC_INFORMATION_MISMATCH_REVIEW" if web_claim_days!=law_claim_days else "NO_STATEMENT_DIFFERENCE",
            "automation":"DETECTION_ONLY"}

def same_legal_population(a,b):
    """No cross-modality deadline collision without signed source population binding."""
    for x in (a,b):
        if not isinstance(x,dict) or not all(isinstance(x.get(k),str) and x[k] for k in ("modality","population","source_epoch")):
            return {"state":"UNRESOLVED","same_population_proven":False}
    if a["modality"]!=b["modality"] or a["population"]!=b["population"] or a["source_epoch"]!=b["source_epoch"]:
        return {"state":"DIFFERENT_SCOPES","same_population_proven":False}
    return {"state":"MATCHING_DESCRIPTIONS_CANDIDATE","same_population_proven":False}
