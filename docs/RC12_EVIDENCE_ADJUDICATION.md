# RC12 — CEE source-version and calendar adjudication
RC11 baseline: `e6772035f625a6534f9f00306911c51a41a33769`.

## Verified positive result
CEE-RS-26-010 is a signed eight-page CEE presidential resolution dated 2026-09-08. Page 8 resolves the CEE-AC-26-149 disagreement **for the mailing schedule**: transmission begins as soon as ballots are available and no later than 2028-09-20, and ends no later than 2028-10-03. Preserve all proposals from the August disagreement as superseded historical statements. Do not claim a certified *entire* electoral calendar from this limited resolution.
Source: https://www.ceepur.org/resoluciones-de-comision/2026/CEE-RS-26-010.pdf

## Version recovery remains blocked
CEE's 2025-03 transparency report reports CEE-SIP-2025-006 marked completed 2025-03-28 for a statistical report concerning November 2024. This is proof of the request disposition only, not original payload delivery to this program.
Source: https://ww2.ceepur.org/sites/ComisionEE/es-pr/Ley141/informe-de-transparencia-202503.pdf

The report approved with amendments under CEE-AC-26-157 on 2026-09-03 is identified at https://ww2.ceepur.org/sites/ComisionEE/es-pr/Documents/INFORME-ESTADISTICO-ELECCIONES-GENERALES-2024.pdf . No bytes of this report were recovered using the current reading interfaces. An attempted selective download of the 2028 signed resolution PDF also failed. **No SHA-256 can be represented as verified.** The relationship between 2025 and 2026 versions is UNRESOLVED.

## Proof strategy
`src/rc12_evidence_gate.py` requires actual byte arrays for both versions and validates exact hashes; distinct hashes establish only byte difference, not logical record identity. No source pair, report structure, table counts, or electoral reporting-unit IDs have been certified. The full 2024 reporting-unit denominator remains unknown and not deducible from preliminary municipal excerpts.

## Software and release boundaries
The 2028 mailing simulation now rejects a 2028-09-27 start as late relative to the signed resolution and flags an end after 2028-10-03. Synthetic fixture passes are not historical election audits or findings about public compliance. No external complaints, voter-level data, WORM provisioning, identity provider, Hub production registration, main merge, deployment or official enforcement.
Independent legal, evidence, privacy and security QA remain OPEN.
