# RC4 — bounded evidence and software audit (2026-11-15)

## Sources and dates
- OGP Ley 58-2020 consolidated revision 2026-11-04, Article 7.12: primaries first Sunday in June.
- Calendar copy labeled CEE, rev 2026-09-29, hosted by PIP electoral commissioner: 2028-06-04. **Hosted copy, not frozen canonical CEE original.**
- 2028 equipment RFP states 2028-06-06: retain as **SOURCE_DATE_CONTRADICTION**. Legal-rule interpretation identifies 2028-06-04. Never delete the original source statement.
- CEE 2024 statistics index links official report. Full PDF exceeded reader limit, so sections, pages, reporting-unit inventory, candidate keys, and data coverage remain **UNKNOWN**.
- Approval CEE-AC-26-157 dated 2026-09-03 does **not** establish the 2024 report publication date.
- All original source payload SHA-256 remain null; URL access is not a byte-level freeze.

## Evidence disposition
Calendar date rule: VERIFIED_FOR_APPLICABLE_STATUTE.
Complete official 2028 calendar: OPEN.
2024 source-denominator and original/corrected pair: OPEN.
2024 real-vote reconciliation: NOT_ATTEMPTED.
Public election-integrity findings: NONE.
No election-specific canonical real data produced.

## QA and integration
- Tests cover empty and populated synthetic exports, exact source field presence, duplicate identities, missing vs zero, contradictions, version reissues, and escaped JSONL payloads.
- Pinned TheHub contract references in `contracts/hub_binding_rc4.json` are **shape inspection only**. TheHub consumer was NOT run or validated.
- Security assessment is **not independent**. No live CEE systems, authentication, voting infrastructure or voter-specific records were accessed.
- Product, discovery, live federation, merges, and production promotion are blocked.
- The only authorized changes are in `dev/evidence-pilot-rc1`. `main` must remain at `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0` for this change window.

## Next material gates
1. Resolve original CEE-hosted revised 2028 calendar provenance and signed amendments.
2. Inspect CEE statistical-report table of contents without bulk dataset ingestion.
3. Obtain authoritative reporting-unit/candidate identifiers and full denominator.
4. Identify genuinely paired original vs certified source versions.
5. Run full exact-HEAD tests, independent security/evidence QA, and pinned TheHub consumer test.
6. Require explicit release approval after complete machine-readable certification.

## Rollback
Development-only: reset the isolated development ref to preserved RC3 commit `cc911b3bb6a69cdeb4f24ed8e71c0c7008e443d9` **only after authorization and verification of the current ref**. Do not force-update `main`.
