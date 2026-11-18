"""RC21: conservative OGP/SUTRA legal and 2028 calendar version gates.

Pure metadata only. Matching names and similar titles do not prove original byte
equivalence; exact source snapshots require separately archived primary bytes.
"""
from __future__ import annotations
from datetime import date

def classify_legal_version_pair(a,b):
    required=("authority","url","revision","original_bytes","sha256")
    if any(not isinstance(x,dict) or any(k not in x for k in required) for x in (a,b)):
        raise ValueError("source version manifest incomplete")
    if any(x["original_bytes"] is False and x["sha256"] is not None for x in (a,b)):
        raise ValueError("hash without original bytes")
    if a["authority"]!=b["authority"]:
        return {"state":"DIFFERENT_AUTHORITIES","byte_relation":"UNVERIFIED","canonical_identity":False}
    if a["revision"]!=b["revision"]:
        return {"state":"DIFFERENT_SOURCE_EPOCHS","byte_relation":"UNVERIFIED","canonical_identity":False}
    return {"state":"SAME_EPOCH_CANDIDATE","byte_relation":"UNVERIFIED","canonical_identity":False}

def adjudicate_law_effectivity(index_date,calculated_date,*,original_enacted_bytes=None,qualified_review=False):
    try:date.fromisoformat(index_date);date.fromisoformat(calculated_date)
    except (TypeError,ValueError) as exc:raise ValueError("invalid date") from exc
    if qualified_review:
        raise PermissionError("no independently authenticated original law and legal-review artifact")
    return {"index_date":index_date,"calculated_date":calculated_date,
            "conflict":index_date!=calculated_date,"status":"OPEN",
            "signed_law_verified":False,
            "legal_effective_date_certified":None}

def validate_calendar_event_rows(rows,*,source_authority_verified=False,complete_amendment_manifest=False):
    if not isinstance(rows,list):raise ValueError("event rows required")
    valid=[];unresolved=[];seen=set()
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or any(not isinstance(row.get(k),str) or not row[k]
            for k in ("id","date","source_id","modality")):
            unresolved.append({"row_index":i,"reason":"INCOMPLETE_EVENT"});continue
        try:date.fromisoformat(row["date"])
        except ValueError:
            unresolved.append({"row_index":i,"reason":"INVALID_DATE"});continue
        if row["id"] in seen:
            unresolved.append({"row_index":i,"reason":"DUPLICATE_EVENT_ID"});continue
        seen.add(row["id"]);valid.append(row)
    assert len(rows)==len(valid)+len(unresolved)
    return {"input":len(rows),"classified":len(valid),"unresolved":unresolved,
            "count_closed":True,"source_authority_verified":source_authority_verified is True,
            "complete_event_denominator":None,
            "certification":"AUDIT_ONLY" if not (source_authority_verified and complete_amendment_manifest) else "REQUIRES_INDEPENDENT_QA"}

def classify_javaa_document(source):
    if not isinstance(source,dict):raise ValueError("source required")
    if source.get("year_scope")==2024:
        return {"usable_as_2028_operative":False,"state":"HISTORICAL_2024_ONLY"}
    if source.get("authority")!="CEE" or source.get("year_scope")!=2028:
        return {"usable_as_2028_operative":False,"state":"SOURCE_SCOPE_UNVERIFIED"}
    return {"usable_as_2028_operative":False,"state":"CANDIDATE_PENDING_SIGNED_SOURCE_AND_HASH"}
