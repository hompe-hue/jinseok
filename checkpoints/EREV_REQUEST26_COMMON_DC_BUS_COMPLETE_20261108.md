# Checkpoint EREV request-controlled common DC bus, 2026-11-08

Completed after checkpoint 7383f9239872f43a36b463132fba30645d2f24db.

Archive: EREV_Request26_Common_DC_Bus_Complete.zip
SHA256: 53dc2f8b9bd158f9805e9a508364f276ad96ace97a99a840285671cf21e6ba89
Library: libfile_19cfdcc07ebc8191af5812991ac820b7
Download: https://chatgpt.com/library?file_id=libfile_19cfdcc07ebc8191af5812991ac820b7&account_id=personal

Full source data and normalized trace retained in archive. No earlier checkpoint, project or rule modified.

# 요청형 26 kW 발전원 공통 DC 버스 검증 완료

## 완료 범위
제출된 Plus, BMS, Vehicle CSV와 앞서 통과한 Generator Monitor 원본을 결합했다. 네 파일 모두 0–16초, 2 ms, 8001행이며 시간축이 정확히 일치한다. 기존 evaluate_bench.py의 10개 조건을 수정 없이 적용했고 전부 통과했다. 시간 이동이나 필터링 없이 실제 Plus 단자 출력으로 평가했다.

| 항목 | 결과 |
|---|---:|
| 정상 구간 발전 | 26.000002 kW |
| 정상 구간 부하 | 10.000000 kW |
| 정상 구간 배터리 충전 | 16.000003 kW |
| 최대 DC 버스 잔차 | 0.003912 W |
| 원래 기준파형 대비 RMSE | 0.031652 kW (기준 ≤0.1 kW) |
| 16초 발전 단자 에너지 | 65.794453 Wh |
| 16초 실제 부하 에너지 | 44.444444 Wh |
| 배터리 순충전 단자 에너지 | 21.350010 Wh |
| SOC | 81.252051 → 81.282523 % |

잔차 정의는 배터리 방전 전력 + 발전원 주입 전력 − 실제 부하 전력이다. Plus 전력/전류는 음수가 공급이므로 부호를 반전했다. BMS Power는 kW, 음수가 방전이므로 부호를 반전했다. 부하는 Vehicle의 소비기 및 모터 전류 합에 동일 버스 전압을 곱해 산출했다. 정상 구간은 3–10초다.

## 모니터와 단자 출력 차이
순간 차이 최대 49.99285 W, RMSE 10.34597 W다. 앞뒤 Generator Monitor 샘플 평균과 비교하면 최대 2.96747 W, RMSE 0.36890 W로 줄어든다. 기록·적분 구간 차이와 부합하지만 Job Log 없이 내부 구현을 단정하지 않는다. 이 진단용 평균은 10개 합격 판정에 사용하지 않았다. 발전원 내부 누적 에너지와 실제 단자 적분의 차이는 0.00000874 Wh다.

## 에너지 해석
BMS Energy 채널의 증가량은 25.767893 Wh이고, 실제 단자 순충전 적분은 21.350010 Wh다. 저장 에너지 지표와 DC 단자 에너지는 정의/경계가 다르므로 이 차이를 공통 버스 수지 오차로 해석하지 않는다. BMS Energy 산식과 배터리 내부 손실의 구체적 분해는 이 CSV만으로 확정하지 않았다.

## 보존한 완료 상태와 한계
앞서 Generator Monitor의 요청·기동·정지·타이머 16개 검증은 원본 SHA-256 동일성 확인 후 결과를 승계했다. 해당 검증을 이번 10개 버스 조건과 혼동하지 않는다. 이전 발전 0 W 실행 및 고정 파형 시험은 별도 결과로 보존한다.

실행 후 저장한 프로젝트와 Job Log는 이번 입력에 없어 실행 프로젝트 해시와 동일 Job 여부를 독립적으로 입증하지 못했다. 네 CSV의 시간축·전압·부하·발전 에너지는 일관된다. 실제 엔진/발전기 효율·연료·열·주행 EMS 검증 완료를 의미하지 않는다.

