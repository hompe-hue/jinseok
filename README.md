> **2026-10-14 C3 공통 배터리 첫 구현확인 준비 완료:** 공통배터리 후보와확인된BMS 모듈신호연결을 반영한 C3_IMPL_61905060.proj를 전달했습니다. 첫 실제실행은REEV_MBE → Cycle Run → C3_IMPL_61905060의ANL060 1회/CSV3개입니다. 저SOC방전제한은아직최종값이 아니며새CRUISE실행은0회입니다. [실행 안내](research/cruise_m_build_20261011/runs/unified_BEV_model_20261014/implementation_060/START_HERE_KO.md) · [전달파일](research/cruise_m_build_20261011/runs/unified_BEV_model_20261014/implementation_060/deliverables.json) · [재개 기록](checkpoints/BOLT_C3_IMPLEMENTATION_READY_20261014.json)

> **2026-10-14 최종 목표·우선순위 정정:** 하나의 공통 Bolt BEV 모델을 개선·검증한 뒤 가상 EREV 기반으로 사용합니다. C2는 과거 온난 검증 버전으로 보존하며 영구 동결하지 않습니다. 공통 배터리 개발 후보는 주행5건/장시간방전2건의 전류·고정전력 입력 전압 점검을 계산상 충족했습니다. 새CRUISE/BMS 확인 전이며 최종 모델로 채택하지 않았습니다. C2 성능4회는 지금 필수 실행이 아닙니다. [최신 판단·계산·순서](research/cruise_m_build_20261011/runs/unified_BEV_model_20261014/DECISION_KO.md) · [재개 기록](checkpoints/BOLT_UNIFIED_BEV_MODEL_20261014.json)

> **2026-10-14 C2 공식 성능 비교 실행자료 준비 완료:** 가속SOC94/100 및 EPA 원본UDDS/HWFET 반복 사본4개를 준비했습니다. C2맵·용량·방전제한은 보존했고 실제CRUISE 성능 실행은0회입니다. 첫 실행은REEV_MBE의C2_ACC_SOC94.proj → Performance/FLA입니다. [첫 실행 안내](research/cruise_m_build_20261011/runs/C2_performance_extension_20261014/START_HERE_KO.md) · [전달파일·해시](research/cruise_m_build_20261011/runs/C2_performance_extension_20261014/deliverables.json) · [재개 기록](checkpoints/BOLT_C2_PERFORMANCE_PREPARED_20261014.json)

> **2026-10-14 C2 적용 범위 정정·방전 확장 재검토 완료:** 058/059는 동일 차량의 보정 미사용 시험 평가(모델SOC79.5–94.2%)입니다. 동결 C2의 ANL064/067 실측전류 입력 재현은 전압RMSE4.03/3.92V와 모델SOC 소진을 보여 저SOC·전체 방전까지의 적용을 지지하지 않습니다. 온난 기준모델은 보존합니다. [새 근거·판단](research/cruise_m_build_20261011/runs/C2_performance_extension_20261014/RESULT_KO.md).

> **2026-10-14 중간보고7장 제작 완료:** 첨부연세대4:3디자인을 유지해 EREV배경·목적, 공식2017Bolt/C2비교, 실제CRUISE토폴로지·실측검증, 도구장단점·보완, 향후연구를 정리했습니다. 확정기준프로젝트는C2_CAL_61905060.proj. 가속·인증항속의C2직접실행은 미완료로구분합니다. [제작결과](research/midterm_20261014/RESULT_KO.md) · [파일/Canva식별자](research/midterm_20261014/deliverables.json) · [재개기록](checkpoints/MIDTERM_CANVA_7SLIDES_20261014.json)

