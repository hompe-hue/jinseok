# EREV T1 26 kW 고정 2 ms 실제 Plus 결과

새 제출 파일 FMU 1 Plus CSV.csv에서 0–16 s, 8,001표본, 2 ms 출력 간격을 확인했다. 이전 파일과 다른 데이터이며, 입력과 출력의 시간을 이동하지 않고 기존 지령 프로파일과 대조했다.

| 지표 | 기존 10 ms 결과 | 새 2 ms 결과 |
|---|---|---|
| 표본 수 | 1,601 | 8,001 |
| 지령 추종 RMSE | 0.157805950 kW | 0.010345966 kW |
| 최대 순간 오차 | 0.749524539 kW | 0.049992850 kW |
| 최대 오차 시각 | 11.52 s | 11.52 s |
| RMSE ≤0.100 kW | 미충족 | 충족 |

RMSE 감소율은 93.4439%다. 새 데이터의 10 ms 공통 시간점만 사용해도 RMSE 0.010344094 kW로, 표본 밀도 변화만으로 생긴 개선으로 설명하기 어렵다. Plus 채널로 계산 가능한 기존 7개 기준은 모두 통과했다. 26 kW 공급과 단자 전압·전류·전력 관계, 기동 전/정지 후 영출력을 확인했다.

자동/From master 설정에서 고정 2 ms 솔버 및 FMU 통신 간격으로 함께 변경한 뒤 시간 응답이 개선됐다. 수치 연동 설정이 기존 오차에 기여했다는 근거다. 두 설정의 개별 기여 및 실제 통신 호출 시각을 식별하려면 실행 로그가 더 필요하다. 실제 엔진·발전기 기동 지연이나 연료소비 특성을 이 시험으로 검증한 것으로 해석할 수 없다.

## 완료 범위와 다음 시작점

고정 2 ms 시험의 Plus 파형 판정을 완료했다. 같은 실행의 BMS Monitor와 Vehicle Monitor CSV를 받아 나머지 세 항목인 실제 부하 10 kW, 공통 DC 버스 최대 잔차 ≤0.1 kW, 배터리 충전 약 16 kW를 확인하면 이번 정차 버스 시험의 10개 수치 판정을 마칠 수 있다. 기존 10 ms BMS/Vehicle 자료를 새 Plus 결과에 결합하지 않는다. 현재 제출된 Plus 결과의 출처는 CSV 및 앞서 확인한 프로젝트 설정에 근거하며 Job Log의 실행 식별까지 확인한 상태는 아니다.

재현 명령은 아래와 같다.

```bash
python analyze_plus.py actual_plus_2ms.csv baseline_plus_10ms.csv .
```

PLUS_COMPARISON.csv에 모든 표본의 단자 전압·전류·공급전력·참조전력·오차를 저장했다. PLUS_RESULT.json에 원본 SHA-256과 기준별 판정값을 저장했다.
{
  "source": "FMU 1 Plus CSV.csv",
  "sha256": "49cb6284ebd69be78bbc895e25fdaa640e6742556b617f76d8ff82b0d506c302",
  "rows": 8001,
  "start_s": 0.0,
  "end_s": 16.0,
  "dt_min_s": 0.0019999999999988916,
  "dt_max_s": 0.002000000000000668,
  "profile_RMSE_kW": 0.01034596589846918,
  "maximum_profile_error_kW": 0.04999284984839975,
  "maximum_profile_error_time_s": 11.52,
  "same_clock_10ms_RMSE_kW": 0.010344093627892046,
  "checks": {
    "window_0_to16": true,
    "temporal_resolution": true,
    "zero_before_delay": true,
    "maximum26kW": true,
    "startup_and_stop_trace_RMSE": true,
    "zero_after_stop": true,
    "current_from_actual_bus_voltage": true
  },
  "baseline": {
    "source": "FMU3.csv",
    "sha256": "4e1e0540e25ae0be905512d4209d8126d4da5e8777a809e14521ebfe55923c75",
    "rows": 1601,
    "start_s": 0.0,
    "end_s": 16.0,
    "dt_min_s": 0.009999999999999787,
    "dt_max_s": 0.010000000000001563,
    "profile_RMSE_kW": 0.15780594953447716,
    "maximum_profile_error_kW": 0.7495245394486921,
    "maximum_profile_error_time_s": 11.52,
    "checks": {
      "window_0_to16": true,
      "temporal_resolution": true,
      "zero_before_delay": true,
      "maximum26kW": true,
      "startup_and_stop_trace_RMSE": false,
      "zero_after_stop": true,
      "current_from_actual_bus_voltage": true
    }
  },
  "RMSE_reduction_percent": 93.44386828951033,
  "pending_original_gates": [
    "actual_demand10kW",
    "DC_balance_max0p1kW",
    "battery_charging16kW"
  ],
  "common_bus_validation": "PENDING_MATCHING_BMS_AND_VEHICLE_EXPORTS",
  "interpretation": "Explicit task/FMU step test supports numerical timing contribution. Both settings changed together, so individual contributions and precise FMU communication schedule remain unresolved."
}
