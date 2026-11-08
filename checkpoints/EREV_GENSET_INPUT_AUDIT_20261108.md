# 발전계 맵 및 기동응답 입력 근거 감사

2026-11-08. T1 공통 DC 버스 시험의 10개 수치 기준 통과 기록 615d5ca 이후의 입력 근거 감사다. 현재 실행 프로젝트와 후보 맵을 변경하지 않고 파일과 계산을 대조했다.

## 현재 기준

2026-11-01 연구 재개 지침의 발전 상한 26 kW, 기동지연 0.5 s, 상승 20 kW/s, 정상하강 50 kW/s, 최소 ON 10 s/OFF 5 s를 현재 가상 발전원의 연구 가정으로 유지한다. 과거 80 kW 엔진·65 kW 발전계 구상과 L3A/MGA 자료는 후보 이력이다. 이번에 65 kW를 기준으로 채택하거나 Volt 맵을 설치하지 않았다. 연구 재개 지침의 다음 순서는 제한 전 요구전력과 배터리 가용출력의 비교다. 연료 분석은 맵과 변환기 경계가 확보된 뒤 확대한다.

## 현재 프로젝트에서 확인한 구성

| 항목 | 저장본 값 | 적용 판단 |
|---|---|---|
| 내장 ICE 배기량 | 2,000 cm³ | 현재 내장 설정을 L3A 1.5 L 입력으로 간주할 근거 부족 |
| 엔진 관성 | 0.134 kg·m² | 저장본 수치. OEM L3A 관성 출처 미확인 |
| 내장 발전기 종류 | asynchronous_machine | L3A/MGA 후보의 PMAC 특성과 차이 |
| 발전기 관성 | 0.05 kg·m² | 저장본 수치. OEM MGA 관성 출처 미확인 |
| Global losses map | true | 별도 인버터 효율과 손실의 중복 여부를 먼저 확인해야 함 |
| 실제 T1 공급원 | Electrical FMU 1 | 26 kW 시간 예약 파형 |
| FMU 외부 입력 | V_bus_V 한 개 | EMS의 ON/OFF 요청과 충전허용전력 입력이 필요 |
| FMU 출력 | I_terminal_A, P_command_W | 단자 전압으로 공급 전류 산정 |

T1 시험의 기존 엔진·발전계는 OFF 상태였다. 내장 구성의 제원 차이가 T1 통과를 취소하는 것은 아니지만, 이후 native Range Extender를 켜려면 별도 입력 추적과 검증이 필요하다. 현재 FMU 소스는 시간 1.5–2.8 s 상승, 11–11.52 s 하강을 직접 계산한다. ON/OFF 요청·최소 유지시간·보호상태를 상태기로 받아 처리하는 범위는 이번 T1 파형 검증에 포함되지 않는다.

## 확보된 후보 맵의 재사용 범위

| 자료 | 수치표 | 확보 수준 | 남은 범위 |
|---|---:|---|---|
| Volt L3A 엔진 | 528점 | 기존 2021 논문 도표의 재구성 후보 | OEM 원시 연료/WOT 배열, 공회전·시동 연료 |
| Volt MGA 전기기 | 1,314점 | 기존 Q1 도표와 Q4 대칭 후보 | 발전 Q4 독립 실측, 전압·온도 의존성, 열 연속 한도 |
| Volt MGB 대안 | 1,380점 | 기존 Q1 도표와 Q4 대칭 후보 | 동일. 현재 발전기로 자동 채택하지 않음 |
| 가상 65 kW 입력 | 과거 Mazda/Prius 맵 스케일링 | 연구 설계 가정의 별도 후보 | 실제 1.5 L·65 kW 하드웨어 인증과 구분 필요 |

기존 수치표의 유한값·중복·Q1/Q4 대칭·효율 단위를 검사했다. MGA/MGB의 Q4 표는 Q1과 정확히 대칭이다. 2021 논문 Figure 5 캡션은 도표를 모터 및 발전 양방향에 활용했다고 명시한다. 이것으로 Q4의 독립 실측이나 OEM 원시 배열 확보를 주장할 수는 없다. 원 GM/SAE 문헌 2015-01-1152, 1208, 1201의 공식 초록과 서지정보를 재확인했으며, 이번에 해당 OEM 원시 수치 배열을 추가 확보하지 못했다.

