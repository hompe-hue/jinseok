# 실험자료 시험조건 대조 — 시작 체크포인트 (2026-10-13)

## 직전 단계 완료

FTP75 generator.csv 검증을 완료하고 GitHub e27fc0c756cd2dc599f1d8dd755118c1a8aa22b4에 원본·검증 JSON·설명·재현 스크립트를 저장했다. 전 구간 2478점의 발전기/엔진 출력·회전수·전류·연료가 0이다. 이 단계는 반복하지 않는다.

## 비교 대상과 현재 결과의 구분

기존 ANL 61905054는 시험 요약 PDF 2쪽의 Day 4 첫 10 mile drive이다. FTP75라고 정의된 시험이 아니다. 해당 표는 시험실 온도 23.34°C, Front 2WD, 순 HV DC 에너지 2172 Wh, 적산 순전하 5.54 Ah를 보고한다. 기존 검증 보완 기록의 계측 Phase_1은 약 1144.899 s이며 표시 SOC 99.9855→98.025%, HPCM2 96.824→93.688%다. 이 기존 결과를 다시 계산하지 않았다.

현재 CRUISE M 실행은 AVL Ftp75.prox 2477 s, 초기 모델 SOC 60%, 보조부하 0.96 kW 가정이다. 따라서 현재 2.555635 kWh를 2172 Wh와 직접 비교해 실차 재현 오차 또는 검증 완료로 판정하지 않는다.

| 조건 | 기존 공개자료 | 현재 모델 / 다음 확인 |
|---|---|---|
| 속도 시계열 | ANL 61905054 실제 속도, 명시된 계측 Phase 구간 | FTP75 구현 점검 완료. 실험 비교에는 동일 Phase의 실제 속도 및 시간 원점 필요 |
| 질량 | EPA2018 ETW 3875 lb = 1757.67043375 kg | 목표 질량은 기존값 유지. Curb weight 1625 kg와 Additional load 132.6704 kg의 실제 반영 및 동역학 질량을 Vehicle 화면에서 확인. EPA ETW를 ANL 시험의 실측 질량으로 자동 동일시하지 않음 |
| 주행저항 | 기존 EPA Target ABC, 126.329493873 N / 0.557774548 N h/km / 0.033456276004 N h²/km² | 단위 및 현재 입력 확인. ANL 개별시험 설정과의 대응 근거 추가 확인 |
| SOC | 표시 SOC/HPCM2/HPCM 좌표가 서로 다름 | 초기60% 상태는 구현 점검 조건. 실험의 표시99.9855%를 모델 초기SOC로 곧바로 복사하지 않고 기존 SOC 정의 등록표·배터리 참조식 좌표에 맞춰 대응 |
| 온도 | ANL 시험실 23.34°C; 기존 배터리 CAN 약22–22.5°C | Environment / Battery defined / E-Motor layout 온도 각각 확인. 시험실 온도와 팩 온도를 같은 변수로 대체하지 않음 |
| 보조부하 | 원본 선택 채널의 LV_DCDC_output_W / HVAC_CAN_kW 및 경계 정의 | 현재 0.96 kW는 예제 가정. 저전압 출력과 HV 입력, 효율 및 중복 여부 확인 후 비교조건 정의 |
| 에너지 경계 | HV 배터리 순 DC Wh | 기존 CSV 단자 V×I 순에너지. Range Energy Left 감소나 AC 라벨 전비와 혼합하지 않음 |

## 바로 다음 GUI 작업

CRUISE M Home의 Vehicle 컴포넌트 Parameters에서 Curb weight, Additional load, Gross weight, Driving resistance 방식과 ABC 단위를 확인한다. 기존 입력값을 임의로 바꾸기 전에 현재 적용 화면을 기록한다. 시험질량 확인이 끝난 다음, 동일 시험 속도·SOC·온도·부하 조건의 입력 준비를 순서대로 진행한다. 아직 실제 조건 정렬이나 실차 비교가 완료된 상태는 아니다.

## 자료 위치와 출처

- ANL 시험 요약 PDF: 기존 raw_source_hashes.json의 ANL2017_Bolt_TestSummary_20240925.pdf. 2쪽을 렌더링해 61905054_1 행과 23.34°C / 2172 Wh / 5.54 Ah 대응을 확인했다.
- Phase 시간 및 SOC: 기존 research/validation_fix_20261006/results/battery_data_quality.json.
- EPA Target ABC/ETW: 기존 source_hashes.json이 가리키는 vehicle_roadload_CRUISE_units.csv 및 기존 구축 README.
- 기존 전체 speed_for_driver.csv를 Phase 구간 확인 없이 완성된 시험 입력으로 import하지 않는다. 전후 구간이 포함돼 있기 때문이다.
