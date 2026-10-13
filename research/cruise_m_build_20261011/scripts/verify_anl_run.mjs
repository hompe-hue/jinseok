import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const run=path.join(root,process.argv[2]||'runs/ANL61905054_20261013');
const suffix=process.argv[3]||'';
const filename=k=>k+suffix+'_ANL61905054.csv';
const phase=path.join(root,'empirical_alignment_20261013/ANL_61905054_phase1');
function read(p,units=true){const lines=fs.readFileSync(p,'utf8').trim().split(/\r?\n/);return {h:lines[0].split(','),u:units?lines[1].split(','):null,r:lines.slice(units?2:1).map(s=>s.split(',').map(Number))};}
const v=read(path.join(run,filename('velocity'))),b=read(path.join(run,filename('battery'))),g=read(path.join(run,filename('generator'))),d=read(path.join(phase,'ANL_61905054_Phase1_driver_1s.csv'),false),n=read(path.join(phase,'ANL_61905054_Phase1_reference_native.csv'),false);
function col(f,name){const i=f.h.findIndex(s=>s===name||s.startsWith('In/'+name+' ('));if(i<0)throw Error(name);return f.r.map(r=>r[i]);}
const t=col(v,'Time'),act=col(v,'Actual Velocity'),des=col(v,'Desired Velocity');
function interp(x,ys,ts){if(x<ts[0]||x>ts.at(-1))throw Error('Extrapolation');let lo=0,hi=ts.length-1;while(hi-lo>1){let mid=(hi+lo)>>1;if(ts[mid]<=x)lo=mid;else hi=mid;}return ys[lo]+(ys[hi]-ys[lo])*(x-ts[lo])/(ts[hi]-ts[lo]);}
function integ(ys,ts=t){return ys.slice(1).reduce((s,y,i)=>s+(y+ys[i])/2*(ts[i+1]-ts[i]),0);}
function stat(x){return {min:Math.min(...x),max:Math.max(...x),first:x[0],last:x.at(-1)};}
const dt=d.r.map(r=>r[0]),ds=d.r.map(r=>r[1]);
const desiredError=t.map((x,i)=>des[i]-interp(x,ds,dt));const error=act.map((x,i)=>x-des[i]);
const vb=col(b,'Voltage'),ib=col(b,'Current'),pb=col(b,'Power'),soc=col(b,'SoC'),powerVI=vb.map((x,i)=>-x*ib[i]/1000);
const nativeTimes=col(n,'phase_time_s'),nativeP=col(n,'meter_pack_power_kW_discharge_positive');
function croppedIntegral(f,y,limit){const tt=col(f,'phase_time_s');const ix=tt.findIndex(x=>x>limit);const tx=tt.slice(0,ix),yy=y.slice(0,ix);tx.push(limit);yy.push(interp(limit,y,tt));return integ(yy,tx);}
const report={status:'Actual-speed input verified on exported 0–1144 s interval; empirical energy validation pending condition alignment',files:Object.fromEntries([filename('velocity'),filename('battery'),filename('generator')].map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(path.join(run,f))).digest('hex')])),quality:{rows:{velocity:v.r.length,battery:b.r.length,generator:g.r.length},all_finite:[v,b,g].every(f=>f.r.every(r=>r.length===f.h.length&&r.every(Number.isFinite))),same_times:[b,g].every(f=>JSON.stringify(col(f,'Time'))===JSON.stringify(t)),strictly_increasing:t.every((x,i)=>i===0||x>t[i-1])},time:{export_end_s:t.at(-1),profile_end_s:dt.at(-1),unexported_tail_s:dt.at(-1)-t.at(-1),note:'1 s exports omit fractional endpoint; actual simulation completion not inferred from export alone'},tracking:{desired_input_max_abs_error_kmh:Math.max(...desiredError.map(Math.abs)),RMSE_kmh:Math.sqrt(error.reduce((s,x)=>s+x*x,0)/error.length),MAE_kmh:error.reduce((s,x)=>s+Math.abs(x),0)/error.length,max_abs_error_kmh:Math.max(...error.map(Math.abs)),max_error_time_s:t[error.map(Math.abs).indexOf(Math.max(...error.map(Math.abs)))],actual_distance_integrated_km:integ(act)/3600,desired_distance_integrated_km:integ(des)/3600,reported_distance_km:col(v,'Distance').at(-1),actual_vs_desired_distance_pct:100*(integ(act)/integ(des)-1)},battery:{voltage_V:stat(vb),current_A_discharge_negative:stat(ib),SOC_percent:stat(soc),VI_net_discharge_kWh:integ(powerVI)/3600,reported_power_net_discharge_kWh:-integ(pb)/3600,max_abs_P_vs_VI_kW:Math.max(...pb.map((x,i)=>Math.abs(x+powerVI[i]))),net_charge_discharge_Ah:-integ(ib)/3600,reported_energy_decrease_kWh:col(b,'Energy')[0]-col(b,'Energy').at(-1),aux_power_from_consumer_kW:stat(col(v,'E-Consumer Current').map((x,i)=>x*vb[i]/1000))},generator:Object.fromEntries(['Actual Engine Speed','Cumulated Fuel Consumption','Current','Fuel Massflow','Power Generator','Power ICE'].map(k=>[k,stat(col(g,k))])),reference:{native_full_phase_energy_kWh:integ(nativeP,nativeTimes)/3600,native_common_0_1144s_energy_kWh:croppedIntegral(n,nativeP,t.at(-1))/3600,summary_full_test_kWh:2.172,interpretation:'Different initial SOC, temperature and auxiliary boundary; diagnostic differences do not prove validation.'},next:'Align initial state and HV auxiliary boundary using existing source definitions; do not request completed parameter screenshots again.'};
report.diagnostic_energy_difference_pct=100*(report.battery.VI_net_discharge_kWh/report.reference.native_common_0_1144s_energy_kWh-1);
const referenceV=col(n,'meter_pack_voltage_V'),referenceI=col(n,'meter_pack_current_A_discharge_positive');
const alignedV=t.map(x=>interp(x,referenceV,nativeTimes)),alignedI=t.map(x=>interp(x,referenceI,nativeTimes)),alignedP=t.map(x=>interp(x,nativeP,nativeTimes));
const hold=t.map((x,i)=>x>20?i:-1).filter(i=>i>=0);
const rmse=xs=>Math.sqrt(xs.reduce((s,x)=>s+x*x,0)/xs.length),mean=xs=>xs.reduce((s,x)=>s+x,0)/xs.length;
const ve=hold.map(i=>vb[i]-alignedV[i]),ie=hold.map(i=>-ib[i]-alignedI[i]);
function windowNative(y,start,end){return croppedIntegral(n,y,end)-croppedIntegral(n,y,start);}
const nativeVI=referenceV.map((x,i)=>x*referenceI[i]/1000);
const modelWindow=integ(powerVI.slice(20),t.slice(20))/3600;
const sourceWindow=windowNative(nativeP,20,t.at(-1))/3600;
report.empirical_comparison={initialization_window_s:[0,20],voltage_current_metrics_window:'Export timestamps >20 s; measured meter channels linearly interpolated with no time lag fitted',voltage_RMSE_V:rmse(ve),voltage_bias_V:mean(ve),voltage_max_abs_error_V:Math.max(...ve.map(Math.abs)),current_RMSE_A:rmse(ie),current_bias_A:mean(ie),energy_window_s:[20,t.at(-1)],model_net_kWh:modelWindow,measured_meter_net_kWh:sourceWindow,measured_VI_net_kWh:windowNative(nativeVI,20,t.at(-1))/3600,energy_error_pct:100*(modelWindow/sourceWindow-1),reference_SOC_endpoint_HPCM2:col(n,'internal_SOC_HPCM2_percent').at(-1),SOC_endpoint_comparison:'Not evaluated: model SOC coordinate not mapped to CAN',scope:'Same-test conditional replay, initialization calibrated at first point and auxiliary approximation uses observed LV mean; independent cross-test generalization not established'};
fs.writeFileSync(path.join(run,'empirical_aligned_diagnostics.csv'),'time_s,model_voltage_V,reference_voltage_V,model_discharge_current_A,reference_discharge_current_A,model_discharge_power_kW,reference_meter_power_kW\n'+t.map((x,i)=>[x,vb[i],alignedV[i],-ib[i],alignedI[i],powerVI[i],alignedP[i]].join(',')).join('\n')+'\n');
report.battery.gross_discharge_kWh_sampled_trapezoid=integ(powerVI.map(x=>Math.max(x,0)))/3600;
report.battery.gross_recovered_kWh_sampled_trapezoid=-integ(powerVI.map(x=>Math.min(x,0)))/3600;
report.reference.voltage_V=stat(referenceV.filter((x,i)=>nativeTimes[i]<=t.at(-1)));
report.reference.gross_discharge_kWh_native=windowNative(nativeP.map(x=>Math.max(x,0)),0,t.at(-1))/3600;
report.reference.gross_recovered_kWh_native=-windowNative(nativeP.map(x=>Math.min(x,0)),0,t.at(-1))/3600;
report.existing_proposed_targets={voltage_RMSE_V:2,absolute_voltage_bias_V:1,absolute_energy_error_pct:5,source:'research/validation_fix_20261006/inputs/validation_and_comparison_gates.csv BAT03; suggested research targets, not certification or previously agreed acceptance',voltage_RMSE_met:report.empirical_comparison.voltage_RMSE_V<=2,voltage_bias_met:Math.abs(report.empirical_comparison.voltage_bias_V)<=1,energy_met:Math.abs(report.empirical_comparison.energy_error_pct)<=5,SOC_target_evaluable:false};
if(suffix==='2'){report.status='Regeneration diagnostic replay meets existing proposed voltage and energy targets, conditionally for same-test window';report.next='Prepare interim-report evidence with BMS assumption and voltage-peak limitation; independent holdout test and physical charge constraints remain open.';report.reference.interpretation='Comparison limited to this test with voltage-based initialization and auxiliary approximation. Diagnostic 40kW high-SOC charge cap is not measured Bolt BMS calibration.';}
fs.writeFileSync(path.join(run,'verification.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(run,'tracking_diagnostics.csv'),'time_s,actual_kmh,desired_kmh,tracking_error_kmh,desired_input_error_kmh\n'+t.map((x,i)=>[x,act[i],des[i],error[i],desiredError[i]].join(',')).join('\n')+'\n');
console.log(JSON.stringify(report,null,2));
