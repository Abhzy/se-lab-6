"""
Lab 6 - Code (Line) Coverage tests for ski_resort_pass.py
Goal: execute every statement of the application at least once.

Run:
    coverage run -m pytest CodeCoverageTest_ski_resort_pass.py
    coverage report -m
"""
import pytest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


def make_group(duration="full_day", skiers=None, locker=False, active=True):
    """Helper that builds a booking group dictionary."""
    return {
        "is_active": active,
        "duration": duration,
        "includes_lodge_locker": locker,
        "skiers": skiers if skiers is not None else [],
    }


def skier(age=30, gear=False, blackout=False):
    """Helper that builds a skier dictionary."""
    return {"age": age, "gear_rental": gear, "blackout_override": blackout}


# ---------------------------------------------------------------- bookings
def test_single_adult_full_day():
    result = process_resort_bookings([make_group(skiers=[skier()])], 15.0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_invalid_input_raises_value_error():
    # line 3: raise ValueError
    with pytest.raises(ValueError):
        process_resort_bookings("not a list", 10.0)


def test_inactive_group_is_skipped():
    # line 10: continue for inactive group; line 60: ZERO_SALES
    result = process_resort_bookings([make_group(active=False, skiers=[skier()])], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_season_pass_adult():
    # line 16: season base rate
    result = process_resort_bookings([make_group("season", [skier()])], 10.0)
    assert result["total_revenue"] == 300.0
    assert result["status"] == "COMPLETED"


def test_half_day_pass_adult():
    # line 20: half_day base rate
    result = process_resort_bookings([make_group("half_day", [skier()])], 10.0)
    assert result["total_revenue"] == 50.0


def test_invalid_duration_is_rejected():
    # lines 22-23: unknown duration -> rejected + continue
    result = process_resort_bookings([make_group("weekly", [skier()])], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_skier_with_invalid_age_is_rejected():
    # lines 33-34: age <= 0
    result = process_resort_bookings([make_group(skiers=[skier(age=0)])], 10.0)
    assert result["status"] == "ZERO_SALES"


def test_blackout_override_full_day_gets_50_percent():
    # lines 37, 41: blackout on non half-day pass -> 50% of base rate
    result = process_resort_bookings([make_group(skiers=[skier(blackout=True)])], 10.0)
    assert result == {"total_revenue": 40.0, "status": "COMPLETED"}


def test_blackout_override_half_day_voids_group():
    # lines 39-40: half_day blackout resets group total and breaks
    group = make_group("half_day", [skier(), skier(blackout=True)])
    result = process_resort_bookings([group], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_child_discount():
    # line 43: age < 12 -> 60%
    result = process_resort_bookings([make_group(skiers=[skier(age=10)])], 10.0)
    assert result["total_revenue"] == 48.0


def test_senior_discount():
    # line 45: age >= 65 -> 70%
    result = process_resort_bookings([make_group(skiers=[skier(age=70)])], 10.0)
    assert result["total_revenue"] == 56.0


def test_gear_rental_and_lodge_locker():
    # line 50: gear rental +35; line 53: locker + facility fee
    group = make_group(skiers=[skier(gear=True)], locker=True)
    result = process_resort_bookings([group], 15.0)
    assert result["total_revenue"] == 130.0  # 80 + 35 + 15


def test_audit_review_when_more_than_four_rejections():
    # line 58: rejected_passes > 4
    skiers = [skier()] + [skier(age=0) for _ in range(5)]
    result = process_resort_bookings([make_group(skiers=skiers)], 10.0)
    assert result == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


# ------------------------------------------------------------- anemometer
def test_anemometer_no_data():
    # line 66
    assert check_chairlift_anemometer([]) == "NO_DATA"


def test_anemometer_suspend_lift():
    # lines 72-74: two consecutive gusts above 45
    assert check_chairlift_anemometer([[50, 60]]) == "SUSPEND_LIFT"


def test_anemometer_safe_operation():
    # line 76: calm reading resets streak; line 77: SAFE_OPERATION
    assert check_chairlift_anemometer([[10, 20, 30]]) == "SAFE_OPERATION"