## 다음 시작점
현재 요청 펄스 시험은 완료다. 다음은 동일 R1 프로젝트 기반의 실제 보호정지, 충전 수용량 제한, 재기동 최소 OFF 시간 시험 준비 및 CRUISE 실행이다. 기존 26 kW, 기동 0.5초, 상승 20 kW/s, 정상 하강 50 kW/s, 최소 ON 10초, 최소 OFF 5초 규칙을 유지한다. 실제 시험 통과 후 기존 수요 사전제한/배터리 가용출력 스크리닝과 S0–S4 비교로 이어간다. 현재 정상 펄스 시험의 재실행은 필요하지 않다.

## 재현 및 파일
`python3 validate_bus.py` 실행. numpy와 pandas가 필요하다. `raw/`는 수정하지 않은 원본 네 CSV, `NORMALIZED_AND_BALANCE.csv`는 단위·부호 정규화 결과, `RESULT.json`은 판정과 상세 수치다. 원래 평가기와 이전 모니터 판정, SHA256SUMS.txt를 포함한다.


## Detailed machine result

```json
{
  "status": "NUMERIC_GATES_PASS",
  "checks": {
    "window_0_to16": true,
    "temporal_resolution": true,
    "actual_demand10kW": true,
    "zero_before_delay": true,
    "maximum26kW": true,
    "startup_and_stop_trace_RMSE": true,
    "zero_after_stop": true,
    "DC_balance_max0p1kW": true,
    "current_from_actual_bus_voltage": true,
    "battery_charging16kW": true
  },
  "maximum_DC_residual_kW": 3.911923059263245e-06,
  "profile_RMSE_kW": 0.0316515709417414,
  "actual_project_and_job_log_review": "STILL_REQUIRED",
  "claim": "Timing/sign/common-bus numerical checks only; no vehicle performance or EREV strategy validation",
  "samples": 8001,
  "output_step_s": 0.002,
  "reference_timing_shift_s": 0,
  "source_sha256": {
    "plus": "3a1006758fe69145bac1d0f8d04eae11037d8cc688891710f85f5bde15eaaec7",
    "bms": "7c518e77234e2d4a2fce08cfeec60f374b3b15c9d55963582485f091bd4e087b",
    "vehicle": "a4d570cf68c435fdc2c527ccea3fceeece6b4d2311e69624d932e10fa3d9c36d",
    "generator": "daacd48d88478c0cc10101878377a94e20606a2975fa467c6956e1ca7d308701"
  },
  "prior_monitor_status": "REQUEST_MONITOR_NUMERIC_GATES_PASS",
  "prior_monitor_checks": {
    "complete_2ms_window": true,
    "request_at_1_to2": true,
    "one_start_only": true,
    "startup_delay_0p5s": true,
    "minimum_on_10s": true,
    "normal_stop_0p52s": true,
    "rising_rate_20kW_s": true,
    "falling_rate_50kW_s": true,
    "maximum26kW": true,
    "unshifted_profile_RMSE_0p1kW": true,
    "terminal_power_sign": true,
    "energy_integration": true,
    "charge_acceptance_limit": true,
    "no_supply_during_start": true,
    "zero_after_off": true,
    "no_protection_after_initialization": true
  },
  "steady_generation_mean_kW": 26.00000244400221,
  "steady_demand_mean_kW": 10.0,
  "steady_battery_charge_mean_kW": 16.00000313164392,
  "maximum_voltage_channel_difference_V": 0.0,
  "maximum_battery_VI_power_difference_kW": 8.881784197001252e-15,
  "maximum_KCL_residual_A": 1.026895516176296e-05,
  "maximum_monitor_load_difference_W": 3.637978807091713e-12,
  "maximum_monitor_vs_terminal_generation_difference_W": 49.99284986095548,
  "monitor_vs_terminal_generation_RMSE_W": 10.345965886148306,
  "terminal_vs_adjacent_monitor_average_max_difference_W": 2.9674658077201457,
  "terminal_vs_adjacent_monitor_average_RMSE_W": 0.3688993345704535,
  "sampling_interpretation": "Diagnostic only: terminal output is close to adjacent monitor sample averages. Consistent with interval sampling/integration, but implementation not established without solver logs. No averaging or shift used for the ten gates.",
  "energy_Wh": {
    "terminal_generation_integral": 65.79445318401876,
    "plus_reported_generation": 65.794453184022,
    "source_reported_generation": 65.79444444444445,
    "actual_load_integral": 44.44444444444444,
    "battery_net_charge_integral": 21.35001024644027,
    "bus_residual_integral": -1.5068659549211105e-06,
    "terminal_minus_source": 8.739574312244258e-06
  },
  "soc_start_percent": 81.2520512871387,
  "soc_end_percent": 81.28252283058134,
  "BMS_stored_energy_proxy_change_Wh": 25.767893022091926,
  "BMS_energy_note": "Stored-energy proxy uses a different boundary/definition from terminal VI integral; do not use it as DC bus residual.",
  "accepted_scope": "Request-driven T1 stationary common DC bus numerical gates, plus prior same-monitor state/timer checks",
  "provenance": "Four submitted traces share exact time axes and consistent electrical channels. Executed saved-project hash and Job Log not supplied; same-job identity remains user-reported, not independently proven.",
  "limitations": [
    "Actual protection, charge curtailment and restart-dwell scenarios remain untested in CRUISE.",
    "This is a virtual DC source; engine, generator efficiency, fuel and vehicle EMS validation remain outside this test."
  ],
  "next_start": "Prepare remaining actual request-source protection, charge-curtailment and restart tests using unchanged original policies; then resume pre-limit demand/availability screening."
}
```

