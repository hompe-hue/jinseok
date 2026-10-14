"""Separate actual058 evidence from screenshot-only067 and frozen-power predictions."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
U=ROOT/'runs/unified_BEV_model_20261014';OUT=U/'common_limits_20261015/actual_058_20261015'
def main():
    cfg=json.loads((U/'development_screen.json').read_text());capacity=cfg['capacity_Ah']
    d=pd.read_csv(OUT/'battery_61905058.csv',skiprows=[1])
    get=lambda n:d[[k for k in d if k.startswith('In/'+n+' (')][0]].to_numpy()
    t=d.Time.to_numpy();s=get('SoC');i=-get('Current');v=get('Voltage')
    ocv=np.loadtxt(U/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(U/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    vp=96*np.interp(s,ocv[:,0],ocv[:,1])-i*32*np.interp(s/100,r[:,0],r[:,1])
    ah=np.r_[0,np.cumsum((i[1:]+i[:-1])/2*np.diff(t)/3600)]
    runtime=dict(voltage_static_identity_max_error_V=float(np.max(abs(v-vp))),SOC_current_integral_max_difference_percent_points=float(np.max(abs(s-(s[0]-100*ah/capacity)))),initial_SOC_percent=float(s[0]),final_SOC_percent=float(s[-1]),minimum_SOC_percent=float(s.min()),maximum_regen_battery_kW=float(-(v*i/1000).min()),expected_project_identity_not_proven_by_CSV=True)
    ref=pd.read_csv(U/'common_limits_20261015/ANL61905067_reference_native.csv');tt=ref.time_s.to_numpy();screen=pd.read_csv(U/'candidate_fixed_power_61905067.csv')
    s0=next(z for z in cfg['metrics'] if z['test']=='61905067')['initial_model_SOC_percent'];rows=[]
    for time in [9906.,10122.]:
        end=min(time,tt[-1]);tr=np.r_[tt[tt<end],end]
        charge=float(np.trapezoid(np.interp(tr,tt,ref.meter_current_A_discharge_positive),tr)/3600)
        energy=float(np.trapezoid(np.interp(tr,tt,ref.meter_power_kW_discharge_positive),tr)/3600)
        rows.append(dict(time_s=time,reference_net_Ah=charge,reference_net_kWh=energy,reference_voltage_V=float(np.interp(time,tt,ref.meter_voltage_V)),SOC_from_reference_current_percent=s0-100*charge/capacity,frozen_measured_power_screen_SOC_percent=float(np.interp(time,screen.time_s,screen.model_SOC_percent))))
    failure=dict(user_report='SOC reached0 before scheduled end and solverfailed',screenshot='067_failure_image8.png',screenshot_right_time_s=9906,screenshot_progress_percent=97,scheduled_end_time_s=10122.190356254578,scheduled_time_remaining_s=216.190356254578,screenshot_time_is_not_exact_first_SOC0_or_solver_error_timestamp=True,failed067_CSV_received=False,solver_error_text_received=False,actual_consumption_or_capacity_cause_identified=False,reference_comparisons=rows,important_distinction='067 fixed-power screen used measured ANL power, not simulated vehicle/controller power; it cannot prove coupled vehicle depletion completion',reference_SOC_is_common_model_coordinate_not_OEM_CAN_SOC=True)
    (OUT/'runtime_058_and_failure_067.json').write_text(json.dumps(dict(actual058_runtime=runtime,failure067=failure),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(actual058_runtime=runtime,failure067=failure),indent=2))
if __name__=='__main__':main()
