"""Reproduce explicitly assumed quasi-static envelopes; not CRUISE M results."""
import json, math
from pathlib import Path
import numpy as np
from scipy.integrate import quad

OUT = Path(__file__).resolve().parents[1]
A, B, C = 126.329494, 0.557775, 0.033456276
MASS = 1757.6704 + 120.0
ETA, AUX, G = 0.95, 0.4, 9.80665
E_USABLE = 58.5

def road(vkmh):
    return A+B*vkmh+C*vkmh**2

def demand(vkmh, grade):
    theta = math.atan(grade)
    return (road(vkmh)+MASS*G*math.sin(theta))*(vkmh/3.6)/1000/ETA+AUX

duration = []
for v, grade in [(100,.04),(120,.04),(120,.06),(100,.05)]:
    p = demand(v, grade)
    duration.append(dict(speed_kmh=v, grade_pct=grade*100, demand_dc_kw=p,
        depletion_minutes={str(pg):60*.1*E_USABLE/(p-pg) if p>pg else None for pg in [26,40,65]}))

height = []
for v, grade, energy in [(100,.05,58.5),(120,.04,58.5),(120,.04,19.5)]:
    p=demand(v,grade)
    rate=(v/3.6)*math.sin(math.atan(grade))
    height.append(dict(speed_kmh=v,grade_pct=grade*100,usable_energy_kwh=energy,
        soc_reserve_pp={str(h):max(p-26,0)*h/rate/3600/energy*100 for h in [300,500,800]}))

accel=[]
for dc in [150,100,60,40]:
    def integrand(v):
        pwh=min(150.,max(dc-AUX,0)*ETA)*1000
        available=pwh-road(v*3.6)*v
        return 1.03*MASS*v/available
    seconds=quad(integrand,80/3.6,120/3.6,epsabs=1e-10)[0]
    accel.append(dict(available_dc_kw=dc,time_80_120_s=seconds))

s=10.0
voc=322.397+1.29836*s-.0184756*s*s+.000143235*s**3
r3=.0806969-.000281326*s+.00000166726*s*s
battery=[]
for np_ in [3,2,1]:
    r=r3*3/np_
    row=dict(parallel=np_,voc_v=voc,r_ohm=r,voltage_only_kw={})
    for vmincell in [2.5,3.0]:
        vmin=96*vmincell
        i_star=max(0,min((voc-vmin)/r,voc/(2*r)))
        row['voltage_only_kw'][str(vmincell)]=i_star*(voc-r*i_star)/1000
    battery.append(row)

def gen(t,pg,r,td,lead=0):
    return np.minimum(pg,r*np.maximum(0,t+lead-td))

# Same special case as existing guide. Deliberately no hindsight in reactive case.
t=np.linspace(0,10,100001)
deficit=np.maximum(80-60-gen(t,26,20,.5),0)
example=dict(demand_kw=80,battery_limit_kw=60,generator_max_kw=26,
    delay_s=.5,ramp_kw_s=20,required_advance_s=1.5,
    reactive_deficit_wh=float(np.trapezoid(deficit,t)/3.6),
    oracle_advance_deficit_wh=float(np.trapezoid(np.maximum(80-60-gen(t,26,20,.5,1.5),0),t)/3.6))

result=dict(evidence_class='ASSUMED_QUASI_STATIC_NOT_CRUISE_M_NOT_MEASURED',
    assumptions=dict(test_mass_kg=1757.6704,additional_mass_kg=120,total_mass_kg=MASS,
        eta_traction=ETA,aux_kw=AUX,usable_energy_kwh=E_USABLE,
        soc_energy_linear_approximation=True,grade_convention='tan(theta)',
        roadload_unchanged_with_extra_mass=True,accel_rotating_mass_factor=1.03,
        battery_current_limit_omitted=True,pack_mass_scaling_omitted=True),
    duration=duration,height=height,acceleration=accel,battery=battery,causality_example=example)
(OUT/'calculation_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
