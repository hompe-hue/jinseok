# 최신 재개 지점 — 2026-10-13

**최신 완료:** 회생진단맵 실행 CSV3종 검증 완료. `../runs/ANL61905054_regen_20261013/RESULT.md`와비교그림·수치표를중간보고에사용한다. 초기20초제외 전압RMSE0.663192V, 에너지오차+3.570158%로기존제안목표를충족했고회생이복구됐다. 실차독립검증/충전전압경계는미완료다. 현재조건을고정하고독립시험자료확보및회생순간전압차이근거검토로진행한다. 아래Charge Power 수정및진단실행요청은이미완료되어반복하지않는다.

**최신 BMS 화면 확인:** Charge Power에서SOC85%이상0kW설정을확인했다.현재88.84–93.14%실행전체가차단범위다.다음은`BMS_charge_diagnosis_20261013/NEXT_RUN_KO.md`의단일충전맵진단변경후실행이다.직전BMS화면요청은완료됐으며반복하지않는다.

**최신 결과 수신:** 실측조건 후보 실행의 CSV 3종을 받았고 `../runs/ANL61905054_aligned_20261013/RESULT.md`에 검증했다. 초기SOC93.142532%, aux0.4kW가 결과에 반영됐다. 순DC에너지2.837658923kWh(+31.68%), 회생충전이 거의없다. 최신 다음 작업은 BMS의 고SOC 충전/회생 제한 진단이다. 아래의 후보실행 요청은 과거이며 반복하지 않는다.

- 완료: FTP75 발전 정지, 질량/주행저항/Environment 확인, ANL61905054 실측 속도 DAT 작성, 초기BEV 실행 CSV 3종 검증. 완료된 설정과 실행을 반복하지 않는다.
- 최신 실행 결과: `../runs/ANL61905054_20261013/RESULT.md` 및 `verification.json`. 속도RMSE0.565088km/h, 실제거리17.0219km, 발전정지, 순DC에너지2.408901893kWh. 아직 독립 실차 검증 통과가 아니다.
- 다음 실행 안내: `ANL_61905054_phase1/NEXT_RUN_KO.md`. 두 모듈 초기SOC93.142532%, Power Consumer→General→Power0.40kW, 배터리22°C, Environment23.34°C. 기존 맵과 질량/주행저항은 고정한다.
- 사용자가 보낸 최신 화면에서 Module1 초기SOC93.142532%, Module1 Thermal Model22°C, Environment23.34°C를 확인했다. Module2 변경은 화면 증거가 없으므로 두 모듈 모두 확인 완료라고 쓰지 않는다. Power Consumer0.40kW 실행 결과는 아직 받지 않았다.
- 초기SOC는 첫 실측전압으로부터 현재표를 역산한 초기화 값이며, 보조부하는 추정값이다. 동일 시험 초기조건 식별과 이후 구간 평가를 구분한다.
- 다음 수신파일: 새 실행의 velocity/battery/generator CSV. 이전 CSV 원본을 덮어쓰지 않는다.

---

## 아래는 과거 시험조건 대조 기록이며 최신 재개 지점이 아니다

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