## Reproducible validator

```python
"""Validate the submitted request-controlled run without shifting time or changing gates.
Run with Python 3, numpy and pandas. All inputs are relative to this script.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from evaluate_bench import evaluate

root = Path(__file__).resolve().parent
sources = {k: root/'raw'/f'{k}.csv' for k in ('plus','bms','vehicle','generator')}
frames = {k: pd.read_csv(p, skiprows=[1]) for k,p in sources.items()}
p,b,v,g = (frames[k] for k in sources)
t = p.Time.to_numpy()
for frame in frames.values():
    assert np.isfinite(frame.to_numpy(float)).all()
    np.testing.assert_array_equal(t, frame.Time)
assert len(t) == 8001
np.testing.assert_allclose(np.diff(t), .002, atol=2e-12, rtol=0)
assert hashlib.sha256(sources['generator'].read_bytes()).hexdigest() == json.loads(
    (root/'PRIOR_REQUEST_MONITOR_RESULT.json').read_text())['source_sha256']
vol = p['Plus/Potential (Electrical FMU 1)'].to_numpy()
np.testing.assert_allclose(vol, b['In/Voltage (BMS Monitor)'], atol=1e-8, rtol=0)
for field in ('Actual Velocity','Desired Velocity'):
    np.testing.assert_allclose(v[f'In/{field} (Vehicle Monitor)'], 0, atol=1e-10)
pg = -p['Plus/Power (Electrical FMU 1)'].to_numpy()/1000
ig = -p['Plus/Current (Electrical FMU 1)'].to_numpy()
pb = -b['In/Power (BMS Monitor)'].to_numpy()
load = vol*(v['In/E-Consumer Current (Vehicle Monitor)'].to_numpy()+
            v['In/E-Motor Current (Vehicle Monitor)'].to_numpy())/1000
gm = g['In/Generated W (Generator Monitor)'].to_numpy()
residual = pb+pg-load
normalized = pd.DataFrame(dict(time_s=t, Pgen_bus_kW=pg, Pdem_actual_DC_kW=load,
    Pbat_discharge_positive_kW=pb, Vbus_V=vol, Igen_injection_positive_A=ig))
result = evaluate(normalized)
maxabs = lambda a: float(np.max(np.abs(a)))
steady = (t>=3)&(t<=10)
integrate = np.trapezoid
previous = json.loads((root/'PRIOR_REQUEST_MONITOR_RESULT.json').read_text())
terminal_energy = float(integrate(pg,t)/3.6)
source_energy = float(g['In/Generated Energy J (Generator Monitor)'].iloc[-1]/3600)
plus_energy = float(-(p['Plus/Energy (Electrical FMU 1)'].iloc[-1]-
                       p['Plus/Energy (Electrical FMU 1)'].iloc[0])/3600)
result.update(
    samples=len(t), output_step_s=.002, reference_timing_shift_s=0,
    source_sha256={k:hashlib.sha256(path.read_bytes()).hexdigest() for k,path in sources.items()},
    prior_monitor_status=previous['status'], prior_monitor_checks=previous['checks'],
    steady_generation_mean_kW=float(np.mean(pg[steady])),
    steady_demand_mean_kW=float(np.mean(load[steady])),
    steady_battery_charge_mean_kW=float(-np.mean(pb[steady])),
    maximum_voltage_channel_difference_V=maxabs(vol-b['In/Voltage (BMS Monitor)']),
    maximum_battery_VI_power_difference_kW=maxabs(
        b['In/Power (BMS Monitor)'].to_numpy()-vol*b['In/Current (BMS Monitor)'].to_numpy()/1000),
    maximum_KCL_residual_A=maxabs(-b['In/Current (BMS Monitor)'].to_numpy()+ig-load*1000/vol),
    maximum_monitor_load_difference_W=maxabs(load*1000-g['In/Load W (Generator Monitor)']),
    maximum_monitor_vs_terminal_generation_difference_W=maxabs(pg*1000-gm),
    monitor_vs_terminal_generation_RMSE_W=float(np.sqrt(np.mean((pg*1000-gm)**2))),
    terminal_vs_adjacent_monitor_average_max_difference_W=maxabs(pg*1000-.5*(gm+np.r_[gm[0],gm[:-1]])),
    terminal_vs_adjacent_monitor_average_RMSE_W=float(np.sqrt(np.mean((pg*1000-.5*(gm+np.r_[gm[0],gm[:-1]]))**2))),
    sampling_interpretation='Diagnostic only: terminal output is close to adjacent monitor sample averages. Consistent with interval sampling/integration, but implementation not established without solver logs. No averaging or shift used for the ten gates.',
    energy_Wh=dict(terminal_generation_integral=terminal_energy,
        plus_reported_generation=plus_energy, source_reported_generation=source_energy,
        actual_load_integral=float(integrate(load,t)/3.6),
        battery_net_charge_integral=float(-integrate(pb,t)/3.6),
        bus_residual_integral=float(integrate(residual,t)/3.6),
        terminal_minus_source=terminal_energy-source_energy),
    soc_start_percent=float(b['In/SoC (BMS Monitor)'].iloc[0]),
    soc_end_percent=float(b['In/SoC (BMS Monitor)'].iloc[-1]),
    BMS_stored_energy_proxy_change_Wh=float((b['In/Energy (BMS Monitor)'].iloc[-1]-b['In/Energy (BMS Monitor)'].iloc[0])*1000),
    BMS_energy_note='Stored-energy proxy uses a different boundary/definition from terminal VI integral; do not use it as DC bus residual.',
    accepted_scope='Request-driven T1 stationary common DC bus numerical gates, plus prior same-monitor state/timer checks',
    provenance='Four submitted traces share exact time axes and consistent electrical channels. Executed saved-project hash and Job Log not supplied; same-job identity remains user-reported, not independently proven.',
    limitations=['Actual protection, charge curtailment and restart-dwell scenarios remain untested in CRUISE.',
                 'This is a virtual DC source; engine, generator efficiency, fuel and vehicle EMS validation remain outside this test.'],
    next_start='Prepare remaining actual request-source protection, charge-curtailment and restart tests using unchanged original policies; then resume pre-limit demand/availability screening.')
normalized['DC_residual_kW']=residual
normalized['monitor_generation_W']=gm
normalized.to_csv(root/'NORMALIZED_AND_BALANCE.csv',index=False)
(root/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('status','checks','maximum_DC_residual_kW','profile_RMSE_kW','energy_Wh')},indent=2))
assert all(result['checks'].values())
```