> **2026-10-14 Bolt C2 온난 BEV 기준모델 검증 마무리:** 미적합 독립058/059 전체7항목 통과. 순DC에너지−3.36/+0.21%, 전압RMSE0.78/1.27V·평균편차+0.22/+0.974V. C2 보정값을 그대로 확정하고 이번 BEV 판정을 위한 추가실행은 없습니다. 저SOC/저온/BMS·발전계 검증은 이 결론의 범위 밖이며 회수에너지와059의좁은전압여유를 명시했습니다. [최종 결과](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/independent_review/RESULT_KO.md) · [다음 단계](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/EREV_BASELINE_HANDOFF_KO.md) · [재개 기록](checkpoints/BOLT_C2_WARM_VALIDATION_COMPLETE_20261014.json)

> **2026-10-14 C2 실제 보정 확인 완료:** actual060/061/066 순DC에너지 오차+0.91/−0.69/−2.36%, 전압RMSE1.40/1.19/0.86V·평균편차+0.37/+0.52/+0.20V로 모두 사전 전체 기준을 충족했습니다. C2 고정 후 다음은 미적합 독립058/059 실행2회·CSV6개입니다. 전체 검증은 아직 미완료이고 C1 독립066 실패는 보존합니다. [실제 결과](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/actual_results/RESULT_KO.md) · [다음 실행](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/NEXT_HOLD_RUNS_KO.md) · [재개 기록](checkpoints/BOLT_C2_ACTUAL_CAL_CONFIRMED_20261014.json)

> **2026-10-14 C2 공통 배터리 보정 후보·실행 준비 완료:** C1 독립066 평균편차 미달을 보존하고060/061/066 공통 유효 배터리를 보완했습니다. 계산상 전압 기준 충족이며 실제 검증은 미완료입니다. 현재 작업은 C2 CAL060/061/066 실행·CSV9개 확인 → 통과 후 새 HOLD058/059입니다. [실행 안내](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/START_HERE_KO.md) · [결과](research/cruise_m_build_20261011/runs/C2_battery_common_20261014/RESULT_KO.md) · [재개 기록](checkpoints/BOLT_C2_CANDIDATE_PREPARED_20261014.json)

> **2026-10-14 C1 독립066 평가 완료·전압 평균편차 미달:** 에너지 −2.36%, 전압 RMSE1.90V는 기준 충족, 평균편차 −1.36V는 미달입니다. C1과 기준은 그대로 보존했습니다. 공통 배터리 C2 보완을 검토하며066은 C2 보정자료로 전환하고 새 독립시험을 분리합니다. [결과·원인 검토](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/actual_results/61905066/RESULT_KO.md) · [재개 기록](checkpoints/BOLT_C1_HOLD066_REVIEW_20261014.json)

> **2026-10-14 C1 실제 보정 확인 통과:** 실제060/061의 에너지 오차 +0.91/−0.69%, 전압 RMSE1.30/1.59V로 연구용 기준을 만족했습니다. C1을 고정하고 다음 작업을 HOLD066 연속 실행1회로 정리했습니다. 최종 독립 검증은 아직 미완료입니다. [실제 결과](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/actual_results/RESULT_KO.md) · [066 전 고정 기록](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/frozen_for066.json) · [재개 기록](checkpoints/BOLT_C1_CAL_CONFIRMED_20261014.json)

> **2026-10-14 C1 전달 파일 수정:** 기존 CAL060/061의 0KB 문제를 수정했습니다. 최신 패키지 버전2를 다시 내려받아 모든 파일 크기·해시와 프로젝트 XML을 확인했습니다. 보정 수치는 그대로이며 CRUISE M 열기·실행 확인은 남아 있습니다. [수정 기록](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/DELIVERY_REPAIR_KO.md) · [재개 기록](checkpoints/BOLT_C1_DELIVERY_REPAIR_20261014.json)

> **2026-10-14 C1 보정안 확정·실행 패키지 준비:** 따뜻한 조건의 차량 수준 유효 보정이며 아직 CRUISE 확인 실행 전입니다. 현재 작업은 C1 CAL060/061 실행 및 새 CSV 6개 비교 → 통과 후 HOLD066 연속 독립 검증입니다. [적용 수치·근거](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/DECISION_KO.md) · [실행 안내](research/cruise_m_build_20261011/runs/final_candidate_C1_20261014/START_HERE_KO.md) · [재개 기록](checkpoints/BOLT_C1_CANDIDATE_FIXED_20261014.json)

