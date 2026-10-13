"""Read-only original EPA/SwRI vs imported map audit; no fitted correction."""
from pathlib import Path
import csv,json,re,hashlib,sys
import numpy as np
import openpyxl
from scipy.interpolate import RegularGridInterpolator,LinearNDInterpolator
from scipy.spatial import Delaunay
root=Path(__file__).resolve().parents[1];src=Path(sys.argv[1]);out=root/'runs/ANL61905060_20261013/original_map_audit';out.mkdir(exist_ok=True)
def arr(text,key):
 s=re.search(re.escape(key)+r'\s*=\s*\[(.*?)\];',text,re.S).group(1)
 r=[np.fromstring(x.replace('\n',' '),sep=' ') for x in s.split(';') if x.strip()]
 return r[0] if len(r)==1 else np.array(r)
m=next(src.glob('7*.m'));text=m.read_text();w=arr(text,'mg.electric_power_W.axis_1.breakpoints');q=arr(text,'mg.electric_power_W.axis_2.breakpoints');p=arr(text,'mg.electric_power_W.table');loss=(p-w[:,None]*q[None,:])/1000
original=RegularGridInterpolator((w,q),loss,bounds_error=True)
dat=root/'inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat';lines=dat.read_text().splitlines();dq=np.fromstring(lines[5],sep=' ');dw=np.fromstring(lines[8],sep=' ');dl=np.array([np.fromstring(x,sep=' ') for x in lines[11:]])/1000
coords=np.array([(x,y) for y in dq for x in dw]);err=original(coords).reshape(len(dq),len(dw))-dl
assert max(abs(err.ravel()))<1e-9
lookup=RegularGridInterpolator((dw,dq),dl.T,bounds_error=True)
xlsx=next(src.glob('3b*.xlsx'));wb=openpyxl.load_workbook(xlsx,read_only=True,data_only=True);raw=np.array([list(r[:7]) for r in list(wb.active.values)[5:] if isinstance(r[0],(int,float))],float);wb.close();assert raw.shape==(252,7)
saved=np.loadtxt(root.parent/'validation_fix_20261006/inputs/bolt_measured_test_points.csv',delimiter=',',skiprows=1,encoding='utf-8-sig');assert np.max(abs(raw-saved))<1e-10
mc=np.c_[raw[:,1]*np.pi/30,raw[:,3]];me=lookup(mc)-raw[:,4]
with (out/'measured_point_residuals.csv').open('w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['speed_rpm','motor_equivalent_torque_Nm','SwRI_loss_kW','imported_map_loss_kW','residual_kW']);wr.writerows(zip(raw[:,1],raw[:,3],raw[:,4],lookup(mc),me))
rows=list(csv.reader((root/'runs/ANL61905060_20261013/velocity_ANL61905060(1).csv').open()));h=rows[0];a=np.array(rows[2:],float)
def col(n):return a[:,next(i for i,k in enumerate(h) if k=='Time' and n=='Time' or k.startswith('In/'+n+' ('))]
t=col('Time');speed=abs(col('E-Motor Speed'));torque=col('E-Motor Torque');runcoords=np.c_[speed*np.pi/30,torque]
pred=lookup(runcoords);norm=np.array([w[-1],max(abs(q))]);hull=Delaunay(mc/norm);inside=hull.find_simplex(runcoords/norm)>=0
nd=LinearNDInterpolator(mc/norm,raw[:,4])(runcoords/norm);finite=np.isfinite(nd);low=(torque>=0)&(torque<=50)&(speed>100);dt=np.diff(t);window=(t[:-1]>=20)&(t[1:]<=3150)
def coverage(mask):return float(np.sum(dt[window&mask[:-1]&mask[1:]]))
def segenergy(y,mask):
 valid=window&mask[:-1]&mask[1:];return float(np.sum(dt[valid]*(y[:-1][valid]+y[1:][valid])/2)/3600)
def st(x):return {'count':len(x),'bias_kW':float(np.mean(x)),'RMSE_kW':float(np.sqrt(np.mean(x*x))),'max_abs_kW':float(max(abs(x)))}
report={'source_files_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [m,xlsx,src/'process_clean.txt',dat]},'boundary_confirmed_from_original_process':'Combined electric motor, inverter and gearing EDU; hub dynamometer mapping; motor-equivalent speed/torque axes; gearing ratio7.05 and ALPHA gear.efficiency_norm1','original_process_sha256_matches_prior':hashlib.sha256((src/'process_clean.txt').read_bytes()).hexdigest()=='92789114e39d78c2db6fbee466c6da3d26ee4646b5086bb9b736468a87b15b30','original_grid_shape_speed_torque':list(loss.shape),'imported_grid_shape_torque_speed':list(dl.shape),'imported_nodes_max_abs_difference_from_original_bilinear_kW':float(max(abs(err.ravel()))),'original_SwRI_measurements_match_existing_252_rows':True,'measured_residual_all':st(me),'measured_residual_lowtorque_0to50Nm':st(me[(raw[:,3]>=0)&(raw[:,3]<=50)]),'runtime_common_window_s':[20,3150],'runtime_lowtorque_seconds':coverage(low),'runtime_lowtorque_inside_measured_hull_seconds':coverage(low&inside),'runtime_lowtorque_outside_measured_hull_seconds':coverage(low&~inside),'runtime_regen_seconds':coverage(torque<0),'runtime_all_loss_kWh':segenergy(pred,np.ones(len(t),bool)),'runtime_lowtorque_loss_kWh':segenergy(pred,low),'direct_measurement_triangulation_diagnostic':{'comparable_supported_seconds':coverage(finite),'EPA_bilinear_loss_supported_kWh':segenergy(pred,finite),'SwRI_piecewise_linear_loss_supported_kWh':segenergy(nd,finite),'note':'Alternative interpolation of same measurements, diagnostic only; no new map or independent validation; unsupported intervals omitted, not zero-filled'},'regen_basis':'Original EPA process states no measured regen dataset; drive losses mirrored with1.05 factor','voltage_temperature':'Single400V nominal map; no independently identified voltage/temperature response','conclusion':'No unit/axis/transpose or general low-torque inflation found in conversion. Loss boundary is EDU as previously applied. Map mismatch to ANL remains; no correction justified solely from9.45percent energy error.','next':'Use frozen model on61905061 cross-test to separate persistent bias from this-cycle differences; retain current61905060 result as energy-target unmet. No arbitrary efficiency/aux fitting.'}
(out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (out/'runtime_support.csv').open('w',newline='') as f:
 wr=csv.writer(f);wr.writerow(['time_s','speed_rpm','torque_Nm','EPA_imported_loss_kW','inside_measured_hull','lowtorque','SwRI_triangulated_loss_kW']);wr.writerows(zip(t,speed,torque,pred,inside.astype(int),low.astype(int),nd))
print(json.dumps({k:v for k,v in report.items() if k!='source_files_sha256'},ensure_ascii=False))
