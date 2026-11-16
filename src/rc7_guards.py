"""RC7 pure, synthetic-only authorization and external checkpoint verification."""
import hashlib,hmac,json,re
from rc6_security import canonical,VerifiedPrincipal
SHA=re.compile(r"^[a-f0-9]{64}$")
ACTIONS={"triage":"analyst","review":"reviewer","approve_draft":"release_officer"}
def authorize(principal,action,*,case_id,now,used_nonces,nonce,issuer="synthetic-rc6-idp"):
    if action not in ACTIONS:raise PermissionError("unsupported action")
    if not isinstance(principal,VerifiedPrincipal):raise PermissionError("no verified principal")
    if principal.issuer!=issuer or principal.role!=ACTIONS[action]:raise PermissionError("role/issuer denied")
    if type(now) is not int or principal.expires_at<=now:raise PermissionError("expired")
    if not isinstance(case_id,str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}",case_id):raise ValueError("case identity")
    if not isinstance(nonce,str) or not re.fullmatch(r"[A-Za-z0-9_-]{16,128}",nonce):raise ValueError("nonce")
    if not isinstance(used_nonces,set):raise TypeError("nonce registry")
    key=(principal.issuer,principal.subject,case_id,nonce)
    if key in used_nonces:raise PermissionError("replay")
    used_nonces.add(key)
    return {"action":action,"subject":principal.subject,"case_id":case_id,"authentication":"SYNTHETIC_FIXTURE_ONLY"}
def build_checkpoint(*,snapshot_sha256,chain_tip,sequence,previous_checkpoint_sha256=None):
    if not isinstance(snapshot_sha256,str) or not SHA.fullmatch(snapshot_sha256):raise ValueError("snapshot hash")
    if not isinstance(chain_tip,str) or not SHA.fullmatch(chain_tip):raise ValueError("chain tip")
    if type(sequence) is not int or sequence<1:raise ValueError("sequence")
    if previous_checkpoint_sha256 is not None and (not isinstance(previous_checkpoint_sha256,str) or not SHA.fullmatch(previous_checkpoint_sha256)):raise ValueError("previous checkpoint")
    o={"snapshot_sha256":snapshot_sha256,"chain_tip":chain_tip,"sequence":sequence,"previous_checkpoint_sha256":previous_checkpoint_sha256}
    o["checkpoint_sha256"]=hashlib.sha256(canonical(o)).hexdigest()
    return o
def verify_checkpoint(candidate,*,trusted_external_digest,minimum_sequence=1):
    if not isinstance(candidate,dict) or not isinstance(trusted_external_digest,str) or not SHA.fullmatch(trusted_external_digest):return False
    try:
        if type(candidate.get("sequence")) is not int or candidate["sequence"]<minimum_sequence:return False
        unsigned={k:v for k,v in candidate.items() if k!="checkpoint_sha256"}
        digest=hashlib.sha256(canonical(unsigned)).hexdigest()
        return hmac.compare_digest(digest,candidate.get("checkpoint_sha256","")) and hmac.compare_digest(digest,trusted_external_digest)
    except (TypeError,ValueError):return False
