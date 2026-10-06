"""R65C-01: preserve source bytes and transcribe the five supplied UI screenshots."""
from pathlib import Path
import csv, json, hashlib, urllib.request, shutil

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT.parent / 'genset_65kW_20261006'
rows = []
for tag in ['EPA_Mazda20_NA_Tier2_ALPHA', 'EPA_Prius_MG1_EST_ALPHA', 'EPA_Prius_MG2_ALPHA']:
    for pattern in ['7*.m', 'process_text.txt', '3a*.html', '3-*.html']:
        for p in (PREV/'sources/extracted'/tag).glob(pattern):
            dest = ROOT/'sources'/tag/p.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
            rows.append({'file':str(dest.relative_to(ROOT)), 'source':str(p),
                         'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(), 'altered':False})
url = 'https://www.energy.gov/sites/prod/files/2014/03/f13/ape006_burress_2013_o.pdf'
p = ROOT/'sources/ORNL_Leaf_2013_merit_review.pdf'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:
    data = r.read()
assert data.startswith(b'%PDF')
p.write_bytes(data)
rows.append({'file':str(p.relative_to(ROOT)), 'source':url, 'sha256':hashlib.sha256(data).hexdigest(),
             'note':'80kW continuous MOTOR test, not generator qualification; 375V, coolant65C, slide12.'})
for i,name in enumerate(['101513','101536','101611','101630','101658'],1):
    p = ROOT.parents[1]/'upload'/f'image(20261006-{name}).png'
    rows.append({'screenshot':i,'local_file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'sources/manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
fields = [
 (1,'ICE','Fuel consumption map unit','Expressed as mass flow','g/s or kg/h','Program subtable unit not shown; offer both files'),
 (1,'ICE','Engine type','Reciprocating 4 stroke','','Keep for reference and virtual NA'),
 (1,'ICE','Transient model','Naturally aspirated','','NA reference; no calibrated transient response available'),
 (1,'ICE','Friction model','unchecked','','Brake-torque map; adding friction may double count'),
 (1,'ICE','Control mode','Torque controlled','','Supervisory torque/speed regulation required'),
 (1,'ICE','Zero load criteria','0 Load => 0 Torque','','Engine-idling fuel must not be replaced by zero'),
 (1,'ICE','Full load gear dependent','unchecked','','No gear-dependent engine WOT source'),
 (1,'ICE','Fuel shut off','unchecked','','Source closed-throttle negative-torque region contains fuel cut; resolve in actual Program'),
 (1,'ICE','Fuel type','Gasoline.bgp','','Fuel properties must match selected map'),
 (1,'ICE','Specific carbon content',0.87591,'-','Screenshot value; Mazda reference FTAG24350=0.826'),
 (1,'ICE','Fuel lower heat',43500,'kJ/kg','Screenshot value; Mazda reference=41835'),
 (1,'ICE','Fuel density',748,'kg/m3','Screenshot value; Mazda reference=750.2 at15C'),
 (2,'Engine Data','Displacement',2,'L','Reference1.998; virtual candidate1.5'),
 (2,'Engine Data','Number of cylinders',4,'-','Reference4; virtual4 assumed'),
 (2,'Engine Data','Engine inertia',0.134,'kg*m2','Screenshot/default; not measured for target'),
 (2,'Engine Data','Inertia of auxiliaries',0,'kg*m2','Screenshot/default; identify coupling hardware'),
 (2,'Engine Data','Stall speed',500,'rpm','Screenshot/default; no validated target'),
 (2,'Engine Data','Maximum engine speed',7500,'rpm','Reference envelope ends6875; virtual same assumed'),
 (2,'Engine Data','Delta static friction',0.1,'N*m','Screenshot/default; no validated target'),
 (3,'Generator','Global losses map','checked','','EPA EMOT includes motor+inverter, excludes gearing'),
 (3,'Generator','Type of motor','Asynchronous motor','','Reference PMSM/IPM; choose matching available synchronous type'),
 (3,'Generator','Characteristics expressed as','Torque','','Keep: rpm and Nm'),
 (3,'Generator','Losses depending on','Torque','','Keep: rpm and torque axes'),
 (3,'Generator','Losses','Efficiency','','Use percent; separate power-loss alternative for startup/zero torque'),
 (3,'Generator','Control mode','Mechanical load','','Keep for positive speed negative torque generator'),
 (3,'Generator','Q1 Motor','checked','','Starter quadrant if same machine cranks engine'),
 (3,'Generator','Q4 Generator','checked','','Positive speed, negative torque'),
 (3,'Generator','Q2 / Q3','unchecked','','Reverse rotation not exported'),
 (3,'Generator','Inertia',0.05,'kg*m2','Screenshot/default; reference MG1=0.00562277135625, MG2=0.010773667'),
 (3,'Generator','Maximum speed','undefined','rpm','Reference source13500, efficiency grid verified only to13000'),
 (3,'Generator','KPI generator max power',150.796447,'kW','Derived from current chart, not direct65kW rating input'),
 (4,'Full Load','columns','Voltage; Speed; Torque','V; rpm; N*m','Current330V must not relabel source650V'),
 (5,'Efficiency','columns','Temperature; Voltage; Speed; Torque; Efficiency','degC; V; rpm; N*m; %','Current0C is chart coordinate, not source test temperature'),
]
with (ROOT/'inputs/UI_fields_transcription.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['image','section','field','screenshot_value','unit','mapping_note']);w.writerows(fields)
checkpoint={'stage':'R65C_01','source_copy_hashes_verified':True,'screenshots_transcribed':5,
            'exact_target_full_map_found':False,'new_physical_rating_evidence':'ORNL80kW motor continuous at7000rpm; not generator rating',
            'existing_inputs_modified':False,'CRUISE_M_run':False,'next':'convert reference charts; separate virtual sensitivity draft'}
(ROOT/'checkpoints/R65C_01.json').write_text(json.dumps(checkpoint,indent=2))
print(json.dumps(checkpoint))
