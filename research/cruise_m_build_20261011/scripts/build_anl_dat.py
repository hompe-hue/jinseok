"""Build a sample-format seven-column profile; preserve prepared speed/time."""
from pathlib import Path
import csv, hashlib, json, math, shutil
root = Path(__file__).resolve().parents[1]
p = root/'empirical_alignment_20261013/ANL_61905054_phase1'
sample = p/'sources/profile_format_sample.dat'
src = p/'ANL_61905054_Phase1_driver_1s.csv'
rows = [(float(r['time_s']), float(r['speed_kmh'])) for r in csv.DictReader(src.open())]
header = sample.read_bytes().decode('ascii').splitlines()[:2]
assert header == ['Time Velocity Gear "Shift Time" "Start Switch" "Min. Velocity" "Max. Velocity"', 's km/h - s - km/h km/h']
assert all(math.isfinite(x) for r in rows for x in r)
assert all(b[0] > a[0] for a,b in zip(rows,rows[1:]))
# No measured speed tolerance envelope is available. Equal lower/upper values
# encode the target only; they are not experimental tolerance measurements.
body = [' '.join([format(t,'.15g'),format(v,'.15g'),'1','0','0' if i==len(rows)-1 else '1',format(v,'.15g'),format(v,'.15g')]) for i,(t,v) in enumerate(rows)]
out = p/'ANL_61905054_BoltEV_Phase1.dat'
out.write_bytes(('\r\n'.join(header+body)+'\r\n').encode('ascii'))
parsed = [list(map(float,s.split())) for s in out.read_text().splitlines()[2:]]
assert len(parsed)==1146 and all(len(r)==7 for r in parsed)
max_error = max(abs(parsed[i][j]-rows[i][j]) for i in range(len(rows)) for j in [0,1])
assert max_error < 1e-10
assert all(r[5] <= r[1] <= r[6] for r in parsed)
distance = sum((b[0]-a[0])*(a[1]+b[1])/2/3600 for a,b in zip(parsed,parsed[1:]))
record = {'vehicle':'2017 Chevrolet Bolt EV','test_id':'ANL 61905054','rows':len(parsed),'columns':7,'duration_s':parsed[-1][0],'distance_km':distance,'max_time_speed_roundtrip_abs_error':max_error,'line_endings':'CRLF','control_columns':{'Gear':1,'Shift Time':0,'Start Switch':'1 except final row 0, following sample'},'speed_bounds':'Min. Velocity = Max. Velocity = target speed; no invented measured tolerance envelope','sha256':{q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in [sample,src,out]},'status':'format and numeric roundtrip verified; CRUISE M GUI import and run pending'}
(p/'dat_format_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ['rows','columns','duration_s','distance_km','status']},ensure_ascii=False))
