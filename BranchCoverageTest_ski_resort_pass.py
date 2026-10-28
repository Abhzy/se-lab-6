"""
Lab 6 - Branch Coverage tests for ski_resort_pass.py
Goal: make every decision (if / elif / else / loop) evaluate to BOTH True and
False, and add boundary / edge cases around each decision.

Run:
    coverage run --branch -m pytest BranchCoverageTest_ski_resort_pass.py
    coverage report -m
"""
import pytest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


def make_group(duration="full_day", skiers=None, locker=False, active=True):
    return {
        "is_active": active,
        "duration": duration,
        "includes_lodge_locker": locker,
        "skiers": skiers if skiers is not None else [],
    }


def skier(age=30, gear=False, blackout=False):
    return {"age": age, "gear_rental": gear, "blackout_override": blackout}


# =====================================================================
# Line 2: if not isinstance(groups, list) or facility_fee < 0
# =====================================================================
@pytest.mark.parametrize("bad_groups", ["text", None, {"a": 1}, 42])
def test_groups_not_a_list_raises(bad_groups):
    # first operand True
    with pytest.raises(ValueError):
        process_resort_bookings(bad_groups, 10.0)


def test_negative_facility_fee_raises():
    # first operand False, second operand True
    with pytest.raises(ValueError):
        process_resort_bookings([make_group(skiers=[skier()])], -0.01)


