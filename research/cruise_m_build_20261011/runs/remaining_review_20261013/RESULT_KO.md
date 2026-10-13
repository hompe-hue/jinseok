# Bolt EV 잔여 검토 — 추가 CRUISE M 실행 없이 완료한 범위

작성일: 2026-10-13. 기준: ANL61905060 DIS80, 이전45kW 61905060/61, 공식 ANL 원본에서 추출한 계측자료 및 기존 저장 프로젝트. **현재 접근 가능한 자료로 잔여 항목을 모두 검토했다. 에너지 +9.484% 오차는 미해소이며 모델 신뢰성 검증 완료를 선언하지 않는다.** 새 모델 입력 수정이나 사용자 실행 요청은 없다.

## 원인을 좁힌 결과

평가구간20–3150초의 순DC 차이는 **0.978064kWh**다. 방전 에너지 과대 **0.941818kWh**와 순회생 부족 **0.036246kWh**의 합이다. 따라서 순회생 부족은 전체 차이의 **3.71%**에 해당한다. 이는 순량의 회계 분해이며 구간별 회생 오차의 상쇄 가능성을 없애거나 각 제어 인과관계를 식별하는 계산은 아니다.

보조HV 에너지는0.347778kWh, 실측LV DC/DC 출력은0.290637kWh다. LV 계측이 정확하고 별도LV 에너지원이 없으며 변환손실·다른HV 보조수요가 음수가 아니라면 보조부하 과대의 상한은 **0.057141kWh**, 전체 차이의 **5.84%**다. HV입력과LV출력은 경계가 달라 실제 보조부하 수정값으로 직접 바꾸지 않는다. 보조부하만으로9.48% 편차를 설명할 수 없다.

동일1초격자에서 정확한 식 Δ(VI)=ΔV·Iref+Vref·ΔI+ΔV·ΔI로 분해하면 전압항0.027976, 전류항0.964167, 교차항0.003285kWh다. 격자VI 차이는0.995428kWh이고, 원래 계측전력의 native 적분과 격자VI의 차이0.017364kWh를 별도로 유지해야 순차이와 닫힌다. 전압항만으로 큰 에너지 편차를 설명하지 못한다. 항의 배분은 기준 선택에 의존하고 전류·전압은 연결돼 있으므로 세 항은 독립적으로 제거할 수 있는 원인량이 아니다.

## 작업별 완료 기록

| 검토 대상 | 확인한 근거와 결과 | 상태 / 수정 판단 |
|---|---|---|
| 방전45kW 제한 | DIS80에서 속도RMSE0.593540→0.421025km/h, 에너지+9.446→+9.484% | 진단 완료. 속도 추종에 영향, 주된 에너지 편차는 남음.80kW를 실차BMS 값으로 확정하지 않음 |
| 충전40kW 제한 | 실측native 피크55.875kW, 모델1초 피크40.003kW. 모델−40±0.25kW 18점. 실측40kW초과 노출에너지0.011097kWh | 제한 후보 확인 완료. 서로 다른 표본화 피크이며 노출량은 회복 가능 에너지 예측이 아님. 충전표 임의 상향 없음 |
| 회생 가중치 경고 | 저장표 속도10,20km/h→가중치0,1; 입력Vehicle/Velocity, 출력E-Drive Control/Recuperation Weight; linear 보간, constant 외삽. DIS801초표본 중 아래303, 위2670, 내부178점 | 범위 밖 입력의 구조 확인 완료. 표 설정대로면10이하0·20이상1로 유지해 가중치 폭주를 뜻하지 않음. 경고297359회와1초표본 수를 동일시하지 않음. 최신프로젝트/가중치trace 없이 현재 경고 해소나 실패 인과는 미확정 |
| 보조전력 | 위LV→HV 조건부 상한0.057141kWh(5.84%) | 주원인 설명력 검토 완료. DC/DC 효율을 임의 적용하지 않음 |
| 전압·전류 기여 | 위VI 항등식 및 native/1초격자 차이 분리. 최대 점별 closure6.74e−15kW 이하 | 계산 검증 완료. 전압만 보정해 에너지 검증 통과할 근거 없음 |
| 배터리 OCV/R/용량/RC | 기존 감사:96S3P168Ah·25°C단일OCV/R·RC비활성, 입력표와내장표 일치. 실측전류 replay도전압편차 유지.167.7/168Ah 차이는미미. depletion시험 긴휴지구간 없음 | 기존 근거 재검토 완료. 구현일치와 물리식별을 구별. CAN/모델SOC 좌표·온도·분극 불확실성 미해소, endpoint 합격판정·OCV/R/C 임의 fitting 금지 |
| Target ABC·시험질량·기구학 | 원본metadata Target28.4/.2018/.01948 및3875lb가 단위변환 후모델값과 일치. Set값은 다른 dyno설정 단계. 반경후보 추정은 독립교정 아님 | 단위/설정 대조 완료. Target−Set전체를 제거하거나 질량·반경 임의조정하지 않음 |
| ABC–EDU 수동 회전손실 경계 | EPA2017방법은coastdownABC의neutral회전저항과 부품맵 중복 가능성 설명. EPA2024 hub EDU에기어/halfshaft/베어링 포함. Bolt호환 분리수치는 미확보 | 경계 검토 완료, 수치보정 보류. 전체무부하 전기손실1.37kWh나 Target−Set2.16kWh를 중복손실로 빼지 않음 |
| 별도구동계 효율 | 저장FinalDrive효율1; Differential저장0.97는loss선택비활성. 이번확인EPA ALPHA3 BEV demo도최종감속효율1을EDU맵손실경계로 설명하고 transmission은placeholder | 일반구조 근거 확인 완료. demo기어비9.5는Bolt7.05와다르고 motorgear0.98도있어 보정상수로 전용하지 않음 |
| EPA 최신/추가 공개자료 | 공식ALPHA3 peer-reviewZIP 직접검사: unpowered_torque_loss표0,0. 공개2026논문abstract에분리테스트방법은있지만 호환수치표 미확보; 공식맵catalog의기존EDU/MOTO 경계 확인 | 이번 공개자료 탐색 완료. 0표는 측정된Boltneutral손실0의 근거가 아님. MOTO를 inverter/기어손실 없이 전체EDU에 대체하지 않음 |
| EDU맵 적용·전압/온도 범위 | DIS80 Q1/Q4/저토크bridge 재현최대1.6e−14kW; 기준400V단일맵과실측전압/온도범위 다름. regen은motoring에서합성된부분 | 구현대조 완료. 실제모터효율·회생손실 독립확정 아님. 단일전압표로전압/온도보정계수 식별 불가 |
| CAN 전류·토크 경계 | Motor_1_current_DMCM1의A단위만으로inverterDC전류를보증하지못함. CANrotor torque와hub/7.05등가EDU출력 동일성미확정 | 미확정 경계 기록 완료. CAN V×I를독립DC계측이나 잔차0.809292kWh를실측모터손실이라고명명하지않음 |
| 시간·전력부호·발전기·파일 | 0–3150초3151점, 기존hash/phase정렬·발전정지·모터DC+aux=배터리DC 확인자료 유지; 마지막0.896995초미수출 | 비교범위 검토 완료. 전체말단추정 없음. 이번추가VI/총량identity통과 |
| 최종신뢰성 판정 | 제안목표전압RMSE≤2V·absbias≤1V·에너지±5%에서61905060DIS80전압통과,에너지실패;61905061 기존전압/에너지미통과 | 현재미완료. 제안목표는인증기준아님. 이미교정/진단에사용한시험을최종미사용검증으로표현하지않음 |

