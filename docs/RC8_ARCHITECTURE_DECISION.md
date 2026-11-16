# RC8 architecture decision — DESIGN_FROZEN_FOR_ISOLATED_TESTS_ONLY

RC7 exact base: a70ea3de37312b340665e9daf578df2ec57a7718.
- Candidate production IDP: Microsoft Entra ID single-tenant OIDC/OAuth2 for API JWT validation. No tenant exists in the project configuration, no licensed account verified, and **selection is provisional**, not a binding procurement or configuration authorization. Official guidance requires signature via JWKS, issuer, audience, tenant and role checks; client role claims alone are not authorization.
- Candidate evidence archive: independently administered AWS S3 Object Lock **Compliance**, version-specific verification, locked retention and independent cross-account checkpoint attestations. No bucket/lock or KMS keys provisioned, and no retention policy approved. AWS notes simple deletion may insert a delete marker even when a locked historical version survives.
- RC8 implements a *local SQLite transactional nonce registry* to test restart persistence and duplicate-key races, not a distributed replay service or production IdP.
- RC8 external-checkpoint simulation writes receipts in a separate local directory; this is not external immutable anchoring or external independent witness.
- Never commit sensitive real complaints to this public repo. Use allowlisted synthetic fixtures only.
- CEE source originals have not been bound to the third-party 2024 CSV listings. Reported fields PREKEY, UNIKEY and COLKEY are source glossary claims, **not certified global IDs**. No source or election denominator closure.
- Continue with source metadata and read-only isolated tests. No real-data publication, production federation, merge, infrastructure mutation, or external referral.

Primary documentation:
https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
https://electionspuertorico.org/datos/2024/
