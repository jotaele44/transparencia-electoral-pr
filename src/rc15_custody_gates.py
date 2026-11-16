"""Offline conservative case-evidence and custody relation gates.

Names, district membership, date adjacency and references cannot independently
prove chain-of-custody, an acta identity, actual destruction, or voter misconduct.
"""
from __future__ import annotations
from hashlib import sha256

STATES={"INDEX_ONLY","TABLED","APPROVED","ORDERED","EXECUTED","RETAINED","UNRESOLVED"}
IDENTITY_FIELDS=("municipality_raw","precinct_raw","unit_raw","college_raw","ballot_type","source_epoch")

def classify_decision(reference):
    if not isinstance(reference,dict):raise ValueError("reference must be object")
    state=reference.get("state","INDEX_ONLY")
    if state not in STATES:raise ValueError("invalid state")
    if state in ("APPROVED","ORDERED","EXECUTED","RETAINED"):
        if not reference.get("source_bytes") or not isinstance(reference.get("source_bytes"),bytes):
            raise ValueError("underlying original decision bytes required")
        digest=reference.get("sha256")
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("source SHA missing")
        if sha256(reference["source_bytes"]).hexdigest()!=digest:
            raise ValueError("source digest mismatch")
        # Source bytes alone cannot prove an actual physical disposition.
        if state=="EXECUTED" and not reference.get("independent_execution_record"):
            raise PermissionError("independent destruction/transfer receipt required")
        return {"state":state,"verified_byte_integrity":True,"custody_proven":False,"certification":"AUDIT_ONLY"}
    return {"state":state,"verified_byte_integrity":False,"custody_proven":False,"certification":"AUDIT_ONLY"}

def verify_precinct_scope(record, target):
    """Exact namespaced identity for candidate discovery; not proof of custody."""
    if not isinstance(record,dict) or not isinstance(target,dict):raise ValueError("invalid record")
    missing=[k for k in IDENTITY_FIELDS if k not in record or k not in target]
    if missing:return {"state":"UNRESOLVED","reason":"MISSING_FIELDS","missing":missing}
    if any(not isinstance(record[k],str) or not isinstance(target[k],str) or not record[k] or not target[k] for k in IDENTITY_FIELDS):
        return {"state":"UNRESOLVED","reason":"INVALID_FIELDS"}
    if any(record[k]!=target[k] for k in IDENTITY_FIELDS):
        return {"state":"CANDIDATE_NOT_IDENTITY","match":False,"custody_proven":False}
    return {"state":"CANDIDATE_NOT_IDENTITY","match":True,"custody_proven":False}

def custody_relation(agreement, manifest):
    """District-only and temporal coincidences are discovery, never execution."""
    if not isinstance(agreement,dict) or not isinstance(manifest,dict):raise ValueError("invalid custody input")
    district=agreement.get("representative_district")
    if district!=manifest.get("representative_district"):
        return {"state":"OUT_OF_SCOPE","execution_proven":False}
    if any(k not in manifest for k in IDENTITY_FIELDS):
        return {"state":"UNRESOLVED","reason":"DISTRICT_OVERLAP_ONLY","execution_proven":False}
    return {"state":"CANDIDATE_NOT_IDENTITY","execution_proven":False}

def reconcile_ledger(rows):
    if not isinstance(rows,list):raise ValueError("list required")
    seen=set(); accepted=[]; unresolved=[]
    for i,r in enumerate(rows):
        if not isinstance(r,dict) or not isinstance(r.get("record_id"),str) or not r["record_id"].strip():
            unresolved.append({"row_index":i,"reason":"INVALID_RECORD_ID"});continue
        if r["record_id"] in seen:
            unresolved.append({"row_index":i,"reason":"DUPLICATE_RECORD_ID"});continue
        seen.add(r["record_id"])
        accepted.append(r["record_id"])
    assert len(rows)==len(accepted)+len(unresolved)
    return {"input_rows":len(rows),"unique_records":len(accepted),"unresolved_rows":unresolved,
            "row_conserved":True,"source_denominator":None,"certification":"AUDIT_ONLY"}
