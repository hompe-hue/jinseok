"""Evaluate genuine C1 CSV exports; freeze for066 only after both CAL runs pass."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
OUT=BASE if (BASE/'candidate_contract.json').exists() else BASE/'runs/final_candidate_C1_20261014'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def col(d,n):
    a=[k for k in d if k=='Time' and n=='Time' or k.startswith('In/'+n+' (')];assert len(a)==1,(n,a)
    return d[a[0]].to_numpy(dtype=float)
def integral(t,x,a,b):
    assert t[0]<=a<b<=t[-1]+1e-9
    tt=np.r_[a,t[(t>a)&(t<b)],b]
    return float(np.trapezoid(np.interp(tt,t,x),tt)/3600)
def errors(x):return dict(RMSE=float(np.sqrt(np.mean(x*x))),bias=float(np.mean(x)),max_abs=float(np.max(abs(x))))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--test',required=True,choices=['61905060','61905061','61905066']);ap.add_argument('--exports',required=True,type=Path)
    args=ap.parse_args();test=args.test;contract=json.loads((OUT/'candidate_contract.json').read_text());case=next(x for x in contract['cases'] if x['test']==test)
    assert sha(OUT/'parameters.json')==contract['parameter_json_sha256'],'Changed parameter contract'
    for name,expected in contract['map_sha256'].items():assert sha(OUT/'inputs'/name)==expected,'Changed map'
    if test=='61905066':
        frozen=json.loads((OUT/'frozen_for066.json').read_text())
        assert frozen['calibration_confirmed'] and frozen['candidate_contract_sha256']==sha(OUT/'candidate_contract.json')
    files={}
    for name in ['battery','velocity','generator']:
        options=[args.exports/f'{name}_C1_{test}.csv',args.exports/f'{name}_ANL{test}.csv']
        chosen=[p for p in options if p.exists()];assert len(chosen)==1,(name,'Provide exactly one alias',options)
        files[name]=chosen[0]
    data={k:pd.read_csv(p,skiprows=[1]) for k,p in files.items()}
    t=col(data['battery'],'Time');assert t[0]==0 and np.all(np.diff(t)>0)
    assert all(np.array_equal(t,col(d,'Time')) and np.isfinite(d.to_numpy(dtype=float)).all() for d in data.values())
    assert t[-1]>=np.floor(case['end_time_s']) and t[-1]<=case['end_time_s']+1e-6,'Truncated/wrong-duration export'
    refpath=OUT/f'references/ANL{test}_reference_native.csv';ref=pd.read_csv(refpath)
    assert sha(refpath)==contract['reference_sha256'][refpath.name],'Changed reference'
    nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'].to_numpy()
    voltage=col(data['battery'],'Voltage');current=-col(data['battery'],'Current');power=voltage*current/1000
    motor=col(data['velocity'],'E-Motor Current')*voltage/1000;aux=col(data['velocity'],'E-Consumer Current')*voltage/1000
    actual=col(data['velocity'],'Actual Velocity');desired=col(data['velocity'],'Desired Velocity');target=np.interp(t,nt,ref.speed_kmh)
    assert np.max(abs(desired-target))<.001,'Wrong profile'
    assert abs(col(data['battery'],'SoC')[0]-case['initial_SOC_percent'])<1e-4,'Wrong candidate initial SOC'
    assert np.max(abs(aux-.4))<1e-5,'Wrong auxiliary demand'
    em=integral(t,power,20,t[-1]);er=integral(nt,ref.meter_power_kW_discharge_positive.to_numpy(),20,t[-1]);energy_error=100*(em/er-1)
    mask=t>20;vr=np.interp(t,nt,ref.meter_voltage_V);volterr=errors((voltage-vr)[mask]);tracking=errors(actual-desired)
    dist=100*(integral(t,actual,0,t[-1])/integral(nt,ref.speed_kmh.to_numpy(),0,t[-1])-1)
    balance=100*abs(integral(t,power-motor-aux,20,t[-1]))/max(abs(em),1e-9)
    generator={n:float(np.max(abs(col(data['generator'],n)))) for n in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
    gate=contract['gates'];checks={
      'energy':abs(energy_error)<=gate['energy_error_abs_percent_max'],'voltage_RMSE':volterr['RMSE']<=gate['voltage_RMSE_V_max'],
      'voltage_bias':abs(volterr['bias'])<=gate['voltage_bias_abs_V_max'],'speed_RMSE':tracking['RMSE']<=gate['speed_RMSE_kmh_max'],
      'distance':abs(dist)<=gate['distance_error_abs_percent_max'],'DC_energy_balance':balance<=gate['integrated_DC_balance_abs_percent_max'],
      'generator_OFF':all(v<1e-8 for v in generator.values())}
    phases=[]
    if test=='61905066':
        for row in pd.read_csv(OUT/'references/phase_windows.csv').to_dict('records'):
            a=max(20,row['start_s']);b=min(t[-1],row['end_s'])
            if b<=a:continue
            keep=(t>=a)&(t<=b);me=integral(t,power,a,b);re=integral(nt,ref.meter_power_kW_discharge_positive.to_numpy(),a,b)
            phases.append(dict(phase=row['phase'],window_s=[a,b],model_kWh=me,reference_kWh=re,energy_error_percent=100*(me/re-1),voltage=errors((voltage-vr)[keep])))
    report={'test':test,'candidate':'C1','role':case['role'],'model_energy_kWh':em,'reference_native_energy_kWh':er,
      'model_gross_discharge_kWh':integral(t,np.maximum(power,0),20,t[-1]),
      'model_gross_recovered_kWh':integral(t,np.maximum(-power,0),20,t[-1]),
      'reference_gross_discharge_kWh':integral(nt,np.maximum(ref.meter_power_kW_discharge_positive.to_numpy(),0),20,t[-1]),
      'reference_gross_recovered_kWh':integral(nt,np.maximum(-ref.meter_power_kW_discharge_positive.to_numpy(),0),20,t[-1]),
      'energy_error_percent':energy_error,'voltage':volterr,'tracking':tracking,'distance_error_percent':dist,'integrated_DC_balance_percent':balance,
      'DC_identity_max_error_kW':float(np.max(abs(power-motor-aux))),'checks':checks,'actual_metrics_passed':all(checks.values()),
      'window_s':[20,float(t[-1])],'unexported_tail_s':float(case['end_time_s']-t[-1]),'phase_diagnostics':phases,
      'expected_saved_project_sha256':case['project_sha256'],'candidate_contract_sha256':sha(OUT/'candidate_contract.json'),
      'CSV_sha256':{p.name:sha(p) for p in files.values()},'reference_sha256':sha(refpath),
      'solver_project_provenance':'Expected savedprojecthash;actual solverlog/runtimehash not supplied. Check user ran provided unedited project.',
      'physical_component_identification':False,'no_endpoint_SOC_PASS':'ModelSOCcoordinateandCANrelationshipnotidentified'}
    resultdir=OUT/'actual_results'/test;resultdir.mkdir(parents=True,exist_ok=True)
    (resultdir/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if test!='61905066':
        paths=[OUT/f'actual_results/{k}/verification.json' for k in ['61905060','61905061']]
        both=all(p.exists() for p in paths)
        if both:
            results=[json.loads(p.read_text()) for p in paths]
            both=all(x['actual_metrics_passed'] and x['candidate_contract_sha256']==sha(OUT/'candidate_contract.json') for x in results)
        frozenpath=OUT/'frozen_for066.json'
        if both:
            hold=next(x for x in contract['cases'] if x['test']=='61905066')
            freeze={'frozen_before066_comparison':True,'calibration_test_ids':['61905060','61905061'],'model_project_sha256':hold['project_sha256'],
              'no_tuning_using066':True,'calibration_confirmed':True,'candidate_contract_sha256':sha(OUT/'candidate_contract.json'),
              'actual_CAL_result_sha256':{p.parent.name:sha(p) for p in paths},'C1_parameter_sha256':contract['parameter_json_sha256']}
            frozenpath.write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
        elif frozenpath.exists():frozenpath.unlink()
        report['ready_for066']=both
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
