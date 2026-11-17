# RC17 META-2028 — Authoritative locator binding and offline snapshot hardening

## Baseline
Exact RC16 `79bbb2b9d10bf79d190c7328d16116d654e9ad44`, unchanged main expected `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`. No main merges or production writes.

## Source-binding improvement (2/2 discovered unresolved IDs)
- `cee_2028_rfp` now binds to the exact CEE March 2026 electronic-counting RFP URL (p.47), not to a generic statistics index. It expressly states 2028-11-07 general election and a June 6 primary, contradicting the first-Sunday-of-June rule.
- `ogp_electoral_code_2026_11_04` now binds to the exact OGP November 2026 amended Code PDF. Article 7.12 requires primary election on the first Sunday of June; for 2028 that is June 4. The revised OGP compilation includes a warning about a corrected October 2026 earlier version. Source versions must remain separate.
- The former count of 2 *missing internal source ID links* is now 0, based on nine discovered source entries. **This is not proof that every required legal source or election event has been discovered.**
Sources:
https://www.ceepur.org/subastas/docs/2026/RFP-Escrutinio/es/SOLICITUD-DE-PROPUESTAS-ESCRUTINIO-ELECTRONICO-2028-%28final%29.pdf
https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/58-2020.pdf?ID=7632

## 2028 calendar discovery
A 21-page candidate calendar marked Rev. 29 sept 2026 is exposed in readable search text from the PIP electoral commissioner's hosting site. This is not a verified CEE-domain original: screenshot attempts failed because of a tool size limit. We did not obtain bytes or hashes. Ten material event candidates (2027-04-02 to 2028-11-07) are indexed with precise source scope and legal uncertainties. This candidate is not an exhaustive denominator or a certified calendar. The original signed CEE-RS-26-010 remains the bounded authority for its mailing date scope.
Calendar candidate: https://www-static.comisionadoelectoralpip.com/wp-content/uploads/2026/10/Calendario-Electoral-Revisado-29-09-2026.pdf

The candidate calendar's 2028-09-23 transmission milestone and signed CEE 2028-09-20 deadline must not be treated as contradictory legal obligations for the same recipients without separately verifying the population, type of voting and statute.

## Implementation
`src/rc17_snapshots.py` requires caller-supplied nonempty exact bytes and ISO UTC evidence for deterministic SHA-256 manifests. It distinguishes BYTE_IDENTICAL / REISSUED_AT_SAME_URL_CANDIDATE / MOVED_AND_BYTE_CHANGED_CANDIDATE. No hash alone proves original document authority, logical identity, publication semantics or change legality. Absent search results never prove deletion and search false negatives remain open.

`src/rc17_units.py` records synthetic raw epoch-specific municipality, precinct, unit, college, ballot type and modality. It preserves leading zeros, separate epochs, duplicate rows and incompleteness; comparison yields sets without canonical equivalence. The authoritative real CEE roster remains missing.

Historical 2024 RC1–RC16 fixtures and safeguard logic were reused, not duplicated. The true historical original-to-final results comparison remains blocked by missing primary source bytes and identities.

## QA and release
Exact-head CI must pass; pinned TheHub validator only tests a synthetic package. Centinelas, MoneySweep and Spiderweb consumers, production identity provider, live source scheduler, WORM/off-site evidence archive, regulatory/legal review and independent QA remain OPEN. All public case outputs stay disabled. No actual source files downloaded in bulk. Certification is AUDIT_ONLY.