예비 26 kW 점은 엔진 2,950 rpm·98 N·m, 발전기 5,900 rpm·−48.02 N·m, 엔진 효율 36%, 발전기 93%, 커플링·인버터·DC/DC 효율 각각 98%, 발전계 보조전력 0.5 kW라는 과거 가정에서 순공급 25.999513 kW와 연료 1.955716 g/s가 재현됐다. 정상상태 후보 계산의 자기일관성 확인이며 채택된 연료소비 모델은 아니다.

발전기 후보 맵의 360 V와 25°C는 가정 단일축이다. 실제 T1 버스는 380.9396–385.6661 V로 8,001개 표본 모두 360 V 단일축과 다르다. 단일축 맵을 그대로 사용해 전압 의존성을 검증했다고 주장할 수 없다. 현재 FMU의 전압별 I=P/V 공급 관계는 이 후보 전기기 효율맵의 전압 검증을 대신하지 않는다.

## 기동응답 근거와 다음 구현

0.5 s 지연, 상승·하강률, 최소 유지시간은 기존 프로토콜의 가정값이다. 이번 자료에서 실측 기동시간·시동연료·온도별 디레이팅 값을 확보하지 못했다. 우선 기존 전력원 연구 가정을 유지하고, EMS 요청·부하·배터리 충전수용·보호 입력을 받아 상태와 실제 공급을 출력하는 전원 인터페이스가 필요하다. 기동 횟수, 상태, 타이머, 요청과 실제 출력은 결과로 기록해야 한다.

입력 감사의 완료조건은 현재 공급원·내장 구성·후보 맵의 식별, 숫자 재현, 동특성 근거의 확보 수준 기록이다. 이 배치에서 완료했다. 다음 작업은 현재 프로토콜의 요청형 전원 인터페이스와 제한 전 요구/배터리 가용출력 신호를 준비하는 것이다. 기존 T1을 재실행할 필요는 없다.

## 원문과 버전

새로 GM 제조사 Drive Unit PDF와 Applied Sciences 논문 v2 PDF를 내려받아 별도 SOURCE_DOCUMENTS.zip에 담았다. 다운로드 원문·URL·SHA-256 및 실패 이력은 sources/DOWNLOAD_MANIFEST.json에 있다. INL 2016 Volt factsheet 직접 다운로드는 HTTP 403으로 실패했으며 URL을 보존했다. SAE 문헌은 공식 초록/서지 확인 범위다.

새 v2 PDF SHA-256은 6cedfa864498ffe3b5e0e994ef74d549fa8fca18c309e8db44315bdba4be8dd4다. 과거 벡터 추출에 사용한 PDF 해시 c64b8ddc와 다르다. 원 도표 추출 코드를 새 PDF에 재실행하거나 옛 숫자표를 조용히 재생성하지 않았다.

## 재현

압축을 푼 감사 패키지에서 Python과 numpy/pandas가 있는 환경으로 python audit_inputs.py를 실행한다. inputs에 저장본·시험 FMU·실제 Plus CSV, archived_maps에 원래 후보 CSV와 체크포인트가 포함돼 있다. AUDIT.json이 채널·수치·해시·적용 제한의 상세 결과다. evidence에 확인한 문서 본문과 기존 입력 안내 및 FMU C 소스를 보존했다.

