"""Conservative reporting-unit key validation for fixture rows; not a CEE identity binder."""
FIELDS=("PREKEY","UNIKEY","COLKEY")
def evaluate(rows, *, ballot):
    if not isinstance(ballot,str) or ballot not in ("ESTATAL","LEGISLATIVA","MUNICIPAL","PRESIDENCIAL","PLEBISCITO"):
        raise ValueError("unsupported ballot")
    if not isinstance(rows,list):raise ValueError("rows list required")
    indexed={}
    unresolved=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict):
            raise ValueError("row must be dict")
        if any(k not in row for k in FIELDS):
            unresolved.append({"row_index":i,"class":"MISSING_KEY_FIELD"})
            continue
        key=tuple(row[k] for k in FIELDS)
        if any(not isinstance(v,str) or not v or not v.isascii() for v in key):
            unresolved.append({"row_index":i,"class":"UNRESOLVED_KEY_ENCODING_OR_TYPE"})
            continue
        if key in indexed:
            unresolved.append({"row_index":i,"class":"DUPLICATE_COMPOSITE_KEY","key":list(key)})
            continue
        indexed[key]=dict(row)
    return {"ballot":ballot,"input_count":len(rows),"keyed_count":len(indexed),"unresolved_count":len(unresolved),"unresolved_rows":unresolved,"keys":[list(x) for x in sorted(indexed)],"identity_status":"CANDIDATE_NOT_IDENTITY","official_denominator":None,"certification":"UNRESOLVED"}

def compare(a,b, *, ballot):
    left=evaluate(a,ballot=ballot)
    right=evaluate(b,ballot=ballot)
    if left["unresolved_count"] or right["unresolved_count"]:
        return {"status":"BLOCKED_UNRESOLVED_KEYS","left":left,"right":right}
    sa={tuple(x) for x in left["keys"]}
    sb={tuple(x) for x in right["keys"]}
    return {"status":"CANDIDATE_NOT_IDENTITY","intersection":len(sa&sb),"a_only":len(sa-sb),"b_only":len(sb-sa),"union":len(sa|sb),"symmetric_difference":len(sa^sb),"left_rows":len(a),"right_rows":len(b),"identity_verified":False}
