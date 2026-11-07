# EREV T1 · 26 kW 공통 DC 버스 · 2 ms 동기화 비교

## CSV 검증 완료

새로 제출된 Plus, Out, BMS Monitor, Vehicle Monitor CSV 네 개는 각각 기존 FMU3, FMU1, BMS Monitor FMU, velocity FMU와 바이트 단위로 일치했다. 0–16 s, 1,601표본, 간격 10 ms다. 새 2 ms 실행 여부나 FMU의 실제 통신 간격은 이 자료만으로 식별할 수 없다. 출력에 P_command_W가 없으며 Job Log는 제출되지 않았다.

기존 기준을 재현했다. 공통 DC 버스 최대 잔차 0.004 W, 26 kW 발전 및 10 kW 부하에서 약 16 kW 배터리 충전, 10개 기준 중 9개 충족이다. 미충족은 지령 추종 RMSE 0.157806 kW(기준 ≤0.100 kW)다. 최대 순간 오차는 11.52 s에서 0.749525 kW다. 15 ms 이동 시 RMSE 0.001798 kW는 시간 지연 진단에만 사용한다. 원본 채널명·파일 SHA·기준별 결과는 CSV_CHECKPOINT.json과 검증 코드에 기록했다.

## 동기화 수정 및 다음 실행

이전 비교본에는 솔버 초기·최대 간격 2 ms와 별도로 Domain Synchronization이 수동 10 ms였다. 새 비교본에서 Domain Synchronization만 0.010 s에서 0.002 s로 변경했다. 솔버 초기·최대 2 ms, FMU From master, 26 kW 지령, 10 kW 정차 부하, 0–16 s, 매 스텝 결과 저장을 유지했다. XML과 압축 구조를 검증했으며 CRUISE M에서 새 비교본의 실행은 아직 확인되지 않았다.

1. EREV_T1_26kW_FMU_Sync2ms.proj를 열고 REEV_MBE → Cycle Run → ANL61905060을 한 번 실행한다. FMU 경로 오류 시 Electrical FMU 1 → File에서 동봉 EREV_T1_26kW.fmu를 선택한다.
2. 방금 완료된 Job을 선택한 뒤 먼저 Plus 단자 CSV의 Time 0.000 → 0.002 → 0.004 s 부근을 확인한다. 정확히 2 ms 간격이면 0–16 s에서 8,001개 표본이다. 가변 간격이면 전체 Time 열과 최대 간격을 확인한다. 다시 10 ms 간격이면 나머지를 내보내기 전에 선택된 실행 화면과 Job Log 또는 상세 화면을 확인한다.
3. 새 실행으로 확인되면 Plus, BMS, Vehicle CSV를 내보낸다. P_command_W와 Job Log는 확인 가능한 경우 포함한다. CSV 간격으로 FMU 통신 간격 자체를 확정할 수는 없다. 기존 RMSE와 공통 DC 버스 기준을 그대로 적용한다.

패키지 SHA-256 `2c1ad451094acbea3f7f2ad301beb56ec1e78cc465cae7635af6ba6a1c179cde`. 실행 ZIP은 별도로 전달했다.

```json
{
  "status": "NUMERIC_GATES_FAIL",
  "checks": {
    "window_0_to16": true,
    "temporal_resolution": true,
    "actual_demand10kW": true,
    "zero_before_delay": true,
    "maximum26kW": true,
    "startup_and_stop_trace_RMSE": false,
    "zero_after_stop": true,
    "DC_balance_max0p1kW": true,
    "current_from_actual_bus_voltage": true,
    "battery_charging16kW": true
  },
  "maximum_DC_residual_kW": 3.911923059263245e-06,
  "profile_RMSE_kW": 0.15780594953447716,
  "actual_project_and_job_log_review": "STILL_REQUIRED",
  "claim": "Timing/sign/common-bus numerical checks only; no vehicle performance or EREV strategy validation",
  "sample_count": 1601,
  "minimum_output_step_s": 0.009999999999999787,
  "maximum_output_step_s": 0.010000000000001563,
  "maximum_abs_profile_error_kW": 0.7495245394486921,
  "maximum_abs_profile_error_time_s": 11.52,
  "diagnostic_only_reference_shift_s": 0.015,
  "diagnostic_only_shifted_RMSE_kW": 0.0017979614699728493,
  "P_command_W_in_exports": false,
  "Job_Log_provided": false,
  "new_2ms_run": "UNVERIFIED",
  "exports": {
    "FMU 1 Plus.csv": {
      "sha256": "4e1e0540e25ae0be905512d4209d8126d4da5e8777a809e14521ebfe55923c75",
      "previous_file": "FMU3.csv",
      "previous_sha256": "4e1e0540e25ae0be905512d4209d8126d4da5e8777a809e14521ebfe55923c75",
      "byte_identical": true
    },
    "FMU 1 Out.csv": {
      "sha256": "812092e08a43fabc8beedc6610d1c4d0847f048b3310558aa78ea195c904cf1f",
      "previous_file": "FMU1.csv",
      "previous_sha256": "812092e08a43fabc8beedc6610d1c4d0847f048b3310558aa78ea195c904cf1f",
      "byte_identical": true
    },
    "BMS Monitor.csv": {
      "sha256": "985408febc3c3a109e9753633223d1f14cbf589ddd28a2bd72b9f4abfbd965a8",
      "previous_file": "BMS Monitor FMU.csv",
      "previous_sha256": "985408febc3c3a109e9753633223d1f14cbf589ddd28a2bd72b9f4abfbd965a8",
      "byte_identical": true
    },
    "Vehicle Monitor.csv": {
      "sha256": "27bc14ea399f9176ecb7ea2ecb10b548238c08f79c2d42991682613fb0473695",
      "previous_file": "velocity FMU.csv",
      "previous_sha256": "27bc14ea399f9176ecb7ea2ecb10b548238c08f79c2d42991682613fb0473695",
      "byte_identical": true
    }
  }
}
```
