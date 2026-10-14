"""Build a common warm static-battery limit candidate, not an OEM BMS identification."""
import base64,copy,hashlib,json,os,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from lxml import etree as E
from audit_dis80_semantic import SavedProject,ROOT
U=ROOT/'runs/unified_BEV_model_20261014'
OUT=U/'common_limits_20261015'
SOURCE=U/'implementation_060/C3_IMPL_61905060_R2.proj'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def writejson(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
    assert sha(SOURCE)=='33c9577a6e4c68155d187f9a44d224fd25ca66d2d0ad8fc318d315565d4ac103'
    OUT.mkdir(parents=True,exist_ok=True)
    ocv=np.loadtxt(U/'Unified_Candidate_Cell_OCV_25C.dat',skiprows=2)
    res=np.loadtxt(U/'Unified_Candidate_Cell_Resistance_25C.dat',skiprows=2)
    cfg=json.loads((U/'development_screen.json').read_text())
    x=np.linspace(0,100,2001)
    def limits(s):
        voc=96*np.interp(s,ocv[:,0],ocv[:,1]);r=32*np.interp(s/100,res[:,0],res[:,1])
        dis=np.minimum(np.minimum(530,np.maximum((voc-242.32)/r,0)),voc/(2*r))
        cha=np.minimum(160,np.maximum((402-voc)/r,0))
        pd=dis*(voc-r*dis)/1000;pc=cha*(voc+r*cha)/1000
        pd=np.where(s<=0,0,pd);pc=np.where(s>=100,0,pc)
        return pd,pc
    pdlim,pclim=limits(x)
    table=pd.DataFrame(dict(SOC_percent=x,discharge_kW=pdlim,charge_kW=pclim));table.to_csv(OUT/'common_limits.csv',index=False)
    code='''#define pwr_dis a[0]
#define pwr_cha a[1]
#define v a[2]
#define i_batt a[3]
#define i_gen a[4]
#define i_cons_1 a[5]
#define i_cons_2 a[6]
#define i_cons_3 a[7]
#define i_cons_4 a[8]
#define i_cons_5 a[9]
#define i_lim_mot y[0]
#define i_lim_gen y[1]
#define i_cons y[2]
#define pwr_cons y[3]
/* Warm static surrogate candidate. These are modelling assumptions, not OEM BMS values.
   pwr_dis/pwr_cha ports convert their kW map outputs to W here.
   Generator current is negative when delivering to the DC bus. */
double den = max(1.0, v);
double dis_cap = min(530.0, max(0.0, pwr_dis / den));
double cha_cap = min(160.0, max(0.0, pwr_cha / den));
i_cons = i_cons_1 + i_cons_2 + i_cons_3 + i_cons_4 + i_cons_5;
pwr_cons = i_cons * v;
/* Voltage bounds are already used in the SOC power maps.
   Do not add a discontinuous voltage trip to this algebraic current loop. */
i_lim_mot = max(0.0, dis_cap - i_gen - i_cons);
/* Preserve the calibrated vehicle regen battery-power cap (40 kW).
   Battery charge acceptance remains separate for future range-extender control.
   Account for generator delivery so two sources cannot independently spend the charge budget. */
i_lim_gen = max(0.0, min(40000.0 / den, cha_cap + i_gen) + i_cons);
'''
    (OUT/'Vehicle_Current_Analysis_candidate.c').write_text(code)
    source=SavedProject(SOURCE)
    (OUT/'Vehicle_Current_Analysis_original.c').write_text(source.decode(source.fields(source.index['35443'])['function_editor']))
    # Dense interpolation approximation, including deliberately conservative endpoint reserves.
    dense=np.linspace(.051,99.949,100001);exact=limits(dense)
    excess=max(float(np.max(np.interp(dense,x,pdlim)-exact[0])),float(np.max(np.interp(dense,x,pclim)-exact[1])))
    assert excess<.01,excess
    reports=[];projects=[]
    for test in ['61905058','61905067']:
        p=SavedProject(SOURCE);changed=set()
        def array(oid,values):
            a=p.resolve(p.fields(p.index[oid])['data']);v=np.asarray(values,dtype=a.get('dtype'));assert np.isfinite(v).all()
            a.set('dim',' '.join(map(str,v.shape)));a.text=base64.b64encode(v.tobytes()).decode();changed.add(a.get('id'))
        def amount(n,key,value):
            a=p.resolve(p.fields(n)[key]);p.fields(a)['value'].text=repr(float(value));changed.add(a.get('id'))
        for oid,values in [('68891',pdlim),('69081',pclim)]:
            aa=p.arrays_under(p.index[oid]);array(aa[0][0],x);array(aa[1][0],values)
        editor=p.resolve(p.fields(p.index['35443'])['function_editor']);assert editor.get('coding')=='base64'
        editor.text=base64.b64encode(code.encode()).decode()
        s0=next(m for m in cfg['metrics'] if m['test']==test)['initial_model_SOC_percent']
        for n in p.nodes('cruise.props.battery.InitialConditions'):amount(n,'initial_charge',s0)
        if test=='61905058':
            driver=pd.read_csv(ROOT/'runs/C2_battery_common_20261014/inputs/ANL61905058_driver_1s.csv')
            ref=pd.read_csv(ROOT/f'runs/C2_battery_common_20261014/references/ANL{test}_reference_native.csv')
            duration=float(driver.time_s.iloc[-1]);ambient=24.0
        else:
            raw=pd.read_csv(ROOT/f'runs/C2_performance_extension_20261014/replay/ANL{test}_frozen_C2_replay.csv')
            duration=float(raw.loc[raw.speed_kmh>1,'t'].iloc[-1])+10
            raw=raw.loc[raw.t<=duration].copy()
            ref=raw[['t','v','i','p','temperature_C','speed_kmh']].rename(columns={'t':'time_s','v':'meter_voltage_V','i':'meter_current_A_discharge_positive','p':'meter_power_kW_discharge_positive','temperature_C':'battery_temperature_C'})
            tt=np.r_[np.arange(0,duration,1),duration]
            driver=pd.DataFrame(dict(time_s=tt,speed_kmh=np.interp(tt,raw.t,raw.speed_kmh)))
            ambient=26.06818994
        assert np.isfinite(driver.to_numpy()).all() and np.all(np.diff(driver.time_s)>0)
        assert ref.meter_voltage_V.min()>250
        driver.to_csv(OUT/f'ANL{test}_driver_1s.csv',index=False)
        ref.to_csv(OUT/f'ANL{test}_reference_native.csv',index=False)
        aa=p.arrays_under(p.index['40662']);assert len(aa)==7
        speed=driver.speed_kmh.to_numpy();tt=driver.time_s.to_numpy();nn=len(tt)
        cols=[tt,speed,np.ones(nn),np.zeros(nn),np.r_[np.ones(nn-1),0],speed,speed]
        for a,col in zip(aa,cols):array(a[0],col)
        amount(p.index['79182'],'end_time',duration)
        for n in p.nodes('cruise.props.battery.InitialConditions'):
            owner=next(z for z in n.iterancestors('object') if z.get('type')=='act.topo.Element')
            temp=[z for z in owner.iter('object') if z.get('type')=='cruise.props.solid_wall.DefinedTemperature'];assert len(temp)==1
            amount(temp[0],'temperature',24.0 if test=='61905058' else 24.5)
        owner=next(z for z in p.index['40662'].iterancestors('object') if z.get('type')=='act.topo.Element')
        task=next(z for z in owner.iterancestors('object') if z.get('type')=='act.topo.Element')
        env=[z for z in task.iter('object') if z.get('type')=='cruise.props.tasks.environment.AmbientTemperatureHumidity'];assert len(env)==1
        ea=p.arrays_under(p.fields(env[0])['distance_based']);array(ea[1][0],[ambient])
        dest=OUT/f'C3_LIMITS_ANL{test}.proj';tmp=dest.with_suffix('.proj.part')
        with zipfile.ZipFile(SOURCE) as zi,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as zo:
            for info in zi.infolist():zo.writestr(copy.copy(info),E.tostring(p.root,encoding='utf-8',xml_declaration=True) if info.filename=='project.xml' else zi.read(info.filename))
        with tmp.open('rb') as f:os.fsync(f.fileno())
        with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
        os.replace(tmp,dest);fd=os.open(OUT,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
        q=SavedProject(dest);assert q.index.keys()==source.index.keys()
        assert [z.get('id') for z in q.root.iter('ref')]==[z.get('id') for z in source.root.iter('ref')]
        # Prevent the R1 UI failure: Case manager, names, slots and active references unchanged.
        for oid in ['82908','82928','82938','82940','82958','73213']:
            assert E.tostring(q.index[oid])==E.tostring(source.index[oid]),oid
        assert E.tostring(q.index['43746'])==E.tostring(source.index['43746'])
        for typ in ['IdleVoltage','OhmicResistanceCharge','OhmicResistanceDischarge']:
            for a,b in zip(source.nodes('cruise.props.commons_battery.'+typ),q.nodes('cruise.props.commons_battery.'+typ)):
                assert all(np.array_equal(z[2],w[2]) for z,w in zip(source.arrays_under(a),q.arrays_under(b)))
        for oid,node in source.index.items():
            if node.tag=='numpy_array' and node.text!=q.index[oid].text:assert oid in changed,oid
        assert np.array_equal(q.arrays_under(q.index['40662'])[0][2],tt)
        assert np.array_equal(q.arrays_under(q.index['40662'])[1][2],speed)
        assert abs(q.amount(q.index['79182'],'end_time')-duration)<1e-8
        assert q.decode(q.fields(q.index['35443'])['function_editor'])==code
        assert 'operating_mode_out = mode_eDrive;' in q.decode(q.fields(q.index['37680'])['function_editor'])
        projects.append(dict(test=test,project=dest.name,sha256=sha(dest),bytes=dest.stat().st_size,end_time_s=duration,initial_model_SOC_percent=s0,profile_rows=nn,embedded_profile_verified=True,Case_metadata_unchanged=True,CRC_XML_verified=True,CRUISE_loaded=False,CRUISE_solved=False))
    for test in ['61905060','61905061','61905066','61905064','61905058','61905059','61905067']:
        d=pd.read_csv(U/f'candidate_fixed_power_{test}.csv');dis,cha=limits(d.model_SOC_percent.to_numpy())
        cha=np.minimum(40,cha)
        gd=np.maximum(d.power_kW-dis,0);gc=np.maximum(-d.power_kW-cha,0)
        reports.append(dict(test=test,maximum_discharge_gap_kW=float(gd.max()),maximum_charge_gap_kW=float(gc.max()),integrated_charge_gap_kWh=float(np.trapezoid(gc,d.time_s)/3600),boundary='Frozen demand screen, not coupled CRUISE prediction'))
    manifest=dict(status='COMMON_LIMIT_CANDIDATE_PENDING_ACTUAL_058_067',source_project_sha256=sha(SOURCE),battery_OCV_R_capacity_unchanged=True,pack_capacity_Ah=cfg['capacity_Ah'],voltage_min_V=242.32,voltage_max_V=402,discharge_current_A=530,charge_current_A=160,vehicle_regen_battery_power_cap_kW=40,parameters_are_not_OEM_BMS_identification=True,temperature_scope='warm static effective OCV/R; no temperature or duration limit model',SOC0_discharge_zero=True,SOC100_charge_zero=True,denominator_guard_V=1,table_interpolation_max_excess_kW=excess,projects=projects,frozen_demand_screen=reports)
    writejson(OUT/'manifest.json',manifest);print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
