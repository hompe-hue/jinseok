"""Read-only TDMS provenance, dyno metadata and boundary diagnostics. No parameter fit."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
from nptdms import TdmsFile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/remaining_source_evidence_20261013';OUT.mkdir(exist_ok=True)
source_root=Path(sys.argv[1]);results=[];metadata=[]
def integral(t,p,lo,hi):
    assert np.all(np.isfinite(t)) and np.all(np.isfinite(p)) and np.all(np.diff(t)>0)
    assert t[0]<=lo and t[-1]>=hi
    tt=np.r_[lo,t[(t>lo)&(t<hi)],hi]
    return float(np.trapezoid(np.interp(tt,t,p),tt)/3600)
for test,end in [('61905060',3150),('61905061',1489)]:
    path=source_root/f'ANL{test}_Raw_Source/{test}_Analysis.tdms';g=TdmsFile.read(path).groups()[0]
    s=int(g.properties['Phase_1_Phase_Start_Fill_Index'])-1;e=int(g.properties['Phase_1_Phase_Stop_Fill_Index'])
    def c(name):return np.asarray(g[name][s:e],float)
    origin=c('Time_H0')[0];td=c('Time_1')-origin;tc=c('Time_3')-origin;th=c('Time_H0')-origin
    def unique(t,*arrays):
        k=np.r_[np.diff(t)>0,True];t=t[k]
        assert np.all(np.diff(t)>0)
        return [t]+[a[k] for a in arrays]
    dyn=[c(n) for n in ['Dyno_Spd_Front','Dyno_TractiveForce_Front','Dyno_LoadCell_Front','Dyno_Spd_Rear']]
    td,vmph,force,loadcell,rear=unique(td,*dyn)
    tc,ns,nq,iv,vv,oil,mtemp,invt=unique(tc,*[c(n) for n in ['Motor_1_speed_DMCM1','Motor_1_torque_DMCM1','Motor_1_current_DMCM1','Motor_1_HV_circuit_voltage_DMCM1','Trans_oil_temp_CAN','Motor_1_temp_calc_DMCM1','Motor_1_inverter_temp_sensor1_DMCM1']])
    gp={k:str(v) for k,v in g.properties.items() if any(x in k for x in ['Dyno_Target','Dyno_Set','Dyno_Test_Weight','Dyno_Config','Dyno_Mode','Vehicle_Name','Test_Cycle_File_Name'])}
    # US road-load convention; metadata names do not themselves declare ABC units.
    conv=np.array([4.4482216152605,4.4482216152605/1.609344,4.4482216152605/1.609344**2])
    target=np.array([float(g.properties['TestInfo_Dyno_Target_'+n]) for n in 'ABC'])*conv
    setting=np.array([float(g.properties['TestInfo_Dyno_Set_'+n]) for n in 'ABC'])*conv
    actual=np.array([126.329494,.557775,.033456276])
    v=vmph*1.609344;ms=v/3.6
    def abc_power(a):return (a[0]+a[1]*v+a[2]*v*v)*ms/1000
    targetwork=integral(td,abc_power(target),20,end);setwork=integral(td,abc_power(setting),20,end)
    # Kinematic effective-radius diagnostic only; keep time mapping without fitted lag.
    rpm=np.interp(td,tc,ns);acc=np.gradient(ms,td)
    mask=(td>=20)&(td<=end)&(v>30)&(abs(acc)<.2)&(rpm>100)
    rr=ms[mask]*7.05*60/(2*np.pi*rpm[mask]);assert len(rr)>100
    maskc=(tc>=20)&(tc<=end)
    prior=json.loads((ROOT/f'independent_tests_20261013/ANL{test}/checkpoint.json').read_text())
    source_hash=hashlib.sha256(path.read_bytes()).hexdigest();assert source_hash==prior['source_sha256']
    assert np.all(np.abs(target-actual)<1e-6)
    assert abs(float(g.properties['TestInfo_Dyno_Test_Weight_lb'])*.45359237-1757.6704)<1e-3
    row=dict(test=test,source_sha256=source_hash,source_hash_matches_prior=True,window_s=[20,end],
        metadata=gp,target_ABC_N_kmh=target.tolist(),set_ABC_N_kmh=setting.tolist(),
        target_minus_model_ABC= (target-actual).tolist(),test_mass_kg=float(g.properties['TestInfo_Dyno_Test_Weight_lb'])*.45359237,
        target_ABC_work_kWh=targetwork,set_ABC_work_kWh=setwork,target_minus_set_work_kWh=targetwork-setwork,
        dyno_front_force_speed_candidate_work_kWh=integral(td,force*ms/1000,20,end),dyno_front_loadcell_speed_candidate_work_kWh=integral(td,loadcell*ms/1000,20,end),
        rear_dyno_speed_max_mph=float(abs(rear).max()),
        kinematic_radius_diagnostic=dict(samples=int(mask.sum()),median_m=float(np.median(rr)),p10_m=float(np.quantile(rr,.1)),p90_m=float(np.quantile(rr,.9)),model_radius_m=.3135,
            caution='Not a calibrated tire-radius measurement: CAN rpm and dyno speed synchronization/scaling, tire slip and effective circumference remain confounded. No lag/radius fitted.'),
        reported_CAN_range=dict(motor_HV_voltage_V=[float(vv[maskc].min()),float(vv[maskc].max())],transmission_oil_C=[float(oil[maskc].min()),float(oil[maskc].max())],motor_calculated_temp_C=[float(mtemp[maskc].min()),float(mtemp[maskc].max())],inverter_sensor1_C=[float(invt[maskc].min()),float(invt[maskc].max())]),
        caveats=['ABC metadata units are interpreted using the documented US convention, not declared by these strings alone.','Set coefficients compensate vehicle-on-dyno losses; must not replace road target with set coefficients in the whole vehicle model.','Force-speed products are channel-boundary diagnostics, not independently certified wheel/shaft power.'])
    results.append(row)
    names=['Dyno_Spd_Front','Dyno_TractiveForce_Front','Dyno_LoadCell_Front','Dyno_Spd_Rear','Motor_1_current_DMCM1','Motor_1_HV_circuit_voltage_DMCM1','Motor_1_torque_DMCM1','Motor_1_speed_DMCM1','Batt_Power_Hioki_P1','Motor_1_phase_u_current_DMCM1','Motor_1_phase_v_current_DMCM1','Motor_1_phase_w_current_DMCM1']
    selected={n:{k:str(v) for k,v in g[n].properties.items() if k in ['unit_string','description','Comment','Location','Enabled','Scale_Type','wf_increment','wf_start_offset']} for n in names if n in g}
    metadata.append(dict(test=test,group_metadata=gp,channels=selected))
    pd.DataFrame(dict(time_s=td,dyno_speed_kmh=v,tractive_force_N=force,loadcell_N=loadcell,interpolated_CAN_rpm=rpm,target_ABC_kW=abc_power(target),set_ABC_kW=abc_power(setting),steady_radius_selection=mask)).to_csv(OUT/f'ANL{test}_boundary_samples.csv',index=False)
(OUT/'summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
(OUT/'selected_TDMS_metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
# Exposure of the entire zero-torque EDU electrical loss, not a neutral drag estimate.
zero=pd.read_csv(ROOT/'runs/regen_zero_torque_bridge_20261013/Q1_zero_torque_nodes.csv');exposure=[]
for test,end in [('61905060',3150),('61905061',1489)]:
    suffix='(1)' if test=='61905060' else ''
    d=pd.read_csv(ROOT/f'runs/ANL{test}_20261013/velocity_ANL{test}{suffix}.csv',skiprows=[1])
    z=np.interp(abs(d['In/E-Motor Speed (Vehicle Monitor)']),zero.rpm,zero.loss)
    exposure.append(dict(test=test,window_s=[20,end],map_zero_torque_total_loss_exposure_kWh=integral(d.Time.to_numpy(),z,20,end),
        caution='Whole inverter/motor/gearing electrical zero-torque loss; not identified mechanical neutral drag; must not subtract it from ABC or DC consumption.'))
(OUT/'zero_torque_loss_exposure.json').write_text(json.dumps(exposure,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
