"""Select steady high-load runs from existing analytical inputs. No AVL execution."""
import csv
import json
import math
from pathlib import Path
import sys

BASELINE_SOC = 16.0
FLOOR_SOC = 5.0
START_SOC = {'S0': 6.0, 'S2': 15.0}
GEN_KW = 26.0
CANDIDATE_PLATEAUS = [(100, 4), (120, 4), (120, 6)]
GOAL_MINUTES = (10, 15)


def soc_to_kwh(soc_delta, battery_kwh):
    return battery_kwh * soc_delta / 100


def hold_minutes(demand, battery_kwh, trigger):
    to_trigger = soc_to_kwh(BASELINE_SOC - trigger, battery_kwh) / demand
    after_trigger = soc_to_kwh(trigger - FLOOR_SOC, battery_kwh) / (demand - GEN_KW)
    return 60 * (to_trigger + after_trigger)


def minimum_soc(duration_h, demand, battery_kwh, trigger):
    post_trigger_h = soc_to_kwh(trigger - FLOOR_SOC, battery_kwh) / (demand - GEN_KW)
    if duration_h <= post_trigger_h:
        return FLOOR_SOC + 100 * duration_h * (demand - GEN_KW) / battery_kwh
    return trigger + 100 * (duration_h - post_trigger_h) * demand / battery_kwh


def main():
    parent = Path(__file__).resolve().parents[1]
    old = json.loads((parent / 'research_direction_20261013/calculation_review.json').read_text())
    battery_kwh = old['assumptions']['usable_energy_kwh']
    demand_lookup = {(r['speed_kmh'], r['grade_pct']): r['demand_dc_kw']
                     for r in old['duration']}
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(['speed_km_h', 'grade_pct', 'duration_goal_min', 'demand_DC_kW',
                     'initial_SOC_pct', 'floor_SOC_pct', 'generator_DC_kW',
                     'S0_predicted_hold_min', 'S2_predicted_hold_min',
                     'S0_min_initial_SOC_pct', 'S2_min_initial_SOC_pct',
                     'S0_headroom_min', 'S2_headroom_min', 'evidence'])
    for speed, grade in CANDIDATE_PLATEAUS:
        demand = demand_lookup[speed, grade]
        assert demand > GEN_KW
        holds = [hold_minutes(demand, battery_kwh, trigger) for trigger in START_SOC.values()]
        assert holds[0] < holds[1]
        for goal in GOAL_MINUTES:
            minima = [minimum_soc(goal / 60, demand, battery_kwh, trigger)
                      for trigger in START_SOC.values()]
            deltas = [h - goal for h in holds]
            assert all((delta >= 0) == (BASELINE_SOC >= minimum)
                       for delta, minimum in zip(deltas, minima))
            round_values = [f'{v:.4f}' for v in [demand, BASELINE_SOC, FLOOR_SOC, GEN_KW,
                                                *holds, *minima, *deltas]]
            writer.writerow([speed, grade, goal, *round_values, 'analytical_case_selection_only'])
    assert math.isclose(demand_lookup[120, 4], 49.91, abs_tol=0.01)


if __name__ == '__main__':
    main()
