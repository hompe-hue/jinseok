"""Prepare C2 test derivatives. Does not run the proprietary CRUISE M solver."""
import base64,copy,hashlib,json,os,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from lxml import etree as E
from audit_dis80_semantic import SavedProject,ROOT
OUT=ROOT if (ROOT/'test_manifest.json').exists() else ROOT/'runs/C2_performance_extension_20261014'
SOURCE=ROOT/'baseline/C2_CAL_61905060.proj' if OUT==ROOT else ROOT/'runs/C2_battery_common_20261014/projects/C2_CAL_61905060.proj'
BASE_HASH='49921958c91e386bf66d997c7abf3b907c499a22f86f3507482c6c5136a8ea25'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(SOURCE)==BASE_HASH
    for x in ['projects','profiles']:(OUT/x).mkdir(parents=True,exist_ok=True)
    schedules={};scheduleinfo=[]
    for cycle in ['UDDS','HWFET']:
        path=OUT/'sources'/f'EPA_{cycle}.txt';data=[]
        for line in path.read_text().splitlines():
            try:t,v=map(float,line.split());data.append((t,v*1.609344))
            except ValueError:pass
        arr=np.array(data);assert arr[0,0]==0 and np.all(np.diff(arr[:,0])==1)
        assert arr[0,1]==0 and arr[-1,1]==0
        duration=int(arr[-1,0]);assert duration==({'UDDS':1369,'HWFET':765}[cycle])
        # Explicit modeled zero-speed 1s joining interval, disclosed as simplification.
        repeated=np.vstack([np.column_stack((arr[:,0]+k*(duration+1),arr[:,1])) for k in range(60)])
        schedules[cycle]=repeated
        pd.DataFrame(arr,columns=['time_s','speed_kmh']).to_csv(OUT/'profiles'/f'EPA_{cycle}_single.csv',index=False)
        pd.DataFrame(repeated,columns=['time_s','speed_kmh']).to_csv(OUT/'profiles'/f'EPA_{cycle}_repeat60.csv',index=False)
        scheduleinfo.append(dict(cycle=cycle,source_sha256=sha(path),single_rows=len(arr),single_end_s=duration,nominal_single_distance_km=float(np.trapezoid(arr[:,1]/3600,arr[:,0])),repeats=60,repeat_end_s=float(repeated[-1,0]),join_zero_speed_s=1,soak_and_preconditioning_fully_reproduced=False))
    cases=[]
    for name,mode,soc in [('C2_ACC_SOC94','ACC',94),('C2_ACC_SOC100','ACC',100),('C2_RANGE_UDDS_SOC100','UDDS',100),('C2_RANGE_HWFET_SOC100','HWFET',100)]:
        p=SavedProject(SOURCE);before=SavedProject(SOURCE);changed=[]
        def amount(n,key,value):
            x=p.resolve(p.fields(n)[key]);p.fields(x)['value'].text=repr(float(value));changed.append(x.get('id'))
        def array(oid,values):
            x=p.resolve(p.fields(p.index[oid])['data']);a=np.asarray(values,dtype=x.get('dtype'));assert np.isfinite(a).all()
            x.set('dim',' '.join(map(str,a.shape)));x.text=base64.b64encode(a.tobytes()).decode();changed.append(x.get('id'))
        for n in p.nodes('cruise.props.battery.InitialConditions'):amount(n,'initial_charge',soc)
        for n in p.nodes('cruise.props.battery.InitialConditions'):
            owner=next(x for x in n.iterancestors('object') if x.get('type')=='act.topo.Element')
            for q in owner.iter('object'):
                if q.get('type')=='cruise.props.solid_wall.DefinedTemperature':amount(q,'temperature',25)
        for n in p.nodes('cruise.props.tasks.environment.AmbientTemperatureHumidity'):
            a=p.arrays_under(p.fields(n)['distance_based']);assert len(a)==3;array(a[1][0],[25])
        for n in p.nodes('cruise.props.vehicle.InitialConditions'):amount(n,'velocity',0)
        duration=40 if mode=='ACC' else float(schedules[mode][-1,0])
        for n in p.nodes('cruise.props.tasks.tasks_settings.EndTimeSelection'):
            p.fields(n)['active'].text='end_time';amount(n,'end_time',duration)
        if mode=='ACC':
            for n in p.nodes('cruise.props.full_load_acceleration.General'):amount(n,'accelerator_pedal_limit',1)
            for n in p.nodes('cruise.props.full_load_acceleration.AbortConditions'):amount(n,'max_simulation_time',40)
            # Use existing Performance/FLA case; its native scenario controls FLA layer.
            active=p.fields(p.index['82908'])['active_case'];assert active.tag=='ref';active.set('id','82984')
            for n in p.nodes('cruise.props.tasks.tasks_settings.OutputSettings'):p.fields(n)['output_after_every'].text='1'
            activecase='Performance / FLA';profile_name=None
        else:
            t,speed=schedules[mode].T;n=len(t);a=p.arrays_under(p.index['40662']);assert len(a)==7
            columns=[t,speed,np.ones(n),np.zeros(n),np.r_[np.ones(n-1),0],speed,speed]
            for (oid,_,_),data in zip(a,columns):array(oid,data)
            profile_name=name
            # Update the display property, pool dictionary key and matching existing case.
            for q in p.nodes('cruise.props.tasks.profile.General'):
                if p.decode(p.fields(q)['name'])=='C2_CAL_61905060':p.fields(q)['name'].text=name
            p.fields(p.index['82936'])['name'].text=name
            for d in p.root.iter('dict'):
                z=list(d)
                for k,v in zip(z[::2],z[1::2]):
                    if k.tag=='str' and k.text=='ANL61905060' and p.resolve(v).get('id')=='40659':k.text=name
            hdr='Time Velocity Gear "Shift Time" "Start Switch" "Min. Velocity" "Max. Velocity"\r\ns km/h - s - km/h km/h\r\n'
            rows=[f'{tt:.6f}\t{vv:.6f}\t1\t0\t{int(on)}\t{vv:.6f}\t{vv:.6f}' for tt,vv,on in zip(t,speed,columns[4])]
            (OUT/'profiles'/f'{name}.dat').write_bytes((hdr+'\r\n'.join(rows)+'\r\n').encode())
            activecase=f'Cycle Run / {name}'
        dest=OUT/'projects'/f'{name}.proj';tmp=dest.with_suffix('.proj.part')
        with zipfile.ZipFile(SOURCE) as zin,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():zout.writestr(copy.copy(info),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if info.filename=='project.xml' else zin.read(info.filename))
        with tmp.open('rb') as f:os.fsync(f.fileno())
        with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
        os.replace(tmp,dest);fd=os.open(dest.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
        check=SavedProject(dest);assert before.index.keys()==check.index.keys()
        # Compare every serialized NumArray / IntArray: only requested profile and ambient arrays may differ.
        changedarrays=[]
        for oid,node in before.index.items():
            if node.tag=='numpy_array' and node.text!=check.index[oid].text:
                changedarrays.append(oid);assert oid in changed
        for typ in ['IdleVoltage','OhmicResistanceCharge','OhmicResistanceDischarge']:
            for a,b in zip(before.nodes('cruise.props.commons_battery.'+typ),check.nodes('cruise.props.commons_battery.'+typ)):
                assert all(np.array_equal(x[2],y[2]) for x,y in zip(before.arrays_under(a),check.arrays_under(b)))
        for n in check.nodes('cruise.props.battery.InitialConditions'):assert check.amount(n,'initial_charge')==soc
        refchanges=[(a.get('id'),b.get('id')) for a,b in zip(before.root.iter('ref'),check.root.iter('ref')) if a.get('id')!=b.get('id')]
        assert refchanges==([('82936','82984')] if mode=='ACC' else [])
        if mode!='ACC':assert all(np.array_equal(x[2],y) for x,y in zip(check.arrays_under(check.index['40662']),columns))
        with zipfile.ZipFile(SOURCE) as zin,zipfile.ZipFile(dest) as zout:
            assert all(zin.read(n)==zout.read(n) for n in zin.namelist() if n!='project.xml')
        cases.append(dict(project=dest.name,sha256=sha(dest),bytes=dest.stat().st_size,mode=mode,initial_SOC_percent=soc,temperature_C=25,case_to_select=activecase,profile=profile_name,maximum_duration_s=duration,mass_kg=1757.6704,source_C2_maps_and_capacity_preserved=True,diagnostic_discharge_map_preserved=True,changed_serialized_arrays=changedarrays,changed_case_ref=refchanges,CRC_XML_readback_passed=True,CRUISE_load_tested=False,CRUISE_solver_tested=False))
    manifest=dict(status='PREPARED_PENDING_USER_CRUISE_RUN',source_C2_sha256=BASE_HASH,cases=cases,official_reference={'acceleration_0_to_60mph_seconds':6.5,'60mph_kmh':96.56064,'EPA_combined_range_miles':238,'EPA_combined_range_km':383.028672,'EPA_city_range_miles':255,'EPA_highway_range_miles':217},schedules=scheduleinfo,certification_reproduction=False,prohibition='Do not refit fixed warm C2 or remove diagnostic discharge limits to force official performance. Actual battery SOC-to-usable-window and GM/EPA vehicle-specific test method are not fully established.')
    (OUT/'test_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(cases,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
