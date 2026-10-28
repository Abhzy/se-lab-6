# Lab 6: Code and Branch Coverage Analysis Report

**Name:** Abhay Natesh Bharadwaj  
**SRN:** PES1UG24AM007
**Repository:** SETAPESU26/L6_L7_08_ski_resort_pass  
**Application under test:** `ski_resort_pass.py` (functions `process_resort_bookings`, `check_chairlift_anemometer`)  
**Tools:** Python 3.12, pytest 9.2, coverage 7.x

---

## 1. Baseline (provided test only)

Command: `coverage run --branch -m pytest test_ski_resort.py` then `coverage report -m`

| File | Stmts | Miss | Branch | BrPart | Cover |
|---|---|---|---|---|---|
| ski_resort_pass.py | 59 | 31 | 42 | 12 | **44%** |

Missing lines: 3, 10, 16, 19-23, 33-34, 37-41, 43, 45, 50, 53, 58, 60, 65-77.  
The single provided test (one adult, full-day pass) never exercised input validation, inactive groups,
season / half-day passes, invalid durations, invalid ages, blackout overrides, child / senior pricing,
gear rental, lodge lockers, the AUDIT_REVIEW / ZERO_SALES statuses, or any of `check_chairlift_anemometer`.

## 2. Code (line) coverage: `CodeCoverageTest_ski_resort_pass.py`

Command: `coverage run -m pytest CodeCoverageTest_ski_resort_pass.py` then `coverage report -m`

| Metric | Result |
|---|---|
| Tests | 16 passed |
| Statements / Missed | 59 / 0 |
| **Line coverage of ski_resort_pass.py** | **100%** (target >= 90%) |

Each test was written to reach a specific previously-missing line group:

| Missing lines | Test(s) that cover them |
|---|---|
| 3 | `test_invalid_input_raises_value_error` |
| 10, 60 | `test_inactive_group_is_skipped` |
| 16 / 20 | `test_season_pass_adult`, `test_half_day_pass_adult` |
| 22-23 | `test_invalid_duration_is_rejected` |
| 33-34 | `test_skier_with_invalid_age_is_rejected` |
| 37, 41 | `test_blackout_override_full_day_gets_50_percent` |
| 38-40 | `test_blackout_override_half_day_voids_group` |
| 43, 45 | `test_child_discount`, `test_senior_discount` |
| 50, 53 | `test_gear_rental_and_lodge_locker` |
| 58 | `test_audit_review_when_more_than_four_rejections` |
| 65-77 | the three anemometer tests (NO_DATA, SUSPEND_LIFT, SAFE_OPERATION) |

## 3. Branch coverage: `BranchCoverageTest_ski_resort_pass.py`

Command: `coverage run --branch -m pytest BranchCoverageTest_ski_resort_pass.py` then `coverage report -m`

| Metric | Result |
|---|---|
| Tests | 62 passed (parametrized cases included) |
| Statements / Missed | 59 / 0 |
| Branches / Partial | 42 / 0 |
| **Branch coverage of ski_resort_pass.py** | **100%** (target >= 90%) |

Decision points covered on both the True and False side:

| Line(s) | Decision | True side | False side |
|---|---|---|---|
| 2 | `not list or fee < 0` | non-list input; negative fee | valid list, fee = 0 |
| 8 | outer `for` | groups present | empty list |
| 9 | `is_active` | inactive / missing key | active |
| 15-23 | duration `if/elif/elif/else` | season, full_day, half_day | invalid, "", None, "SEASON" |
| 27 | skier `for` | skiers present | none / missing key |
| 32 | `age <= 0` | 0, -1, -50, missing | 1 |
| 36 / 38 | blackout / half_day | blackout on full_day, season, half_day | not blackout |
| 42 / 44 | child / senior | 11 / 65+ | 12 and 64 (adult) |
| 49 | gear rental | with gear | without gear |
| 52 | lodge locker | with locker | without / missing |
| 57 | `rejected > 4` | 5 rejections | exactly 4 rejections |
| 59 | `revenue == 0` | ZERO_SALES | COMPLETED |
| 65 | `not wind_streams` | `[]`, `None` | data present |
| 68 / 70 | lift / reading loops | multiple lifts | empty lift readings |
| 71 / 73 | `> 45` / streak `>= 2` | 46 and 46 | exactly 45; single gust; broken streak |

## 4. Line vs. branch coverage: observations

* Unlike the lab's `calculate_discount` example, line coverage here does not hide untested branches. The
  16 tests written for line coverage also gave 100% branch coverage under `--branch`. Almost every decision
  in this code is an `if/elif/else` chain or a `continue`, so executing every line forces both outcomes.
* What coverage.py cannot measure are the **boundary and edge conditions**. The branch-coverage file adds tests that
  a line-/branch-percentage cannot demand, for example:
  * `age` 11 / 12 and 64 / 65 (child, adult and senior boundaries);
  * exactly 4 versus 5 rejections (`> 4` boundary) and AUDIT_REVIEW outranking ZERO_SALES;
  * speed exactly 45 mph (`> 45`, not `>= 45`) and streaks that reset or do not carry between lifts;
  * `facility_fee = 0` and `-0.01` for the `or` condition on line 2. coverage.py counts line 2 as one branch point
    and does not track each operand of `or` separately, so this needs explicit tests.
* **Behaviour worth noting from testing:** for a `half_day` pass, a `blackout_override` skier discards the whole
  group's total and breaks out of the loop, but the lodge-locker fee is still added afterwards (line 52-53).
  `test_blackout_half_day_locker_fee_still_added` documents this (revenue = locker fee only).
  Similarly, a skier with `age <= 0` is skipped before gear rental is checked, so no gear fee is charged.
* No dead code was found: every statement and every branch is reachable.

## 5. Summary

| Stage | Tests | Line cov. | Branch cov. |
|---|---|---|---|
| Baseline (`test_ski_resort.py`) | 1 | 44% (total incl. branches) | partial (12 partial branches) |
| `CodeCoverageTest_ski_resort_pass.py` | 16 | **100%** | 100% |
| `BranchCoverageTest_ski_resort_pass.py` | 62 | **100%** | **100%** |

Both targets (>= 90%) are met. Screenshots: `screenshots/code_coverage_screenshot.png` and
`screenshots/branch_coverage_screenshot.png`.
