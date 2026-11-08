# EREV T1 26 kW 정차 공통 DC 버스 시험 완료

기존에 정한 수치 기준 10개를 모두 충족했다. 제출된 Plus, BMS Monitor2, Vehicle Monitor2는 모두 0–16 s의 2 ms 간격 8,001표본이며 시간축이 완전히 일치한다. Plus와 BMS 버스 전압도 모든 표본에서 일치한다.

| 항목 | 결과 |
|---|---|
| 정상상태 발전 공급전력 평균 | 26.000002 kW |
| 정상상태 DC 소비전력 평균 | 10.000000 kW |
| 정상상태 배터리 충전전력 평균 | 16.000003 kW |
| 최대 DC 버스 전력수지 잔차 | 0.003912 W |
| 지령 파형 RMSE | 0.010346 kW, 기준 ≤0.100 kW |
| SOC | 81.252051% → 81.282523% |
| 기준 충족 | 10/10 |

정상상태 평균은 기존 기준과 같은 3–10 s 구간이다. 부호는 발전 공급과 배터리 방전을 양으로 정의했다. 전력수지는 배터리 방전전력 + 발전 공급전력 − DC 소비전력으로 계산했다. 배터리 충전 시 방전 기준 전력은 음수가 된다. 16 s 전 구간 전력 적분은 발전 65.794453 Wh, 소비 44.444444 Wh, 배터리 순충전 21.350010 Wh다. 적분은 CSV 표본의 사다리꼴 적분으로 계산했다.

평가 기준을 바꾸거나 참조 시간축을 이동하지 않았다. 기존 10 ms 시험의 파형 RMSE 0.157806 kW에 비해 이번 2 ms 시험은 93.44% 개선됐다. 솔버와 FMU 통신 간격을 동시에 고정한 진단이므로 각 설정의 기여는 분리되지 않았다.

이번 완료 범위는 26 kW 지령형 FMU와 배터리·10 kW 정차 부하 사이의 공통 DC 버스 수치 검증이다. 실제 엔진·발전계 맵, 연료소비, 기동 지연의 실측 재현성과 주행 중 EMS 성능에 대한 검증은 후속 단계다. 프로젝트 파일의 설정은 앞서 확인했으며, Job Log와 P_command_W 출력은 제공되지 않았다. 평가 코드가 기록하는 actual_project_and_job_log_review 필드는 전체 실행 출처 확인이 남아 있다는 뜻이다.

## 재현과 재개

동봉 validate_bus.py를 실행하면 원본 CSV 세 개의 시간축, 채널 전압, 정차 조건을 대조하고 변경하지 않은 evaluate_bench.py의 열 가지 기준을 적용한다. 결과와 SHA-256은 RESULT.json, 표본별 전력수지는 NORMALIZED_AND_BALANCE.csv에 저장했다.

```bash
python validate_bus.py
```

T1 수치 판정을 완료한 뒤 기존 연구 계획의 다음 시험/발전계 모델 단계 요구사항을 읽어 재개한다. T1을 반복 실행할 필요 없이 이 완료 체크포인트를 기준으로 이어간다.
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
  "profile_RMSE_kW": 0.01034596589846918,
  "actual_project_and_job_log_review": "STILL_REQUIRED",
  "claim": "Timing/sign/common-bus numerical checks only; no vehicle performance or EREV strategy validation",
  "samples": 8001,
  "output_step_s": 0.002,
  "source_hashes": {
    "plus": "49cb6284ebd69be78bbc895e25fdaa640e6742556b617f76d8ff82b0d506c302",
    "bms": "42b42d8ce9ef09e841bbbde31b1c2310c9f40b27e12219f314003c44b9bec683",
    "vehicle": "6c1e1d274804fd38759f8a6a0c8cb2f3ef86e7f94bf6574407deb2ffbc269a3a"
  },
  "steady_generation_mean_kW": 26.000002444001915,
  "steady_demand_mean_kW": 10.0,
  "steady_battery_charge_mean_kW": 16.00000313164354,
  "maximum_voltage_channel_difference_V": 0.0,
  "maximum_battery_VI_power_difference_kW": 7.105427357601002e-15,
  "maximum_KCL_residual_A": 1.026895516176296e-05,
  "energy_from_trapezoid_Wh": {
    "generated": 65.79445318401505,
    "demand": 44.44444444444444,
    "battery_discharge_positive": -21.35001024535675,
    "residual": -1.5057861394095358e-06
  },
  "soc_start_percent": 81.2520512871387,
  "soc_end_percent": 81.28252283061417,
  "accepted_scope": "T1 26 kW stationary common DC bus numerical gates only",
  "next_stage": "Resume existing research gates after T1 checkpoint commit",
  "runtime_provenance": "Saved Explicit2ms project settings reviewed; Job Log and command output not supplied"
}
