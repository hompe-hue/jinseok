"""R65C-02. Convert published maps; keep the optional virtual design explicitly assumed.
No MATLAB execution, no CRUISE M import or simulation, no baseline modification.
"""
from pathlib import Path
import re,csv,json,math,hashlib
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'inputs'
RPM=60/(2*np.pi); TEMP=0.0  # Coordinate for a single-temperature map, NOT test temperature.
S_ENGINE=1.5/1.998; S_GEN=80/60
def arr(s,k):
    m=re.search(re.escape(k)+r'\s*=\s*\[(.*?)\];',s,re.S)
    if not m: raise ValueError(k)
    a=np.asarray([np.fromstring(r.replace(',',' ').replace('\n',' ').replace('\t',' '),sep=' ')
                  for r in m[1].split(';') if r.strip()])
    return a.ravel() if min(a.shape)==1 else a
def val(s,k):return float(re.search(re.escape(k)+r'\s*=\s*([-+0-9.eE]+)',s)[1])
def write(name,headers,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)
def clean(a):return float(round(float(a),9))
def source(tag):
    f=next((ROOT/'sources'/tag).glob('7*.m'));return f.read_text(),f

engine,ef=source('EPA_Mazda20_NA_Tier2_ALPHA')
en=arr(engine,'engine.fuel_map_speed_radps')*RPM
et=arr(engine,'engine.fuel_map_torque_Nm'); fuel=arr(engine,'engine.fuel_map_gps')
ewn=arr(engine,'engine.full_throttle_speed_radps')*RPM; ewt=arr(engine,'engine.full_throttle_torque_Nm')
ecn=arr(engine,'engine.closed_throttle_speed_radps')*RPM; ect=arr(engine,'engine.closed_throttle_torque_Nm')
assert fuel.shape==(len(et),len(en))
for prefix,scale in [('REF_Engine20NA',1.0),('A_Engine15NA80',S_ENGINE)]:
    # Raw rectangular fuel grid includes model-completed points outside torque limits.
    for unit,factor in [('g_s',1),('kg_h',3.6)]:
        write(prefix+'_Fuel_'+unit+'.csv',['Speed (rpm)','Torque (N*m)',f'Fuel mass flow ({unit})'],
              [[clean(n),clean(t*scale),clean(fuel[j,i]*scale*factor)] for i,n in enumerate(en) for j,t in enumerate(et)])
        write(prefix+'_Fuel_'+unit+'_matrix.csv',['Torque (N*m) / Speed (rpm)']+[clean(n) for n in en],
              [[clean(t*scale)]+[clean(x*scale*factor) for x in fuel[j]] for j,t in enumerate(et)])
    # Densify capped virtual WOT; retain an explicit 80kW supervisory power cap.
    if scale==1: wn=ewn;wt=ewt
    else:
        wn=np.unique(np.r_[np.arange(0,ewn[-1]+1,25),ewn])
        wt=np.interp(wn,ewn,ewt)*scale
        np.minimum(wt,np.divide(80000,wn/RPM,out=np.full_like(wn,np.inf),where=wn>0),out=wt)
    write(prefix+'_FullLoad.csv',['Speed (rpm)','Torque (N*m)'],[[clean(n),clean(t)] for n,t in zip(wn,wt)])
    write(prefix+'_ClosedThrottle.csv',['Speed (rpm)','Torque (N*m)'],[[clean(n),clean(t*scale)] for n,t in zip(ecn,ect)])
    masks=[]
    for i,n in enumerate(en):
        hi=np.interp(n,wn,wt);lo=np.interp(n,ecn,ect)*scale
        for j,t in enumerate(et*scale):
            masks.append([clean(n),clean(t),int(n>=500 and lo-1e-9<=t<=hi+1e-9),
                          'inside_envelope' if n>=500 and lo-1e-9<=t<=hi+1e-9 else 'map_extension_not_operating_point'])
    write(prefix+'_AllowedMask.csv',['rpm','torque_Nm','inside_envelope','status'],masks)

