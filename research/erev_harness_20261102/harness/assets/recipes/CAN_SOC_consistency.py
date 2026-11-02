"""Endpoint SOC scale consistency, not independent battery capacity measurement."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

P = Path(__file__).resolve().parent
R = P.parents[1]
SRC = P/'inputs'
if not SRC.exists():
    SRC = R.parent/'feedback/research/public_validation_batch_20261016/actual_20261016'

rows = []
for code, internal, display in [('060','HPCM2_SOC_percent','displayed_SOC_percent'),
                                ('066','SOC_internal_CAN_percent','SOC_displayed_CAN_percent')]:
    d = pd.read_csv(SRC/'references'/('ANL61905'+code+'_reference_native.csv'))
    b = pd.read_csv(SRC/code/('battery_PUBLIC_'+code+'.csv'),skiprows=[1])
    end = float(b.Time.iloc[-1]); t = d.iloc[:,0].to_numpy(float)
    q = cumulative_trapezoid(d.meter_current_A_discharge_positive,t,initial=0)/3600
    tgrid = np.arange(end+1)
    net_ah = float(np.interp(end,t,q))
    model_initial = float(b.filter(like='In/SoC (').iloc[0,0])
    for channel in [internal,display]:
        soc = d[channel].to_numpy(float)
        start = float(soc[0]); last = float(np.interp(end,t,soc)); change = start-last
        nominal = start - np.interp(tgrid,t,q)*100/180
        actual = np.interp(tgrid,t,soc)
        rows.append(dict(test='61905'+code,channel=channel,CAN_start_percent=start,CAN_end_percent=last,
            CAN_SOC_drop_percentage_points=change,measured_net_Ah=net_ah,
            conditional_endpoint_capacity_Ah=100*net_ah/change,
            relative_to_180Ah_percent=100*((100*net_ah/change)/180-1),
            SOC_change_RMSE_with_180Ah_after_initial_alignment_percentage_points=float(np.sqrt(np.mean((nominal-actual)**2))),
            CAN_minus_model_initial_SOC_percentage_points=start-model_initial,
            OEM_SOC_scale_definition_verified=False,independent_capacity_measurement=False))

pd.DataFrame(rows).to_csv(P/'CAN_SOC_scale_consistency.csv',index=False)
print(pd.DataFrame(rows).round(6).to_string(index=False))
