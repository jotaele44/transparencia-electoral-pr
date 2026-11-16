# RC11 CEE source recovery — bounded findings

## Preserved baseline
RC10 exact head: `d343a39349de85a0d3c4e0aba5a00c65e65774c8`. RC6 and main baselines remain recorded in `evidence/rc11_source_manifest.json`. RC11 is isolated from main.

## Major primary-source discovery
CEE-AC-26-157 is dated 2026-09-03. Its signed/sealed one-page agreement records unanimous approval, with amendments, of the 2024 General Election Statistical Report and gives the exact CEE-hosted PDF URL. The PDF is identified but not byte-acquired; web reader rejected the 33,580,272-byte response for exceeding its 32 MB extraction limit. This byte count is only the reader's error metadata, not a verified file-size statement. SHA-256 remains null.

The CEE March 2025 transparency report lists CEE-SIP-2025-006 (Informe Estadístico Elecciones Noviembre 2024) as completed 2025-03-28. This is a distinct prior delivery event. It must not be assumed byte-identical or logically identical to the report approved with amendments in September 2026. Recover both exact manifestations and compare.

## Reporting-unit namespace
The 2024 CEE procedural manual and CEE-AC-25-013 use municipality/precinct/unit/college fields for official administrative records. CEE-AC-25-038 approves a manual for updates to the Electoral Units Program and associated transactions. These establish the official locator vocabulary, not stable cross-election IDs. PREKEY/UNIKEY/COLKEY are still third-party column descriptions and remain CANDIDATE_NOT_IDENTITY.

## Isabela 032 / Unit 73 documented matter
CEE-AC-25-005 (2025-01-29) records a PPD petition concerning alleged ballots with one/no initials and requests correction of summary acts for Isabela 032, Unit 73. It includes an attached sworn statement and incident forms. The Commission denied the petition No Ha Lugar. The affidavit's claim of more than 100 ballots and the 930-elector size context for the accessible-home unit are different quantities. Neither is a verified number of uncounted votes. The affidavit says the issue was referred on 2024-12-06; the resolution says it was not elevated to the plenary/President. Preserve this procedural contradiction. Do not label it fraud or a proven vote discrepancy.

## Acquisition limitations
The 2024 statistical report itself has not been downloaded or hashed. No official full reporting-unit inventory has been acquired. No 2024 preliminary/final row pairs have been authenticated. No real vote comparisons performed. No personal voter data acquired. No bulk downloads.

## Required next tests
1. Recover 2025 CEE-SIP-2025-006 delivered payload and the 2026 CEE-AC-26-157 approved report separately.
2. Hash original bytes; record exact retrieval UTC, source URL, page count, file size, HTTP headers, PDF metadata, and source dates.
3. Extract report structure and complete denominator without inferring from 256 pages or 100% language.
4. Bind precinct/unit/college keys across source epochs only with authoritative mapping evidence.
5. Keep special voting modalities separate; reconcile ballot type, contest and unit scope.
6. Reconcile Isabela 032 Unit 73 from actual official actas, tally sheets and certified returns before any numerical conclusion.
7. Independent legal, privacy, evidence and security QA.

## Release
AUDIT_ONLY. No allegations, referrals, live Hub, production writes, main merge or certification authorized.
