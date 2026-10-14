"""Evaluate genuine CRUISE M exports against066 without changing parameters."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
OUT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--exports',type=Path,required=True);ap.add_argument('--frozen-manifest',type=Path)
args=ap.parse_args()
ref=pd.read_csv(OUT/'references/ANL61905066_reference_native.csv')
prep=json.loads((OUT/'066_preparation.json').read_text())
assert hashlib.sha256((OUT/'references/ANL61905066_reference_native.csv').read_bytes()).hexdigest()==prep['sha256']['references/ANL61905066_reference_native.csv']
files={k:args.exports/f'{k}_ANL61905066.csv' for k in ['battery','velocity','generator']}
data={k:pd.read_csv(p,skiprows=[1]) for k,p in files.items()}
def col(d,n):
    matches=[x for x in d.columns if x=='Time' and n=='Time' or x.startswith('In/'+n+' (')]
    assert len(matches)==1,(n,matches)
    return d[matches[0]].to_numpy(dtype=float)
t=col(data['battery'],'Time')
assert np.all(np.diff(t)>0) and np.isfinite(t).all()
assert all(np.array_equal(t,col(d,'Time')) and np.isfinite(d.to_numpy(dtype=float)).all() for d in data.values())
nt=ref.time_s.to_numpy();assert t[0]>=nt[0] and t[-1]<=nt[-1]+1e-8 and t[-1]>20
vm=col(data['battery'],'Voltage');im=-col(data['battery'],'Current');pm=vm*im/1000
actual=col(data['velocity'],'Actual Velocity');desired=col(data['velocity'],'Desired Velocity')
target=np.interp(t,nt,ref.speed_kmh)
assert np.max(abs(desired-target))<.001,'Wrong mission orprofile'
motor=col(data['velocity'],'E-Motor Current')*vm/1000
aux=col(data['velocity'],'E-Consumer Current')*vm/1000
generator={n:float(np.max(abs(col(data['generator'],n)))) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Fuel Massflow','Power Generator','Power ICE']}
off=all(v<1e-8 for v in generator.values())
def integral(time,y,lo,hi):
    assert time[0]<=lo<hi<=time[-1]+1e-9
    z=np.r_[lo,time[(time>lo)&(time<hi)],hi]
    return float(np.trapezoid(np.interp(z,time,y),z)/3600)
def errors(x):return {'RMSE':float(np.sqrt(np.mean(x*x))),'bias':float(np.mean(x)),'max_abs':float(np.max(abs(x)))}
lo,hi=20.,float(t[-1]);mask=t>20
vr=np.interp(t,nt,ref.meter_voltage_V)
ir=np.interp(t,nt,ref.meter_current_A_discharge_positive)
pr=ref.meter_power_kW_discharge_positive.to_numpy()
em=integral(t,pm,lo,hi);er=integral(nt,pr,lo,hi)
voltage=errors((vm-vr)[mask]);tracking=errors(actual-desired)
energy_error=100*(em/er-1)
regions=[]
for p in pd.read_csv(OUT/'references/phase_windows.csv').to_dict('records'):
    a=max(lo,p['start_s']);b=min(hi,p['end_s'])
    if b<=a:continue
    q=(t>=a)&(t<=b);me=integral(t,pm,a,b);re=integral(nt,pr,a,b)
    regions.append({'phase':p['phase'],'window_s':[a,b],'model_kWh':me,'reference_kWh':re,'energy_error_percent':100*(me/re-1),
        'voltage':errors((vm-vr)[q]),'tracking':errors((actual-desired)[q])})
frozen=None
if args.frozen_manifest:
    frozen=json.loads(args.frozen_manifest.read_text())
    assert frozen.get('frozen_before066_comparison') is True
    assert frozen.get('calibration_test_ids')==['61905060','61905061']
    assert frozen.get('model_project_sha256') and frozen.get('no_tuning_using066') is True
criteria={'energy_abs_error_le5percent':abs(energy_error)<=5,'voltage_RMSE_le2V':voltage['RMSE']<=2,
    'voltage_abs_bias_le1V':abs(voltage['bias'])<=1,'generator_OFF':off,
    'DC_balance_identity':float(np.max(abs(pm-motor-aux)))<1e-5}
report={'test':'61905066','actual_export_rows':len(t),'actual_export_window_s':[float(t[0]),float(t[-1])],
    'comparison_window_s':[lo,hi],'unexported_tail_s':float(nt[-1]-hi),
    'model_kWh':em,'reference_native_kWh':er,'energy_error_percent':energy_error,
    'voltage':voltage,'current':errors((im-ir)[mask]),'tracking':tracking,
    'distance_error_percent':100*(integral(t,actual,0,hi)/integral(nt,ref.speed_kmh.to_numpy(),0,hi)-1),
    'model_gross_discharge_kWh':integral(t,np.maximum(pm,0),lo,hi),
    'model_gross_recovered_kWh':-integral(t,np.minimum(pm,0),lo,hi),
    'reference_gross_discharge_kWh':integral(nt,np.maximum(pr,0),lo,hi),
    'reference_gross_recovered_kWh':-integral(nt,np.minimum(pr,0),lo,hi),
    'generator_max_abs':generator,'phase_primary_windows':regions,'criteria':criteria,
    'criteria_are_research_targets_not_certification':True,'metrics_targets_met':all(criteria.values()),
    'frozen_manifest':frozen,'holdout_status':'Freeze manifest received; solver/project identity still must be reviewed' if frozen else 'NOT_FINAL_HOLDOUT_WITHOUT_FREEZE_MANIFEST',
    'no_endpoint_SOC_PASS':'CAN andmodelSOCcoordinate relationship unverified',
    'solver_completion':'Actual output window only; solver log required forfullcompletion',
    'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files.values()}}
(OUT/'actual_066_results').mkdir(exist_ok=True)
(OUT/'actual_066_results/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
pd.DataFrame(regions).to_csv(OUT/'actual_066_results/phase_metrics.csv',index=False)
print(json.dumps(report,ensure_ascii=False,indent=2))
