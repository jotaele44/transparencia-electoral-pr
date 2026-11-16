# RC14 — CEE source recovery and Isabela Unit 73 scope adjudication

## 1. Exact baseline and release boundary
RC13 exact HEAD preserved: `cdf6079ff3b5e22b5e60eb606dd0b37cb099374a`.
Main baseline: `b90b4e78f3e6cd66f5e78d508ad590a15e569eb0`.
All RC14 work is isolated on `dev/rc14-cee-report-acquisition`. No production, federation, external referral or main-branch change.

## 2. 2025 and 2026 statistical report manifestations
The March 2025 CEE transparency report lists CEE-SIP-2025-006, "Informe Estadístico Elecciones Noviembre 2024", as completed 2025-03-28. The row does not identify the delivered payload, a filename, a delivery URL, or a hash.
Source: https://ww2.ceepur.org/sites/ComisionEE/es-pr/Ley141/informe-de-transparencia-202503.pdf

The official CEE statistics index explicitly links "Elecciones 2024" to:
https://ww2.ceepur.org/sites/ComisionEE/es-pr/Documents/INFORME-ESTADISTICO-ELECCIONES-GENERALES-2024.pdf
The web reader rejected this specific PDF as too large to fetch (reader-reported content length 33,580,272 bytes). That value is tool error metadata, not a source-certified file size. No original bytes, PDF metadata, page count, table headers, or SHA-256 were obtained.
Index: https://ww2.ceepur.org/Home/Estadisticas
Approval with amendments: CEE-AC-26-157, 2026-09-03:
https://www.ceepur.org/acuerdos-de-comision/docs/2026/CEE-AC-26-157.pdf

**Version relationship remains UNRESOLVED.** The request-completion date is not a source version date and does not establish payload identity.

## 3. Isabela Precinct 032 and Unit 73
CEE Office of Geoelectoral Planning's precinct relation, revised 2024-10-05, lists:
- Municipality: Isabela
- Precinct: 032
- Senatorial district: 4
- Representative district: 16
- Units: 22

Source: https://ww2.ceepur.org/sites/comisionee/es-pr/planificacion/documents/relacionprecintos.pdf

The table gives a count but does not list unit IDs or colleges and does not state whether special modalities are included. Do not convert 22 into the full reporting-unit denominator or assume Unit 73 is an extra twenty-third regular unit.

CEE's 2024 General Election and Canvass Manual, approved 2024-10-11, states in Section 5.1 that certified college acts for special modalities 72, 73, 74, 76 and 77 are aggregated into the corresponding precinct results. It identifies Unit 73 as Voto Fácil Acceso en Domicilio. The 2024 absentee/advance-voting regulation identifies the nomenclature as Unit 73, College 01.
Manual: https://ww2.ceepur.org/sites/ComisionEE/es-pr/Secretaria/Manuales/Manual%20de%20Procedimientos%20para%20las%20Elecciones%20Generales%20y%20Escrutinio%202024.pdf
Regulation: https://ww2.ceepur.org/sites/ComisionEE/es-pr/Secretaria/Documents/REGLAMENTO%20DE%20VOTO%20AUSENTE%20Y%20VOTO%20ADELANTADO%20DE%20PRIMARIAS%20Y%20ELECCIONES%20GENERALES%202024.pdf

This is a source-bound modality classification, not proof of any ballot quantity or outcome. The dedicated 2024 domicile-vote procedures manual and Isabela 032 Unit 73 original actas have not been recovered.

## 4. Separate Lares comparator — do not merge
CEE-RS-24-038, signed 2024-12-21, addresses Lares Precinct 053 Unit 73 (domicile vote), not Isabela. It reports a voter list of 1,714 and 1,515 voters, and enumerates ballot initial categories by ballot type. Each reported three-way ballot sum has been checked arithmetically in a dedicated test. The resolution applies a two-initial minimum under its cited 2024 domicile manual.
Source: https://ww2.ceepur.org/sites/ComisionEE/es-pr/ResolucionesSecretaria/PAPELETAS%20CON%20SITUACIONES%20SOBRE%20LAS%20INICIALES%20-%20LARES%20053%20UNIDAD%2073%20%28DESACUERDO%20CEE-AC-24-177%29.pdf

Lares and Isabela share a special modality and similar ballot-initial issue category. They are distinct precinct cases. No Lares counts, facts, or disposition are transferred to Isabela.

## 5. Isabela primary records required
The target is Isabela / 032 / special Unit 73 / College 01. Required source records:
1. Acta de Votación del Colegio de Fácil Acceso en el Domicilio.
2. Acta de Incidencias of that domicile-vote college.
3. Acta de Cuadre de Papeletas / ballot inventory.
4. Domicile route list and aggregate route summary, with voter-level personal information protected.
5. Certified college act(s) for Unit 73 and the matching precinct aggregation.
6. Matching preliminary election-night and certified results for the same geographic grain, modality and ballot type.
7. Relevant CEE local/precinct actas and any later administrative or judicial disposition.

CEE-AC-25-005 is an administrative disagreement resolution, not a substitute for those original actas. Its twelve-page visual review is recorded in the RC11 evidence ledger; its original bytes and hash remain unverified.

## 6. Results portal and available partials
The CEE event index links to the official 2024 results portal, but the portal fetch failed with an unknown status. A CEE 256-page mayoral night-of-election PDF is available at municipality grain, generated 2024-11-06 06:00:11. It is not a Unit 73 or college-level result. The final House certification dated 2024-12-31 says 100% of colleges reported but the numeric denominator is not exposed in the inspected metadata. Neither record closes the Isabela Unit 73 comparison.

## 7. Certification
Original statistical report payloads acquired: 0. Verified original hashes: 0. Isabela Unit 73 original actas: 0. Authenticated preliminary/certified pairs: 0. Real vote rows reconciled: 0. Complete 2024 reporting-unit denominator: UNKNOWN. Independent evidence/legal/security QA: OPEN. Status: AUDIT_ONLY.
