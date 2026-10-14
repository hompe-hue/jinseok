"""Detect frozen-demand conflicts with existing C3 diagnostic controller maps.
This is not a simulation of unmet power or a measured real BMS envelope.
"""
from pathlib import Path
import json,sys
import numpy as np
import pandas as pd
from audit_dis80_semantic import SavedProject,ROOT
OUT=ROOT/'runs/unified_BEV_model_20261014'
def main():
    p=SavedProject(OUT/'implementation_060/C3_IMPL_61905060_R2.proj')
    dis=p.arrays_under(p.index['68891']);cha=p.arrays_under(p.index['69081']);rec=p.arrays_under(p.index['43746'])
    assert rec[0][1]['items']==['velocity~km_h']
    report=[]
    for test in ['61905060','61905061','61905066','61905064','61905058','61905059','61905067']:
        d=pd.read_csv(OUT/f'candidate_fixed_power_{test}.csv');t=d.time_s.to_numpy();v=d.candidate_voltage_V.to_numpy();soc=d.model_SOC_percent.to_numpy();demand=d.power_kW.to_numpy()
        # Exact controller expression with generatorOFF and400W auxiliaries.
        pdis=np.interp(soc,dis[0][2],dis[1][2]);pcha=np.interp(soc,cha[0][2],cha[1][2]);den=np.maximum(350,v)
        allowed_dis=.4+np.maximum(0,pdis*1000/den-400/v)*v/1000
        allowed_cha=pcha*v/den
        gapdis=np.maximum(demand-allowed_dis,0);gapcha=np.maximum(-demand-allowed_cha,0)
        def stats(gap):
            hit=np.flatnonzero(gap>.1)
            return dict(first_s=None if not len(hit) else float(t[hit[0]]),first_SOC_percent=None if not len(hit) else float(soc[hit[0]]),maximum_gap_kW=float(gap.max()),sample_count_over_0p1kW=int(len(hit)),integrated_gap_kWh=float(np.trapezoid(gap,t)/3600))
        report.append(dict(test=test,discharge_conflict=stats(gapdis),charge_conflict=stats(gapcha),boundary='Frozen power demand screen, not rerun vehicle/controller',real_BMS_identification=False))
    result=dict(diagnostic_maps=dict(discharge_SOC_percent=dis[0][2].tolist(),discharge_kW=dis[1][2].tolist(),charge_SOC_percent=cha[0][2].tolist(),charge_kW=cha[1][2].tolist()),current_denominator_floor_V=350,floor_is_not_cutoff=True,recuperation_weight_input='vehicle velocity km/h, notSOC',recuperation_velocity_kmh=rec[0][2].tolist(),recuperation_weights=rec[1][2].tolist(),tests=report,no_parameters_modified=True)
    (OUT/'diagnostic_power_limit_conflicts.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
