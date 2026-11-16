"""RC14: conservative 2024 Puerto Rico special-unit and result-scope gates."""
from __future__ import annotations
from hashlib import sha256

SPECIAL_UNIT_MODALITIES = {
    "72": "VOTO_ADELANTADO_POR_CORREO",
    "73": "VOTO_FACIL_ACCESO_EN_DOMICILIO",
    "74": "COLEGIO_ESPECIAL_JAVAA",
    "76": "VOTO_CONFINADO",
    "77": "VOTO_AUSENTE",
}

def _valid_original_bytes(record):
    raw=record.get("original_bytes")
    digest=record.get("sha256")
    return (isinstance(raw,bytes) and isinstance(digest,str) and len(digest)==64
            and all(c in "0123456789abcdef" for c in digest)
            and sha256(raw).hexdigest()==digest)

def classify_reporting_unit(record):
    required=("source_epoch","municipality_raw","precinct_raw","unit_raw","college_raw","ballot_type","unit_class","authority","binding_source_id")
    if not isinstance(record,dict) or any(k not in record for k in required):
        return {"state":"UNRESOLVED","reason":"MISSING_RAW_IDENTITY_FIELDS"}
    if any(not isinstance(record[k],str) or not record[k] for k in required):
        return {"state":"UNRESOLVED","reason":"INVALID_RAW_IDENTITY_FIELDS"}
    if record["authority"]!="CEE":
        return {"state":"UNRESOLVED","reason":"NON_AUTHORITATIVE_BINDING"}
    code=record["unit_raw"]
    unit_class=record["unit_class"]
    if unit_class=="SPECIAL_MODALITY":
        if record["binding_source_id"]!="cee_general_manual_2024":
            return {"state":"UNRESOLVED","reason":"SPECIAL_MODALITY_SOURCE_NOT_BOUND"}
        modality=SPECIAL_UNIT_MODALITIES.get(code)
        if modality is None:
            return {"state":"UNRESOLVED","reason":"UNKNOWN_SPECIAL_MODALITY_CODE"}
        if code=="73":
            if record.get("college_raw")!="01":
                return {"state":"UNRESOLVED","reason":"UNIT_73_COLLEGE_NOT_BOUND_TO_01"}
            if record.get("college_binding_source_id")!="cee_absentee_advance_regulation_2024":
                return {"state":"UNRESOLVED","reason":"UNIT_73_COLLEGE_SOURCE_NOT_BOUND"}
        return {"state":"SPECIAL_MODALITY","modality":modality,"identity":"SOURCE_BOUND_MODALITY_NOT_VOTER_OR_BALLOT_IDENTITY"}
    if unit_class=="REGULAR_PRECINCT_UNIT":
        if code in SPECIAL_UNIT_MODALITIES:
            return {"state":"UNRESOLVED","reason":"SPECIAL_CODE_CONFLICTS_WITH_REGULAR_CLASS"}
        if record["binding_source_id"]!="cee_authoritative_unit_roster":
            return {"state":"UNRESOLVED","reason":"REGULAR_UNIT_ID_NOT_IN_AUTHORITATIVE_ROSTER"}
        return {"state":"REGULAR_UNIT_CANDIDATE","identity":"SOURCE_EPOCH_SCOPED_NOT_CROSS_EPOCH_CANONICAL"}
    return {"state":"UNRESOLVED","reason":"UNIT_CLASS_NOT_AUTHORIZED"}

def isabela_032_denominator(source_reported_units, *, college_count=None, special_unit_inclusion=None):
    if source_reported_units != 22:
        raise ValueError("unexpected source-reported count; do not silently override CEE relation")
    if special_unit_inclusion not in (None,"INCLUDED","EXCLUDED"):
        raise ValueError("special unit inclusion must be explicit or unknown")
    return {"municipality_raw":"Isabela","precinct_raw":"032","reported_units":22,
            "special_unit_73":"SEPARATE_SPECIAL_MODALITY","special_unit_inclusion_in_22":special_unit_inclusion,
            "college_count":college_count,"complete_reporting_unit_denominator":None,
            "certification":"OPEN"}

def validate_special_acta_binding(acta, *, municipality_raw, precinct_raw, unit_raw, college_raw):
    required=("source_id","authority","source_epoch","signed","municipality_raw","precinct_raw","unit_raw","college_raw","modality")
    if not isinstance(acta,dict) or any(k not in acta for k in required):
        return {"eligible":False,"reason":"ACTA_MANIFEST_INCOMPLETE"}
    if not _valid_original_bytes(acta):
        return {"eligible":False,"reason":"ACTA_ORIGINAL_BYTES_OR_HASH_UNVERIFIED"}
    if acta["authority"]!="CEE" or acta["signed"] is not True:
        return {"eligible":False,"reason":"ACTA_NOT_AUTHENTICATED_CEE_RECORD"}
    expected=(municipality_raw,precinct_raw,unit_raw,college_raw,"VOTO_FACIL_ACCESO_EN_DOMICILIO")
    observed=tuple(acta[k] for k in ("municipality_raw","precinct_raw","unit_raw","college_raw","modality"))
    if observed!=expected:
        return {"eligible":False,"reason":"ACTA_SCOPE_IDENTITY_MISMATCH"}
    return {"eligible":True,"identity":"SOURCE_BOUND_ACTA_CANDIDATE","source_id":acta["source_id"],"sha256":acta["sha256"]}

def can_compare_result_pair(preliminary, certified):
    if not isinstance(preliminary,dict) or not isinstance(certified,dict):
        return {"eligible":False,"reason":"MISSING_RESULT_MANIFEST"}
    required=("source_id","authority","geographic_level","source_epoch","identity_state","ballot_type","signed")
    if any(k not in preliminary or k not in certified for k in required):
        return {"eligible":False,"reason":"RESULT_MANIFEST_INCOMPLETE"}
    if preliminary["authority"]!="CEE" or certified["authority"]!="CEE":
        return {"eligible":False,"reason":"NON_CEE_SOURCE"}
    if preliminary["signed"] is not True or certified["signed"] is not True:
        return {"eligible":False,"reason":"RESULT_CERTIFICATION_NOT_VERIFIED"}
    if preliminary["geographic_level"]!=certified["geographic_level"]:
        return {"eligible":False,"reason":"GEOGRAPHIC_GRAIN_MISMATCH"}
    if preliminary["geographic_level"]!="PRECINCT_UNIT_COLLEGE":
        return {"eligible":False,"reason":"RESULT_GRAIN_NOT_TARGET_UNIT_COLLEGE"}
    if preliminary["identity_state"]!="VERIFIED_BINDING" or certified["identity_state"]!="VERIFIED_BINDING":
        return {"eligible":False,"reason":"IDENTITY_NOT_VERIFIED"}
    if preliminary["ballot_type"]!=certified["ballot_type"]:
        return {"eligible":False,"reason":"BALLOT_TYPE_MISMATCH"}
    if preliminary["source_epoch"]==certified["source_epoch"]:
        return {"eligible":False,"reason":"DISTINCT_RESULT_EPOCHS_REQUIRED"}
    if not _valid_original_bytes(preliminary) or not _valid_original_bytes(certified):
        return {"eligible":False,"reason":"RESULT_ORIGINAL_BYTES_OR_HASH_UNVERIFIED"}
    return {"eligible":True,"identity":"SOURCE_BOUND_RESULT_PAIR_CANDIDATE","certification":"OPEN"}
