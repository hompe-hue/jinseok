"""Verify preserved imports. This does not run or validate CRUISE M."""
from pathlib import Path
import csv, math, zipfile, json, hashlib
root = Path(__file__).resolve().parents[1]
p = root / 'inputs'
lines = (p/'Bolt_EDU_Loss_400V_AVL_RegularMap.dat').read_text().splitlines()
assert lines[:3] == ['# regular map', '# dimensions', '17 17']
assert lines[4] == 'moment~Nm' and lines[7] == 'ang_vel~rad_s' and lines[10] == 'power~W'
torques = list(map(float, lines[5].split()))
speeds = list(map(float, lines[8].split()))
loss = [list(map(float, l.split())) for l in lines[11:]]
assert len(loss)==17 and all(len(r)==17 for r in loss)
assert all(v>=0 and math.isfinite(v) for r in loss for v in r)
source = list(csv.reader((p/'sources/bolt_loss_matrix_kW.csv').open(encoding='utf-8-sig')))
assert len(source)==13 and len(source[0])==18
for j, t in enumerate(map(float, source[0][1:])):
    assert math.isclose(t, torques[j], abs_tol=1e-10)
    for row in source[1:]:
        omega=float(row[0])*math.pi/30
        i=min(range(17), key=lambda k:abs(speeds[k]-omega))
        assert math.isclose(speeds[i], omega, abs_tol=1e-9)
        assert math.isclose(loss[j][i], float(row[j+1])*1000, abs_tol=1e-7)
ocv=(p/'battery/Bolt_Cell_OCV_25C.dat').read_text().splitlines()
res=(p/'battery/Bolt_Cell_Resistance_25C.dat').read_text().splitlines()
assert ocv[:2]==['"State of Charge" Voltage','% V']
assert res[:2]==['"State of Charge" Resistance','[-] Ohm']
assert len(ocv)==len(res)==103
for s in range(101):
    x,u=map(float,ocv[s+2].split()); y,r=map(float,res[s+2].split())
    assert math.isclose(x,s) and math.isclose(y,s/100,abs_tol=1e-10)
    assert math.isclose(u,(322.397+1.29836*s-.0184756*s*s+.000143235*s**3)/96,abs_tol=1e-10)
    assert math.isclose(r,(.0806969-.000281326*s+.00000166726*s*s)*3/96,abs_tol=1e-12)
for name in ['Bolt_Cell_OCV_25C.dat','Bolt_Cell_Resistance_25C.dat']:
    raw=(p/'battery'/name).read_bytes()
    assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n',b'')
with zipfile.ZipFile(p/'Bolt_Battery_Cell_Import_20261011.zip') as z:
    for name in ['Bolt_Cell_OCV_25C.dat','Bolt_Cell_Resistance_25C.dat']:
        member=next(n for n in z.namelist() if n.endswith(name))
        assert z.read(member)==(p/'battery'/name).read_bytes()
report={'status':'PASS','motor_original_points_preserved':204,'motor_regular_map_points':289,
        'battery_points_per_table':101,'CRUISE_M_executed':False,
        'input_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in sorted(p.rglob('*')) if f.is_file()}}
print(json.dumps(report,ensure_ascii=False,indent=2))