audit={'classification':{'REF':'Published completed reference, not every cell is measured',
                         'A':'Optional virtual sensitivity draft; NOT approved/calibrated hardware input'},
       'temperature_coordinate_degC':TEMP,'temperature_condition':'Source temperature axis absent; 0 is indexing only',
       'voltage_V':650,'quadrants':'Q1 rpm>0,T>0; Q4 rpm>0,T<0',
       'engine':{'source_sha256':hashlib.sha256(ef.read_bytes()).hexdigest(),'scale':S_ENGINE,
                 'fuel_rule':'q15(n,T15)=scale*q20(n,T15/scale); WOT=min(scale*T20,80000/omega)',
                 'virtual_max_shaft_kW':80,'actual_15NA_fuel_map':False},'generators':{}}
machines={}
for tag in ['MG1_EST','MG2']:
    s,f=source('EPA_Prius_'+tag+'_ALPHA')
    n=arr(s,'mg.electric_power_W.axis_1.breakpoints')*RPM
    t=arr(s,'mg.electric_power_W.axis_2.breakpoints'); p=arr(s,'mg.electric_power_W.table')
    wn=arr(s,'mg.positive_torque_limit_Nm.axis_1.breakpoints')*RPM
    wt=arr(s,'mg.positive_torque_limit_Nm.table')
    keep=wn>=0;wn=wn[keep];wt=wt[keep]
    if tag=='MG2':
        nt=arr(s,'mg.negative_torque_limit_Nm.table')
        nn=arr(s,'mg.negative_torque_limit_Nm.axis_1.breakpoints')*RPM
        assert np.allclose(nn,wn) and np.allclose(nt,-wt)
        q4_load='Negative torque envelope present in EPA source; generator quadrant completed'
    else:
        nt=-wt
        q4_load='A: mirrored positive envelope; source MG1 has no negative torque limit table'
    positive=n>1e-6;nn=n[positive];pp=p[positive]
    omega=nn/RPM
    loss=pp-omega[:,None]*t[None,:]
    assert np.isfinite(pp).all() and loss.min()>=-1e-6
    efficiency=np.zeros_like(pp)
    for i,w in enumerate(omega):
        for j,tq in enumerate(t):
            if tq>0:efficiency[i,j]=100*w*tq/pp[i,j]
            elif tq<0:efficiency[i,j]=100*pp[i,j]/(w*tq)
    assert np.all((efficiency[:,t!=0]>0)&(efficiency[:,t!=0]<=100))
    interp4=RegularGridInterpolator((nn,t[t<0]),efficiency[:,t<0]/100,bounds_error=True)
    machines[tag]={'n':nn,'t':t,'p':pp,'wn':wn,'wt':wt,'eff':efficiency,'q4_interp':interp4,
                   'inertia':val(s,'mg.inertia_kgm2')}
    configurations=[('REF_'+tag,1.0)]
    if tag=='MG1_EST':configurations.append(('A_Gen80_MG1EST',S_GEN))
    for prefix,scale in configurations:
        # Source maximum13500; export chart including cutoff but use13000 grid-domain limit.
        fulln=wn;fullt=wt*scale
        if scale!=1:
            fulln=np.unique(np.r_[np.arange(0,13000+1,25),wn[wn<=13000]])
            fullt=np.interp(fulln,wn,wt)*scale
            np.minimum(fullt,np.divide(80000,fulln/RPM,out=np.full_like(fulln,np.inf),where=fulln>0),out=fullt)
        q1=[[650,clean(v),clean(q)] for v,q in zip(fulln,fullt)]
        q4=[[650,clean(v),clean(-q)] for v,q in zip(fulln,fullt)]
        headers=['Voltage (V)','Speed (rpm)','Torque (N*m)']
        write(prefix+'_FullLoad_Q1.csv',headers,q1);write(prefix+'_FullLoad_Q4.csv',headers,q4)
        write(prefix+'_FullLoad_Q1Q4.csv',headers,q1+q4)
        all_eff=[];mask=[]
        for label,indices in [('Q1',np.flatnonzero(t>0)),('Q4',np.flatnonzero(t<0))]:
            erows=[]
            for i,rpm in enumerate(nn):
                envelope=np.interp(rpm,wn,wt)*scale
                for j in indices:
                    torque=t[j]*scale
                    inside=abs(torque)<=envelope+1e-7 and rpm/RPM*abs(torque)<=60000*scale+1e-6
                    erows.append([TEMP,650,clean(rpm),clean(torque),clean(efficiency[i,j])])
                    mask.append([clean(rpm),clean(torque),label,int(inside),'inside_FullLoad' if inside else 'extension_outside_FullLoad'])
            write(prefix+'_Efficiency_'+label+'.csv',
                  ['Temperature (degC)','Voltage (V)','Speed (rpm)','Torque (N*m)','Efficiency (%)'],erows)
            all_eff.extend(erows)
        write(prefix+'_Efficiency_Q1Q4.csv',
              ['Temperature (degC)','Voltage (V)','Speed (rpm)','Torque (N*m)','Efficiency (%)'],all_eff)
        write(prefix+'_AllowedMask.csv',['rpm','torque_Nm','quadrant','inside_FullLoad','status'],mask)
        # Full positive-speed loss surface INCLUDING stationary and zero torque rows.
        # Alternative numeric data only: CRUISE M power-loss column/unit UI has not been supplied.
        lrows=[]
        for i,rpm in enumerate(n):
            if rpm<-1e-6:continue
            for j,tq in enumerate(t):
                lrows.append([TEMP,650,clean(rpm),clean(tq*scale),clean((p[i,j]-rpm/RPM*tq)*scale)])
        write(prefix+'_PowerLoss_W_ALTERNATIVE.csv',
              ['Temperature (degC)','Voltage (V)','Speed (rpm)','Torque (N*m)','Power loss (W)'],lrows)
        audit['generators'][prefix]={'power_model_shaft_cap_kW':60*scale,'torque_scale':scale,
             'efficiency_rows':len(all_eff),'Q1_rows':int(len(nn)*sum(t>0)),'Q4_rows':int(len(nn)*sum(t<0)),
             'inside_envelope_rows':sum(r[3] for r in mask),'full_load_Q4_origin':q4_load,
             'Q4_efficiency':'EPA completed estimate, derived using P_DC_signed/P_shaft_signed',
             'Q1_efficiency':'P_shaft_positive/P_DC_positive',
             'zero_speed_and_zero_torque_efficiency':'omitted as undefined; stationary losses retained in alternative',
             'minimum_rpm':float(nn[0]),'max_rpm_in_efficiency_grid':float(nn[-1]),
             'source_max_rpm':val(s,'mg.max_speed_radps')*RPM,
             'temperature':TEMP,'inverter_losses_included':True,'gear_losses_included':False,
             'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
             'scaled_inertia':'not derived; no physical rotor geometry scaling claimed' if scale!=1 else machines[tag]['inertia']}

