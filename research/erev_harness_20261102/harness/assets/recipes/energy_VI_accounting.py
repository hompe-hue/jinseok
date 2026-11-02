"""Exact symmetric V/I accounting on export grid, with explicit native reference bridge."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
SRC=P/'inputs'
if not SRC.exists():SRC=ROOT.parent/'feedback/research/public_validation_batch_20261016/actual_20261016'

def integral(t,y,a,b):
    x=np.r_[a,t[(t>a)&(t<b)],b]
    assert t[0]<=a and t[-1]>=b and np.all(np.diff(t)>0)
    return float(np.trapezoid(np.interp(x,t,y),x)/3600)

rows=[]
for code in ['058','059','060','066']:
    b=pd.read_csv(SRC/code/('battery_PUBLIC_'+code+'.csv'),skiprows=[1])
    ref=pd.read_csv(SRC/'references'/('ANL61905'+code+'_reference_native.csv'))
    t=b.Time.to_numpy(float);rt=ref.iloc[:,0].to_numpy(float);end=float(t[-1])
    vm=b.filter(like='In/Voltage (').iloc[:,0].to_numpy(float)
    im=-b.filter(like='In/Current (').iloc[:,0].to_numpy(float)
    vr=np.interp(t,rt,ref.meter_voltage_V)
    ir=np.interp(t,rt,ref.meter_current_A_discharge_positive)
    current_term=.5*(vm+vr)*(im-ir)/1000
    voltage_term=.5*(im+ir)*(vm-vr)/1000
    assert np.max(abs(current_term+voltage_term-(vm*im-vr*ir)/1000))<1e-10
    em=integral(t,vm*im/1000,20,end)
    er=integral(rt,ref.meter_power_kW_discharge_positive.to_numpy(float),20,end)
    eri=integral(t,vr*ir/1000,20,end)
    ei=integral(t,current_term,20,end);ev=integral(t,voltage_term,20,end)
    er_native_vi=integral(rt,ref.meter_voltage_V.to_numpy(float)*ref.meter_current_A_discharge_positive.to_numpy(float)/1000,20,end)
    bridge=eri-er;closure=em-er-ei-ev-bridge
    assert abs(closure)<1e-10
    rows.append(dict(test='61905'+code,observed_energy_gap_kWh=em-er,
        symmetric_current_difference_term_kWh=ei,symmetric_voltage_difference_term_kWh=ev,
        reference_sampling_and_power_definition_bridge_kWh=bridge,
        reference_VI_sampling_bridge_kWh=eri-er_native_vi,
        reference_native_VI_vs_meter_power_bridge_kWh=er_native_vi-er,
        closure_residual_kWh=closure,
        physical_cause_contributions_identified=False))
pd.DataFrame(rows).to_csv(P/'energy_VI_accounting.csv',index=False)
(P/'energy_accounting_QA.json').write_text(json.dumps(dict(
    pointwise_symmetric_identity_verified=True,native_reference_bridge_explicit=True,
    integrated_max_abs_closure_kWh=max(abs(x['closure_residual_kWh']) for x in rows),
    causal_driver_contributions_identified=False,parameter_correction_adopted=False),indent=2)+'\n')
print(pd.DataFrame(rows).round(8).to_string(index=False))
