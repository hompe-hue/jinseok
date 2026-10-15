"""One effective common candidate, five frozen confirmation cases; no solver execution."""
import argparse,base64,copy,hashlib,json,os,shutil,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from lxml import etree as E
from audit_dis80_semantic import ROOT,SavedProject
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-directory',type=Path,required=True);a=ap.parse_args()
    source=a.source_directory/'C3_LIMITS_ANL61905067.proj';assert sha(source)=='48adab1848b68edac991e7d937ad5a56d363ba16af554e4226863f00cee6338c'
    out=ROOT/'runs/unified_BEV_model_20261014/final_candidate_batch_20261015';out.mkdir(parents=True,exist_ok=True)
    C2=ROOT/'runs/C2_battery_common_20261014';diag=ROOT/'runs/unified_BEV_model_20261014/diagnostic_067_end9500_20261015'
    ocv=np.loadtxt(a.source_directory/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2);r=np.loadtxt(a.source_directory/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2);newr=r[:,1]*1.1
    q1=pd.read_csv(C2/'inputs/C1_EDU_Q1_loss_nodes.csv');q4=pd.read_csv(C2/'inputs/C1_EDU_Q4_loss_nodes.csv');zero=q1[q1.torque_Nm==0].sort_values('rpm')
    params=dict(status='FINAL_COMMON_CANDIDATE_NOT_ADOPTED',pack_capacity_Ah=169.3568460332183,cell_capacity_Ah=56.45228201107276,OCV_unchanged=True,R_scale_relative_to_C3=1.1,original_R_gain=1.0337329877479744,new_R_gain=1.0337329877479744*1.1,EDU_original_beta=.6480886994,EDU_Q1_delta_beta=.17,EDU_Q1_new_beta=.6480886994+.17,EDU_Q4_nodes_unchanged=True,EDU_speed_taper='clip(rpm/250,0,1): no extra subtraction at standstill; full correction from first nonzero map speed250rpm',EDU_rule='Effective motoring speed-baseline overlap subtraction extended by0.17; Q1 torque-dependent increments retained. Existing Q4 is unchanged; lowtorque bridge follows its original Q4 and new Q1 endpoint.',discharge_current_assumption_A=530,charge_current_assumption_A=160,voltage_min_assumption_V=242.32,voltage_max_assumption_V=402,vehicle_regen_cap_kW=40,all_are_effective_model_parameters_not_OEM_identification=True,selection='delta_beta0.17 approximates the observed067 net-energy residual (0.9673/5.6058=0.17255) while maintaining existing six-run energy gates; Rscale1.10 gives voltage-bias margin across cases. Same parameters for all cases; no claim of unique physical optimum',initialization='Common first5s |I|<3A median V/I inverse using updated common OCV/R; no manual per-case offset',confirmation_tests=['61905067','61905060','61905058','61905059','61905066'],gates=dict(energy_error_abs_percent_max=5,voltage_RMSE_V_max=2,voltage_bias_abs_V_max=1,speed_RMSE_kmh_max=1,distance_error_abs_percent_max=.5,DC_balance_abs_percent_max=1),new_CRUISE_runs=0)
    (out/'parameters.json').write_text(json.dumps(params,indent=2)+'\n');parameter_hash=sha(out/'parameters.json')
    shutil.copyfile(a.source_directory/'Unified_Candidate_Cell_OCV_25C.dat',out/'Common_Cell_OCV_25C.dat')
    (out/'Common_Cell_Resistance_25C.dat').write_text('SoC Resistance\n- Ohm\n'+''.join(f'{s:.17g} {v:.17g}\n' for s,v in zip(r[:,0],newr)))
    for label,d,factor in [('Q1',q1,1),('Q4',q4,0)]:
        d=d.copy();d['candidate_loss_kW']=d.C1_loss_kW-.17*factor*np.interp(d.rpm,zero.rpm,zero.original_loss_kW)*np.clip(d.rpm/250,0,1);assert (d.candidate_loss_kW>0).all();d.to_csv(out/f'Common_EDU_{label}_loss_nodes.csv',index=False)
    soc_grid=np.linspace(0,100,2001);U=96*np.interp(soc_grid,ocv[:,0],ocv[:,1]);R=32*np.interp(soc_grid/100,r[:,0],newr)
    dis=np.minimum(np.minimum(530,np.maximum((U-242.32)/R,0)),U/(2*R));cha=np.minimum(160,np.maximum((402-U)/R,0));pdlim=dis*(U-R*dis)/1000;pclim=cha*(U+R*cha)/1000;pdlim[0]=0;pclim[-1]=0
    pd.DataFrame(dict(SOC_percent=soc_grid,discharge_kW=pdlim,charge_kW=pclim)).to_csv(out/'Common_power_limits.csv',index=False)
    contract={c['test']:c for c in json.loads((C2/'candidate_contract.json').read_text())['cases']};projects=[];hashes=[]
    before=SavedProject(source)
    for test in params['confirmation_tests']:
        p=SavedProject(source);changed=set()
        def array(oid,values):
            n=p.resolve(p.fields(p.index[oid])['data']);v=np.asarray(values,dtype=n.get('dtype'));assert np.isfinite(v).all();n.set('dim',' '.join(map(str,v.shape)));n.text=base64.b64encode(v.tobytes()).decode();changed.add(n.get('id'))
        def amount(n,key,value):
            v=p.resolve(p.fields(n)[key]);p.fields(v)['value'].text=repr(float(value));changed.add(v.get('id'))
        for typ in ['OhmicResistanceCharge','OhmicResistanceDischarge']:
            for n in p.nodes('cruise.props.commons_battery.'+typ):
                aa=p.arrays_under(n);assert np.array_equal(aa[2][2],r[:,1]);array(aa[2][0],newr)
        labels=set()
        for n in p.nodes('cruise.props.electric_machine.PowerLoss'):
            aa=p.arrays_under(n)
            if len(aa)!=5 or not len(aa[1][2]) or not np.all(aa[1][2]==400):continue
            label='Q1' if aa[3][2].min()>=0 else 'Q4';d=q1 if label=='Q1' else q4;assert np.max(abs(aa[2][2]-d.rpm))<1e-9 and np.max(abs(aa[3][2]-d.torque_Nm))<1e-9
            assert np.max(abs(aa[4][2]-d.C1_loss_kW))<1e-9
            values=d.C1_loss_kW-.17*(1 if label=='Q1' else 0)*np.interp(d.rpm,zero.rpm,zero.original_loss_kW)*np.clip(d.rpm/250,0,1);assert np.all(values>0);array(aa[4][0],values);labels.add(label)
        assert labels=={'Q1','Q4'}
        for oid,values in [('68891',pdlim),('69081',pclim)]:
            aa=p.arrays_under(p.index[oid]);assert np.array_equal(aa[0][2],soc_grid);array(aa[1][0],values)
        if test=='61905067':
            driver=pd.read_csv(diag/'ANL61905067_driver_1s.csv');refpath=diag/'ANL61905067_reference_native.csv';temp=24.5;ambient=26.0681899413573;end=10122.190356254578
        else:
            datpath=C2/'inputs'/contract[test]['input_profile'];assert sha(datpath)==contract[test]['input_profile_sha256']
            dat=np.loadtxt(datpath,skiprows=2);assert dat.shape[1]==7
            driver=pd.DataFrame(dict(time_s=dat[:,0],speed_kmh=dat[:,1]));refpath=C2/f'references/ANL{test}_reference_native.csv';temp=contract[test]['battery_temperature_C'];ambient=contract[test]['environment_temperature_C'];end=contract[test]['end_time_s']
        ref=pd.read_csv(refpath);nt=ref['time_s' if 'time_s' in ref else 'phase_time_s'];rest=(nt<=5)&(abs(ref.meter_current_A_discharge_positive)<3);assert rest.any();v0=float(ref.meter_voltage_V[rest].median());i0=float(ref.meter_current_A_discharge_positive[rest].median())
        s0=brentq(lambda s:96*np.interp(s,ocv[:,0],ocv[:,1])-i0*32*np.interp(s/100,r[:,0],newr)-v0,0,100)
        for n in p.nodes('cruise.props.battery.InitialConditions'):
            amount(n,'initial_charge',s0);owner=next(z for z in n.iterancestors('object') if z.get('type')=='act.topo.Element');temps=[z for z in owner.iter('object') if z.get('type')=='cruise.props.solid_wall.DefinedTemperature'];assert len(temps)==1;amount(temps[0],'temperature',temp)
        t=driver.time_s.to_numpy();speed=driver.speed_kmh.to_numpy();assert np.all(np.diff(t)>0) and abs(t[-1]-end)<1e-6;N=len(t)
        aa=p.arrays_under(p.index['40662']);assert len(aa)==7
        for arr,values in zip(aa,[t,speed,np.ones(N),np.zeros(N),np.r_[np.ones(N-1),0],speed,speed]):array(arr[0],values)
        amount(p.index['79182'],'end_time',end)
        owner=next(z for z in p.index['40662'].iterancestors('object') if z.get('type')=='act.topo.Element');task=next(z for z in owner.iterancestors('object') if z.get('type')=='act.topo.Element');env=[z for z in task.iter('object') if z.get('type')=='cruise.props.tasks.environment.AmbientTemperatureHumidity'];assert len(env)==1;ea=p.arrays_under(p.fields(env[0])['distance_based']);array(ea[1][0],[ambient])
        dest=out/f'BEV_FINAL_CANDIDATE_{test}.proj';tmp=dest.with_suffix('.proj.part')
        with zipfile.ZipFile(source) as zi,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for info in zi.infolist():zo.writestr(copy.copy(info),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if info.filename=='project.xml' else zi.read(info.filename))
        with tmp.open('rb') as f:os.fsync(f.fileno())
        with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
        os.replace(tmp,dest);fd=os.open(out,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
        check=SavedProject(dest);assert E.tostring(check.root)==E.tostring(p.root);assert check.index.keys()==before.index.keys()
        assert [n.get('id') for n in check.root.iter('ref')]==[n.get('id') for n in before.root.iter('ref')]
        for oid in ['82908','82928','82938','82940','82958','73213','39417','43746','35443','37680']:assert E.tostring(check.index[oid])==E.tostring(before.index[oid]),oid
        for oid,n in before.index.items():
            if n.tag=='numpy_array' and n.text!=check.index[oid].text:assert oid in changed,oid
        for n in check.nodes('cruise.props.battery.General'):assert abs(check.amount(check.resolve(check.fields(n)['maximum_charge']),'const')-56.45228201107276)<1e-10
        assert abs(check.amount(check.index['79182'],'end_time')-end)<1e-8
        assert np.array_equal(check.arrays_under(check.index['40662'])[1][2],speed)
        core=[]
        for typ in ['cruise.props.commons_battery.IdleVoltage','cruise.props.commons_battery.OhmicResistanceCharge','cruise.props.commons_battery.OhmicResistanceDischarge','cruise.props.electric_machine.PowerLoss']:
            for n in check.nodes(typ):core.append((typ,[(unit,hashlib.sha256(v.tobytes()).hexdigest()) for oid,unit,v in check.arrays_under(n)]))
        for oid in ['68891','69081']:core.append((oid,[(unit,hashlib.sha256(v.tobytes()).hexdigest()) for _,unit,v in check.arrays_under(check.index[oid])]))
        core_hash=hashlib.sha256(json.dumps(core,sort_keys=True).encode()).hexdigest();hashes.append(core_hash)
        with zipfile.ZipFile(source) as zi,zipfile.ZipFile(dest) as zo:assert all(zi.read(n)==zo.read(n) for n in zi.namelist() if n!='project.xml')
        driver.to_csv(out/f'ANL{test}_driver_1s.csv',index=False);shutil.copyfile(refpath,out/f'ANL{test}_reference_native.csv');assert sha(refpath)==sha(out/f'ANL{test}_reference_native.csv')
        projects.append(dict(test=test,project=dest.name,sha256=sha(dest),bytes=dest.stat().st_size,end_time_s=end,initial_model_SOC_percent=s0,battery_temperature_C=temp,environment_temperature_C=ambient,parameter_sha256=parameter_hash,common_core_map_sha256=core_hash,embedded_profile_verified=True,Case_metadata_unchanged=True,CRC_XML_verified=True,CRUISE_loaded=False,CRUISE_solved=False))
    assert len(set(hashes))==1
    manifest=dict(status='FINAL_COMMON_CANDIDATE_BATCH_PENDING_USER_CRUISE',projects=projects,common_parameters=params,parameter_sha256=parameter_hash,all_five_core_maps_identical=True,source_project_sha256=sha(source),final_BEV_model_adopted=False)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    script=(a.source_directory/'evaluate_C3_common_limits.py').read_text();script=script.replace("choices=['61905058','61905067']","choices=['61905060','61905058','61905059','61905066','61905067']")
    (out/'evaluate_final_candidate.py').write_text(script)
    print(json.dumps(dict(projects=projects,all_five_core_maps_identical=True),indent=2))
if __name__=='__main__':main()