# Virtual sizing validation uses interpolation of the EXPORTED EFFICIENCY table,
# not interpolation of electrical power (the two operations are not identical).
gen=machines['MG1_EST']; fn=RegularGridInterpolator((en,et),fuel.T,bounds_error=True)
ETA_DCDC=.97; AUX=1.0; NET=65.0; J_ENGINE=.134; J_GEN=.05
def engine_limit(rpm):return min(np.interp(rpm,ewn,ewt)*S_ENGINE,80000/(rpm/RPM))
def gen_limit(rpm):return min(np.interp(rpm,gen['wn'],gen['wt'])*S_GEN,80000/(rpm/RPM))
def eta(rpm,tq):return float(gen['q4_interp']((rpm,-tq/S_GEN)))
def net(rpm,tq):return rpm/RPM*tq/1000*eta(rpm,tq)*ETA_DCDC-AUX
operating=[]
for rpm in [3000,3500,4000,4500,4750,5000,5250,5500,5750,6000,6250]:
    em=engine_limit(rpm);gm=gen_limit(rpm);limit=min(em,gm);maxnet=net(rpm,limit)
    if maxnet>=NET:
        lower=15*S_GEN
        req=brentq(lambda tq:net(rpm,tq)-NET,lower,limit,xtol=1e-11)
        eshaft=rpm/RPM*req/1000;dc=eshaft*eta(rpm,req);q=float(fn((rpm,req/S_ENGINE)))*S_ENGINE
        operating.append([rpm,clean(em),clean(gm),clean(maxnet),1,clean(req),clean(-req),clean(eshaft),
                          clean(eta(rpm,req)*100),clean(dc),clean(NET),clean(q),clean(q*3.6),clean(q*3600/eshaft),
                          'ASSUMED_warm_virtual_1to1_not_continuous_hardware_rating'])
        assert req<=em+1e-7 and req<=gm+1e-7 and eshaft<=80+1e-7
        assert abs(dc*ETA_DCDC-AUX-NET)<1e-7
    else:
        operating.append([rpm,clean(em),clean(gm),clean(maxnet),0,'','','','','','','','','',
                          'INFEASIBLE_65kW_at_this_rpm_under_virtual_maps'])
