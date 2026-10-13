"""Audit original ANL channels without interpreting undocumented CAN values as sensors."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from nptdms import TdmsFile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/core_evidence_20261013'; OUT.mkdir(parents=True,exist_ok=True)
names=['Motor_1_HV_circuit_voltage_DMCM1','Motor_1_inverter_supply_voltage_circuit_DMCM1',
 'Motor_1_current_DMCM1','Motor_1_torque_DMCM1','Motor_1_speed_DMCM1',
 'Motor_1_phase_u_current_DMCM1','Motor_1_phase_v_current_DMCM1','Motor_1_phase_w_current_DMCM1',
 'Axle_torque_CAN','Veh_axle_torque_HPCM','Trans_output_shaft_speed_HPCM',
 'HVBatt_current_high_CAN','HVBatt_current_low_CAN','HVBatt_voltage_CAN',
 'HVBatt_HEV_batt_pack_current_HPCM','HVBatt_pack_capacity_HPCM2','HVBatt_pack_resistance_HPCM2',
 'HVBatt_pack_SOC_HPCM2','HVBatt_SOC_HPCM','HVBatt_pack_SOC_gauge_HPCM2','HVBatt_SOC_displayed_CAN3',
 'HVBatt_cell_temp_1_CAN3','HVBatt_SOC_CAN4_needs further scaling_kWh','HVBatt_pack_heater_power_required_HPCM2',
 'HVAC_AC_comp_power_delivered_by HVBatt_HPCM2','HVAC_ac_comp_power_consumption_HPCM']
def stats(x):
 return {'min':float(np.min(x)),'max':float(np.max(x)),'mean':float(np.mean(x))}
def error(x):
 return {'RMSE':float(np.sqrt(np.mean(x*x))),'bias':float(np.mean(x)),'max_abs':float(np.max(abs(x)))}
def integral(t,x): return float(np.trapezoid(x,t)/3600)
reports=[]
metadata={}
for test in ['61905060','61905061']:
 cp=json.loads((ROOT/f'independent_tests_20261013/ANL{test}/checkpoint.json').read_text())
 source=OUT/f'sources/ANL{test}.tdms'; sha=hashlib.sha256(source.read_bytes()).hexdigest()
 assert sha==cp['source_sha256']
 g=TdmsFile.read(source).groups()[0]; origin=float(g['Time_H0'][cp['phase_start_row_zero_based']])
 metadata[test]={'source_url':cp['source_url'],'sha256':sha,'channels':{n:dict(g[n].properties) for n in names},
  'available_channel_names':[c.name for c in g.channels()]}
 raw=pd.DataFrame({'CAN_phase_time_s':g['Time_3'][:]-origin,**{n:g[n][:] for n in names}})
 duplicates=int(raw.CAN_phase_time_s.duplicated().sum())
 raw=raw.drop_duplicates('CAN_phase_time_s',keep='last').sort_values('CAN_phase_time_s')
 assert np.all(np.diff(raw.CAN_phase_time_s)>0)
 ref=pd.read_csv(ROOT/f'independent_tests_20261013/ANL{test}/reference_native.csv')
 hi=3150 if test=='61905060' else 1489
 tt=np.r_[20,ref.phase_time_s[(ref.phase_time_s>20)&(ref.phase_time_s<hi)].to_numpy(),hi]
 assert raw.CAN_phase_time_s.min()<=tt.min() and raw.CAN_phase_time_s.max()>=tt.max()
 vals={n:np.interp(tt,raw.CAN_phase_time_s,raw[n]) for n in names}
 mv=np.interp(tt,ref.phase_time_s,ref.meter_voltage_V); mi=np.interp(tt,ref.phase_time_s,ref.meter_current_A_discharge_positive)
 mp=np.interp(tt,ref.phase_time_s,ref.meter_power_kW_discharge_positive)
 lv=np.interp(tt,ref.phase_time_s,ref.LV_DCDC_output_W)/1000
 rpm=vals['Motor_1_speed_DMCM1']; tq=vals['Motor_1_torque_DMCM1']; current=vals['Motor_1_current_DMCM1']
 generic=vals['Motor_1_HV_circuit_voltage_DMCM1']*current/1000
 mech=tq*rpm*2*np.pi/60/1000
 # Both are undocumented CAN estimates; agreement would not establish independent sensor accuracy.
 axle=vals['Axle_torque_CAN']; axle_mech=axle*rpm/7.05*2*np.pi/60/1000
 low=(abs(rpm)<500)&(abs(tq)>20)
 regen=mech<-1
 drive=mech>1
 voltage_offset=vals['Motor_1_HV_circuit_voltage_DMCM1']-mv
 # Hypothetical DC interpretation can be checked for contradictions, not certified from a match.
 # Exact sensor/current clock and unknown HV auxiliaries still constrain causal interpretation.
 contradiction=drive&(generic<mech-1)
 r={
  'test':test,'window_s':[20,hi],'rows':len(tt),'duplicate_CAN_clock_rows_kept_last':duplicates,
  'source_sha256':sha,
  'generic_current':{'raw_unit':g['Motor_1_current_DMCM1'].properties.get('unit_string'),
   'meter_current_comparison_A':error(current-mi),
   'generic_VI_proxy_net_kWh':integral(tt,generic),'meter_net_kWh':integral(tt,mp),
   'LV_output_kWh':integral(tt,lv),'CAN_torque_rpm_mech_candidate_kWh':integral(tt,mech),
   'proxy_minus_mech_candidate_kWh':integral(tt,generic-mech),
   'drive_rows_proxy_below_mech_by_gt1kW':int(contradiction.sum()),
   'minimum_proxy_minus_mech_during_drive_kW':float(np.min((generic-mech)[drive])),
   'low_speed_loaded_rows':int(low.sum()),
   'low_speed_loaded_generic_current_A':stats(current[low]) if low.any() else None,
   'low_speed_loaded_meter_current_A':stats(mi[low]) if low.any() else None,
   'generic_current_motor_torque_correlation':float(np.corrcoef(current,tq)[0,1]),
   'voltage_offset_from_meter_V':error(voltage_offset),
   'interpretation':'Unit A and sign alone do not define DC/phase/torque-current. Proxy and CAN mechanical inconsistencies cannot identify which estimate is wrong. Do not use generic V*I as independent inverter DC power.'},
  'torque_boundary':{'axle_minus_7p05_motor_Nm':error(axle-7.05*tq),
   'axle_CAN_power_candidate_net_kWh':integral(tt,axle_mech),
   'axle_minus_motor_power_candidate_kWh':integral(tt,axle_mech-mech),
   'interpretation':'Both CAN estimates lack sensor location/accuracy definitions. Neither establishes measured rotor or hub torque; do not identify passive gear losses from their difference.'},
  'battery_undocumented_values':{n:{'unit_string':g[n].properties.get('unit_string'),**stats(vals[n])} for n in ['HVBatt_pack_capacity_HPCM2','HVBatt_pack_resistance_HPCM2']},
  'battery_current_channels':{n:{'raw_minus_discharge_positive_meter':error(vals[n]-mi),'negated_raw_minus_discharge_positive_meter':error(-vals[n]-mi)} for n in ['HVBatt_HEV_batt_pack_current_HPCM','HVBatt_current_high_CAN']},
  'SOC_coordinate':{},
  'battery_temperature_C':stats(vals['HVBatt_cell_temp_1_CAN3']),
  'SOC_CAN4_requires_scaling':{'raw_unit':g['HVBatt_SOC_CAN4_needs further scaling_kWh'].properties.get('unit_string'),**stats(vals['HVBatt_SOC_CAN4_needs further scaling_kWh'])},
  'HV_accessory_reported_channels':{n:{'unit':g[n].properties.get('unit_string'),**stats(vals[n])} for n in ['HVBatt_pack_heater_power_required_HPCM2','HVAC_AC_comp_power_delivered_by HVBatt_HPCM2','HVAC_ac_comp_power_consumption_HPCM']}
 }
 ah=np.r_[0,np.cumsum((mi[:-1]+mi[1:])/2*np.diff(tt))/3600]
 for name in ['HVBatt_pack_SOC_HPCM2','HVBatt_SOC_HPCM','HVBatt_pack_SOC_gauge_HPCM2','HVBatt_SOC_displayed_CAN3']:
  soc=vals[name]; delta=float(soc[0]-soc[-1]);qapp=float(100*ah[-1]/delta) if abs(delta)>1e-9 else None
  r['SOC_coordinate'][name]={'start_percent':float(soc[0]),'end_percent':float(soc[-1]),'delta_percentage_points':delta,
   'net_meter_Ah':float(ah[-1]),'apparent_Ah_per_full_CAN_SOC_span':qapp,
   'not_physical_capacity':'SOC estimator reserve/offset/nonlinearity/recalibration and timing not independently defined; ratio cannot replace168Ah.'}
 r['SOC_HPCM2_minus_HPCM_percentage_points']=stats(vals['HVBatt_pack_SOC_HPCM2']-vals['HVBatt_SOC_HPCM'])
 pd.DataFrame({'phase_time_s':tt,**vals,'meter_voltage_V':mv,'meter_current_A':mi,'meter_power_kW':mp,
  'generic_VI_proxy_kW':generic,'CAN_motor_mech_candidate_kW':mech,'CAN_axle_mech_candidate_kW':axle_mech}).to_csv(OUT/f'ANL{test}_CAN_boundary.csv',index=False)
 reports.append(r)
(OUT/'CAN_metadata.json').write_text(json.dumps(metadata,indent=2,default=str)+'\n')
(OUT/'CAN_boundary_summary.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
