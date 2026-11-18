# RC21 — Legal source versions and calendar authority audit

RC20 baseline: `8775499abea221afdf73e76dbf831547d12faeff`; main frozen: `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`. Branch: `dev/rc21-legal-calendar-evidence`.

## Results
The official SUTRA Ley 39-2026 legislation and metadata record exists: https://sutra.oslpr.org/prontuarios/leyes-aprobadas/158328 . SUTRA enacted-file PDF and DOC links were identified but no original signed source bytes retrieved. Official law index: https://sutra.oslpr.org/prontuarios/leyes-aprobadas?page=5&per_page=50 . It states April 8, 2026 as effective date; earlier RC19 computed April 9. Preserve that disagreement until obtaining signed original and qualified legal date interpretation.

The OGP publishes distinct dated consolidated versions of Law 58-2020 (revisions May 7, June 11, November 4, 2026), with different URLs and release epochs. They are different source manifestations; differing dates do not establish payload inequality or any canonical legal equivalence. Their original bytes and SHA256 remain unavailable. The latest OGP compilation reflects the 50-day absentee APPLICATION deadline. CEE public guidance retains a 45-day reference; the UOCAVA 45-day BALLOT TRANSMISSION requirement has separate scope. The record does not establish actual administered CEE deadline or an affected elector.

CEE 2024 JAVAA historical regulation is available but cannot be promoted as a signed 2028 operative regulation. The 2028 signed calendar's full original on an authoritative CEE domain was not recovered. The PIP-hosted CEE-titled September 29, 2026 calendar is a candidate only. Neither complete event nor amendments denominators are closed. No new original PDF source bytes were downloaded or hashed.

## Implemented
`evidence/rc21_legal_calendar_manifest.json` records ten source manifestations and three distinct legal/source discrepancies. `src/rc21_legal_versions.py` separates source version epochs, preserves both effectivity dates and requires independent review before certifying calendar claims. Positive/negative regressions cover missing dates, duplicate events, false source identities, and historical 2024 JAVAA scope. RC19 read-only HTTP tests remain inherited; no live polling was performed.

## Outstanding
Original enacted Ley39 bytes, authoritative 2028 JAVAA rule, signed full calendar and amendments, complete source/event denominators, actual Centinelas/Spiderweb/MoneySweep producer runtime integration, isolated rollback, independent QA and formal release authorization. Status AUDIT_ONLY; production and main merge BLOCKED.