def test_zero_facility_fee_is_valid():
    # boundary: fee == 0 is NOT negative -> condition False
    result = process_resort_bookings([make_group(skiers=[skier()], locker=True)], 0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_empty_group_list_is_zero_sales():
    # outer for-loop never executes
    assert process_resort_bookings([], 10.0) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


# =====================================================================
# Line 9: if not group.get("is_active", False)
# =====================================================================
def test_inactive_group_explicit_false():
    result = process_resort_bookings([make_group(active=False, skiers=[skier()])], 10.0)
    assert result["status"] == "ZERO_SALES"


def test_group_missing_is_active_defaults_to_inactive():
    result = process_resort_bookings([{"duration": "full_day", "skiers": [skier()]}], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_inactive_group_does_not_affect_active_group():
    groups = [make_group(active=False, skiers=[skier()]), make_group(skiers=[skier()])]
    assert process_resort_bookings(groups, 10.0)["total_revenue"] == 80.0


# =====================================================================
# Lines 15-23: duration if / elif / elif / else
# =====================================================================
@pytest.mark.parametrize("duration, expected", [
    ("season", 300.0),
    ("full_day", 80.0),
    ("half_day", 50.0),
])
def test_each_valid_duration(duration, expected):
    result = process_resort_bookings([make_group(duration, [skier()])], 10.0)
    assert result == {"total_revenue": expected, "status": "COMPLETED"}


def test_missing_duration_defaults_to_full_day():
    group = {"is_active": True, "skiers": [skier()]}
    assert process_resort_bookings([group], 10.0)["total_revenue"] == 80.0


@pytest.mark.parametrize("bad_duration", ["weekly", "", None, "SEASON"])
def test_invalid_duration_is_rejected(bad_duration):
    result = process_resort_bookings([make_group(bad_duration, [skier()])], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


# =====================================================================
# Line 27: for skier in skiers  (empty / non-empty / missing key)
# =====================================================================
def test_active_group_with_no_skiers():
    assert process_resort_bookings([make_group(skiers=[])], 10.0)["status"] == "ZERO_SALES"


def test_active_group_missing_skiers_key():
    group = {"is_active": True, "duration": "full_day"}
    assert process_resort_bookings([group], 10.0)["status"] == "ZERO_SALES"


def test_multiple_skiers_in_one_group():
    result = process_resort_bookings([make_group(skiers=[skier(), skier(age=10)])], 10.0)
    assert result["total_revenue"] == 128.0  # 80 + 48


# =====================================================================
# Line 32: if age <= 0
# =====================================================================
@pytest.mark.parametrize("age", [0, -1, -50])
def test_non_positive_age_rejected(age):
    result = process_resort_bookings([make_group(skiers=[skier(age=age)])], 10.0)
    assert result["status"] == "ZERO_SALES"


def test_age_one_is_valid_boundary():
    # boundary: age == 1 -> condition False, child rate
    result = process_resort_bookings([make_group(skiers=[skier(age=1)])], 10.0)
    assert result["total_revenue"] == 48.0


def test_missing_age_defaults_to_zero_and_is_rejected():
    result = process_resort_bookings([make_group(skiers=[{}])], 10.0)
    assert result["status"] == "ZERO_SALES"


def test_gear_rental_not_charged_for_rejected_skier():
    # 'continue' on line 34 skips the gear-rental check
    result = process_resort_bookings([make_group(skiers=[skier(age=0, gear=True)])], 10.0)
    assert result["total_revenue"] == 0.0


# =====================================================================
# Lines 36-47: blackout / child / senior / adult
# =====================================================================
def test_blackout_full_day():
    result = process_resort_bookings([make_group("full_day", [skier(blackout=True)])], 10.0)
    assert result == {"total_revenue": 40.0, "status": "COMPLETED"}


def test_blackout_season():
    result = process_resort_bookings([make_group("season", [skier(blackout=True)])], 10.0)
    assert result == {"total_revenue": 150.0, "status": "COMPLETED"}


def test_blackout_half_day_first_skier_breaks_loop():
    group = make_group("half_day", [skier(blackout=True), skier()])
    assert process_resort_bookings([group], 10.0)["status"] == "ZERO_SALES"


def test_blackout_half_day_discards_earlier_skiers():
    group = make_group("half_day", [skier(gear=True), skier(blackout=True), skier()])
    assert process_resort_bookings([group], 10.0)["total_revenue"] == 0.0


def test_blackout_half_day_locker_fee_still_added():
    # break leaves the loop, but the locker fee on line 53 is still charged
    group = make_group("half_day", [skier(blackout=True)], locker=True)
    result = process_resort_bookings([group], 15.0)
    assert result == {"total_revenue": 15.0, "status": "COMPLETED"}


def test_blackout_takes_priority_over_child_and_senior_rates():
    child = process_resort_bookings([make_group(skiers=[skier(age=5, blackout=True)])], 10.0)
    senior = process_resort_bookings([make_group(skiers=[skier(age=80, blackout=True)])], 10.0)
    assert child["total_revenue"] == 40.0
    assert senior["total_revenue"] == 40.0


@pytest.mark.parametrize("age, expected", [
    (11, 48.0),   # child (< 12)
    (12, 80.0),   # boundary: first adult age
    (30, 80.0),   # adult
    (64, 80.0),   # boundary: last adult age
    (65, 56.0),   # boundary: first senior age
    (90, 56.0),   # senior
])
def test_age_boundaries_full_day(age, expected):
    result = process_resort_bookings([make_group(skiers=[skier(age=age)])], 10.0)
    assert result["total_revenue"] == expected


# =====================================================================
# Line 49: gear rental   /   Line 52: lodge locker
# =====================================================================
def test_gear_rental_true_and_false():
    with_gear = process_resort_bookings([make_group(skiers=[skier(gear=True)])], 10.0)
    without = process_resort_bookings([make_group(skiers=[skier(gear=False)])], 10.0)
    assert with_gear["total_revenue"] == 115.0
    assert without["total_revenue"] == 80.0


def test_gear_rental_applies_per_skier():
    group = make_group(skiers=[skier(gear=True), skier(gear=True), skier()])
    assert process_resort_bookings([group], 10.0)["total_revenue"] == 310.0  # 115+115+80


def test_locker_true_and_false():
    with_locker = process_resort_bookings([make_group(skiers=[skier()], locker=True)], 15.0)
    without = process_resort_bookings([make_group(skiers=[skier()], locker=False)], 15.0)
    assert with_locker["total_revenue"] == 95.0
    assert without["total_revenue"] == 80.0


def test_locker_fee_charged_once_per_group_not_per_skier():
    group = make_group(skiers=[skier(), skier()], locker=True)
    assert process_resort_bookings([group], 15.0)["total_revenue"] == 175.0  # 160 + 15


def test_locker_missing_key_defaults_false():
    group = {"is_active": True, "duration": "full_day", "skiers": [skier()]}
    assert process_resort_bookings([group], 15.0)["total_revenue"] == 80.0


def test_multiple_groups_accumulate():
    groups = [
        make_group("full_day", [skier(gear=True)]),   # 115
        make_group(active=False, skiers=[skier()]),   # skipped
        make_group("half_day", [skier(age=10)]),      # 30
    ]
    assert process_resort_bookings(groups, 10.0) == {"total_revenue": 145.0, "status": "COMPLETED"}


# =====================================================================
# Lines 57-61: final status decisions
# =====================================================================
def test_exactly_four_rejections_is_not_audit():
    # boundary: rejected_passes == 4 -> not > 4
    skiers = [skier()] + [skier(age=0) for _ in range(4)]
    result = process_resort_bookings([make_group(skiers=skiers)], 10.0)
    assert result == {"total_revenue": 80.0, "status": "COMPLETED"}


def test_five_rejections_triggers_audit():
    # boundary: rejected_passes == 5 -> > 4
    skiers = [skier()] + [skier(age=0) for _ in range(5)]
    result = process_resort_bookings([make_group(skiers=skiers)], 10.0)
    assert result == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


def test_audit_takes_priority_over_zero_sales():
    groups = [make_group("weekly", [skier()]) for _ in range(5)]
    assert process_resort_bookings(groups, 10.0) == {"total_revenue": 0.0, "status": "AUDIT_REVIEW"}


def test_rejections_accumulate_across_groups():
    groups = [make_group("weekly", [skier()]) for _ in range(4)]
    groups.append(make_group(skiers=[skier(blackout=True)]))  # 5th rejection, pays 40
    assert process_resort_bookings(groups, 10.0) == {"total_revenue": 40.0, "status": "AUDIT_REVIEW"}


def test_zero_sales_status():
    assert process_resort_bookings([make_group(skiers=[])], 10.0)["status"] == "ZERO_SALES"


def test_completed_status_and_rounding():
    result = process_resort_bookings([make_group(skiers=[skier()], locker=True)], 0.333)
    assert result == {"total_revenue": 80.33, "status": "COMPLETED"}


# =====================================================================
# check_chairlift_anemometer
# =====================================================================
@pytest.mark.parametrize("empty", [[], None])
def test_anemometer_no_data(empty):
    assert check_chairlift_anemometer(empty) == "NO_DATA"


def test_anemometer_two_consecutive_gusts_suspend():
    assert check_chairlift_anemometer([[46, 46]]) == "SUSPEND_LIFT"


def test_anemometer_exactly_45_is_not_a_gust():
    # boundary: speed == 45 -> not > 45
    assert check_chairlift_anemometer([[45, 45, 45]]) == "SAFE_OPERATION"


def test_anemometer_single_gust_is_safe():
    assert check_chairlift_anemometer([[100]]) == "SAFE_OPERATION"


def test_anemometer_non_consecutive_gusts_reset_streak():
    assert check_chairlift_anemometer([[50, 10, 50, 10, 50]]) == "SAFE_OPERATION"


def test_anemometer_suspend_after_calm_readings():
    assert check_chairlift_anemometer([[10, 20, 50, 60]]) == "SUSPEND_LIFT"


def test_anemometer_streak_does_not_carry_between_lifts():
    assert check_chairlift_anemometer([[10, 50], [50, 10]]) == "SAFE_OPERATION"


def test_anemometer_second_lift_triggers_suspend():
    assert check_chairlift_anemometer([[10, 20], [50, 50]]) == "SUSPEND_LIFT"


def test_anemometer_empty_lift_readings_are_safe():
    assert check_chairlift_anemometer([[]]) == "SAFE_OPERATION"
    assert check_chairlift_anemometer([[], [10]]) == "SAFE_OPERATION"


def test_anemometer_early_exit_ignores_later_lifts():
    assert check_chairlift_anemometer([[50, 50], [10]]) == "SUSPEND_LIFT"
