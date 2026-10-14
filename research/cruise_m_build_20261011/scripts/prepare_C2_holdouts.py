"""Fresh-test input QA only, after C2 fit. No model/outcome comparison or tuning."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
from nptdms import TdmsFile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'runs/C2_battery_common_20261014'
meta=json.loads((ROOT/'runs/final_candidate_C1_20261014/actual_results/61905066/next_holdout_metadata.json').read_text())
records=[]
for m in meta:
 test=m['test'];src=ROOT/f'runs/calibration_gate_20261014/sources/ANL{test}.tdms'
 assert hashlib.sha256(src.read_bytes()).hexdigest()==m['source_sha256']
 with TdmsFile.open(src) as f:
  g=f.groups()[0];a=m['start_row_zero_based'];b=m['stop_row_exclusive']
  names={'Time_H0':'s','Dyno_Spd_Front':'mph','Batt_Volt_Hioki_U1':'V','Batt_Curr_Hioki_I1':'A','Batt_Power_Hioki_P1':'kW','HVBatt_cell_temp_1_CAN3':'C'}
  for n,unit in names.items():assert g[n].properties['unit_string']==unit
  arrays={n:g[n][a:b] for n in names};tt=arrays['Time_H0']-arrays['Time_H0'][0];assert np.all(np.diff(tt)>0)
  for n in ['Time','Time_3']:assert np.max(abs(g[n][a:b]-arrays['Time_H0']))<1e-9
  speed=arrays['Dyno_Spd_Front']*1.609344
  ref=pd.DataFrame(dict(time_s=tt,speed_kmh=speed,meter_voltage_V=arrays['Batt_Volt_Hioki_U1'],meter_current_A_discharge_positive=arrays['Batt_Curr_Hioki_I1'],meter_power_kW_discharge_positive=arrays['Batt_Power_Hioki_P1'],battery_temperature_C=arrays['HVBatt_cell_temp_1_CAN3']))
  assert np.isfinite(ref.to_numpy()).all() and ref.meter_voltage_V.between(250,450).all()
  grades=[n for n in g.channels() if 'grade' in n.name.lower() and 'trace' in n.name.lower()];assert grades
  grade=g['Drive_trace_grade'][a:b];assert np.max(abs(grade))<1e-8
  duration=float(tt[-1]);t=np.r_[np.arange(np.floor(duration)+1),duration];v=np.interp(t,tt,speed)
  distance=float(np.trapezoid(speed,tt)/3600);resampled=float(np.trapezoid(v,t)/3600);assert distance>1 and abs(resampled/distance-1)<1e-4
  ref.to_csv(OUT/f'references/ANL{test}_reference_native.csv',index=False)
  pd.DataFrame(dict(time_s=t,speed_kmh=v)).to_csv(OUT/f'inputs/ANL{test}_driver_1s.csv',index=False)
  records.append(dict(test=test,role='C2_FRESH_HOLD_PENDING_CAL',source_sha256=m['source_sha256'],native_rows=len(ref),driver_rows=len(t),duration_s=duration,initial_voltage_V=m['initial_voltage_V'],initial_current_A=m['initial_current_A'],initial_battery_temperature_C=24.,initial_environment_temperature_C=float(m['phase_metadata']['Phase_1_Cell_Temp_C']),native_distance_km=distance,resampling_distance_error_percent=100*(resampled/distance-1),max_speed_kmh=float(speed.max()),grade_zero=True,source_test_name=m['phase_metadata']['TestInfo_Test_name'],explanation='Metadata GMLC Charging retained; selected phase has actual dyno driving. No C2 voltage/energy prediction compared;parameters not changed.',C2_performance_compared=False))
(OUT/'fresh_holdout_input_QA.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
