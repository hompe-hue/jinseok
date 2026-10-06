"""Reconstruct published Volt Gen2 vector contours; no OEM numeric grid or CRUISE run."""
from pathlib import Path
import csv,json,math,hashlib
import fitz,numpy as np
from scipy.interpolate import LinearNDInterpolator
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/'inputs'; OUT=ROOT/'results'
IN.mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
SRC=ROOT/'sources/MDPI_PowerLosses_2021_vor.pdf'; page=fitz.open(SRC)[7]; drawings=page.get_drawings()
CONFIG={
 'L3A':dict(indices=(12,88),boundary=88,axes=(207.3,353.46,400.5,263.28,1000,6000,140), levels=[round(.11+.01*i,2) for i in range(26)],use=[5,7,9,11,13,15,17,19,21,23,25],speed=range(1100,5901,200),torque=range(20,141,5),pmax=75,tmax=140),
 'MGA':dict(indices=(125,158),boundary=158,axes=(138.3,287.4,612.84,460.98,0,10000,118),levels=[.1,.25,.4,.6,.7,.75,.8,.825,.85,.875,.9,.91,.92,.93,.94,.95],use=[1,2,3,4,6,7,8,9,10,11,12,13,14],speed=range(500,9901,200),torque=range(5,119,5),pmax=48,tmax=118),
 'MGB':dict(indices=(188,208),boundary=208,axes=(337.14,485.7,612.84,460.98,0,10000,280),levels=[.3,.4,.6,.75,.8,.825,.85,.875,.9,.91,.92,.93,.94,.95,.96],use=[0,2,3,4,7,10,11,12,13,14],speed=range(500,9901,200),torque=range(10,281,10),pmax=87,tmax=280)
}
def csvwrite(name,fields,rows):
 with (IN/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def xy(c,p):
 x0,x1,y0,y1,n0,n1,tmax=c['axes'];return ((p.x-x0)/(x1-x0)*(n1-n0)+n0,(y0-p.y)/(y0-y1)*tmax)
def extract(c,indices):
 points=[]
 for j in indices:
  for seg in drawings[j]['items']:
   if seg[0]!='l': raise ValueError('Nonlinear PDF segment requires explicit implementation')
   for point in seg[1:]:points.append(xy(c,point))
 return np.array(points)
MODELS={}; legends=[];qa={}
for name,c in CONFIG.items():
 a,b=c['indices'];colors=list(dict.fromkeys(tuple(round(v,4) for v in drawings[j]['color']) for j in range(a,b)))
 assert len(colors)==len(c['levels'])
 pts=[];vals=[]; raw=[]
 for j in range(a,b):
  d=drawings[j]; idx=colors.index(tuple(round(v,4) for v in d['color']))
  if idx not in c['use']:continue
  pp=extract(c,[j]);eta=c['levels'][idx]
  # Keep points inside plotted axes. Ignore contour label discontinuity, preserve vector vertices.
  pp=pp[(pp[:,0]>=c['axes'][4])&(pp[:,0]<=c['axes'][5])&(pp[:,1]>0)&(pp[:,1]<=c['tmax'])]
  pts.extend(pp.tolist());vals.extend([eta]*len(pp))
  raw.extend(dict(speed_rpm=float(n),torque_Nm=float(t),efficiency_pct=eta*100,pdf_drawing_index=j) for n,t in pp)
 pp=np.array(pts);vv=np.array(vals);uniq,inv=np.unique(np.round(pp,6),axis=0,return_inverse=True)
 means=np.bincount(inv,weights=vv)/np.bincount(inv)
 norm=np.array([c['axes'][5]-c['axes'][4],c['tmax']]);interp=LinearNDInterpolator(uniq/norm,means)
 boundary=extract(c,[c['boundary']]);order=np.argsort(boundary[:,0]);boundary=boundary[order]
 # Same x repeated: top curve uses maximal torque; black line has no alternative enclosed polygon.
 ns=np.unique(np.round(boundary[:,0],6));ts=np.array([boundary[np.isclose(boundary[:,0],n,atol=1e-5),1].max() for n in ns])
 def full(n,ns=ns,ts=ts,c=c):
  if n<ns.min() or n>ns.max():return math.nan
  return min(float(np.interp(n,ns,ts)),c['tmax'],c['pmax']*1000/(n*2*math.pi/60))
 MODELS[name]=(interp,norm,full,c)
 csvwrite(name+'_contour_vertices.csv',['speed_rpm','torque_Nm','efficiency_pct','pdf_drawing_index'],raw)
 curve=[dict(speed_rpm=int(n),source_plot_torque_Nm=float(np.interp(n,ns,ts)),scenario_capped_torque_Nm=full(n)) for n in range(1100 if name=='L3A' else 500,5901 if name=='L3A' else 9901,100)]
 csvwrite(name+'_full_load_source_and_cap.csv',list(curve[0]),curve)
 preview=[]; physical=[]; rejected=[]
 for n in c['speed']:
  for t in c['torque']:
   eta=float(interp(np.array([n,t])/norm).item());lim=full(n)
   reason=''
   if not np.isfinite(eta):reason='outside_contour_convex_hull'
   elif not np.isfinite(lim) or t>.97*lim:reason='outside_scenario_full_load_margin'
   if reason:rejected.append(dict(speed_rpm=n,torque_Nm=t,reason=reason));continue
   p=n*t*2*math.pi/60000
   if name=='L3A':
    # LHV =43MJ/kg is a modelling assumption, not fuel-property measurement for the published map.
    bsfc=3600/(eta*43); fuel_g_s=p/(eta*43)
    physical.append(dict(speed_rpm=n,torque_Nm=t,efficiency_pct=eta*100,BSFC_g_kWh=bsfc,fuel_g_s=fuel_g_s))
    preview.append(dict(Speed_rpm=n,Torque_Nm=t,FuelConsumption_g_s=fuel_g_s))
   else:
    physical.append(dict(speed_rpm=n,torque_abs_Nm=t,efficiency_pct=eta*100))
    for sign in [1,-1]:preview.append(dict(Temperature_degC=25,Voltage_V=360,Speed_rpm=n,Torque_Nm=sign*t,Efficiency_pct=eta*100))
 csvwrite(name+'_warm_core_physical.csv',list(physical[0]),physical)
 csvwrite(name+'_CRUISE_PREVIEW_assumed_axes.csv',list(preview[0]),preview)
 csvwrite(name+'_rejected_grid_points.csv',['speed_rpm','torque_Nm','reason'],rejected)
 if name=='L3A':fl=[dict(Speed_rpm=r['speed_rpm'],Torque_Nm=r['scenario_capped_torque_Nm']) for r in curve]
 else:fl=[dict(Voltage_V=360,Speed_rpm=r['speed_rpm'],Torque_Nm=sign*r['scenario_capped_torque_Nm']) for r in curve for sign in [1,-1]]
 csvwrite(name+'_FullLoad_CRUISE_PREVIEW.csv',list(fl[0]),fl)
 err=np.max(abs(np.asarray(interp(uniq/norm))-means))
 qa[name]=dict(contour_vertices=len(raw),unique_vertices=len(uniq),grid_points=len(physical),preview_rows=len(preview),rejected_grid_points=len(rejected),vertex_reconstruction_max_abs=float(err),max_eta_grid_pct=max(r['efficiency_pct'] for r in physical),cap_interpretation='scenario ceiling; nameplate is not continuous thermal rating')
 for i in c['use']:legends.append(dict(component=name,color_rgb=str(colors[i]),efficiency_pct=100*c['levels'][i],pdf_page=8,provenance='label-calibrated vector contour; not OEM raw measurement'))
 csvwrite(name+'_axis_calibration.csv',['x0_pt','x1_pt','y0_pt','y1_pt','n0_rpm','n1_rpm','tmax_Nm'],[dict(zip(['x0_pt','x1_pt','y0_pt','y1_pt','n0_rpm','n1_rpm','tmax_Nm'],c['axes']))])
csvwrite('contour_legend.csv',list(legends[0]),legends)
# Feasibility is a steady-state map sweep, not vehicle simulation. Fix r per scenario.
def eta(name,n,t):
 f,norm,full,c=MODELS[name]
 if n<c['axes'][4] or n>c['axes'][5] or t<=0 or t>.97*full(n):return math.nan
 return float(f(np.array([n,t])/norm).item())
rows=[];targets=[]
for gen in ['MGA','MGB']:
 for ratio in [.45,.5,.6,.75,1.,1.25,1.5,2.]:
  candidates=[]
  for ne in np.arange(1200,5801,50):
   for te in np.arange(25,141,1):
    ee=eta('L3A',ne,te)
    if not np.isfinite(ee):continue
    ng=ne*ratio;tg=.98*te/ratio;eg=eta(gen,ng,tg)
    if not np.isfinite(eg):continue
    pe=ne*te*2*math.pi/60000
    net=pe*.98*eg*.98*.98-.5
    fuel=pe/(ee*43)
    candidates.append(dict(generator=gen,ratio_generator_over_engine=ratio,engine_rpm=float(ne),engine_torque_Nm=float(te),generator_rpm=float(ng),generator_torque_Nm=-float(tg),engine_shaft_kW=pe,generator_efficiency_pct=eg*100,engine_efficiency_pct=ee*100,net_bus_kW=net,fuel_g_s=fuel,net_fuel_g_kWh=fuel*3600/net if net>0 else math.inf))
  if not candidates:continue
  maximum=max(candidates,key=lambda x:x['net_bus_kW']);rows.append(maximum)
  for target in [20,26,30,35,40,45,65]:
   near=[x for x in candidates if abs(x['net_bus_kW']-target)<.15]
   if near:
    best=min(near,key=lambda x:x['net_fuel_g_kWh']);targets.append(dict(target_net_kW=target,status='candidate_within_reconstructed_warm_core',**best))
   else:targets.append(dict(target_net_kW=target,status='NOT_FOUND_in_this_sweep',**{k:maximum[k] if k in ['generator','ratio_generator_over_engine'] else '' for k in maximum}))
csvwrite('genset_peak_sweep.csv',list(rows[0]),rows)
csvwrite('genset_target_candidates.csv',list(targets[0]),targets)
assumptions=dict(generator_rpm_over_engine_rpm='fixed values [.45,.5,.6,.75,1,1.25,1.5,2]; new coupling, not Voltec PG ratio',coupling_efficiency=.98,inverter_efficiency=.98,DC_DC_efficiency=.98,genset_aux_kW=.5,LHV_MJ_kg=43,full_load_margin=.97,thermal='warm steady-state; no continuous rating or starting map established',temperature_axis_degC=25,voltage_axis_V=360,voltage_basis='vehicle nominal voltage; map test voltage unconfirmed',Q4='positive speed negative torque; eta(|T|) mirrored from published positive map, not independently measured',generator_map_boundary='machine map provisionally excludes TPIM; confirm OEM source before claiming absolute fuel/range',extrapolation='disabled; LinearND inside contour hull; highest enclosed island capped at highest retained contour',fuel_source='eta digitized from secondary reconstruction of Conlon2015; not measured fuel grid')
(OUT/'audit.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),qa=qa,assumptions=assumptions,actual_CRUISE_M_run=False),ensure_ascii=False,indent=2))
print(json.dumps(dict(qa=qa,best_by_generator={g:max([r for r in rows if r['generator']==g],key=lambda x:x['net_bus_kW']) for g in ['MGA','MGB']}),indent=2))