> **2026-10-14 DIS80 저장본 연결 완료:** 현재 파일의 80 kW 상한·060 프로파일·OCV/R·EDU 표를 실제 출력과 대조했습니다. 저장본 요청은 해결됐고, 오차 보정·066 독립 검증은 남아 있습니다. [최신 분석](research/cruise_m_build_20261011/runs/dis80_project_closure_20261014/RESULT_KO.md) · [재개 기록](checkpoints/BOLT_DIS80_PROJECT_CLOSURE_20261014.json)

> **Bolt BEV 실측 비교 재개(2026-10-14):** [새 구간별 잔차 진단·남은 작업·066 준비](research/cruise_m_build_20261011/runs/validation_closure_20261014/RESULT_KO.md) · [재개 기록](checkpoints/BOLT_VALIDATION_CLOSURE_20261014.json).066 연속 7630.893초 입력과 자동 비교 코드 준비 완료. 보정 입력 동결·066 실제 CRUISE 실행은 미완료입니다. 최신 업로드 .proj는 이전45kW 저장본이므로 DIS80 현재 저장 프로젝트1개가 다음 필요한 입력입니다.

> **EREV 구동 경계 확인(2026-10-14):** [엔진의 기계 구동과 발전 전력 공급의 구분](research/research_direction_20261013/EREV_POWER_PATH_CLARIFICATION_20261014.md) · [재개 기록](checkpoints/EREV_POWER_PATH_20261014.json). 순수 직렬 구조에서 발전 전기는 구동 전기 부하에 기여할 수 있고, 배터리는 수요와 발전의 차이를 충전/방전합니다. PHEV와 병렬형은 동의어가 아닙니다. 모델 변경·새 실행은 없습니다.

> **최신 연구 방향과 중간보고 준비(2026-10-13):** [비판적 검토·계산·실행 계획](research/research_direction_20261013/RESULT_KO.md) · [12장 발표 원고](research/research_direction_20261013/midterm_content.json) · [다음 세션 재개 기록](checkpoints/RESEARCH_DIRECTION_20261013.json). 유한 주행 미션의 성능 유지 경계와 기존 S0~S4의 조건부 효과를 중심에 둡니다. 054의 조건부 재현 목표 충족과 060 에너지 +9.484% 미충족을 함께 보고하며, 066 독립 평가와 전체 모델 검증은 아직 완료하지 않았습니다.

> **최신 작업:** [Bolt 핵심 근거 검토](research/cruise_m_build_20261011/runs/core_evidence_20261013/RESULT_KO.md) · [재개 기록](checkpoints/CORE_EVIDENCE_20261013.json). 새 CAN·soak·완전충전 자료를 검토했습니다. 에너지 +9.484% 편차와 계측경계 불확실성은 남아 있으며, 모델입력 변경이나 추가 사용자 실행 요청은 없습니다.

> **최신 검토(2026-10-13):** Bolt EV 잔여 항목의 접근 가능한 자료 검토를 완료했습니다. [검토 결과](research/cruise_m_build_20261011/runs/remaining_review_20261013/RESULT_KO.md)와 [재개 기록](checkpoints/REMAINING_REVIEW_20261013.json)을 먼저 읽으세요. DIS80 에너지 +9.484% 편차는 미해소이며, 추가 사용자 실행이나 모델 입력 변경은 없습니다. Bolt 분리손실 및 계측경계 근거가 다음 시작점입니다.

> 최신 BOLT EV 비교 재개: [완료 결과·다음 시작점](checkpoints/bolt_validation_resume_20261013_2114.md) · [지속 게시 승인](checkpoints/PROJECT_PUBLICATION_AUTHORIZATION.md) · [실제 게시 상태](checkpoints/PROJECT_PUBLICATION_STATUS.json).

