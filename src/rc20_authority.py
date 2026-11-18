"""RC20 source classification and legally non-adjudicative deadline evidence gates."""
from __future__ import annotations
from datetime import date
from hashlib import sha256

def classify_source(document):
    if not isinstance(document,dict):raise ValueError("source record required")
    for k in ("id","kind","authority","url"):
        if not isinstance(document.get(k),str) or not document[k]:raise ValueError("missing source provenance")
    if not document["url"].startswith("https://"):raise ValueError("invalid source locator")
    if document["kind"]=="CANDIDATE_STATISTICAL_ORIENTATION_GUIDE_NOT_ELECTION_CALENDAR":
        return {"type":"STATISTICAL_GUIDE","may_certify_complete_calendar":False,"certification":"AUDIT_ONLY"}
    if document.get("original_bytes_acquired") is False and document.get("sha256") is not None:
        raise ValueError("fabricated source hash")
    return {"type":document["kind"],"may_certify_complete_calendar":False,"certification":"AUDIT_ONLY"}

def reconcile_effective_date(*,indexed_date,computed_date,original_statute_bytes=None,verified_official_interpretation=None):
    try:a=date.fromisoformat(indexed_date);b=date.fromisoformat(computed_date)
    except (TypeError,ValueError) as exc:raise ValueError("invalid legal date") from exc
    if verified_official_interpretation is not None:
        raise PermissionError("independent legal adjudication unavailable")
    return {"official_index_date":a.isoformat(),"computed_date":b.isoformat(),
            "date_conflict":a!=b,"status":"LEGAL_INTERPRETATION_OPEN",
            "original_enacted_source_bytes_available":isinstance(original_statute_bytes,bytes) and bool(original_statute_bytes),
            "operational_deadline_established":False,"legal_violation_proven":False}

def scope_absentee_guidance(*,cee_application_days,statutory_application_days,federal_transmission_days):
    if any(type(x) is not int or not 0<=x<=365 for x in (cee_application_days,statutory_application_days,federal_transmission_days)):
        raise ValueError("invalid day window")
    return {"cee_vs_code_text_difference":cee_application_days!=statutory_application_days,
            "federal_transmission_separate_from_application":True,
            "actual_cee_administered_deadline":None,"affected_voter_count":None,
            "adjudication":"HUMAN_LEGAL_SOURCE_REVIEW_REQUIRED","fraud_or_violation_proven":False}

def count_source_rows(sources):
    if not isinstance(sources,list):raise ValueError("source list required")
    ids=[];unresolved=[]
    for i,s in enumerate(sources):
        if not isinstance(s,dict) or not isinstance(s.get("id"),str) or not s["id"] or s["id"] in ids:
            unresolved.append(i);continue
        ids.append(s["id"])
    return {"input_rows":len(sources),"unique_ids":len(ids),"unresolved_indices":unresolved,
            "conserved":len(sources)==len(ids)+len(unresolved),
            "complete_source_denominator":None,"certification":"AUDIT_ONLY"}
