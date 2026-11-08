# EREV T1 26 kW · 명시적 2 ms 간격 진단

사용자가 CRUISE M 실행 후 저장한 Sync2ms 프로젝트를 조사했다. 초기 0.002 s, 최대 2 ms, 수동 동기화 0.002 s, 자동 솔버, FMU From master가 저장돼 있다. 이전 설명에서 설정 미저장이나 이전 결과 선택 가능성을 강조했으나, 화면과 저장본은 Sync2ms 프로젝트 사용을 뒷받침한다. 같은 10 ms 출력이 계속된 원인은 아직 확정되지 않았다. CSV 간격 자체로 실제 내부 연산·통신 간격을 확정할 수 없다.

진단용 복제본에서 전역 솔버 모드를 fixed로, 고정 간격을 0.002 s로 설정했다. Electrical FMU 1의 component_step_size 선택은 const, 값은 0.002 s다. 두 간격의 동시 변경으로 통신 간격을 명시적으로 제한하는 시험이다. 개별 설정의 기여를 분리하는 시험 결과로 해석할 수 없다. 변경은 XML의 네 필드뿐이며, 다른 ZIP 항목과 FMU 바이너리는 원본과 동일함을 검증했다. CRUISE M 실행은 사용자 PC에서 확인해야 한다.

1. 동봉 EREV_T1_26kW_FMU_Explicit2ms.proj를 연다.
2. FMU 경로 오류가 있으면 Electrical FMU 1 → File에서 동봉 EREV_T1_26kW.fmu를 선택한다.
3. Cycle Run → ANL61905060을 한 번 실행한다. 완료 후 해당 실행의 Plus CSV를 내보낸다.
4. Time 0.000, 0.002, 0.004 s 및 0–16 s 범위를 확인한다. 일정 2 ms 간격이면 8,001개 표본이다. 동일 간격으로 나오는 경우 BMS Monitor와 Vehicle Monitor도 같은 실행에서 내보낸다.
5. P_command_W가 보이면 포함하고, 실행 화면의 Details에서 확인 가능한 로그/설정도 보관한다. 다시 10 ms이면 해당 프로젝트를 저장하고 CSV와 함께 전달한다.

이 시험의 목적은 공통 DC 버스 공급과 수치 시간 응답의 확인이다. 기존 RMSE 기준 0.100 kW와 버스 잔차 기준은 유지한다. 실제 엔진 기동 지연·연료소비·65 kW급 발전계 특성은 별도 모델 검증 단계다. 기존 26 kW 정차 시험에서는 발전 26 kW, 부하 10 kW, 배터리 충전 약 16 kW 및 버스 잔차 약 0.004 W를 확인했다.
{
  "source": "EREV_T1_26kW_FMU_Sync2ms.proj",
  "source_sha256": "8b9e8c802bf024fc10995c73b5140d83ac04f8b6b05538fd56469e7049e39ec5",
  "output": "EREV_T1_26kW_FMU_Explicit2ms.proj",
  "output_sha256": "3a9b59154485708945147bed4834bc3bf0f37817ba68105452b177162f82fec4",
  "user_saved_settings": {
    "task_mode": "auto",
    "initial_step_s": 0.002,
    "maximum_step_ms": 2.0,
    "synchronization_s": 0.002,
    "FMU_step": "from_master"
  },
  "changes": [
    {
      "object_id": "79908",
      "field": "time_step_type",
      "before": "<compose type=\"cruise.props.tasks.tasks_settings.TimeStepType\">\n<str>auto</str>\n</compose>",
      "after": "<compose type=\"cruise.props.tasks.tasks_settings.TimeStepType\">\n<str>fixed</str>\n</compose>"
    },
    {
      "object_id": "79909",
      "field": "value",
      "before": "<num>0.01</num>",
      "after": "<num>0.002</num>"
    },
    {
      "object_id": "76805",
      "field": "active",
      "before": "<str>from_master</str>",
      "after": "<str>const</str>"
    },
    {
      "object_id": "76806",
      "field": "value",
      "before": "<num>1.0</num>",
      "after": "<num>0.002</num>"
    }
  ],
  "root_cause": "UNRESOLVED: saved settings alone do not establish effective runtime communication step",
  "static_verification": "PASS: four scalar fields only, XML parse and ZIP CRC pass",
  "CRUISE_M_execution": "PENDING",
  "next_start": "Run Explicit2ms ANL61905060 once; inspect first Plus Time values and export matching BMS/Vehicle if new result confirmed"
}