## Unchanged ten-gate evaluator

```python
"""Check the defined16s actual bench export after explicit sign/unit normalization.
Numeric gates cannot establish solver provenance or saved-project identity.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
FIELDS=['time_s','Pgen_bus_kW','Pdem_actual_DC_kW','Pbat_discharge_positive_kW','Vbus_V','Igen_injection_positive_A']

def evaluate(d):
    if not set(FIELDS).issubset(d.columns):raise ValueError('Missing normalized fields: '+str(sorted(set(FIELDS)-set(d.columns))))
    a=d[FIELDS].to_numpy(float)
    if len(a)<3 or not np.isfinite(a).all():raise ValueError('Nonfinite or too few samples')
    t,pg,load,pb,v,i=a.T
    if np.any(np.diff(t)<=0) or np.any(v<=0):raise ValueError('Nonincreasing time or nonpositive voltage')
    expect=np.where(t<11,np.clip(20*(t-1.5),0,26),np.maximum(0,26-50*(t-11)))
    def maxabs(x):return float(np.max(np.abs(x))) if len(x) else float('inf')
    error=pb+pg-load
    checks=dict(window_0_to16=abs(t[0])<=1e-6 and abs(t[-1]-16)<=1e-6,
        temporal_resolution=np.max(np.diff(t))<=.020001,
        actual_demand10kW=maxabs(load-10)<=.1,
        zero_before_delay=maxabs(pg[t<=1.5])<=.05,
        maximum26kW=abs(float(pg.max())-26)<=.1,
        startup_and_stop_trace_RMSE=float(np.sqrt(np.mean((pg-expect)**2)))<=.1,
        zero_after_stop=maxabs(pg[t>=11.54])<=.05,
        DC_balance_max0p1kW=maxabs(error)<=.1,
        current_from_actual_bus_voltage=maxabs(i-pg*1000/v)<=.5,
        battery_charging16kW=maxabs(pb[(t>=3)&(t<=10)]+16)<=.2)
    return dict(status='NUMERIC_GATES_PASS' if all(checks.values()) else 'NUMERIC_GATES_FAIL',
        checks={k:bool(v) for k,v in checks.items()},
        maximum_DC_residual_kW=maxabs(error),profile_RMSE_kW=float(np.sqrt(np.mean((pg-expect)**2))),
        actual_project_and_job_log_review='STILL_REQUIRED',
        claim='Timing/sign/common-bus numerical checks only; no vehicle performance or EREV strategy validation')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--csv',required=True,type=Path);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--project',type=Path);ap.add_argument('--job-log',type=Path);args=ap.parse_args()
    r=evaluate(pd.read_csv(args.csv));r['source_csv_sha256']=hashlib.sha256(args.csv.read_bytes()).hexdigest()
    r['scope']='User-provided normalized export; runtime provenance is not inferred from numeric agreement'
    for k,p in [('project',args.project),('job_log',args.job_log)]:
        r[k+'_sha256']=hashlib.sha256(p.read_bytes()).hexdigest() if p else None
    args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(r['status']);raise SystemExit(0 if all(r['checks'].values()) else 1)
```