# 논문 연구 자료

Bolt 기반 BEV 검증과 Volt 발전계 기반 가상 EREV/EMS 연구의 CRUISE M 입력자료 및 작업 기록입니다.

## 최신 단계 — 2026-10-13

[회생 복구 후 실측 비교와 중간보고 자료](research/cruise_m_build_20261011/runs/ANL61905054_regen_20261013/RESULT.md): 초기화구간 이후 전압RMSE0.663V, 에너지차이+3.57%. 기존 제안 목표를 해당시험 조건부 재현에서 만족했다. 회생 충전맵은 진단가정이며 독립시험·실차 충전전압 경계검증은 후속과제다. [최신 재개 지점](research/cruise_m_build_20261011/empirical_alignment_20261013/RESUME.md)을 우선한다.

[FTP75 발전 정지 검증 완료](research/cruise_m_build_20261011/runs/FTP75_2477s_20261012_1626/generator_verification.md): 사용자 generator.csv의 0–2477초 / 2478점에서 발전기·엔진 출력/회전수·전류·연료가 모두 0이며, 기존 배터리/속도 export와 일치합니다.

[ANL 실측 속도 실행 검증 완료](research/cruise_m_build_20261011/runs/ANL61905054_20261013/RESULT.md). [최신 재개 지점](research/cruise_m_build_20261011/empirical_alignment_20261013/RESUME.md)을 확인하세요. 후보 적용 및 회생진단 실행까지 완료됐습니다. 기존 설정 화면 확인은 반복하지 않습니다. 독립 실차 검증 통과는 아직 판정하지 않았습니다.

화면 자료 복구의 최신 반영 범위는 [PUBLISH_STATUS.json](research/cruise_m_build_20261011/session_recovery_20261012_1649/PUBLISH_STATUS.json)에 기록합니다.

## 복구 기록 — 2026-10-12

[CRUISE M 입력표 복구: 최신 완료 상태와 다음 시작점](research/cruise_m_build_20261011/session_recovery_20261012_1649/RESUME.md)

FTP75 실행·수치 점검과 Report Page 오류 해결까지 기존 커밋에 저장돼 있습니다. 누락된 결과 CSV와 화면 자료를 추가했습니다. FTP75 발전 정지 확인은 완료됐습니다. 과거의 첫 실행 전 체크리스트보다 최신 runs 체크포인트와 위 인계 기록을 우선합니다.

## 초기 구축 기록 — 2026-10-11

[CRUISE M 구축 기록과 재개 체크리스트](research/cruise_m_build_20261011/README.md)

- 모터 EDU 손실맵 regular DAT 및 배터리 OCV/R DAT import 성공을 화면에서 확인했습니다.
- 작동한 DAT·ZIP, 원본 export 문법, 주요 화면 6장, 설정의 확인/미확인 상태와 입력 검산을 보관했습니다.
- 마지막 REEV_MBE Data Checks는 `No data check messages`. 주행 시뮬레이션과 실측 대비 검증은 아직 미완료입니다.
- 다음 시작점은 Range Extender Control로 발전을 비활성화하고 Power Consumer 보조부하 조건을 확인하는 것입니다.
- 실제 Windows CRUISE M 프로젝트 파일은 아직 전달받지 않아 저장소에 없습니다.

## 기존 연구 자료

- [검증 보완 및 SOC/완성맵 적용 한계](research/validation_fix_20261006/README_검증보완.md)
- [Bolt + Volt Gen2 가상 EREV 자료](research/bolt_volt_genset_20261006/README_가상EREV.md)
- [이전 Range Extender 입력자료](research/range_extender_20261006/RESUME.md)

이전 65 kW 표는 가정 기반 후보이며 실측 연속 정격 검증이 아닙니다. 과거 GitHub 쓰기 거절 기록은 이전 시도에 관한 것으로, 이후 동기화 완료 기록과 최신 커밋으로 실제 반영 상태를 확인합니다.

