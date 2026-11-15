# RC6 threat model — development only

Baseline: `bf235988df3401424aee374a013fc18b631c9d74`. All changes isolated to `dev/rc6-security-integrity`.

## Trust boundaries
1. Public CEE/OCE information is untrusted input. It does not confer legal authority, ownership or verified identity.
2. A role string submitted by a client is NOT authenticated. RC6 supports only an offline synthetic HMAC verification *fixture*, not a live identity provider. Secrets must be injected by a trusted process, never in source files or logs. Authentication in production remains BLOCKED until IdP integration, verified issuer/audience/expiry, protected keys, replay resistance, key rotation, and independent testing.
3. Application-controlled event hashes detect accidental/tampered fields but do NOT prove immutable evidence storage. A privileged actor can rewrite the whole file and recompute hashes. WORM/object-lock storage, anchored signed checkpoints, independent retention and restore testing remain OPEN.
4. Data minimization: only allowlisted structured fields are admitted to public case envelopes; free text and source bytes are withheld. Names, contacts, IP addresses, voter IDs, location and document contents must never enter a public export.
5. Legal routing is conservative: the case domain suggests CEE/OCE, never proves jurisdiction, standing, eligibility, filing deadlines or wrongdoing. No external submission.
6. Source identity: only verified content hashes from actual source bytes count. A valid 64-character synthetic fixture hash is NOT proof of source acquisition.
7. Public findings, external referrals, production deployment, GitHub main merges and TheHub registration are blocked.

## Formal limits
- `src/rc6_security.py`: offline synthetic-only role and public-case envelope checks.
- `src/rc6_evidence_store.py`: append-only *local demo* with O_EXCL writes, fsync, event chaining, but no independent immutable backing.
- Existing RC5 case workflow is NOT production-safe and is intentionally not promoted.
- TheHub runtime validation is OPEN. Schema shape compatibility is not equivalent to consumer integration.
- Sensitive case files must never be committed to this public repository.

## QA requirements
Positive and negative tests: forged signatures, expired/audience mismatch, replay logic, same reviewer, role mismatch, invalid cases, private fields, free text, hash collisions/duplication, truncated chain, missing source, rollback and deterministic output. An independent security assessment and privacy impact assessment are prerequisites to actual deployment.
