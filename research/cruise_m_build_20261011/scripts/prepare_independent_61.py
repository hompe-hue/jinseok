"""Recover unavailable 61905061 run inputs from already acquired source; no model tuning."""
from pathlib import Path
import csv, hashlib, json, sys, zipfile
import numpy as np
from nptdms import TdmsFile

root=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]); out=root/'independent_tests_20261013/ANL61905061';out.mkdir(parents=True,exist_ok=True)
receipt=json.loads(src.with_name('download.json').read_text())
assert hashlib.sha256(src.read_bytes()).hexdigest()==receipt['sha256']
g=TdmsFile.read(src).groups()[0];props=g.properties
start=int(props['Phase_1_Phase_Start_Fill_Index'])-1;stop=int(props['Phase_1_Phase_Stop_Fill_Index'])
def col(n):return np.asarray(g[n][:][start:stop],dtype=float)
t=col('Time_H0');t=t-t[0];v=col('Dyno_Spd')*1.609344
assert np.all(np.isfinite(t)) and np.all(np.diff(t)>0) and np.max(np.diff(t))<2
assert abs(t[-1]-props['Phase_1_Phase_Length_s'])<1e-6
fields={'phase_time_s':t,'speed_kmh':v,'meter_voltage_V':col('Batt_Volt_Hioki_U1'),'meter_current_A_discharge_positive':col('Batt_Curr_Hioki_I1'),'meter_power_kW_discharge_positive':col('Batt_Power_Hioki_P1'),'LV_DCDC_output_W':col('DCDC_Out_Power_Hioki_P3'),'displayed_SOC_percent':col('HVBatt_SOC_displayed_CAN3'),'HPCM2_SOC_percent':col('HVBatt_pack_SOC_HPCM2'),'battery_temperature_C':col('HVBatt_cell_temp_1_CAN3'),'CAN_clock_s':col('Time_3')}
assert all(np.all(np.isfinite(a)) for a in fields.values())
with (out/'reference_native.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(fields);w.writerows(zip(*fields.values()))
times=np.r_[np.arange(int(np.floor(t[-1]))+1),t[-1]] if t[-1]%1 else np.arange(int(t[-1])+1)
speed=np.interp(times,t,v);assert np.min(speed)>=-0.01;speed=np.maximum(speed,0)
with (out/'driver_1s.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['time_s','speed_kmh']);w.writerows(zip(times,speed))
header=(root/'empirical_alignment_20261013/ANL_61905054_phase1/sources/profile_format_sample.dat').read_text().splitlines()[:2]
lines=[' '.join([f'{x:.15g}',f'{y:.15g}','1','0','0' if i==len(times)-1 else '1',f'{y:.15g}',f'{y:.15g}']) for i,(x,y) in enumerate(zip(times,speed))]
dat=out/'ANL61905061_BoltEV_Phase1.dat';dat.write_bytes(('\r\n'.join(header+lines)+'\r\n').encode('ascii'))
parsed=np.loadtxt(dat,skiprows=2);assert parsed.shape==(len(times),7)
assert np.max(np.abs(parsed[:,0]-times))<1e-10 and np.max(np.abs(parsed[:,1]-speed))<1e-10
trap=getattr(np,'trapezoid',np.trapz)
native_km=trap(v,t)/3600;driver_km=trap(speed,times)/3600
ocv=np.loadtxt(root/'inputs/battery/Bolt_Cell_OCV_25C.dat',skiprows=2)
res=np.loadtxt(root/'inputs/battery/Bolt_Cell_Resistance_25C.dat',skiprows=2)
initial_v=fields['meter_voltage_V'][0];initial_i=fields['meter_current_A_discharge_positive'][0]
def pack(s):return 96*np.interp(s,ocv[:,0],ocv[:,1])-32*np.interp(s/100,res[:,0],res[:,1])*initial_i
assert pack(0)<=initial_v<=pack(100)
lo,hi=0.,100.
for _ in range(80):
 mid=(lo+hi)/2
 if pack(mid)<initial_v:lo=mid
 else:hi=mid
soc=(lo+hi)/2
record={'test_id':'61905061','stage':'recovered_run_inputs_only','source_sha256':receipt['sha256'],'source_url':receipt['source'],'phase_start_row_zero_based':start,'phase_stop_row_exclusive':stop,'duration_s':float(t[-1]),'native_rows':len(t),'driver_rows':len(times),'native_distance_km':native_km,'driver_distance_km':driver_km,'resampling_distance_difference_percent':(driver_km/native_km-1)*100,'initial_voltage_V':initial_v,'initial_current_A':initial_i,'initial_SOC_model_percent':soc,'initial_SOC_basis':'First low-load voltage inversion using unchanged imported OCV/R tables; initialization only, not physical/CAN SOC mapping','initial_battery_temperature_C':fields['battery_temperature_C'][0],'test_cell_temperature_C':props['Phase_1_Cell_Temp_C'],'aux_kW_held':0.4,'peak_discharge_power_kW':max(fields['meter_power_kW_discharge_positive']),'BMS_45kW_rule':'Preserve existing example setting from user screenshot; not a measured Bolt limit','source_summary_energy_kWh':props['Phase_1_Elec_Whr_Whr']/1000,'CAN_clock_caution':'Raw merged CAN clock retained; no new continuous SOC interpolation or endpoint SOC validation','run_status':'CRUISE M import/run pending; Windows project unavailable','next_test':'Evaluate61905060 and61905061 fixed-model comparison together; do not declare validation from preparation','prior_prepared_files_unavailable':True,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
(out/'checkpoint.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(out/'NEXT_RUN_KO.md').write_text(f'''# 다음 실행: ANL61905061\n\n기존 회생복구 BEV 케이스를 복사하여 별도 케이스로 실행한다.\n\n| 항목 | 입력 |\n|---|---:|\n| 속도 DAT | ANL61905061_BoltEV_Phase1.dat |\n| 종료시간 | {t[-1]:.9f} s |\n| Module 1/2 초기 SOC | 둘 다 {soc:.6f}% |\n| Battery Defined temperature | {fields['battery_temperature_C'][0]:.2f} °C |\n| Environment temperature | {props['Phase_1_Cell_Temp_C']:.6f} °C |\n| Power Consumer → General → Power | 0.40 kW / W 단위면 400 W |\n\n초기 SOC는 현행 OCV/R표와 첫 실측 저부하 전압으로 초기화한 값이다. 실측 표시 SOC와 동일한 좌표라고 주장하지 않는다. 보조부하는 앞선 실행의 0.40 kW를 유지하며 이번 시험에 맞춰 재식별하지 않는다.\n\n질량·ABC·모터/배터리맵·용량·회생진단 충전맵·기존 45 kW 방전제한은 유지한다. 발전은 BEV 비활성 상태로 유지하고 결과 CSV에서 출력·연료 0을 확인한다. 기존 발전제어가 새 SOC에서 작동한다면 BEV 실행으로 판정하지 않는다.\n\n실측 피크 방전전력 {record['peak_discharge_power_kW']:.3f} kW가 현행 45 kW를 넘는다. 속도 추종오차가 나면 제한의 영향을 결과로 기록한다. 결과에 맞추기 위해 이번 실행 중 한계를 조정하지 않는다.\n\n실행 후 velocity_ANL61905061.csv, battery_ANL61905061.csv, generator_ANL61905061.csv를 export한다. 새 Report Page에서 새 케이스를 선택한다. 기존 61905054 CSV를 덮어쓰지 않는다.\n\n이번 완료범위는 원본 기반 입력파일 복구·형식 검증이다. CRUISE M 실행과 독립 실측 비교는 미완료이며 다음 시작점이다. 61905061 입력 준비와 실제 실행 결과 비교를 구분한다.\n''')
print(json.dumps({k:record[k] for k in ['duration_s','initial_SOC_model_percent','initial_battery_temperature_C','test_cell_temperature_C','driver_rows','resampling_distance_difference_percent']}))
