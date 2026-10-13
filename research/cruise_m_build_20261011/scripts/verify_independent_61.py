from pathlib import Path
import csv,json,hashlib,shutil
import numpy as np
root=Path(__file__).resolve().parents[1];out=root/'runs/ANL61905061_20261013';out.mkdir(parents=True,exist_ok=True)
upload=Path('/workspace/scratch/d24978bde066/upload')
def load(path,units=True):
 rows=list(csv.reader(path.open()));return rows[0],np.array(rows[2 if units else 1:],float)
files={}
for kind in ['velocity','battery','generator']:
 src=upload/f'{kind}_ANL61905061.csv';dst=out/src.name
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copy2(src,dst)
 files[kind]=load(dst)
def col(kind,name):
 h,a=files[kind];ix=next(i for i,k in enumerate(h) if k==name or k.startswith('In/'+name+' ('));return a[:,ix]
t=col('velocity','Time');assert all(np.array_equal(t,col(k,'Time')) for k in files)
assert np.all(np.diff(t)>0) and all(np.all(np.isfinite(a)) for h,a in files.values())
h,n=load(root/'independent_tests_20261013/ANL61905061/reference_native.csv',False)
ref={k:n[:,i] for i,k in enumerate(h)};nt=ref['phase_time_s'];assert t[0]>=nt[0] and t[-1]<=nt[-1]
def interp(y):return np.interp(t,nt,y)
trap=getattr(np,'trapezoid',np.trapz)
def integ(x,tt=t,start=0,end=None):
 end=tt[-1] if end is None else end
 assert start>=tt[0] and end<=tt[-1]
 ts=np.r_[start,tt[(tt>start)&(tt<end)],end];return float(trap(np.interp(ts,tt,x),ts))
def stat(x):return {'first':float(x[0]),'last':float(x[-1]),'min':float(x.min()),'max':float(x.max())}
def metrics(x):return {'RMSE':float(np.sqrt(np.mean(x*x))),'bias':float(np.mean(x)),'MAE':float(np.mean(abs(x))),'max_abs':float(max(abs(x)))}
act=col('velocity','Actual Velocity');des=col('velocity','Desired Velocity');v=col('battery','Voltage');i=-col('battery','Current');p=v*i/1000;soc=col('battery','SoC');pr=ref['meter_power_kW_discharge_positive'];vr=interp(ref['meter_voltage_V']);ir=interp(ref['meter_current_A_discharge_positive']);rp=interp(pr);err=act-des
driver=np.loadtxt(root/'independent_tests_20261013/ANL61905061/driver_1s.csv',delimiter=',',skiprows=1);profile_error=des-np.interp(t,driver[:,0],driver[:,1]);held=t>20
gen={k:stat(col('generator',k)) for k in ['Actual Engine Speed','Cumulated Fuel Consumption','Current','Desired Engine Speed','Fuel Massflow','Power Generator','Power ICE']}
off=all(max(abs(x['min']),abs(x['max']))<1e-8 for x in gen.values())
energy=integ(p,start=20)/3600;re=integ(pr,nt,20,t[-1])/3600
ve=metrics((v-vr)[held]);ie=metrics((i-ir)[held]);enerr=(energy/re-1)*100
mask=(rp>45)&(err<-1);near=abs(p-45)<.25
cp=json.loads((root/'independent_tests_20261013/ANL61905061/checkpoint.json').read_text())
report={'status':'ANL61905061 exported run verified; empirical comparison complete for common interval, model adequacy evaluated below','source_hashes':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in out.glob('*.csv')},'quality':{'rows':len(t),'same_times':True,'all_finite':True,'end_s':float(t[-1]),'profile_end_s':float(nt[-1]),'unexported_tail_s':float(nt[-1]-t[-1]),'simulation_completion':'Fractional endpoint is not exported; full run completion not inferred solely from 1s CSV'},'condition_checks':{'initial_SOC_observed_percent':float(soc[0]),'initial_SOC_expected_percent':cp['initial_SOC_model_percent'],'initial_SOC_matches':abs(soc[0]-cp['initial_SOC_model_percent'])<1e-5,'desired_profile_max_error_kmh':float(max(abs(profile_error))),'desired_profile_matches':max(abs(profile_error))<1e-5,'aux_kW_from_consumer':stat(col('velocity','E-Consumer Current')*v/1000),'temperature':'CSV has no battery/environment temperature; not independently confirmed'},'tracking':{**metrics(err),'actual_distance_km':integ(act)/3600,'desired_distance_km':integ(des)/3600,'reported_distance_km':float(col('velocity','Distance')[-1]),'distance_error_percent':(integ(act)/integ(des)-1)*100,'max_abs_error_time_s':float(t[np.argmax(abs(err))]),'reference_power_above45_and_speed_deficit_over1kmh_samples':int(mask.sum())},'battery':{'voltage_V':stat(v),'current_discharge_positive_A':stat(i),'power_discharge_positive_kW':stat(p),'SOC_percent':stat(soc),'net_energy_kWh':integ(p)/3600,'gross_discharge_kWh':integ(np.maximum(p,0))/3600,'gross_recovered_kWh':-integ(np.minimum(p,0))/3600,'net_Ah':integ(i)/3600,'reported_power_vs_VI_max_error_kW':float(max(abs(p+col('battery','Power')))),'samples_power_near45kW_within0p25':int(near.sum())},'generator':gen,'generator_off':off,'empirical_comparison':{'voltage_current_sample_window_s':[21,float(t[-1])],'initialization_window_excluded_s':[0,20],'voltage_V':ve,'current_A':ie,'energy_window_s':[20,float(t[-1])],'model_net_kWh':energy,'reference_net_kWh':re,'energy_error_percent':enerr,'reference_VI_net_kWh':integ(ref['meter_voltage_V']*ref['meter_current_A_discharge_positive']/1000,nt,20,t[-1])/3600,'reference_full_phase_net_kWh':integ(pr,nt)/3600,'reference_peak_discharge_kW':float(max(pr)),'scope':'Independent driving test with fixed previous maps/aux; first-point voltage used for initialization, not independent SOC identification; tracking adequacy required for interpretation','SOC_coordinate':'No physical/CAN model coordinate mapping; endpoint SOC error not scored'},'existing_proposed_targets':{'voltage_RMSE_limit_V':2,'absolute_voltage_bias_limit_V':1,'absolute_energy_error_limit_percent':5,'voltage_RMSE_met':ve['RMSE']<=2,'voltage_bias_met':abs(ve['bias'])<=1,'energy_met':abs(enerr)<=5,'basis':'Existing research proposals, not certification acceptance'},'BMS_diagnosis':{'existing_example_limit_kW':45,'reference_peak_kW':float(max(pr)),'inference':'Model power saturation and simultaneous speed deficit may implicate retained example limit; CSV lacks commanded BMS limit signal, so causality is not conclusively isolated','physical_Bolt_limit_identified':False}}
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item())+'\n')
with (out/'aligned_diagnostics.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['time_s','actual_kmh','desired_kmh','tracking_error_kmh','model_voltage_V','reference_voltage_V','model_discharge_current_A','reference_discharge_current_A','model_discharge_power_kW','reference_discharge_power_kW']);w.writerows(zip(t,act,des,err,v,vr,i,ir,p,rp))
print(json.dumps({k:report[k] for k in ['condition_checks','tracking','battery','generator_off','empirical_comparison','existing_proposed_targets']},ensure_ascii=False,default=lambda x:x.item()))
