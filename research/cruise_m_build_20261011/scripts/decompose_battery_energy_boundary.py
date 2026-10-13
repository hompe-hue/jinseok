"""Exact accounting identity on the saved common-time grid; not a causal fit."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/battery_energy_boundary_20261013'
OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for test in ['61905060','61905061']:
    d=pd.read_csv(ROOT/'runs'/('ANL'+test+'_20261013')/'aligned_diagnostics.csv')
    t=d.time_s.to_numpy()
    def integrate(x):return float(np.trapezoid(np.asarray(x),t)/3600)
    vm=d.model_voltage_V; vr=d.reference_voltage_V
    im=d.model_discharge_current_A; ir=d.reference_discharge_current_A
    pm=d.model_discharge_power_kW; pr=d.reference_discharge_power_kW
    components={
        'voltage_difference_at_model_current_kWh':integrate(im*(vm-vr)/1000),
        'current_difference_at_measured_voltage_kWh':integrate(vr*(im-ir)/1000),
        'reference_VI_minus_meter_power_kWh':integrate(vr*ir/1000-pr),
        'model_power_minus_model_VI_kWh':integrate(pm-vm*im/1000)}
    gap=integrate(pm-pr)
    assert abs(sum(components.values())-gap)<1e-10
    row={'test':test,'rows':len(d),'end_time_s':float(t[-1]),'common_grid_model_energy_kWh':integrate(pm),'common_grid_reference_energy_kWh':integrate(pr),'gap_kWh':gap,**components,'identity_error_kWh':sum(components.values())-gap,'voltage_accounting_fraction_of_gap_percent':components['voltage_difference_at_model_current_kWh']/gap*100}
    rows.append(row)
pd.DataFrame(rows).to_csv(OUT/'energy_accounting.csv',index=False)
(OUT/'summary.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
