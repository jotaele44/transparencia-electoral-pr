"""RC26: proposed Hub municipality-only administrative location contract.

This is a *candidate* compatible schema, applied only to a disposable copy.
It does not mutate pinned upstream Hub or Centinelas schemas. Municipality
presence never implies WGS84 geometry or canonical geographic identity.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json

def candidate_observation_schema(official_schema):
    if not isinstance(official_schema,dict):raise ValueError("actual pinned schema required")
    location=official_schema.get("properties",{}).get("location")
    if not isinstance(location,dict) or location.get("required")!=["lat","lon"]:
        raise ValueError("pinned Hub location schema drift, fail closed")
    props=location.get("properties")
    if not isinstance(props,dict) or not {"lat","lon","municipality"}<=set(props):
        raise ValueError("location properties unexpectedly changed")
    proposal=deepcopy(official_schema)
    new=proposal["properties"]["location"]
    del new["required"]
    new["oneOf"]=[
      {"required":["lat","lon"]},
      {"required":["municipality"],"not":{"anyOf":[{"required":["lat"]},{"required":["lon"]}]}}
    ]
    # Both branches preserve the original primitive type/range contracts;
    # malformed municipality and half-point combinations are rejected.
    new["minProperties"]=1
    return proposal

def candidate_receipt(official_schema,proposal):
    encode=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return {"official_schema_sha256":sha256(encode(official_schema)).hexdigest(),
            "candidate_schema_sha256":sha256(encode(proposal)).hexdigest(),
            "source_schema_modified":False,"producer_schema_modified":False,
            "admin_location_preserved":True,"geometric_point_synthesized":False,
            "legal_identity_proven":False,"production_change_authorized":False,
            "state":"SCHEMA_PROPOSAL_NOT_DEPLOYED"}