공식 출처
- GM Drive Unit PDF. https://media.gm.com/content/dam/Media/microsites/product/Volt_2016/doc/VOLT_DRIVEUNIT.pdf
- SAE 엔진·시스템 원문 서지. https://doi.org/10.4271/2015-01-1152
- SAE 전기기 원문 서지. https://doi.org/10.4271/2015-01-1208
- SAE 인버터 원문 서지. https://doi.org/10.4271/2015-01-1201
- Applied Sciences 저자 논문. https://doi.org/10.3390/app11177779
- 저자 소속기관 공개 원문 등록. https://iris.unipa.it/handle/10447/524960
- INL 차량 제원. https://avt.inl.gov/sites/default/files/pdf/phev/fact2016chevroletvolt.pdf
{
  "audit_status": "COMPLETE",
  "active_research_contract": "2026-11-01 resume bundle: 26 kW net DC source with assumed response; fuel extension conditional",
  "completed_T1_checkpoint": "615d5ca56312ee5be9700f85dd775c76f645d3a7",
  "native_component_settings": {
    "engine_displacement_cm3": 2000.0,
    "engine_inertia_kgm2": 0.134,
    "generator_type": "asynchronous_machine",
    "generator_inertia_kgm2": 0.05,
    "generator_global_losses_map": true,
    "project_sha256": "3a9b59154485708945147bed4834bc3bf0f37817ba68105452b177162f82fec4"
  },
  "archived_map_candidates": {
    "L3A": {
      "file": "L3A_CRUISE_PREVIEW_assumed_axes.csv",
      "sha256": "1bd6d7a0d58446e759a7736dc4e7d901b53af5b172d2830a9e3176e91279c0ee",
      "rows": 528,
      "columns": [
        "Speed_rpm",
        "Torque_Nm",
        "FuelConsumption_g_s"
      ],
      "duplicates": 0
    },
    "MGA": {
      "file": "MGA_CRUISE_PREVIEW_assumed_axes.csv",
      "sha256": "95a4276feaf9f4e1f9adbc45f864569b75f851a3f8ed6a09d5d0436acd4885e0",
      "rows": 1314,
      "columns": [
        "Temperature_degC",
        "Voltage_V",
        "Speed_rpm",
        "Torque_Nm",
        "Efficiency_pct"
      ],
      "duplicates": 0,
      "voltage_axes": [
        360
      ],
      "temperature_axes": [
        25
      ],
      "Q4_exact_mirror": true
    },
    "MGB": {
      "file": "MGB_CRUISE_PREVIEW_assumed_axes.csv",
      "sha256": "7114ab1f0ae20047f046a6bbc7d3d1d5843fc16e21ee94891b732addfcfcc71b",
      "rows": 1380,
      "columns": [
        "Temperature_degC",
        "Voltage_V",
        "Speed_rpm",
        "Torque_Nm",
        "Efficiency_pct"
      ],
      "duplicates": 0,
      "voltage_axes": [
        360
      ],
      "temperature_axes": [
        25
      ],
      "Q4_exact_mirror": true
    }
  },
  "reconstructed_26kW_point": {
    "target_net_kW": 26,
    "status": "candidate_within_reconstructed_warm_core",
    "generator": "MGA",
    "ratio_generator_over_engine": 2.0,
    "engine_rpm": 2950.0,
    "engine_torque_Nm": 98.0,
    "generator_rpm": 5900.0,
    "generator_torque_Nm": -48.02,
    "engine_shaft_kW": 30.27448120509364,
    "generator_efficiency_pct": 93.0,
    "engine_efficiency_pct": 36.0,
    "net_bus_kW": 25.999512548377574,
    "fuel_g_s": 1.955715840122328,
    "net_fuel_g_kWh": 270.79650094746603,
    "recalculated_net_kW": 25.999512548377577,
    "recalculated_fuel_g_s": 1.9557158401223282
  },
  "candidate_voltage_coverage": {
    "map_axis_V": 360,
    "actual_bus_min_V": 380.9395830165346,
    "actual_bus_max_V": 385.6660648002075,
    "actual_points_outside_single_axis": 8001,
    "meaning": "Single assumed axis does not establish measured voltage dependence"
  },
  "current_FMU": {
    "sha256": "ab10c6b3111f52d317fe27b5668479f908406ed0a964d4544a0dbe8f5f9b1c23",
    "ports": [
      {
        "name": "V_bus_V",
        "causality": "input"
      },
      {
        "name": "I_terminal_A",
        "causality": "output"
      },
      {
        "name": "P_command_W",
        "causality": "output"
      },
      {
        "name": "current_sign",
        "causality": "parameter"
      }
    ],
    "waveform": "time scheduled 0-16 s",
    "request_input_present": false,
    "charge_limit_input_present": false,
    "physical_engine_start_model": false
  },
  "fuel_extension_ready": false,
  "generator_dynamics_measured": false,
  "implementation_next_gate": "Request/state/protection interface then pre-limit demand/available-power screening under the existing contract"
}
