# RC18 — META-2028 legal publication and source monitoring audit

Baseline RC17 a5346b1668edddd5e5ddc71fb62e936cdcc39367; main b90b4e78f3e6cd66f5e78d508ad590a15e569eb0. Isolated RC18 branch only.

## Calendar recovery
Bounded official-source searches found the original CEE-AC-26-149 disagreement and signed CEE-RS-26-010, but did not locate an independently verified official CEE-domain full calendar. A September 29, 2026 calendar PDF exists on the PIP commissioner's site; without a signed binding and original source bytes, it remains a secondary-hosted candidate. A selective direct-download attempt for the signed CEE-RS-26-010 PDF failed. Zero original PDF SHA256s were verified. The full calendar/event denominator and amendment completeness are unknown.

## Current official information versus current law compilation
CEE official information page https://ww2.ceepur.org/Home/SolicituddeVoto presently says an absentee-vote application should be submitted no later than 45 days before the election and cites Art. 9.35(4). The OGP November 4, 2026 amended election code compilation https://bvirtualogp.pr.gov/ogp/Bvirtual/leyesreferencia/PDF/58-2020.pdf?ID=7632 says in Article 9.36(5) 50 days. Secondary LexJuris text for Act 39-2026 (March 10, 2026) also states the 50-day provision. This is a public source text conflict, not evidence of actual CEE policy implementation, electoral disenfranchisement, or deliberate deception. The official original Act 39, operative CEE JAVAA instructions and webpage publication history must be verified.

## Mailing scopes
CEE-RS-26-010 addresses advance ballot mailing, latest start September 20, 2028, and completion by October 3. The candidate revised calendar lists absentee ballot transfer for September 23. Distinct modality and population mean a direct normative contradiction is NOT yet established. The signed original, federal UOCAVA timetable, and full CEE binding calendar require legal review.

## Code and tests
src/rc18_publication.py is an offline read-only function collection. It accepts caller-supplied nonempty original bytes, exact HTTPS source URL, UTC capture time, controlled content-type, PDF signature and SHA-256. It compares byte-level revisions via RC17 functions but cannot claim source authority, semantic or legal alteration, or a real compliance failure. No network, file writes, automated alerts, voter records or public cases.

## Cross-repository interface inspection
evidence/rc18_cross_repo_manifest_audit.json records exact Git commits and federation.json Git blob SHA-1 from real Centinelas, MoneySweep and Spiderweb repositories. These are not SHA-256s. MoneySweep is declared non-production diagnostic and not ready for live Hub execution; the other repositories' readiness flags do not authorize new activation. No external consumer runtime was executed, and no production writes occurred.

## Certification
Original official 2028 calendar bytes, full event and electoral-unit denominators, real vote pairings, independent legal, security, evidence and privacy QA all remain OPEN. Production certification BLOCKED. All RC18 code and tests are development-only; CI success is software PASS only.
