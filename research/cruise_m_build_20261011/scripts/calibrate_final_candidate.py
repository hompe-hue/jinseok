"""Empirical warm-BEV candidate fit on060/061 only, not component identification.

Preserve torque-dependent EDU loss increments; calibrate a speed-baseline
subtraction. Fit a monotone effective OCV correction at two SOC knots and one
R multiplier from measured-current replay with common initialization rule.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid,solve_ivp
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import least_squares,brentq
from audit_dis80_semantic import SavedProject,ROOT

OUT=ROOT/'runs/final_candidate_C1_20261014';OUT.mkdir(parents=True,exist_ok=True)
def col(d,n):
    a=[k for k in d if k.startswith('In/'+n+' (')];assert len(a)==1,(n,a)
    return d[a[0]].to_numpy()
def energy(x,t):
    tt=np.r_[20,t[(t>20)&(t<t[-1])],t[-1]]
    return float(np.trapezoid(np.interp(tt,t,x),tt)/3600)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    source=Path(sys.argv[1]);proj=SavedProject(source)
    maps={};maparrays={}
    for n in proj.nodes('cruise.props.electric_machine.PowerLoss'):
        aa=proj.arrays_under(n)
        if len(aa)!=5 or not len(aa[1][2]) or not np.all(aa[1][2]==400):continue
        temp,v,rpm,tq,loss=[x[2] for x in aa]
        label='Q1' if tq.min()>=0 else 'Q4'
        d=pd.DataFrame(dict(rpm=rpm,tq=tq,loss=loss))
        g=d.pivot(index='tq',columns='rpm',values='loss').sort_index().sort_index(axis=1)
        assert g.notna().all().all()
        maps[label]=(g.index.to_numpy(),g.columns.to_numpy(),RegularGridInterpolator((g.index,g.columns),g.to_numpy(),bounds_error=True))
        maparrays[label]=aa
    assert set(maps)=={'Q1','Q4'}
    zeroq,zerow,f=maps['Q1'];zero=f(np.c_[np.zeros(len(zerow)),zerow]);edgeq=maps['Q4'][0].max()
    bounds=[]
    for label,aa in maparrays.items():
        baseline=np.interp(aa[2][2],zerow,zero)*(1 if label=='Q1' else 1.05)
        bounds.append(float(np.min(aa[4][2]/baseline)))
    beta_limit=min(1.,min(bounds)*.999)
    ocv0=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
    r0=np.loadtxt(ROOT/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
    def tables(z):
        delta=np.interp(ocv0[:,0],[0,50,60,70,85,100],[0,0,z[0],z[1],0,0])
        return ocv0[:,1]+delta/96,r0[:,1]*z[2]
    def funcs(z):
        uu,rr=tables(z)
        return lambda s:96*np.interp(s,ocv0[:,0],uu),lambda s:32*np.interp(s/100,r0[:,0],rr)
    def init(v,i,z):
        u,r=funcs(z)
        return brentq(lambda s:u(s)-i*r(s)-v,0,100)
    data=[]
    region=json.loads((ROOT/'runs/validation_closure_20261014/residual_regions.json').read_text())
    for test,folder,suffix in [('61905060','ANL61905060_DIS80_20261013','DIS80'),('61905061','ANL61905061_20261013','')]:
        vpath=ROOT/f'runs/{folder}/velocity_ANL{test}{suffix}.csv';bpath=ROOT/f'runs/{folder}/battery_ANL{test}{suffix}.csv'
        v=pd.read_csv(vpath,skiprows=[1]);b=pd.read_csv(bpath,skiprows=[1]);assert np.array_equal(v.Time,b.Time)
        refpath=ROOT/f'independent_tests_20261013/ANL{test}/reference_native.csv';ref=pd.read_csv(refpath)
        t=b.Time.to_numpy();w=col(v,'E-Motor Speed');q=col(v,'E-Motor Torque');shaft=col(v,'E-Motor Power Mech.')
        volt=col(b,'Voltage');motor=col(v,'E-Motor Current')*volt/1000;aux=col(v,'E-Consumer Current')*volt/1000
        assert np.all(abs(aux-.4)<1e-8)
        baseline=np.interp(w,zerow,zero)
        multiplier=np.where(q>=0,1.,np.where(q<=edgeq,1.05,1+.05*q/edgeq))
        # Inactive motor at zero shaft/zeroDC does not consume the map baseline.
        active=(abs(motor)>1e-8)|(abs(shaft)>1e-8)
        basis=np.where(active,baseline*multiplier,0.)
        nt=ref.phase_time_s.to_numpy();ir=np.interp(t,nt,ref.meter_current_A_discharge_positive);vr=np.interp(t,nt,ref.meter_voltage_V)
        native_i=ref.meter_current_A_discharge_positive.to_numpy()
        ah=cumulative_trapezoid(native_i,nt,initial=0)/3600
        ahgrid=np.interp(t,nt,ah)
        known=next(x for x in region if x['test']==test)
        data.append(dict(test=test,t=t,mask=t>20,ref=ref,vr=vr,ir=ir,ah=ahgrid,reference_kWh=known['reference_native_kWh'],
          initial_V=float(ref.meter_voltage_V.iloc[0]),initial_I=float(native_i[0]),shaft=shaft,motor=motor,aux=aux,power=motor+aux,basis=basis,
          source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [vpath,bpath,refpath]}))
    a=np.array([energy(d['basis'],d['t'])/d['reference_kWh'] for d in data]);y=np.array([energy(d['power'],d['t'])/d['reference_kWh']-1 for d in data])
    beta=float(np.clip(a@y/(a@a),0,beta_limit))
    for d in data:d['candidate_power']=d['power']-beta*d['basis']
    # Fit only calibrated test voltage. Each test carries equal overall weight.
    def residual(z):
        u,r=funcs(z);parts=[]
        for d in data:
            s0=init(d['initial_V'],d['initial_I'],z);s=s0-d['ah']/168*100
            err=u(s)-d['ir']*r(s)-d['vr'];mask=d['mask']
            parts.append(err[mask]/np.sqrt(mask.sum()))
        return np.concatenate(parts)
    # Bound empirical OCV correction to50mV/cell; no unconstrained polynomial.
    max_delta=.05*96
    fit=least_squares(residual,[0,0,1],bounds=([-max_delta,-max_delta,.5],[max_delta,max_delta,2.]),xtol=1e-12,ftol=1e-12,gtol=1e-10,max_nfev=120)
    assert fit.success,fit.message
    z=fit.x;newu,newr=tables(z)
    assert np.all(np.diff(newu)>0) and np.all(newr>0)
    results=[]
    u,r=funcs(z)
    for d in data:
        t=d['t'];power=d['candidate_power'];s0=init(d['initial_V'],d['initial_I'],z)
        def current(tt,s):
            uu=float(u(s));rr=float(r(s));pp=float(np.interp(tt,t,power))*1000
            disc=uu*uu-4*rr*pp
            assert disc>0
            return 2*pp/(uu+np.sqrt(disc))
        sol=solve_ivp(lambda tt,s:[-current(tt,float(s[0]))/3600/168*100],(t[0],t[-1]),[s0],t_eval=t,max_step=.5,rtol=1e-8,atol=1e-10)
        assert sol.success
        ss=sol.y[0];ii=np.array([current(tt,s) for tt,s in zip(t,ss)]);vv=u(ss)-ii*r(ss)
        e=vv[d['mask']]-d['vr'][d['mask']]
        sm=s0-d['ah']/168*100;em=(u(sm)-d['ir']*r(sm)-d['vr'])[d['mask']]
        en=energy(power,t);ee=100*(en/d['reference_kWh']-1)
        rec=dict(test=d['test'],initial_SOC_rule_percent=float(s0),measured_current_replay_voltage_RMSE_V=float(np.sqrt(np.mean(em*em))),
          measured_current_replay_voltage_bias_V=float(em.mean()),frozen_shaft_power_energy_error_percent=ee,
          frozen_power_replay_voltage_RMSE_V=float(np.sqrt(np.mean(e*e))),frozen_power_replay_voltage_bias_V=float(e.mean()),
          screened_energy_kWh=en,reference_native_kWh=d['reference_kWh'],model_SOC_range_percent=[float(ss.min()),float(ss.max())],
          screen_targets_met=bool(abs(ee)<=5 and np.sqrt(np.mean(e*e))<=2 and abs(e.mean())<=1),source_sha256=d['source_sha256'])
        results.append(rec)
        pd.DataFrame(dict(time_s=t,candidate_frozen_DC_kW=power,candidate_voltage_V=vv,reference_voltage_V=d['vr'],candidate_SOC_percent=ss,candidate_current_A=ii)).to_csv(OUT/f'CAL{d["test"]}_screen.csv',index=False)
    params={'candidate':'C1','status':'CANDIDATE_SCREENED_CRUISE_NOT_RUN','source_project_sha256':sha(source),
      'calibration_tests':['61905060','61905061'],'heldout_test':'61905066','no_fit_on066':True,
      'EDU_speed_baseline_subtraction_fraction':beta,'EDU_fraction_positive_loss_limit':beta_limit,
      'EDU_rule':'LossC1(T,w)=LossOriginal(T,w)-beta*LossOriginal(0,w); Q4 subtracts1.05 timesQ1zero baseline; lowtorque bridge follows changedboundarynodes. Keep torque-dependent differences and loss>0.',
      'battery_OCV_pack_correction_V_at_SOC60':float(z[0]),'battery_OCV_pack_correction_V_at_SOC70':float(z[1]),
      'battery_OCV_correction_SOC_knots_percent':[0,50,60,70,85,100],'battery_OCV_correction_values_V':[0,0,float(z[0]),float(z[1]),0,0],
      'battery_R_multiplier':float(z[2]),'initial_SOC_rule':'Firstlow-loadV/I inversionusingC1OCV/R;capacity168Ah;nomannualoffset;noCANmappingclaim',
      'OCV_cell_correction_bound_mV':50,'OCV_bound_active':bool(np.any(abs(z[:2])>max_delta-1e-5)),
      'preserved':['mass','TargetABC','gear7.05','radius0.3135','aux0.4kW','battery96S3P168Ah','originalRCoff','regencontrollerdistribution','80kWdiagnosticBMSmap'],
      'physical_component_identification':False,'new_CRUISE_results':False,'results':results,
      'candidate_screen_gate_met':all(x['screen_targets_met'] for x in results),
      'limitations':['Effectivevehicle-level warmBEVcalibration,notmeasuredneutralgearorcellOCV/Ridentification','Fixedshaft/controltrace screening; actualCRUISErequired','LowSOC/lowtemperature/highSOCOCVgeneralizationnotvalidated','061screenusesold45kWtrajectory;C1confirmationusescommon80kWmap']}
    (OUT/'parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2)+'\n')
    (OUT/'inputs').mkdir(exist_ok=True)
    for fname,values,x in [('C1_Cell_OCV_25C.dat',newu,ocv0[:,0]),('C1_Cell_Resistance_25C.dat',newr,r0[:,0])]:
        header=['"State of Charge" Voltage','% V'] if 'OCV' in fname else ['"State of Charge" Resistance','- Ohm']
        (OUT/'inputs'/fname).write_bytes(('\r\n'.join(header+[f'{s:.12g}\t{v:.16g}' for s,v in zip(x,values)])+'\r\n').encode())
    for label,aa in maparrays.items():
        base=np.interp(aa[2][2],zerow,zero)*(1 if label=='Q1' else 1.05)
        loss=aa[4][2]-beta*base;assert np.all(loss>0)
        pd.DataFrame(dict(temperature_K=aa[0][2],voltage_V=aa[1][2],rpm=aa[2][2],torque_Nm=aa[3][2],original_loss_kW=aa[4][2],C1_loss_kW=loss)).to_csv(OUT/'inputs'/f'C1_EDU_{label}_loss_nodes.csv',index=False)
    print(json.dumps(params,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
