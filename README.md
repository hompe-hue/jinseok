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

