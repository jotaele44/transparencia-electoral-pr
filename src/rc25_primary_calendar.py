"""RC25: preserve raw CEE RFP date and separately evaluate first-Sunday law.

No unilateral calendar replacement, no temporal promotion from procurement
prose to signed calendar and no operative compliance findings.
"""
from __future__ import annotations
from datetime import date, timedelta

def first_sunday_june(year):
    if type(year) is not int or not 2000<=year<=2200:
        raise ValueError("year outside bounded election horizon")
    first=date(year,6,1)
    return first+timedelta(days=(6-first.weekday())%7)

def classify_primary_date(*,source_date,year,source_class,legal_rule_text):
    if not isinstance(source_date,str):raise ValueError("literal source date required")
    try:raw=date.fromisoformat(source_date)
    except ValueError as e:raise ValueError("invalid raw date") from e
    if raw.year!=year:raise ValueError("calendar year inconsistency")
    if source_class!="PROCUREMENT_RFP_CONTEXT":
        raise ValueError("unexpected source type")
    if legal_rule_text!="FIRST_SUNDAY_JUNE":
        raise ValueError("legal text not independently identified")
    statutory=first_sunday_june(year)
    return {"raw_rfp_date":raw.isoformat(),"raw_weekday":raw.strftime("%A").upper(),
            "statutory_derived_candidate":statutory.isoformat(),
            "statutory_weekday":statutory.strftime("%A").upper(),
            "source_conflict":raw!=statutory,
            "operative_date_certified":False,
            "complete_official_calendar_verified":False,
            "publication_action":"HUMAN_REVIEW_REQUIRED" if raw!=statutory else "NO_DATE_DISAGREEMENT",
            "classification":"RAW_SOURCE_VS_STATUTORY_RULE_NOT_CANONICAL"}

def review_frozen_members(manifest):
    """Validate conservation of claimed frozen-file entries, not original bytes."""
    if not isinstance(manifest,dict):raise ValueError("manifest required")
    sources=manifest.get("sources");counts=manifest.get("counts",{})
    if not isinstance(sources,list) or not isinstance(counts,dict):
        raise ValueError("source rows and counts required")
    if any(type(counts.get(k)) is not int or counts[k]<0 for k in ("requested","acquired","failed","blocked")):
        raise ValueError("invalid counts")
    if counts["requested"]!=counts["acquired"]+counts["failed"]+counts["blocked"]:
        raise ValueError("acquisition conservation failure")
    if counts["acquired"]!=len(sources):raise ValueError("source row mismatch")
    ids=set()
    for item in sources:
        if not isinstance(item,dict) or not isinstance(item.get("id"),str) or not item["id"]:
            raise ValueError("missing source ID")
        if item["id"] in ids:raise ValueError("duplicate exact source ID")
        ids.add(item["id"])
        sha=item.get("sha256")
        if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("source hash malformed")
        if type(item.get("bytes")) is not int or item["bytes"]<=0:
            raise ValueError("missing source byte length")
    return {"listed_source_manifestations":len(sources),"counts_closed":True,
            "original_bytes_independently_rehashed_by_this_function":False,
            "source_authority_certified":False,"release":"AUDIT_ONLY"}
