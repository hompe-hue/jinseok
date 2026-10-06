"""Synthetic dimensional and rejection checks; not vehicle validation."""
import json
import numpy as np
import pandas as pd
from evaluate_cruise_trace import evaluate,compare,ROOT

def check():
    t=np.arange(1001,dtype=float)
    d=pd.DataFrame({'time_s':t,'speed_kmh':36.,'motor_speed_rpm':2000.,'motor_torque_Nm':30.,'pack_voltage_V':400.,'pack_current_A':25.,'soc_fraction':.5,'fuel_g_s':2.,'engine_on':1.,'stored_energy_kWh':30.})
    m=json.loads((ROOT/'inputs/trace_metadata_template.json').read_text());m['powertrain']='EREV'
    r=evaluate(d,m)
    assert abs(r['distance_km']-10)<1e-10
    assert abs(r['net_battery_DC_kWh']-10/3.6)<1e-10
    assert abs(r['fuel_kg']-2)<1e-10
    assert not r['full_range_claim_ready'] and not r['comparison_ready_without_range_claim']
    bad=d.copy();bad.loc[0,'motor_torque_Nm']=400
    assert evaluate(bad,m)['map_outside_domain_rows']==1
    bad=d.copy();bad.loc[1,'time_s']=0
    try:evaluate(bad,m)
    except ValueError:pass
    else:raise AssertionError('Repeated time accepted')
    bad=d.copy();bad['soc_fraction']=50.
    try:evaluate(bad,m)
    except ValueError:pass
    else:raise AssertionError('Percent SOC accepted as fraction')
    # For comparison-gate checks only, explicit fixtures declare all conditions matched.
    fixture={**r,'comparison_ready_without_range_claim':True,'metadata':{k:'fixture' for k in ['vehicle_model_id','battery_parameter_id','soc_definition','cycle_id','temperature_condition','auxiliary_condition','initialization_id','energy_boundary','genset_parameter_id','fuel_map_id']}}
    assert compare(fixture,fixture)['fuel_comparison_accepted']
    other={**fixture,'end_stored_energy_kWh':30.2}
    assert not compare(fixture,other)['fuel_comparison_accepted']
    out={'test_origin':'SYNTHETIC_FIXTURE_NOT_CRUISE_M','checks_passed':['distance_units','battery_DC_energy_units','fuel_mass_units','unverified_metadata_rejected','outside_full_load_detected','duplicate_time_rejected','SOC_percent_rejected','unequal_terminal_energy_rejected'],'CRUISE_M_executed':False}
    (ROOT/'results/evaluator_checks.json').write_text(json.dumps(out,indent=2));print(out)

if __name__=='__main__':check()
