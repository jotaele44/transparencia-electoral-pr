"""RC19: deterministic date calculations and modality-specific legal comparison.

This module computes candidate deadlines from cited inputs. It does not set
an election date, interpret individual eligibility, or make compliance findings.
"""
from datetime import date, timedelta

def _iso_date(value):
    if not isinstance(value, str):
        raise ValueError("ISO date required")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("invalid ISO date") from exc
    if parsed.isoformat() != value:
        raise ValueError("canonical YYYY-MM-DD required")
    return parsed

def days_before(election_date, days):
    election = _iso_date(election_date)
    if type(days) is not int or not 0 <= days <= 366:
        raise ValueError("days must be integer 0..366")
    return (election - timedelta(days=days)).isoformat()

def first_sunday_of_june(year):
    if type(year) is not int or not 1900 <= year <= 2200:
        raise ValueError("year outside supported range")
    first = date(year, 6, 1)
    return (first + timedelta(days=(6 - first.weekday()) % 7)).isoformat()

def build_2028_deadline_matrix():
    election = "2028-11-07"
    primary_statutory = first_sunday_of_june(2028)
    return {
        "general_election": {
            "date": election, "source": "CEE_2028_ELECTRONIC_COUNTING_RFP",
            "classification": "OFFICIAL_CEE_PROCUREMENT_DOCUMENT_DATE"
        },
        "local_primary": {
            "statutory_rule": "first Sunday of June in general-election year",
            "computed_date": primary_statutory,
            "source": "OGP_LAW_58_2020_REV_2026_11_04_ART_7_12",
            "classification": "COMPUTED_FROM_CURRENT_OFFICIAL_CODE"
        },
        "primary_date_conflict": {
            "cee_rfp_date": "2028-06-06",
            "statutory_computed_date": primary_statutory,
            "state": "UNRESOLVED_SOURCE_DATE_CONTRADICTION",
            "legal_violation_proven": False,
            "reason": "RFP is not the signed full electoral calendar; preserve both source statements"
        },
        "absentee_application": {
            "date": days_before(election, 50),
            "days_before": 50,
            "current_code_article": "9.36(5)",
            "scope": "general elections and primaries; special-election exception may permit shorter term",
            "source": "OGP_LAW_58_2020_REV_2026_11_04",
            "classification": "STATUTORY_DEADLINE_COMPUTED"
        },
        "advance_application": {
            "date": days_before(election, 50),
            "days_before": 50,
            "current_code_article": "9.39(5)",
            "scope": "general elections and primaries; special-election exception may permit shorter term",
            "source": "OGP_LAW_58_2020_REV_2026_11_04",
            "classification": "STATUTORY_DEADLINE_COMPUTED"
        },
        "uocava_transmission": {
            "date": days_before(election, 45),
            "days_before": 45,
            "current_code_article": "52_USC_20302(a)(8)(A)",
            "scope": "covered absent uniformed-services and overseas voters for federal-office elections, when valid request is received at least 45 days before election",
            "classification": "FEDERAL_BALLOT_TRANSMISSION_DEADLINE_NOT_APPLICATION_DEADLINE"
        },
        "cee_advance_mail_start": {
            "date": "2028-09-20",
            "operator": "start no later than",
            "source": "CEE_RS_26_010",
            "classification": "SIGNED_CEE_RESOLUTION_DEADLINE"
        },
        "cee_advance_mail_completion": {
            "date": "2028-10-03",
            "operator": "complete no later than",
            "source": "CEE_RS_26_010",
            "classification": "SIGNED_CEE_RESOLUTION_DEADLINE"
        },
        "javaa_processing": {
            "date": days_before(election, 30),
            "operator": "must begin no later than 30 calendar days before election",
            "source": "OGP_LAW_58_2020_REV_2026_11_04_ART_9_42(3)",
            "classification": "STATUTORY_LATEST_START_COMPUTED"
        }
    }

def compare_cee_absentee_page_to_current_code():
    """Separate stale public instructions from UOCAVA ballot-transmission rules."""
    return {
        "cee_page_claim": {"days": 45, "article": "9.35(4)", "modality": "ABSENTEE_APPLICATION"},
        "current_code": {"days": 50, "article": "9.36(5)", "modality": "ABSENTEE_APPLICATION"},
        "cee_advance_page_claim": {"days": 50, "article": "9.38(4)", "modality": "ADVANCE_APPLICATION"},
        "current_advance_code": {"days": 50, "article": "9.39(5)", "modality": "ADVANCE_APPLICATION"},
        "uocava_rule": {"days": 45, "article": "52_USC_20302(a)(8)(A)", "modality": "COVERED_FEDERAL_BALLOT_TRANSMISSION"},
        "findings": {
            "absentee_page_text_mismatch": True,
            "absentee_page_article_reference_stale": True,
            "advance_page_article_reference_stale": True,
            "uocava_45_day_rule_is_not_the_general_absentee_application_deadline": True,
            "actual_cee_administered_deadline": None,
            "affected_voters": None,
            "statutory_violation_proven": False,
            "classification": "CEE_PUBLIC_GUIDANCE_REQUIRES_CORRECTION_OR_AUTHORITATIVE_EXPLANATION"
        }
    }

def compare_mail_timeline():
    """Keep advance-vote mailing and UOCAVA transmission in separate legal lanes."""
    return {
        "advance_vote_by_mail_start_no_later_than": "2028-09-20",
        "uocava_covered_ballot_transmission_no_later_than": "2028-09-23",
        "advance_vote_by_mail_completion_no_later_than": "2028-10-03",
        "same_modality": False,
        "same_legal_population": False,
        "direct_contradiction_established": False,
        "classification": "DISTINCT_DUTIES_AND_POPULATIONS"
    }
