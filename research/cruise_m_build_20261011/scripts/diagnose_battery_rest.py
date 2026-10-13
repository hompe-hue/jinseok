"""Frozen-model low-load voltage diagnostic; no OCV/R fitting or chemical SOC claim."""
from pathlib import Path
import json,csv
import numpy as np
root=Path(__file__).resolve().parents[1]
for test in ['61905060','61905061']:
 run=root/f'runs/ANL{test}_20261013';o=run/'battery_rest_diagnosis';o.mkdir(exist_ok=True)
 a=np.genfromtxt(run/'aligned_diagnostics.csv',delimiter=',',names=True);t=a['time_s'];bv=next(run.glob('battery_ANL*.csv'));rows=list(csv.reader(bv.open()));h=rows[0];b=np.array(rows[2:],float);soc=b[:,next(i for i,x in enumerate(h) if x.startswith('In/SoC ('))]
 res=np.loadtxt(root/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2);rp=32*np.interp(soc/100,res[:,0],res[:,1]);dv=a['model_voltage_V']-a['reference_voltage_V'];di=a['model_discharge_current_A']-a['reference_discharge_current_A']
 mask=(t>20)&(abs(a['desired_kmh'])<.1)&(abs(a['actual_kmh'])<.1)&(abs(a['reference_discharge_current_A'])<3)&(abs(a['model_discharge_current_A'])<3)
 idx=np.flatnonzero(mask);groups=np.split(idx,np.flatnonzero(np.diff(idx)>1)+1) if len(idx) else [];intervals=[]
 for ix in groups:
  if len(ix)<11:continue
  intervals.append({'start_s':float(t[ix[0]]),'end_s':float(t[ix[-1]]),'duration_s':float(t[ix[-1]]-t[ix[0]]),'voltage_bias_V':float(np.mean(dv[ix])),'voltage_RMSE_V':float(np.sqrt(np.mean(dv[ix]**2))),'observed_reference_voltage_change_V':float(a['reference_voltage_V'][ix[-1]]-a['reference_voltage_V'][ix[0]]),'model_voltage_change_V':float(a['model_voltage_V'][ix[-1]]-a['model_voltage_V'][ix[0]]),'mean_current_difference_A':float(np.mean(di[ix])),'current_difference_drop_using_existing_R_V':float(np.mean(-rp[ix]*di[ix])),'model_SOC_first_last_percent':[float(soc[ix[0]]),float(soc[ix[-1]])]})
 report={'test_id':test,'selection':'Post20s, measured/model speed<0.1kmh, abs measured/model current<3A; contiguous rest windows>=10s','selected_lowload_samples':len(idx),'rest_intervals':intervals,'existing_R_model_scope':'Current imported 25C single-temperature static OCV/R model;32*cellR for96S3P','interpretation':'Voltage residual persisting at low current is not explained by load-current difference alone. Do not call short stops equilibrium OCV; prior polarization, initial history, OCV coordinates, temperature or measurement definition may contribute. R/OCV not fitted.','next':'Require physical battery dynamic/OCV validation evidence before changing model; keep mismatch in interim report, do not tune initial SOC to held-out voltage.'}
 (o/'diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 with (o/'rest_voltage_samples.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['time_s','model_voltage_V','reference_voltage_V','voltage_error_V','current_difference_A','existing_Rpack_ohm','current_difference_voltage_drop_V']);w.writerows(zip(t[idx],a['model_voltage_V'][idx],a['reference_voltage_V'][idx],dv[idx],di[idx],rp[idx],-rp[idx]*di[idx]))
 print(json.dumps({'test_id':test,'selected_samples':len(idx),'intervals':intervals},ensure_ascii=False))
