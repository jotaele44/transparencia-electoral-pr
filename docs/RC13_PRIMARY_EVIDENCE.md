# RC13 — primary-source manifestation and cross-epoch identity gates

## Scope and official discovery
CEE's March 2025 information-access report has a single identified row, CEE-SIP-2025-006, "Informe Estadístico Elecciones Noviembre 2024", **Completado 3/28/2025**. It was visually checked on the report's first page. The completion row neither identifies the delivered PDF nor proves the delivered content or its date of original publication.

The CEE statistics index contains a separate official link labelled Elecciones 2024, and CEE-AC-26-157 records 2026-09-03 approval of the 2024 statistical report *with amendments*. Neither original report byte stream was recovered during this attempt; the targeted CEE transparency PDF download also failed. Therefore a PDF URL, web rendering, page image or information-access completion is never promoted to a frozen source manifestation. Original-byte SHA-256 remains null.

CEE official index references:
- https://ww2.ceepur.org/Home/Estadisticas
- https://ww2.ceepur.org/sites/ComisionEE/es-pr/Ley141/informe-de-transparencia-202503.pdf
- https://www.ceepur.org/acuerdos-de-comision/docs/2026/CEE-AC-26-157.pdf
- https://ww2.ceepur.org/sites/ComisionEE/es-pr/Documents/INFORME-ESTADISTICO-ELECCIONES-GENERALES-2024.pdf

## Identity invariants
- Require original bytes, exact SHA-256 and distinct epoch before even considering version comparison.
- Equal hashes establish BYTE identity only; a supplied crosswalk file remains CANDIDATE_NOT_IDENTITY until authoritative content and legal scope undergo independent adjudication.
- Raw tuple: source_epoch, municipality_raw, precinct_raw, unit_raw, college_raw, ballot_type. No spelling normalization, leading-zero removal, name-only equivalence, or 2024 cross-epoch row merging.
- Separate special modalities (72/73/74/76/77) and ballot types; mixed/invalid/duplicate rows remain unresolved with count closure.
- No real vote totals, official unit denominator, certified PREKEY/UNIKEY/COLKEY equivalence, or Isabela 032 Unit 73 ballot-acta pairing is asserted.

## Existing 2028 resolution
Preserve signed CEE-RS-26-010, 2026-09-08: mailing begins when ballots available no later than September 20, 2028, and completes no later than October 3, 2028. The agreement CEE-AC-26-149's earlier proposals remain historical; the rule is restricted to mailing dates and does not certify the entire 2028 calendar.

## Audit and security
This is test-only, on an isolated branch. TheHub integration uses pinned consumer b7a60e613fecb36448c719651625892b2bded565. Authentication (IdP), independent WORM object retention, live monitoring, electoral legal assessments, and case/publication release have not been implemented or certified.

No bulk datasets downloaded, no production resources modified, no election claims or referrals issued.
