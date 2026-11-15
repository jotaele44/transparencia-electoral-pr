"""Pure, offline election-publication difference detection. No network or alerts sent."""
from datetime import date

REQUIRED = ("source_id", "source_version", "publication_kind", "record_id", "published_at", "document_sha256")

def classify(first, second):
    """Reconcile complete row sets. Versioned records are not silently merged."""
    def keyed(rows, side):
        result = {}
        for r in rows:
            if not isinstance(r, dict) or any(k not in r or not isinstance(r[k], str) or not r[k].strip() for k in REQUIRED):
                raise ValueError(side + ": missing/invalid required metadata")
            h = r["document_sha256"]
            if len(h) != 64 or any(c not in "0123456789abcdef" for c in h):
                raise ValueError(side + ": invalid source hash")
            k = (r["source_id"], r["record_id"])
            if k in result:
                raise ValueError(side + ": duplicate record identity")
            result[k] = r
        return result
    a, b = keyed(first, "before"), keyed(second, "after")
    events=[]
    for k in sorted(a.keys() | b.keys()):
        old, new = a.get(k), b.get(k)
        if old is None: status = "NEW_RECORD"
        elif new is None: status = "MISSING_IN_NEW_SNAPSHOT"
        elif old == new: status = "UNCHANGED"
        elif old["document_sha256"] != new["document_sha256"] or old["source_version"] != new["source_version"]: status = "REISSUED_OR_REVISED"
        else: status = "METADATA_CHANGED"
        events.append({"identity":list(k), "status":status, "before":old, "after":new, "evidence_state":"CANDIDATE_NOT_IDENTITY"})
    return {"before_count":len(a),"after_count":len(b),"intersection_count":len(a.keys() & b.keys()),"union_count":len(a.keys() | b.keys()),"symmetric_difference_count":len(a.keys() ^ b.keys()),"events":events,"certification":"PROVISIONAL"}

def verify_calendar(calendar):
    by_id={}
    for event in calendar["events"]:
        if event["id"] in by_id: raise ValueError("duplicate calendar event id")
        by_id[event["id"]]=event
        date.fromisoformat(event["date"])
    general=by_id["pr-2028-general"]
    if date.fromisoformat(general["date"]).weekday()!=1: raise ValueError("general election weekday mismatch")
    sunday=by_id["pr-2028-primary-rule-derived"]
    d=date.fromisoformat(sunday["date"])
    if d.weekday()!=6 or d.day>7: raise ValueError("first Sunday rule mismatch")
    asserted=by_id["pr-2028-primary-rfp-stated"]
    if asserted["date"]!=sunday["date"] and asserted["legal_status"]!="UNRESOLVED":
        raise ValueError("contradiction silently resolved")
    if calendar["source_manifestations_frozen"]!=0: raise ValueError("unverified source freeze")
    return True
