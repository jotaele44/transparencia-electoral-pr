"""Conservative legal eligibility screening; cannot generate, file or certify complaints."""
from rc6_security import VerifiedPrincipal,route
ALLOWED_STATUS={"OPEN","PROVISIONAL"}
def assess_route(*,domain,source_ids,legal_basis_verified,standing_reviewed,deadline_reviewed,reviewer,analyst):
    if not isinstance(analyst,VerifiedPrincipal) or not isinstance(reviewer,VerifiedPrincipal):raise PermissionError("verified roles required")
    if analyst.role!="analyst" or reviewer.role!="reviewer" or analyst.subject==reviewer.subject:raise PermissionError("independent review required")
    authority=route(domain)
    if not isinstance(source_ids,list) or not source_ids or any(not isinstance(s,str) or not s.strip() for s in source_ids) or len(source_ids)!=len(set(source_ids)):raise ValueError("unique source ids required")
    if any(type(x) is not bool for x in (legal_basis_verified,standing_reviewed,deadline_reviewed)):raise ValueError("boolean attestations required")
    approved=(authority in ("CEE","OCE") and legal_basis_verified and standing_reviewed and deadline_reviewed)
    return {"suggested_authority":authority,"eligible_for_draft_referral":approved,"submission_authorized":False,"filing_performed":False,"legal_determination":"REQUIRES_CASE_SPECIFIC_AUTHORIZED_REVIEW","source_ids":sorted(source_ids)}
