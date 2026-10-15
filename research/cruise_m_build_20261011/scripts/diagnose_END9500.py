"""Actual diagnostic evidence; counterfactual battery replay is labelled separately."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];U=ROOT/'runs/unified_BEV_model_20261014';OUT=U/'diagnostic_067_end9500_20261015/actual'
def col(d,n):return d[[k for k in d if k.startswith('In/'+n+' (')][0]].to_numpy(float)
def main():
    b=pd.read_csv(OUT/'battery_END9500.csv',skiprows=[1]);veh=pd.read_csv(OUT/'velocity_END9500.csv',skiprows=[1]);t=b.Time.to_numpy();v=col(b,'Voltage');i=-col(b,'Current');s=col(b,'SoC');P=v*i/1000;em=v*col(veh,'E-Motor Current')/1000;aux=v*col(veh,'E-Consumer Current')/1000;shaft=col(veh,'E-Motor Power Mech.')
    ref=pd.read_csv(U/'diagnostic_067_end9500_20261015/ANL61905067_reference_native.csv');nt=ref.time_s.to_numpy();ri=np.interp(t,nt,ref.meter_current_A_discharge_positive);rv=np.interp(t,nt,ref.meter_voltage_V)
    screen=pd.read_csv(U/'candidate_fixed_power_61905067.csv');pv=np.interp(t,screen.time_s,screen.candidate_voltage_V);ps=np.interp(t,screen.time_s,screen.model_SOC_percent)
    cap=169.3568460332183;u=np.loadtxt(U/'diagnostic_067_end9500_20261015/Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(U/'diagnostic_067_end9500_20261015/Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    vp=96*np.interp(s,u[:,0],u[:,1])-i*32*np.interp(s/100,r[:,0],r[:,1]);ah=np.r_[0,np.cumsum((i[1:]+i[:-1])/2*np.diff(t)/3600)];refah=np.r_[0,np.cumsum((ri[1:]+ri[:-1])/2*np.diff(t)/3600)]
    mask=t>20;total=(v-rv)[mask];battery=(pv-rv)[mask];demand=(v-pv)[mask];segments=[]
    for lo,hi in [(20,3000),(3000,6000),(6000,9000),(9000,9500)]:
        m=(t>lo)&(t<=hi);err=(v-rv)[m];segments.append(dict(window_s=[lo,hi],voltage_bias_V=float(err.mean()),voltage_RMSE_V=float(np.sqrt(np.mean(err**2)))))
    steady=(t>=300)&(t<=9500);speed=col(veh,'Actual Velocity');road=(126.329494+.557775*speed+.033456276*speed**2)*speed/3.6/1000
    summary=dict(status='ACTUAL067_DIAGNOSTIC_ANALYZED_NOT_FULL_VALIDATION',actual_window_s=[0,9500],full067_validation_complete=False,actual_total_energy_error_percent=2.185941985833284,extra_DC_energy_kWh=.9672991750082,average_extra_DC_power_W=.9672991750082*3600/(9500-20)*1000,extra_charge_Ah=float(ah[-1]-refah[-1]),actual_final_SOC_percent=float(s[-1]),SOC_from_reference_I_percent=float(s[0]-100*refah[-1]/cap),reference_power_replay_final_SOC_percent=float(ps[-1]),actual_final_voltage_V=float(v[-1]),reference_final_voltage_V=float(rv[-1]),terminal_voltage_error_V=float(v[-1]-rv[-1]),counterfactual_bias_decomposition=dict(total_V=float(total.mean()),battery_at_measured_power_V=float(battery.mean()),changed_power_demand_V=float(demand.mean()),changed_demand_fraction_of_total_mean_bias=float(demand.mean()/total.mean()),note='Algebraic difference between actual run and fixed-measured-power battery replay. Not independent identification of component losses.'),battery_application_checks=dict(max_OCV_R_voltage_identity_error_V=float(np.max(abs(v-vp))),max_current_integral_SOC_difference_percent_points=float(np.max(abs(s-(s[0]-100*ah/cap))))),steady_300_9500=dict(mean_battery_kW=float(P[steady].mean()),mean_motor_mechanical_kW=float(shaft[steady].mean()),mean_effective_EDU_loss_kW=float((em-shaft)[steady].mean()),mean_aux_kW=float(aux[steady].mean()),mean_TargetABC_power_at_actual_speed_kW=float(road[steady].mean()),nonzero_actual_brake_samples=int(np.count_nonzero(col(veh,'Brake Pressure Actual')[steady]>1e-6))),voltage_segments=segments,primary_mechanism='Model consumes more netDC energy at matched speed, accumulates extra charge depletion, then traverses the steep lowSOC OCV curve earlier',physical_residual_split_identified=False,no_capacity_or_initial_SOC_change_applied=True)
    try:
        from nptdms import TdmsFile
        raw=ROOT/'runs/C2_performance_extension_20261014/sources/ANL61905067.tdms'
        with TdmsFile.open(raw) as f:
            g=f.groups()[0];base=float(g['Time_H0'][int(g.properties['Phase_1_Phase_Start_Fill_Index'])-1]);ht=g['Time_H0'][:]-base;ct=g['Time_3'][:]-base
            hd=g['DCDC_Out_Power_Hioki_P3'][:];cm=g['Motor_1_speed_DMCM1'][:]*g['Motor_1_torque_DMCM1'][:]*2*np.pi/60/1000
            hm=(ht>=300)&(ht<=9500)&np.isfinite(hd);cmask=(ct>=300)&(ct<=9500)&np.isfinite(cm)
            summary['ANL_supporting_channels']=dict(DCDC_measured_output_mean_W=float(hd[hm].mean()),CAN_estimated_motor_mechanical_mean_kW=float(cm[cmask].mean()),CAN_vs_model_mechanical_difference_kW=float(shaft[steady].mean()-cm[cmask].mean()),limitations=['DCDC output is not HV input; efficiency and other HV loads are unknown','CAN torque is an ECU estimate, not an independent calibrated shaft torque measurement','Separate fill clocks referenced to meter phase start; channel uncertainty and offset are not fully identified'],original_TDMS_sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
    except ImportError:summary['ANL_supporting_channels']='nptdms unavailable; main export and reference evidence unaffected'
    (OUT/'depletion_diagnosis.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