## File hashes

```text
bfe5d0b9df7d00e1931112bfdc1f8ba76add72a35400441024bb3146f92f9001  NORMALIZED_AND_BALANCE.csv
ff26bc76e8c82a2506dfad4228c09e959e159b056de2e5755d5483240da9e475  PRIOR_REQUEST_MONITOR_RESULT.json
4d66bc53633b504c3ff396f329ec10244f233fb56240381b07103d501fe8bcad  RESULT.json
717bdf53776413b8e378668c56a9b4747eea73834f26f17b3a7e49b69a2b785a  RESULT_KO.md
984cb694a49b3a375b2c10ea424fd3f27bdc3c554a6792b7226b2e0625734012  VERIFICATION.log
daa5cc8caf0694c1f13ee5e034b089ab9ccf13bd79146383652a55c4d1901bd0  evaluate_bench.py
7c518e77234e2d4a2fce08cfeec60f374b3b15c9d55963582485f091bd4e087b  raw/bms.csv
daacd48d88478c0cc10101878377a94e20606a2975fa467c6956e1ca7d308701  raw/generator.csv
3a1006758fe69145bac1d0f8d04eae11037d8cc688891710f85f5bde15eaaec7  raw/plus.csv
a4d570cf68c435fdc2c527ccea3fceeece6b4d2311e69624d932e10fa3d9c36d  raw/vehicle.csv
a431e3c5ff19fdfdd38e1573f0b98d135fd1db55f3b02ea0bf9487646b258104  validate_bus.py
```
