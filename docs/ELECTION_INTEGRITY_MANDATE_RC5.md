# RC5 Election integrity oversight mandate — development only

## Permitted scope
Monitor public election law, CEE/OCE orders, publication versions, precinct/reporting-unit boundaries, procurement evidence and official result certifications. Preserve original-vs-amended records and contradictory evidence. Flag discrepancies for source-grounded human investigation. Create **offline draft referral packets** only after evidence verification, independent review, and authorization.

## Prohibited operations
No voting system access, voter-level record acquisition, credentials, automated complaint submission, sanctions, altering official results, public accusations, live alerts, or autonomous findings of fraud. Scores rank **review priority**, never guilt, election validity, or systemic compromise. Enforcement is reserved to competent authorities.

## Legal jurisdiction routing — authority not assumed
- CEE: specifically electoral complaints and controversies, Electoral Code Law 58-2020, Article 3.5 (16 LPRA 4515); procedural eligibility, standing, sworn requirements and timelines must be reviewed before filing.
- OCE: campaign finance, Law 222-2011 as amended, Article 3.003A and related powers; disclosure, audits, contributions and expenditures. MoneySweep remains canonical financial producer.
- Courts/other agencies: referral channel only after case-specific jurisdictional review; no automated judicial assertion.
- These design notes are NOT a legal opinion or a determination of complainant standing.

## Case lifecycle
DETECTED -> TRIAGED -> EVIDENCE_VERIFIED -> HUMAN_REVIEWED -> REFERRAL_READY -> REFERRED -> OFFICIAL_DISPOSITION -> CLOSED.

A separate WITHDRAWN state permits withdrawal without destroying history. Hard gates forbid REFERRAL_READY without independently sourced evidence and HUMAN_REVIEWED. REFERRED requires a separate affirmative authorization and actual external receipt; this software performs no network or outbound submissions.

## Evidence rules
- Every finding is a review candidate, not a criminal accusation.
- Immutable events include event id, timestamp, actor, reason, source refs; audit-chain integrity via SHA-256 computed on canonical JSON.
- Required verified source hash must be 64 lowercase hexadecimal characters and cannot be fabricated from URL strings.
- Preserve contrary evidence and source-version conflicts.
- No voter identifiers, street addresses of private individuals, credentials or personal contacts in public case payloads. Invalid records fail closed.
- Stage synthetic fixtures only; no populated real case dockets, referrer identity, or deadlines are certified.

## Authority sources (metadata only; original bytes not frozen)
- https://bvirtualogp.pr.gov/ogp/Bvirtual/LeyesOrganicas/pdf/58-2020.pdf
- https://bvirtualogp.pr.gov/ogp/BVirtual/LeyesOrganicas/pdf/222-2011.pdf

## Release gates
No public allegations, external referral, live federation, deployment, or production until primary-source freeze, valid legal basis, independent QA, privacy assessment, provenance, rollback, consumer validation and explicit authorization all PASS.
