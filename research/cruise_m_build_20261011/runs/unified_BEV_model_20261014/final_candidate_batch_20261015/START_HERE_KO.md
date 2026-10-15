# 하나의 공통 BEV 후보 — 확인 실행5건

배터리 용량·OCV를 유지하고 구동측 유효 손실 및 공통 저항을 보완한 후보다.5개 파일은 **동일한 차량·배터리·손실·충방전 제한**이며 시험 속도/온도/종료시간/동일식으로 역산한 초기SOC만 다르다. 공통 핵심 표의 해시가5개 모두 같음을 확인했다. 실제 CRUISE 실행 전이고 최종 채택은 아직 아니다.

## 먼저067 전체를 실행

1. ZIP을 모두 풀고 `BEV_FINAL_CANDIDATE_61905067.proj`를 연다.
2. `REEV_MBE → Cycle Run → ANL61905060`을 선택한다. **모든 파일의 Case 이름은 ANL61905060**이며 연결 오류를 예방하기 위해 이름을 유지했다. 각 파일에는 해당 시험의 실제 속도 프로파일이 내장돼 있다.
3. End time **10122.190356초**, 초기 모델SOC **81.764106%**를 확인하고 Run 한다. End time9500으로 바꾸거나 SOC를 추가로 올리지 않는다.
4. 실패하면 이후 실행을 보류하고 실패 시각·Details 오류를 전달한다. 정상 종료하면 같은 패키지의 아래4건을 이어서 실행한다.

| 순서 | 프로젝트 | End time(s) | 초기 모델SOC(%) |
|---|---|---:|---:|
| 1 | BEV_FINAL_CANDIDATE_61905067.proj | 10122.190356 | 81.764106 |
| 2 | BEV_FINAL_CANDIDATE_61905060.proj | 3150.896995 | 84.493821 |
| 3 | BEV_FINAL_CANDIDATE_61905058.proj | 1489.898579 | 98.782103 |
| 4 | BEV_FINAL_CANDIDATE_61905059.proj | 2221.897881 | 94.016831 |
| 5 | BEV_FINAL_CANDIDATE_61905066.proj | 7630.892723 | 98.386055 |

모든 파일에서 같은 모델/Case를 선택한다. 파일별 프로파일은 내장되어 별도DAT 입력이 필요 없다. CSV는 시험별 폴더로 보관한다. 새 후보에서 손실/저항이 달라져 이전060/058 통과를 그대로 합칠 수 없으므로 한 번의 공통 확인 묶음으로 다시 확인한다.061은 사전 회귀 계산만 유지하고 새 필수 실행으로 추가하지 않는다.

## 내보낼 결과

각 시험마다 기존과 동일한 **battery·velocity·generator CSV 3개**, 합계15개다. 파일에 시험 번호를 붙인다(예:`battery_61905067.csv`). 기존 항목/단위 행을 유지한다. 실행 저장본과 solver log도 보관한다.

- battery:Voltage,Current,SoC 및 기존 배터리 모니터 항목.
- velocity:Desired/Actual Velocity,E-Motor Current,E-Consumer Current,E-Motor Power Mech.,E-Motor Speed/Torque,Brake Pressure Actual 및 기존 항목.
- generator:기존 발전기/엔진7신호.

폴더예:`exports/61905067/battery_61905067.csv` . 자동 비교:`python evaluate_final_batch.py --package . --exports-root ./exports` . 한 건만 먼저 분석할 경우 `python evaluate_final_candidate.py --package . --test 61905067 --exports ./exports/61905067` . Python이 없어도CSV만 전달하면 분석한다.

## 통과하면 종료할 범위

온난 조건의 동일Bolt 시험차량 자료를 **하나의 공통 유효 모델**로 재현하는 BEV 기초 검증이다. 에너지±5%,전압RMSE≤2 V·평균편차±1 V,속도RMSE≤1 km/h,거리±0.5%,DC수지≤1%,발전기OFF,유효 기간 완료/SOC정의역 유지로 판정한다. 원래 기준을 완화하지 않는다.

5건 실제 결과가 충족되면 이 범위의BEV 검증을 끝내고 공식 성능 비교·가상EREV로 진행한다.067은 **실측 속도를 입력한 에너지/전압 재현**이므로 저SOC 최대출력이나 실차 저SOC 감속을 유발하는BMS 정책 검증까지 주장하지 않는다. 이미 열람/보정에 사용한 동일 차량 자료이므로 독립 검증으로 부르지 않는다.

## 후보의 근거와 가정

직전9500초의 실제 진단은0.9673 kWh 과소진, 같은 시점 약1.91%p SOC차이, 끝점−10.57 V 전압오차를 보였다. 따라서 용량을 임의로 늘리기보다 주행저항/EDU 유효 손실 경계를 보완했다. 자세한 내용은 `DIAGNOSTIC_RESULT_KO.md`, 사전 계산은 `common_residual_sensitivity.csv`·`tail_forecast.json`, 공통 파라미터는 `parameters.json`을 참조한다.

사전 계산과 전체067 꼬리 구간 예상은 CRUISE 차량/제어의 실제 결과가 아니다. 최저SOC0.57–0.77% 예상은 정상 종료 보장이 아니다.530/160 A 및242.32/402 V는 여전히 모델 가정이며 OEM 정책 전체가 식별된 것은 아니다. 확인된 유효 범위와 남은 가정을 최종 결과/중간보고에 함께 기록한다.
