"""Frozen C1 measured-current replays and diagnostic capacity sweep; no fitting.

066 has already been evaluated. Any future parameter adoption based on it
requires a new version and a fresh independent test. This script changes none.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'runs/final_candidate_C1_20261014'
def col(d,n):return d[[x for x in d if x.startswith('In/'+n+' (')][0]].to_numpy()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--exports',required=True,type=Path);args=ap.parse_args()
    ocv=np.loadtxt(BASE/'inputs/C1_Cell_OCV_25C.dat',skiprows=2);res=np.loadtxt(BASE/'inputs/C1_Cell_Resistance_25C.dat',skiprows=2)
    def voltage(s,i):return 96*np.interp(s,ocv[:,0],ocv[:,1])-i*32*np.interp(s/100,res[:,0],res[:,1])
    data={}
    for test in ['61905060','61905061','61905066']:
        ref=pd.read_csv(BASE/f'references/ANL{test}_reference_native.csv');b=pd.read_csv(args.exports/f'battery_C1_CAL_{test}.csv',skiprows=[1])
        t=b.Time.to_numpy();nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'].to_numpy();ir=np.interp(t,nt,ref.meter_current_A_discharge_positive);vr=np.interp(t,nt,ref.meter_voltage_V)
        ah=np.interp(t,nt,cumulative_trapezoid(ref.meter_current_A_discharge_positive,nt,initial=0))/3600
        s0=brentq(lambda s:voltage(s,float(ref.meter_current_A_discharge_positive.iloc[0]))-float(ref.meter_voltage_V.iloc[0]),0,100)
        data[test]=(t,ir,vr,ah,s0,b,ref,nt)
    t,ir,vr,ah,s0,b,ref,nt=data['61905066'];vm=col(b,'Voltage');sm=col(b,'SoC');im=-col(b,'Current');sr=s0-ah/168*100;replay=voltage(sr,ir);mask=t>20
    runtime=voltage(sm,im)-vm;assert abs(runtime).max()<.05
    phases=[]
    for p in pd.read_csv(BASE/'references/phase_windows.csv').to_dict('records'):
        k=(t>=max(20,p['start_s']))&(t<=min(t[-1],p['end_s']));e=(replay-vr)[k]
        phases.append({'phase':p['phase'],'measured_current_replay_bias_V':float(e.mean()),'measured_current_replay_RMSE_V':float(np.sqrt(np.mean(e*e))),
          'C1_state_current_effect_mean_V':float((vm-replay)[k].mean()),'model_SOC_start_percent':float(sm[k][0]),'model_SOC_end_percent':float(sm[k][-1]),'replayed_SOC_end_percent':float(sr[k][-1])})
    diagnosis={'initial_model_SOC_percent':float(sm[0]),'final_model_SOC_percent':float(sm[-1]),'final_measured_current_replayed_SOC_percent':float(sr[-1]),
      'measured_current_replay_bias_V':float((replay-vr)[mask].mean()),'measured_current_replay_RMSE_V':float(np.sqrt(np.mean((replay-vr)[mask]**2))),
      'C1_runtime_voltage_formula_max_abs_V':float(abs(runtime).max()),'model_demand_relative_to_measured_current_replay_mean_V':float((vm-replay)[mask].mean()),
      'model_Ah':float(np.trapezoid(im,t)/3600),'measured_Ah_native_to_export_end':float(ah[-1]),'max_single_second_SOC_change_pp':float(abs(np.diff(sm)).max()),
      'phases':phases,'scope':'Frozenmaps/sameinitialrule replay;notCANmappingoruniquecellparameteridentification'}
    out=BASE/'actual_results/61905066'
    (out/'battery_replay_diagnosis.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
    pd.DataFrame(dict(time_s=t,model_SOC_percent=sm,measured_current_replay_SOC_percent=sr,model_voltage_V=vm,reference_voltage_V=vr,measured_current_replay_voltage_V=replay,model_discharge_current_A=im,reference_current_A=ir)).to_csv(out/'battery_replay_aligned.csv',index=False)
    original_u=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2);original_r=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
    def original(s,i):return 96*np.interp(s,original_u[:,0],original_u[:,1])-i*32*np.interp(s/100,original_r[:,0],original_r[:,1])
    old_s0=brentq(lambda s:original(s,float(ref.meter_current_A_discharge_positive.iloc[0]))-float(ref.meter_voltage_V.iloc[0]),0,100)
    old_replay=original(old_s0-ah/168*100,ir);speed=np.interp(t,nt,ref.speed_kmh);low=(speed<=1)&(abs(ir)<=3)&mask;late=low&(t>4882)
    original_diag={'original_OCV_R_measured_current_replay_bias_V':float((old_replay-vr)[mask].mean()),'original_OCV_R_measured_current_replay_RMSE_V':float(np.sqrt(np.mean((old_replay-vr)[mask]**2))),
      'original_initial_SOC_rule_percent':float(old_s0),'low_load_definition':'measuredspeed<=1kmh andabs(measuredcurrent)<=3A;after20s',
      'low_load_samples':int(low.sum()),'C1_low_load_voltage_bias_V':float((vm-vr)[low].mean()),'late_low_load_samples':int(late.sum()),
      'C1_late_low_load_voltage_bias_V':float((vm-vr)[late].mean()),'late_low_load_mean_abs_measured_current_A':float(np.mean(abs(ir[late]))),
      'no_parameters_changed':True,'scope':'Originalstaticmodelalsobiases;OCV/capacity/history/hysteresis/temperaturearenotuniquelyidentified'}
    (out/'original_baseline_diagnosis.json').write_text(json.dumps(original_diag,indent=2)+'\n')
    sweep=[]
    for gain in [.95,.975,1.,1.025,1.05]:
        row={'capacity_gain':gain,'capacity_Ah':168*gain,'test_metrics':{}}
        for test,(tt,ii,vv,a,start,*_) in data.items():
            s=start-a/(168*gain)*100;e=(voltage(s,ii)-vv)[tt>20]
            row['test_metrics'][test]={'bias_V':float(e.mean()),'RMSE_V':float(np.sqrt(np.mean(e*e)))}
        sweep.append(row)
    (out/'capacity_sensitivity.json').write_text(json.dumps({'scope':'Prespecifieddiagnosticgrid,notparameterfit;noadoption;measuredcurrentreplaynotCRUISE','grid':sweep,'current_C1_unchanged':True},indent=2)+'\n')
    print(json.dumps({'diagnosis':diagnosis,'original':original_diag,'capacity_sensitivity':sweep},indent=2))

if __name__=='__main__':main()
