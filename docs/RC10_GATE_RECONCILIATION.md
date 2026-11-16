# RC10 bounded evidence-proof gate

RC6 preserved: 4fcadb41ac1523cf2348e3889627f2e481744f08.
RC9 reused: faa24424aa9a61fe6d6bfbe139f9a826511e6e48.

The new RC10 proof module tests only synthetic source manifestations, exact byte SHA256, conservative source key intersections, duplicate/error conservation, and denominator uncertainty. It never certifies real source authority or CEE reporting-unit identity. Actual CEE byte hashes and original-to-certified pair remain missing.

The RC9 findings (Adjuntas 40/46 and Aguada 63/66) are partial source excerpts, not complete election coverage. The third-party CSV remains unbound to authoritative CEE originals. No real vote rows acquired.

Microsoft Entra ID is only a candidate OIDC provider; verify token issuer, audience, tenant, signing key and replay with trusted authority before deployment. AWS S3 Object Lock compliance is an unprovisioned candidate: protection is per object version and may be obscured by newer delete markers.

References:
https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
https://openid.net/specs/openid-connect-core-1_0.html
https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html

No production, federation activation, complaint submission, public allegation, or main merge permitted. Independent evidence, legal and security QA remain open. Rollback to RC9 only with explicit authorization.
