"""Audit actual exported CRUISE traces. Templates intentionally cannot pass.
Required CSV: time_s,speed_kmh,motor_speed_rpm,motor_torque_Nm,pack_voltage_V,
pack_current_A,soc_fraction. Positive battery current means discharge.
For EREV additionally: fuel_g_s,engine_on,stored_energy_kWh.
Run: python scripts/evaluate_cruise_trace.py trace.csv metadata.json --output result.json
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import Delaunay

ROOT=Path(__file__).resolve().parents[1]

def integral(t,y):return float(np.trapezoid(y,t))

def map_monitor(d):
    a=pd.read_csv(ROOT/'inputs/bolt_map_provenance_and_limits.csv')
    limits=pd.read_csv(ROOT/'inputs/bolt_full_load_limits.csv')
    raw=pd.read_csv(ROOT/'inputs/bolt_measured_test_points.csv')
    ns=np.sort(a.speed_rpm.unique());ts=np.sort(a.torque_Nm.unique())
    loss=a.pivot(index='speed_rpm',columns='torque_Nm',values='loss_kW').reindex(index=ns,columns=ts).to_numpy()
    lookup=RegularGridInterpolator((ns,ts),loss,bounds_error=False,fill_value=np.nan)
    hull=Delaunay(raw[['motor_equivalent_speed_rpm','motor_equivalent_torque_Nm']].to_numpy())
    n=d.motor_speed_rpm.to_numpy();t=d.motor_torque_Nm.to_numpy();omega=n*2*np.pi/60
    lim=limits[limits.speed_rpm>=0].sort_values('speed_rpm')
    hi=np.interp(n,lim.speed_rpm,lim.Q1_torque_Nm);lo=np.interp(n,lim.speed_rpm,lim.Q4_torque_Nm)
    in_rectangle=(n>=ns[0])&(n<=ns[-1])&(t>=ts[0])&(t<=ts[-1])
    allowed=in_rectangle&(n<=8250)&(t<=hi+1e-7)&(t>=lo-1e-7)&(abs(omega*t)<=150000+1e-7)
    predicted_loss=lookup(np.column_stack([n,t])); predicted_loss[~allowed]=np.nan
    support=np.where(t<0,'REGEN_ESTIMATE_1p05',np.where(hull.find_simplex(np.column_stack([n,t]))>=0,'COMPLETED_INSIDE_MEASURED_HULL','COMPLETED_OUTSIDE_MEASURED_HULL'))
    support[~allowed]='OUTSIDE_ALLOWED_DOMAIN'
    shaft=omega*t/1000; electrical=shaft+predicted_loss
    row=np.clip(np.searchsorted(ns,n,side='right')-1,0,len(ns)-2)
    col=np.clip(np.searchsorted(ts,t,side='right')-1,0,len(ts)-2)
    h=a.pivot(index='speed_rpm',columns='torque_Nm',values='inside_measured_point_convex_hull').reindex(index=ns,columns=ts).to_numpy().astype(bool)
    envelope=a.pivot(index='speed_rpm',columns='torque_Nm',values='runtime_allowed').reindex(index=ns,columns=ts).to_numpy().astype(bool)
    stencil_outside_hull=~(h[row,col]&h[row+1,col]&h[row,col+1]&h[row+1,col+1])
    stencil_outside_envelope=~(envelope[row,col]&envelope[row+1,col]&envelope[row,col+1]&envelope[row+1,col+1])
    return allowed,support,shaft,electrical,stencil_outside_hull,stencil_outside_envelope

def evaluate(df,meta):
    required=['time_s','speed_kmh','motor_speed_rpm','motor_torque_Nm','pack_voltage_V','pack_current_A','soc_fraction']
    if not set(required)<=set(df):raise ValueError('Missing required trace columns')
    if len(df)<2:raise ValueError('At least two actual output rows are required')
    if not np.isfinite(df[required].to_numpy()).all():raise ValueError('Nonfinite required observations')
    t=df.time_s.to_numpy()
    if not (np.diff(t)>0).all():raise ValueError('Time must increase strictly; resolve clock duplicates first')
    if (np.diff(t)>meta.get('maximum_export_gap_s',2.)).any():raise ValueError('Export gaps exceed declared maximum')
    if not df.soc_fraction.between(0,1).all():raise ValueError('SOC must be fraction, not percent')
    if (df.speed_kmh<0).any():raise ValueError('This evaluator requires forward vehicle speed')
    allowed,support,shaft,electric,stencil_hull,stencil_envelope=map_monitor(df)
    distance=integral(t,df.speed_kmh)/3600
    netdc=integral(t,df.pack_voltage_V*df.pack_current_A/1000)/3600
    monitor=[]
    # Energy per class: integrate interval mechanical throughput; no interpolation across classes.
    dt=np.diff(t); weights=(abs(shaft[:-1])+abs(shaft[1:]))*.5*dt/3600
    for kind in sorted(set(support)):
        ix=support[:-1]==kind
        monitor.append({'class':kind,'sample_rows':int((support==kind).sum()),'interval_start_class_mechanical_throughput_kWh':float(weights[ix].sum())})
    blockers=[]
    if meta.get('origin')!='CRUISE_M_actual_export':blockers.append('Trace is not declared an actual CRUISE M export')
    if not allowed.all():blockers.append('Operating point outside full-load/speed/power or rectangular bounds')
    if meta.get('soc_definition') not in ['model_coulomb_SOC','ANL_displayed_SOC','ANL_HPCM2_SOC','ANL_HPCM_SOC']:blockers.append('SOC definition unspecified')
    for key in ['battery_parameter_id','vehicle_model_id','cycle_id','temperature_condition','auxiliary_condition','initialization_id','energy_boundary']:
        if not meta.get(key):blockers.append('Missing comparison metadata: '+key)
    out={'status':'OFFLINE_TRACE_AUDIT','CRUISE_M_run_verified_by_this_script':False,'distance_km':distance,'net_battery_DC_kWh':netdc,
         'net_battery_DC_kWh_per_100km':netdc/distance*100 if distance>0 else None,
         'start_SOC_fraction':float(df.soc_fraction.iloc[0]),'end_SOC_fraction':float(df.soc_fraction.iloc[-1]),
         'map_support':monitor,'map_outside_domain_rows':int((~allowed).sum()),
         'bilinear_stencil_has_outside_measured_hull_nodes_rows':int((stencil_hull&allowed).sum()),
         'bilinear_stencil_has_outside_full_load_nodes_rows':int((stencil_envelope&allowed).sum()),
         'pack_voltage_observed_min_max_V':[float(df.pack_voltage_V.min()),float(df.pack_voltage_V.max())],
         'EDU_single_voltage_map_V':400,'EDU_voltage_dependence_unidentified':True,
         'battery_model_validation_passed':meta.get('battery_validation_status')=='PASS_ON_INDEPENDENT_DATA',
         'label_comparison_ready':False,'full_range_claim_ready':False,'blockers':blockers,'metadata':meta}
    if not out['battery_model_validation_passed']:blockers.append('Battery has not passed independent SOC/current/voltage validation')
    if meta.get('powertrain_validation_status')!='PASS_ON_INDEPENDENT_DATA':blockers.append('Powertrain has not passed independent cycle validation')
    if meta.get('powertrain')=='EREV':
        for key in ['genset_parameter_id','fuel_map_id']:
            if not meta.get(key):blockers.append('Missing comparison metadata: '+key)
        fields=['fuel_g_s','engine_on','stored_energy_kWh']
        if not set(fields)<=set(df) or not np.isfinite(df[fields].to_numpy()).all():
            blockers.append('Missing finite EREV fuel/start/stored-energy observations')
        else:
            if (df.fuel_g_s<0).any():raise ValueError('Negative fuel flow')
            fuel=integral(t,df.fuel_g_s)/1000
            on=df.engine_on.to_numpy()>0.5
            starts=int((~on[:-1]&on[1:]).sum())+int(on[0])
            density=meta.get('fuel_density_kg_L')
            out.update({'fuel_kg':fuel,'fuel_L':fuel/density if isinstance(density,(int,float)) and density>0 else None,'fuel_kg_per_100km':fuel/distance*100 if distance>0 else None,
                'engine_on_entries_including_initial_on':starts,'start_stored_energy_kWh':float(df.stored_energy_kWh.iloc[0]),'end_stored_energy_kWh':float(df.stored_energy_kWh.iloc[-1])})
            if not meta.get('start_and_warmup_fuel_included'):blockers.append('Fuel is steady-state-only or start/warmup inclusion unspecified')
            if not meta.get('fuel_map_validity_checked'):blockers.append('Fuel map operating bounds not checked')
    # Full range needs observed successful depletion of both declared energy inventories.
    for key in ['range_stop_event_verified','speed_tracking_passed','mission_initial_inventories_recorded']:
        if not meta.get(key):blockers.append('Range gate not satisfied: '+key)
    out['full_range_claim_ready']=not blockers
    out['comparison_ready_without_range_claim']=not [b for b in blockers if not b.startswith('Range gate')]
    return out

def compare(a,b,initial_tolerance=.1,terminal_tolerance=.1):
    """Fuel ordering is accepted only for equal conditions and stored energy.
    These tolerances are declared research settings, not certification standards.
    No fuel-equivalent correction is silently invented.
    """
    mismatch=[]
    for key in ['vehicle_model_id','battery_parameter_id','soc_definition','cycle_id','temperature_condition','auxiliary_condition','initialization_id','energy_boundary','genset_parameter_id','fuel_map_id']:
        va=a['metadata'].get(key);vb=b['metadata'].get(key)
        if va is None or va!=vb:mismatch.append('Different or missing '+key)
    for key,tolerance in [('start_stored_energy_kWh',initial_tolerance),('end_stored_energy_kWh',terminal_tolerance)]:
        if key not in a or key not in b or abs(a[key]-b[key])>tolerance:mismatch.append('Stored energy not matched: '+key)
    if not a.get('comparison_ready_without_range_claim') or not b.get('comparison_ready_without_range_claim'):mismatch.append('Trace audit gates unresolved')
    return {'fuel_comparison_accepted':not mismatch,'reasons':mismatch,'fuel_difference_kg_B_minus_A':b.get('fuel_kg',0)-a.get('fuel_kg',0) if not mismatch else None,'terminal_energy_tolerance_kWh':terminal_tolerance}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('trace',type=Path);ap.add_argument('metadata',type=Path);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();r=evaluate(pd.read_csv(args.trace),json.loads(args.metadata.read_text()))
    args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False));print(r['status'],r['blockers'])