write('A_65kW_OperatingPoints.csv',['rpm_engine_and_gen_1to1','engine_WOT_Nm','gen_fullLoad_abs_Nm','maximum_net_bus_kW',
      'can_reach_65kW','engine_torque_Nm','generator_torque_Nm','engine_shaft_kW','gen_and_inverter_eta_pct',
      'rectified_DC_before_converter_kW','net_bus_kW','fuel_g_s','fuel_kg_h','BSFC_g_kWh','status'],operating)
audit['virtual_operating_validation']={'method':'bilinear exported efficiency surface and root solve within both WOT envelopes',
      'net_cap_kW':NET,'DCDC_efficiency_A':ETA_DCDC,'genset_aux_kW_A':AUX,'gear_ratio_A':1,
      'gear_efficiency_A':1,'engine_max_shaft_kW_A':80,'gen_max_shaft_kW_A':80,
      'warm_only':True,'continuous_thermal_rating_verified':False,'voltage_direct330V_valid':False,
      'engine_inertia_default_A':J_ENGINE,'generator_inertia_default_A':J_GEN,
      'scale_not_Honda_or_EMRAX_hardware':'Engine scaled Mazda NA, generator scaled EPA MG1_EST; never label as actual product'}
audit['checks']=['Finite grids and monotonic axes','Positive-speed electrical=shaft+loss',
      'Efficiency percent0to100 and quadrant sign','0rpm and0Nm efficiency not invented',
      'Operating65net inside engine and generator full load','65net balance after converter and aux',
      'Original definitions unchanged','No CRUISE M execution or GUI import verification']
(ROOT/'logs/chart_QA.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
(ROOT/'checkpoints/R65C_02.json').write_text(json.dumps({'stage':'R65C_02','charts_written':True,'numeric_checks_passed':True,
      'virtual_model_status':'DRAFT_NOT_APPLIED','actual_target_maps_found':False,'next':'make workbook and input guide; save deliverables',
      'CRUISE_M_run':False,'existing_inputs_modified':False},indent=2))
print(json.dumps({'chart_csv_count':len(list(OUT.glob('*.csv'))),'virtual65_feasible_rpm':[r[0] for r in operating if r[4]],
                  'rpm6000':[r for r in operating if r[0]==6000],'temperature_coordinate_only':TEMP},ensure_ascii=False))
