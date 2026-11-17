"""RC17 epoch-scoped electoral unit candidate inventory.

Explicitly NOT an authoritative CEE identity crosswalk. Synthetic fixture-only.
"""
FIELDS=("source_epoch","municipality_raw","precinct_raw","unit_raw","college_raw","ballot_type","modality")

def index_units(rows):
    if not isinstance(rows,list):raise ValueError("rows must be list")
    found={};unresolved=[]
    for index,r in enumerate(rows):
        if not isinstance(r,dict) or r.get("synthetic") is not True:
            unresolved.append({"index":index,"reason":"NOT_SYNTHETIC"});continue
        if any(not isinstance(r.get(k),str) or not r[k] for k in FIELDS):
            unresolved.append({"index":index,"reason":"MISSING_OR_INVALID_RAW_KEYS"});continue
        key=tuple(r[k] for k in FIELDS)
        if key in found:
            unresolved.append({"index":index,"reason":"DUPLICATE_EXACT_KEY"});continue
        found[key]=r
    assert len(rows)==len(found)+len(unresolved)
    return found,unresolved

def compare_epochs(a,b):
    aa,au=index_units(a);bb,bu=index_units(b)
    keys_a=set(aa);keys_b=set(bb);inter=keys_a&keys_b
    all_keys=keys_a|keys_b
    return {"a_rows":len(a),"b_rows":len(b),"a_indexed":len(aa),"b_indexed":len(bb),
        "a_unresolved":au,"b_unresolved":bu,
        "intersection":len(inter),"a_only":len(keys_a-keys_b),"b_only":len(keys_b-keys_a),
        "union":len(all_keys),"symmetric_difference":len(keys_a^keys_b),
        "identity":"CANDIDATE_NOT_IDENTITY","verified_cross_epoch_bindings":0,
        "real_official_unit_denominator":None,"certification":"AUDIT_ONLY"}
