> **R2 수정본:** 이전C3의Case이름과CaseList내부인덱스가불일치했다. 정상실행된C2의Case/프로파일/Pool구조를그대로보존해수정했다. 기존불안정창은덮어쓰기저장하지말고종료한뒤R2파일을연다. Case와Profile은 **ANL61905060** 이름을유지한다. 파일명만C3이며배터리는C3값이다. CRUISE프로그램에서수정본을열고실행하는확인은아직남아있다.

# 지금 할 일: 공통 배터리 C3 구현 확인1회

기존 C2 성능4회를 다시 실행하지 않는다. 새 공통 배터리 후보가 실제 차량·제어와 연결되어 계산대로 작동하는지 ANL060 주행1회로 먼저 확인한다. 이것은 보정에 쓴 시험의 구현 확인이며 최종/독립 검증이 아니다.

1. C3_IMPL_61905060_R2.proj를 연다. 기존파일에 DAT를 수동으로 덮어쓰지 않는다.
2. **모델REEV_MBE**, **Cases → Cycle Run → ANL61905060**만 선택한다. 다른case 일괄 실행은 선택 해제한다. 이전result/report 이름이 남으면 이case의 결과를 새Data Browser/Report Page에 선택한다.
3. 프로파일은내장ANL060 실측3150.897초이다. 별도FTP75/WLTC/가속프로파일을 선택하지 않는다. 초기SOC 약84.4861%, 배터리24.5°C, 기존060 환경·시험질량·보조부하0.4kW를 유지했다.
4. Data Checks 후 실제계산을 실행한다. 경고/실패가 나면 메시지를 함께 보관한다. 결과표의초기SOC와엔진/발전기0을 확인한다.
5. 이전과같이**battery,velocity,generator CSV3개**를1초간격으로 내보낸다. 첫행Time0부터 마지막Time3150까지 누락없이저장한다. 예: battery_C3_060.csv,velocity_C3_060.csv,generator_C3_060.csv.
6. 실행한저장프로젝트와solver log도같이보관한다. CSV3개로에너지·전압·속도·거리·DC수지·발전정지를먼저평가한다. 파일명만바꾼옛C2 CSV를사용하지않는다.

주요신호는기존과같다. battery: Voltage/Current/SoC. velocity: Actual Velocity/Desired Velocity/E-Motor Current/E-Consumer Current. generator: 엔진회전수/누적연료/전류/요구회전수/연료유량/발전기출력/엔진출력7개.

## 이번 사본에서 바뀐 것

- 하나의공통배터리OCV/R곡선과유효용량169.356846Ah, 공통초기화규칙으로얻은SOC를적용했다.
- BMS Power Module2가Module2손실을받던연결을Module2전력으로수정했다(저장된두모델모두).
- 저장된모델중하나의SoC Module2가Module1 SOC를받던연결을Module2 SOC로수정했다. REEV_MBE의기존SOC2연결은이미올바랐다.
- 모터/EDU손실맵,주행입력,차량제원,회생분배,보조부하를유지했다. 배터리OCV/R/SOC/용량은모든주행의공통개발후보값이다.

## 남아 있는 제어 경계

기존SOC20%에서0kW가되는방전제한표와회생SOC가중치등은이번짧은온난구현확인에서유지했다. 저SOC시험에는이진단제한을그대로최종사용할수없다. Vehicle Current Analysis의350V는전류계산시분모하한이며350V미만에서차단하는실차BMS정책이아니다. 실제차단전압으로해석하지않는다.

따라서이파일로곧바로EPA전구간항속이나EREV저SOC성능을최종평가하지않는다. 공통배터리구현확인과BMS경계보완을거친다. 실제CRUISE열기/solver는아직실행하지않았다. ZIP/배터리맵/용량/초기SOC/신호연결의저장데이터만검사했다.

자동평가: `python scripts/evaluate_C3_implementation.py --exports <CSV폴더>`. 기존연구기준에너지±5%,전압RMSE2V/평균편차1V,속도RMSE1km/h,거리0.5%,DC수지1%,발전정지를사용한다. 통과해도최종BEV모델채택으로자동승격하지않는다.