## 구체적 다음 시작점

추가 CRUISE M 실행은 지금 요청하지 않는다. 먼저 **Bolt호환neutral/backdrive 또는분리기어손실 수치와 측정경계**를 확보해야 ABC–EDU 겹침을 실제보정할 수 있다. 공개방법론만으로 겹침량을 확정할 수 없다. 같은시험의전류정의/rotor·hub계측경계 문서도 필요하다. 배터리는SOC좌표가정과 충분한휴지/펄스·온도자료를 구별해야 한다. 이 자료들은이번접근가능범위에서 미확보이며 해결됐다고 표시하지 않는다.

회생경고만 정리할 경우 기존특성을 보존하는 후보는 (0,0),(10,0),(20,1),(140,1) 속도km/h–가중치 쌍이다. 현재양의속도가140이하일때 기존constant외삽 특성과같다. 이 변경은경고범위를정리하는 제안일뿐 에너지모델보정이나실차회생전략검증이 아니다. 최신프로젝트에직접적용하지않았다. 입력이음수나140초과이면 추가도메인검토가필요하다.

입력변경 근거가 생기면 해당항목만 바꾸고 그때 추가실행으로영향을 검증한다. 그전까지 동일한DIS80진단을61905061에반복하는 요청은 하지 않는다. 변경 후최종검증은 튜닝에사용하지않은시험과조건으로 분리해야한다.

## 재현과 출처

`python research/cruise_m_build_20261011/scripts/review_remaining_dis80.py` 실행. `review.json`에 입력hash·에너지항·map설정·connection IDs, `recup_domain_occupancy.csv`에전체3151표본, `Remaining_Review.ipynb`에실행기록을 보존한다. `alpha_source_manifest.json`에는직접다운로드한EPA archivehash·검사한파일·줄번호와전용불가판단을 기록했다. 기존checkpoint DIS80_VALIDATION_20261013.json과remaining_evidence_20261013.json의결과를 대체/보완한다.

- EPA2017회전손실경계방법: https://19january2021snapshot.epa.gov/sites/static/files/2017-06/documents/sae-2017-01-0899-fleet-level-modeling-real-world-factors-influencing-greenhouse-gas-emission-simulation-in-alpha.pdf
- EPA연구자2024EDU측정방법논문: https://www.researchgate.net/publication/379946298_Development_of_Benchmarking_Methods_for_Electric_Vehicle_Drive_Units
- SAE2026publisherabstract: https://saemobilus.sae.org/papers/development-comparison-benchmarking-methods-electric-vehicle-drive-units-2026-01-0198
- EPA공식mapcatalog: https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-emotor-alpha-maps
- EPA ALPHA3공식catalog와peer-reviewarchive: https://www.epa.gov/regulations-emissions-vehicles-and-engines/advanced-light-duty-powertrain-and-hybrid-analysis-alpha

각항목은 위표에서작업별완료기록으로 남겼다. 미확보자료·물리식별·신규출력 검증은완료항목에합쳐숨기지않는다. 지속게시승인: checkpoints/PROJECT_PUBLICATION_AUTHORIZATION.md.

## 재현 코드 추가 점검

기존 audit_uploaded_project.py와 audit_mechanical_loss_selection.py의 XML 인덱스가 같은id를 가진 ref노드로 실제정의를 덮어쓸 수 있는 오류를 발견했다. 정의노드만 인덱싱하도록 수정하고 저장프로젝트로 두 스크립트를 다시 실행했다. 두 실행exit0, OCV/R 6개표 최대차0, Q1/Q4 최대차1.07e−14/7.11e−15kW, 기구학최대잔차3.64e−12rpm. 기존물리경계 판단은 유지됐다. 이는감사코드수정이며CRUISE 모델수정이아니다. 재검사출력은project_audit_20261013/audit.json 및mechanical_loss_selection_20261013/summary.json에있다.
