# CRUISE M 입력표 복구 — 새 세션 인계

2026-10-12 16:49 KST 요청에 따른 저장·인계 기록. 저장 직전 origin/main을 확인했으며 기준 커밋은 `aa4adda5e48ab9bb5f1f2659d174ef8538f462be`이다. 기존 입력·실행 단계는 다시 수행하거나 재정의하지 않았다.

## 최신 완료 상태

- 모터/배터리 DAT import 기록과 원본은 기존 경로를 유지한다.
- WLTC 120 s 및 1800 s 실행, Energy 표시 정의 복구, 보조부하 960 W 확인은 기존 runs 체크포인트에 저장돼 있다.
- FTP75 실행 및 수치 일관성 점검은 `runs/FTP75_2477s_20261012_1626/checkpoint.json`이 최신이다. 2478점, 0–2477 s, 실제거리 17.8007515 km, 속도 RMSE 0.599775 km/h, SOC 60→55.7597634%, 단자 순방전에너지 2.5556346 kWh이다. 기존 수치 분석을 반복하지 않았다.
- 반복된 `Domain of chart cannot be determined` 오류는 사용자가 Report Page를 새로 만들어 해결했다. 같은 오류 해결을 위해 시뮬레이션을 다시 돌리는 단계로 돌아가지 않는다.
- FTP75 및 마지막 WLTC의 누락된 battery/velocity CSV 원본을 각 runs 폴더에 추가했다. 동일 SHA256 파일은 중복 저장하지 않았다. 2026-10-11~12의 추가 복구 자료와 화면은 이 폴더에 있으며 전체 파일 대응·SHA256·추가/기저장 여부는 `file_manifest.json`에 있다.

## 다음 시작점 — FTP75 BEV 발전 정지 검증

최신 화면 `screenshots/image(20261012-074057).png`에서 FTP75 → Range Extender Monitor → In 신호가 Report Tree에 들어간 것을 확인했다. In 폴더에는 Actual Engine Speed, Cumulated Fuel Consumption, Current, Desired Engine Speed, Fuel Massflow, Load Signal Generator, Operating Mode, Power Generator, Power ICE 등이 표시된다. 따라서 어떤 폴더를 추가할지 다시 찾는 단계는 끝났으며, 다음은 필요한 신호를 개별 표시하거나 CSV로 내보내 수치를 확인하는 단계다.

1. 기존 FTP75 결과와 현재 Report Page를 유지한다.
2. `Range Extender Monitor → In`의 **Power Generator / Fuel Massflow / Cumulated Fuel Consumption / Actual Engine Speed / Power ICE**를 구분해 표시하거나 export한다. 폴더 전체를 넣어 서로 다른 단위의 축과 범례가 겹친 화면만으로 판단하지 않는다.
3. 각 신호의 시간 범위 0–2477 s, 단위, 최대 절대값과 누적 연료의 처음/끝 값을 확인한다. Cumulated Fuel Consumption은 초기값과 증가량을 구분한다.
4. 위 출력·연료·회전수가 전 구간 0인지 수치로 확인한 뒤 해당 파일 및 검증 체크포인트를 저장·commit한다. 현재 스크린샷만으로 전 구간 0을 확정하지 않았다. CSV가 없으므로 이 검증은 아직 미완료다.
5. 이 단계를 완료·검증·commit한 뒤에만 선정한 Bolt 공개 실험자료의 시험조건 정렬 및 독립 비교 단계로 넘어간다.

## 유지할 규칙과 한계

- BEV 검증 먼저, 이후 Bolt 기반 가상 직렬 EREV. i3는 제외한다. 기존 맵 출처·가정과 번호 단계의 완료조건은 변경하지 않는다.
- 0.96 kW는 예제 보조부하 가정이다. 2477 s 전체 소비량은 FTP 인증 가중 결과가 아니며 실차 검증 완료를 뜻하지 않는다.
- 기존 과거 README의 '첫 실행 전' 상태보다 최근 runs 체크포인트가 우선한다.
- Windows CRUISE M native 프로젝트는 아직 제공되지 않았다. 이 백업은 입력자료·결과 CSV·화면·기록이며 실제 GUI 프로젝트 전체 백업이 아니다.
- 이전 세션 대화 전문 및 오류로 중단된 응답 전체는 조회하지 못했다. 확인된 GitHub 기록, 현재 대화에 제공된 세션 발췌, 복구 파일과 직접 확인한 화면만 인계했다. 별도 기록 제외 요청을 받은 방법론 상담 대화는 저장하지 않았다.
- 이 요청의 범위는 자료 저장과 새 세션 재개 지점 인계다. 새 모델 설정·발전계 선택·실측 대비 검증을 완료했다고 표시하지 않는다.

## 검증

`recovery_verification.json`: 파일 SHA256 및 FTP75 CSV의 2478점/0–2477 s/유한수 값 확인. 기존 입력·수치 검산을 반복하지 않았다. 기존 동일 파일 및 체크포인트는 보존했다.
