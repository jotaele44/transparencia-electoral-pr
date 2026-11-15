"""Offline conservative result reconciliation. No inferred candidate equivalence."""
from collections import Counter

FIELDS = ("election_id", "contest_id", "reporting_unit_id", "candidate_id", "vote_method")

def reconcile(left, right):
    def index(rows, side):
        out = {}
        for row in rows:
            if not isinstance(row, dict) or any(k not in row for k in (*FIELDS, "votes")):
                raise ValueError(f"{side}: missing fields")
            key = tuple(row[k] for k in FIELDS)
            if any(not isinstance(v, str) or not v.strip() for v in key):
                raise ValueError(f"{side}: invalid identifier")
            if type(row["votes"]) is not int or row["votes"] < 0:
                raise ValueError(f"{side}: invalid vote count")
            if key in out:
                raise ValueError(f"{side}: duplicate composite key")
            out[key] = row["votes"]
        return out
    a, b = index(left, "left"), index(right, "right")
    rows = []
    for key in sorted(a.keys() | b.keys()):
        status = ("LEFT_ONLY" if key not in b else "RIGHT_ONLY" if key not in a else "VALUE_DIFFERENCE" if a[key] != b[key] else "MATCH")
        rows.append({"key": dict(zip(FIELDS, key)), "left_votes": a.get(key), "right_votes": b.get(key), "status": status})
    c = Counter(row["status"] for row in rows)
    return {"left_count": len(a), "right_count": len(b), "union_count": len(rows), "intersection_count": len(a.keys() & b.keys()), "symmetric_difference_count": len(a.keys() ^ b.keys()), "counts": {k: c[k] for k in ("MATCH", "VALUE_DIFFERENCE", "LEFT_ONLY", "RIGHT_ONLY")}, "rows": rows, "certification": "UNRESOLVED"}
