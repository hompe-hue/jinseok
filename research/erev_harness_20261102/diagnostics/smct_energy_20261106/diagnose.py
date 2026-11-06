"""Reconcile the SMCT battery-terminal energy residual on both native clocks."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def interp(x, t, y):
    return np.interp(x, t, y)


def integral(t, y):
    return float(np.trapezoid(y, t) / 3600)


def zeros(t, y):
    k = np.where(y[:-1] * y[1:] < 0)[0]
    return t[k] - y[k] * (t[k + 1] - t[k]) / (y[k + 1] - y[k])


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--battery", type=Path, required=True)
    parser.add_argument("--velocity", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    b = pd.read_csv(args.battery, skiprows=[1])
    v = pd.read_csv(args.velocity, skiprows=[1])
    r = pd.read_csv(args.reference)
    t, rt = b.Time.to_numpy(), r.time_s.to_numpy()
    assert np.array_equal(t, v.Time)
    assert np.all(np.diff(t) > 0) and np.all(np.diff(rt) > 0)
    edges = np.r_[20., np.arange(1000., 8000., 1000.), 7630.]
    lo, hi = edges[[0, -1]]
    assert t[0] <= lo < hi <= t[-1] and rt[0] <= lo < hi <= rt[-1]
    vm = b["In/Voltage (BMS Monitor)"].to_numpy()
    im = -b["In/Current (BMS Monitor)"].to_numpy()
    vr, ir = r.meter_voltage_V.to_numpy(), r.meter_current_A_discharge_positive.to_numpy()
    pm, pr = vm * im / 1000, r.meter_power_kW_discharge_positive.to_numpy()
    sa = v["In/Actual Velocity (Vehicle Monitor)"].to_numpy()
    sr = r.speed_kmh.to_numpy()
    lv = r.LV_DCDC_output_W.to_numpy() / 1000
    assert all(np.all(np.isfinite(s)) for s in (vm, im, vr, ir, pr, sa, sr, lv))
    grid = np.unique(np.r_[edges, t, rt, zeros(t, pm), zeros(rt, pr), zeros(rt, sr - 1)])
    x = grid[(grid >= lo) & (grid <= hi)]
    mid = (x[1:] + x[:-1]) / 2
    dt = np.diff(x)
    m = interp(x, t, pm)
    p = interp(x, rt, pr)
    average = lambda y: (y[:-1] + y[1:]) / 2
    wm, wr = average(m), average(p)
    residual = (wm - wr) * dt / 3600

    # Simpson integrates products of linearly interpolated voltage and current
    # exactly on each interval of the union grid.
    def vi_terms(s):
        u, i = interp(s, t, vm), interp(s, t, im)
        ur, ii = interp(s, rt, vr), interp(s, rt, ir)
        return (u + ur) * (i - ii) / 2000, (i + ii) * (u - ur) / 2000, u * i / 1000, ur * ii / 1000

    y, z = np.asarray(vi_terms(x)), np.asarray(vi_terms(mid))
    ei, ev, evi_m, evi_r = ((y[:, :-1] + 4 * z + y[:, 1:]) * dt / 21600).sum(axis=1)
    em, er = integral(x, m), integral(x, p)
    assert abs(em - 12.258042531685845) < 1e-9 and abs(er - 11.400765518287717) < 1e-9
    bridge_m, bridge_r = em - evi_m, evi_r - er
    gap = em - er
    assert abs(gap - ei - ev - bridge_m - bridge_r) < 1e-10

    def group(name, mask):
        return dict(group=name, duration_s=float(dt[mask].sum()),
                    model_net_kWh=float((wm[mask] * dt[mask]).sum() / 3600),
                    reference_net_kWh=float((wr[mask] * dt[mask]).sum() / 3600),
                    gap_kWh=float(residual[mask].sum()))

    windows = [group(f"{a:g}–{b:g}", (mid >= a) & (mid < b)) for a, b in zip(edges[:-1], edges[1:])]
    moving = interp(mid, rt, sr) > 1
    modes = [group("measured_speed_le_1_kmh", ~moving),
             group("moving_measured_pack_discharge", moving & (wr >= 0)),
             group("moving_measured_pack_charge", moving & (wr < 0))]
    assert all(abs(sum(row["gap_kWh"] for row in groups) - gap) < 1e-10 for groups in (windows, modes))

    md, mr = (wm.clip(min=0) * dt).sum() / 3600, ((-wm).clip(min=0) * dt).sum() / 3600
    rd, rr = (wr.clip(min=0) * dt).sum() / 3600, ((-wr).clip(min=0) * dt).sum() / 3600
    assert abs((md - rd) + (rr - mr) - gap) < 1e-10
    grid1 = np.arange(lo + 1, hi + 1)
    summary = dict(
        window_s=[lo, hi], model_net_kWh=em, reference_net_kWh=er, gap_kWh=gap,
        gap_percent=100 * gap / er,
        model_discharge_kWh=float(md), reference_discharge_kWh=float(rd),
        excess_discharge_kWh=float(md - rd), model_charge_magnitude_kWh=float(mr),
        reference_charge_magnitude_kWh=float(rr), reduced_charge_magnitude_kWh=float(rr - mr),
        symmetric_current_term_kWh=float(ei), symmetric_voltage_term_kWh=float(ev),
        model_native_power_to_VI_bridge_kWh=float(bridge_m),
        reference_VI_to_native_meter_bridge_kWh=float(bridge_r),
        equivalent_gap_mean_kW=gap * 3600 / (hi - lo),
        model_aux_kWh=0.4 * (hi - lo) / 3600,
        measured_LV_DCDC_output_kWh=integral(x, interp(x, rt, lv)),
        actual_model_vs_measured_speed_RMSE_kmh=float(np.sqrt(np.mean(
            (interp(grid1, t, sa) - interp(grid1, rt, sr)) ** 2))),
        source_sha256={name: hash_file(getattr(args, name)) for name in ("battery", "velocity", "reference")},
    )
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("time_windows", windows), ("measured_operating_groups", modes)):
        with (args.output / (name + ".csv")).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0], lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
