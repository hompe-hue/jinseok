"""Bind the uploaded DIS80 saved state to existing outputs, without running CRUISE.

All objects are found by semantic type and table contents, not historic IDs.
Output agreement is consistency evidence, not cryptographic runtime provenance.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from audit_dis80_semantic import SavedProject,ROOT,OUT

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def col(d,prefix):
    names=[x for x in d if x.startswith('In/'+prefix+' (')]
    assert len(names)==1,(prefix,names)
    return d[names[0]].to_numpy()

def main():
    source=Path(sys.argv[1]);p=SavedProject(source)
    run=ROOT/'runs/ANL61905060_DIS80_20261013'
    v=pd.read_csv(run/'velocity_ANL61905060DIS80.csv',skiprows=[1])
    b=pd.read_csv(run/'battery_ANL61905060DIS80.csv',skiprows=[1])
    assert np.array_equal(v.Time,b.Time)
    driver=pd.read_csv(ROOT/'independent_tests_20261013/ANL61905060/driver_1s.csv')
    candidates=[]
    for n in p.nodes('cruise.props.tasks.profile.VelocityProfileTime'):
        arrays=p.arrays_under(n)
        if len(arrays)!=7 or len(arrays[0][2])!=len(driver):continue
        t,s=arrays[0][2],arrays[1][2]
        if np.max(abs(t-driver.time_s.to_numpy()))<1e-9 and np.max(abs(s-driver.speed_kmh.to_numpy()))<1e-9:
            candidates.append((n,arrays))
    assert len(candidates)==1
    profile,arrays=candidates[0]
    desired_error=float(np.max(abs(np.interp(v.Time,arrays[0][2],arrays[1][2])-col(v,'Desired Velocity'))))
    assert desired_error<1e-6
    initial=[p.amount(n,'initial_charge') for n in p.nodes('cruise.props.battery.InitialConditions')]
    assert len(initial)==2 and all(abs(x-col(b,'SoC')[0])<1e-6 for x in initial)
    limits=[]
    for n in p.nodes('cruise.props.general_map.GeneralCharacteristic'):
        aa=p.arrays_under(n)
        if len(aa)==2 and np.array_equal(aa[0][2],[0,20,30,40,75,85,99.5]):
            limits.append({'serializer_id':n.get('id'),'SOC_percent':aa[0][2].tolist(),'discharge_limit_kW':aa[1][2].tolist()})
    assert len(limits)==1 and limits[0]['discharge_limit_kW']==[0,0,24,80,80,80,80]
    aux=p.amount(p.nodes('cruise.props.basic_electric_components.PowerConsumerGeneral')[0],'power')
    assert aux==.4
    battery_maps=[]
    for type_suffix,file in [('IdleVoltage','Bolt_Cell_OCV_25C.dat'),('OhmicResistanceCharge','Bolt_Cell_Resistance_25C.dat'),('OhmicResistanceDischarge','Bolt_Cell_Resistance_25C.dat')]:
        expected=np.loadtxt(ROOT/'inputs/battery'/file,skiprows=2)
        for i,n in enumerate(p.nodes('cruise.props.commons_battery.'+type_suffix)):
            aa=p.arrays_under(n);assert len(aa)==3
            actual=np.c_[aa[1][2],aa[2][2]]
            assert actual.shape==expected.shape
            err=float(np.max(abs(actual-expected)));assert err<1e-10
            battery_maps.append({'type':type_suffix,'module_occurrence':i,'max_difference':err,'input_sha256':sha(ROOT/'inputs/battery'/file)})
    lines=(ROOT/'inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat').read_text().splitlines()
    q=np.array([float(x) for x in lines[5].split()]);w=np.array([float(x) for x in lines[8].split()]);loss=np.array([[float(x) for x in row.split()] for row in lines[11:]])
    lookup=RegularGridInterpolator((q,w),loss,bounds_error=False,fill_value=np.nan)
    motor=[];zero=None
    for n in p.nodes('cruise.props.electric_machine.PowerLoss'):
        aa=p.arrays_under(n)
        if len(aa)!=5 or not len(aa[0][2]):continue
        temp,vv,rpm,tq,pl=[a[2] for a in aa]
        if not np.all(vv==400):continue
        pred=lookup(np.c_[tq,rpm*2*np.pi/60])/1000
        assert np.isfinite(pred).all()
        err=float(np.max(abs(pred-pl)));assert err<1e-12
        label='Q1' if tq.min()>=0 else 'Q4'
        motor.append({'quadrant':label,'rows':len(pl),'max_difference_from_original_kW':err})
        if label=='Q1':
            mask=tq==0;order=np.argsort(rpm[mask]);zero=(rpm[mask][order],pl[mask][order])
    assert len(motor)==2 and zero is not None
    profile_summary={'serializer_id':profile.get('id'),'columns':7,'rows':len(arrays[0][2]),'end_s':float(arrays[0][2][-1]),'full_profile_matches060':True,'exported_desired_speed_matches':True,'max_export_desired_speed_difference_kmh':desired_error,'tolerance_kmh':1e-6}
    abc_node=p.nodes('cruise.props.vehicle.ResistanceFunction')[0]
    abc=[p.amount(abc_node,k) for k in ['constant_part','linear_part','square_part']]
    audit={'project_sha256':sha(source),'source_library_file_id':'libfile_2c19e581644c819189bc1ea13487aaee',
        'CRC_passed':True,'profile':profile_summary,'initial_SOC_percent':initial,'limit_table':limits[0],
        'aux_kW':aux,'ABC':abc,'battery_tables':battery_maps,'motor_tables':motor,
        'runtime_provenance':'Saved inputs and observed outputs consistent; no solver log or embedded runtime project hash received',
        'not_a_validated_low_SOC_BMS_map':True,'model_validation_complete':False,
        'CSV_tail_not_exported_s':float(arrays[0][2][-1]-v.Time.iloc[-1]),
        'input_sha256':{f:sha(run/f) for f in ['battery_ANL61905060DIS80.csv','velocity_ANL61905060DIS80.csv','generator_ANL61905060DIS80.csv']}}
    (OUT/'binding_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    # Fixed-output energy sensitivity only: no loss map/ABC edit is prescribed.
    previous=json.loads((ROOT/'runs/validation_closure_20261014/residual_regions.json').read_text())
    records=[]
    for test,folder,suffix in [('61905060','ANL61905060_DIS80_20261013','DIS80'),('61905061','ANL61905061_20261013','')]:
        vel=ROOT/'runs'/folder/('velocity_ANL'+test+suffix+'.csv')
        d=pd.read_csv(vel,skiprows=[1]);t=d.Time.to_numpy();keep=t>=20
        rpm=col(d,'E-Motor Speed');speed=col(d,'Actual Velocity')
        assert rpm.min()>=zero[0].min() and rpm.max()<=zero[0].max()
        z=np.interp(rpm,zero[0],zero[1]);ez=float(np.trapezoid(z[keep],t[keep])/3600)
        dist=float(np.trapezoid(speed[keep],t[keep])/3600)
        rec=next(x for x in previous if x['test']==test)
        e=rec['native_residual_kWh'];ref=rec['reference_native_kWh']
        lower=max(0,(e-.05*ref)/ez);upper=min(1,(e+.05*ref)/ez)
        records.append({'test':test,'time_window_s':[20,float(t[-1])],
          'model_Q1_zero_torque_loss_integral_kWh':ez,'native_residual_kWh':e,
          'model_distance_km':dist,'energy_equivalent_constant_force_N':e*3600/dist,
          'algebraic_zero_loss_fraction_for_zero_residual':e/ez,
          'algebraic_fraction_interval_for_energy5percent':[lower,upper],
          'source_velocity_sha256':sha(vel)})
    interval=[max(x['algebraic_fraction_interval_for_energy5percent'][0] for x in records),min(x['algebraic_fraction_interval_for_energy5percent'][1] for x in records)]
    screen={'records':records,'common_algebraic_fraction_interval':interval,
        'fraction_identified':False,'correction_applied':False,
        'scope':'Fixed-state subtraction experiment. Zero-torque EDU loss includes electrical/magnetic/gearing losses; it is not measured passive neutral loss. Common interval is compatibility, not parameter identification or CRUISE prediction. 061 uses its existing45kW result.'}
    (OUT/'overlap_identifiability_screen.json').write_text(json.dumps(screen,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'binding':audit,'screen':screen},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
