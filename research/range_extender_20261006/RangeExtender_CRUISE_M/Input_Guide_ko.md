# CRUISE M Range Extender 입력자료와 적용 범위

작성일: 2026-10-06. 사용자 제공 이미지 1~5에 대응하는 수치 입력표이다. CRUISE M에서 직접 import하거나 모델을 실행하지는 않았다. 열 이름과 단위의 대응 및 수치 계산을 검증했다.

## 1. 사용할 표 선택

| 자료군 | 엔진 | 발전기 | 사용 범위 |
|---|---|---|---|
| REF 공개 기준표 | EPA Mazda 1.998 L 자연흡기 완성맵 | EPA Prius MG1 EST 또는 MG2, 60 kW 축출력 모델·650 V | 공개 수치 맵의 재현·입력 형식 확인. 사용자 목표인 실제 1.5 L·순발전 65 kW 자료는 아니다. |
| A 가상 후보표 | Mazda NA 맵을 1.5 L로 배기량 비례 축소하고 최대 축출력 80 kW로 제한 | EPA MG1 EST를 토크·전력 80/60배 확대, 효율 유지, 650 V 유지 | 설계 가정에 따른 예비 시뮬레이션용 초안. 실측·제품 검증·연속 정격 인증 자료가 아니다. 기존 모델에는 적용하지 않았다. |

자료를 단순한 정격 제원에서 만든 일정 효율표로 대체하지 않았다. 원본 맵의 전기입력/출력·축출력 관계에서 효율을 계산했다. 다만 EPA 완성맵 자체도 보간·외삽·추정을 포함한다. 특히 MG1 EST 전체가 MG2 자료를 이용한 추정 모델이고, MG1 원본에는 음의 토크 Full load 표가 없어 이번 Q4 곡선은 양의 곡선을 대칭 복사한 추가 가정이다. MG2에는 원본 음의 토크 곡선이 있다. 따라서 MG1 자료군의 REF 표기도 모든 값이 직접 실측이라는 뜻은 아니다.

## 2. 화면별 입력표

| 화면 | 필요한 데이터 | A 가상 후보 CSV | 공개 기준 CSV |
|---|---|---|---|
| 이미지1 Engine Program의 Full load 하위표 | 회전수 rpm, 브레이크 토크 N·m | A_Engine15NA80_FullLoad.csv | REF_Engine20NA_FullLoad.csv |
| 이미지1 Engine Program의 Fuel consumption 하위표 | 회전수 rpm, 토크 N·m, 연료 질량유량 | A_Engine15NA80_Fuel_g_s.csv 또는 Fuel_kg_h.csv | REF_Engine20NA_Fuel_g_s.csv 또는 Fuel_kg_h.csv |
| 이미지2 Engine Data | 배기량, 관성, 속도 한계 등 | Scalars 시트의 A 값 | Scalars 시트의 REF 값 |
| 이미지3 Generator 설정 | 사분면·효율 기준·관성·속도 제한 | Scalars 시트 | Scalars 시트 |
| 이미지4 Full Load | Voltage(V), Speed(rpm), Torque(N·m) | A_Gen80_MG1EST_FullLoad_Q1Q4.csv | REF_MG1_EST_FullLoad_Q1Q4.csv 또는 REF_MG2_FullLoad_Q1Q4.csv |
| 이미지5 Efficiency | Temperature(°C), Voltage(V), Speed(rpm), Torque(N·m), Efficiency(%) | A_Gen80_MG1EST_Efficiency_Q1Q4.csv | REF_MG1_EST_Efficiency_Q1Q4.csv 또는 REF_MG2_Efficiency_Q1Q4.csv |

Q1, Q4를 따로 입력하는 편집 방식이면 각 _Q1.csv / _Q4.csv를 사용한다. Excel INDEX 시트에서 CSV 파일명과 해당 시트를 찾을 수 있다. 표의 숫자 영역을 화면의 대응 열에 입력한다. 설치된 CRUISE M의 CSV import 지원 여부와 메뉴는 확인하지 않았으므로 자동 import 파일이라고 단정하지 않는다. 이미지에 보이지 않는 엔진 Program 하위표의 정확한 열 순서·질량유량 단위는 편집창에서 확인해야 한다. 행렬형 연료표도 함께 제공했다.

엔진 연료표는 kg/h = 3.6 × g/s이다. 질량유량을 요구하는 곳에 BSFC(g/kWh)를 그대로 넣으면 안 된다. 발전기 효율은 92.878이라는 숫자가 92.878%를 뜻한다. 0.92878을 넣으면 안 된다. Full load의 Q4 토크는 음수이고 회전수는 양수다. 두 사분면의 효율값은 모두 양수다.

## 3. 권장 입력값의 출처와 한계

| 화면 항목 | 공개 기준 또는 가상 후보의 값 | 근거·처리 |
|---|---|---|
| Engine type | Reciprocating 4 stroke | 이미지의 항목 유지 |
| Transient model | Naturally aspirated | NA 맵 사용. 시간응답은 별도 검증이 필요 |
| Control mode | Torque controlled | 엔진 회전수 조절을 위한 발전기 부하/상위제어 필요 |
| Engine displacement | REF 1.998 L / A 1.5 L | REF는 EPA 원본, A는 목표 배기량 가정 |
| Number of cylinders | 4 | REF 원본 4, A도 4로 가정 |
| Engine inertia | 0.134 kg·m², 임시 | 사용자 화면 값. 목표 엔진 실측값이 아니다 |
| Inertia of auxiliaries | 0 kg·m², 임시 | 화면 값. 커플링·플라이휠을 포함하는지 확인 |
| Stall speed | 500 rpm, 임시 | 화면 값. 목표 엔진 검증값이 아니다 |
| Maximum engine speed | 6875 rpm | REF WOT의 끝점; A도 그대로 사용한 가정. 끝점 토크는 0 |
| Delta static friction | 0.1 N·m, 임시 | 화면 값. 실제 목표 데이터가 없음 |
| Fuel lower heat | 41835 kJ/kg | 해당 Mazda LEV III 맵의 FTAG24350 연료. 다른 연료를 쓰면 소비량 해석 재검토 |
| Fuel density | 750.2 kg/m³, 15°C | 같은 FTAG24350 연료 |
| Specific carbon content | 0.826 | 같은 연료의 탄소 질량분율 |
| Friction model | 일단 별도 추가하지 않음 | 연료표는 브레이크 토크 기준. 추가 마찰을 중복 계산하지 않도록 실제 컴포넌트 정의 확인 |
| Generator type | 원자료는 IPM/PMSM 계열 | 현재 Asynchronous motor와 종류가 다름. 설치 버전에서 해당 동기기 옵션 선택 |
| Characteristics / Losses depending on | Torque / Torque | 이미지의 방식에 맞춘 rpm–Nm 표 |
| Losses | Efficiency | % 표 제공. 정지·무부하 손실은 별도 손실표가 더 적합 |
| Control mode | Mechanical load | 이미지의 방식과 대응 |
| Quadrants | Q1, Q4 | Q1 시동·모터링 / Q4 발전. Q2·Q3 역회전은 제공하지 않음 |
| Generator inertia | REF MG1 0.00562277135625 / MG2 0.010773667 kg·m² | EPA 모델 파라미터. A 80 kW로 단순 비례 확대하지 않음; A는 화면의 0.05를 임시 사용 |
| Maximum generator speed | 13000 rpm을 데이터 사용 한계로 설정 | 원본 속도 한계 13500 rpm이지만 효율 수치 격자는 13000 rpm까지 |
| Global losses map | 전기기+인버터의 합산 손실로 사용 | EPA EMOT 경계에는 인버터가 포함되고 기어는 제외됨. 모델 블록 경계와 일치시키고 인버터 손실을 중복 추가하지 않음 |

화면의 330 V를 원자료의 650 V 대신 적는 것은 유효한 전압 변환이 아니다. 이 표는 650 V 발전측 DC 링크와 별도 DC/DC 변환기가 있는 가상 토폴로지에 대응한다. 배터리측은 실제 Vbus에 따라 동작한다. 변환기 효율 97%와 발전계 보조소비 1 kW는 A 계산에서만 사용한 가정이다. 전압·전류 정격, 양방향 시동 가능 여부, 배터리 전압 범위와 변환기 냉각은 아직 검증하지 않았다. 330 V에 직접 연결할 실제 발전기 맵을 확보한 것으로 표현하면 안 된다.

Temperature = 0°C는 화면 형식을 맞추기 위한 단일 온도 좌표이며 0°C 시험자료가 아니다. EPA 수치 맵에 온도 축이 없기 때문에 실제 온도별 성능·냉각·열 디레이팅은 계산할 수 없다. 단일 좌표 표가 모든 온도에서 자동 적용되는지도 CRUISE M에서 확인해야 한다.

## 4. Full load와 효율을 함께 사용해야 하는 이유

전기동력 원본 격자에는 Full load 밖의 확장점도 포함된다. 입력용 효율표는 직사각형 맵을 유지하려고 이 값을 보존했다. AllowedMask.csv의 inside_FullLoad=0인 점은 운전 가능한 점이 아니다. 실제 명령 토크는 Full load, 축출력 상한, 효율 격자의 사용 범위를 모두 만족하도록 제한한다. 원본 60 kW 맵에서 Full load 밖의 효율점으로 65 kW를 계산하는 것은 허용하지 않는다.

원자료의 부호는 Pshaft = ωT, PDC = Pshaft + Ploss이다. Q1에서는 η = Pshaft/PDC이고, Q4에서는 η = |PDC|/|Pshaft|이다. 발전 효율을 모터 효율과 무조건 같게 복사하지 않았다. 음의 회전수는 기존 검증에서 부호 해석이 불명확한 부분이 있어 제외했다.

0 rpm 또는 0 N·m에서는 효율비가 정의되지 않거나 무부하 손실을 제대로 표현하지 못한다. 그래서 효율표는 1000~13000 rpm 및 0이 아닌 토크 격자만 포함한다. 저속·정지·시동에 대해 확인되지 않은 효율을 채워 넣지 않았다. _PowerLoss_W_ALTERNATIVE.csv에는 0 rpm과 0 N·m를 포함한 W 단위 손실표를 보존했다. 그 표를 쓰려면 해당 버전의 손실 기반 입력 옵션과 단위를 확인해야 하며, 현재 Efficiency 편집창에 W 값을 그대로 붙여넣으면 안 된다.

시동부터 동작하는 모델에는 별도 저속/정지 손실 처리 또는 손실 기반 지도가 필요하다. Q1의 낮은 회전수 구간이 단순히 외삽되지 않도록 한다. 시동 에너지와 시동 연료, 최소 회전수, 시간 지연, 상승률, cold-start 보정은 이 파일에서 실측으로 확보하지 않았다. 정지 상태에서는 연료 OFF 제어가 필요하고, 아이들 상태에서 0 토크라는 이유로 연료를 0으로 만들어서는 안 된다. 원본 negative-torque 연료영역의 fuel-cut 처리와 화면 Fuel shut off 옵션도 엔진 Program 정의와 함께 검토해야 한다.

## 5. 순발전 65 kW 가상 후보 계산

가상 엔진 배기량 스케일 k = 1.5/1.998 = 0.75075075이다. T15(n) = min(k·T20(n), 80000/ω), q15(n,T) = k·q20(n,T/k)로 만들었다. 이는 동일 회전수·BMEP에서 토크와 연료를 배기량 비례로 가정한 것이며 실제 1.5 L NA의 연비 맵이 아니다. 80 kW 상한을 WOT에 넣었고 제어기에도 80 kW 상한을 적용해야 한다. 촘촘한 WOT 보간만으로 모든 중간 회전수의 출력을 완벽하게 제한할 수는 없다.

가상 발전기는 MG1 EST의 토크 축·Full load·기계전력·전기전력·손실을 80/60 = 1.33333333배 확대하고 회전수와 효율은 유지한 모델이다. 이 스케일링은 EMRAX 또는 Honda 제품의 실측 맵을 뜻하지 않는다. 80 kW는 가상 기계의 축출력 제한이고 65 kW는 DC/DC 및 발전계 보조소비 이후 배터리측 순출력 제한이다. 두 값을 동일한 정격으로 취급하지 않는다.

배터리측 Pnet = Pshaft × ηgen+inv × 0.97 − 1 kW로 계산했다. 기어비 1:1, 기어효율 100%, warm 상태, 정속을 가정했다. CSV로 내보낸 효율의 bilinear 보간을 사용했고 엔진·발전기 양쪽의 Full load 안에서 토크를 풀었다. 원본 전력 격자 자체를 보간하는 것과 효율 격자를 보간하는 것은 다르므로 입력 방식에 맞춰 후자를 적용했다.

| 가상 모델 회전수 | 엔진 최대토크 | 양쪽 한계 내 최대 순출력 | 순발전 65 kW 도달 |
|---|---|---|---|
| 3000 rpm | 148.383 N·m | 39.579 kW | 불가 |
| 4000 rpm | 149.071 N·m | 55.195 kW | 불가 |
| 4500 rpm | 148.947 N·m | 62.188 kW | 불가 |
| 4750 rpm | 147.146 N·m | 64.946 kW | 불가 |
| 5000 rpm | 145.344 N·m | 67.625 kW | 가능, 이 가상 정속 계산에 한정 |
| 6000 rpm | 127.324 N·m | 70.906 kW | 가능, 이 가상 정속 계산에 한정 |

6000 rpm, 순발전 65 kW 계산점: 엔진 +116.595 N·m, 발전기 −116.595 N·m, 엔진 축출력 73.259 kW, 발전기+인버터 효율 92.878%, 변환기 전단 DC 68.041 kW, 97% 변환 후 보조소비 1 kW를 차감하여 65 kW. 같은 점의 가상 연료량은 6.075721 g/s = 21.872595 kg/h, BSFC 약 298.567 g/kWh이다. 이 연료량은 가정으로 확대한 Mazda 맵의 계산값이며 실제 Honda 1.5 L의 소비량·최대효율을 주장하지 않는다.

이 결과는 “80 kW 최대출력의 1.5 L NA 엔진이면 저회전에서도 65 kW를 낼 수 있다”는 주장을 뒷받침하지 않는다. 여기서는 5000 rpm 이상에서만 일부 계산점이 성립한다. 연속 73 kW급 엔진 운전과 발전기·인버터·변환기의 열 정격은 제조사 자료 또는 시험으로 추가 확인해야 한다. 차량 운행 중 가속 응답, 출력 안정성, 연속 정격은 검증하지 않았다.

## 6. 출처와 원본 다운로드

EPA 엔진 완성맵 목록: https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-engine-alpha-maps

EPA 전기기 완성맵 목록: https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-emotor-alpha-maps

Mazda 다운로드: https://www.epa.gov/sites/default/files/2018-04/2014-mazda-2.0l-skyactiv-engine-tier-2-fuel-alpha-map-package-03-29-18.zip

주의: 위 링크명은 Tier2이지만 실제 내부 m-file과 연료자료는 2014 Mazda 2.0 L LEV III이다. 실제 내부 원본명·연료 성상을 따라 표를 만들었다. 이름을 Tier2로 조용히 바꾸지 않았다.

MG1 EST 다운로드: https://www.epa.gov/system/files/other-files/2023-09/est-2010-toyota-prius-60kw-650v-mg1-emot-alpha-map-package-dated-09-18-23.zip

MG2 다운로드: https://www.epa.gov/system/files/other-files/2023-04/2010-Toyota-Prius-60kW-650V-MG2-EMOT-ALPHA-Map-Package-Dated-04-06-23.zip

ORNL 2013 공개발표: https://www.energy.gov/sites/prod/files/2014/03/f13/ape006_burress_2013_o.pdf

ORNL 발표 11~12쪽에는 Leaf 80 kW 모터의 375 V, 냉각수 65°C 시험조건과 7000 rpm에서의 연속 운전 자료가 있다. 이것은 80 kW급 전기기 연속 운전의 보조 근거이지, 이번 후보 발전기 Q4 전체 맵이나 65 kW 순발전 연속 정격의 인증 자료가 아니다. 이번 입력표로 혼합하지 않았다.

인용 권장: EPA 2014 Mazda 2.0L SKYACTIV Engine LEV III Fuel, Version2018-02; EPA EST2010 Toyota Prius60kW650V MG1 EMOT, Version2023-09; EPA2010 Toyota Prius60kW650V MG2 EMOT, Version2023-04. 실제 원본 m-file의 suggested citation을 참고한다.

## 7. 검증 및 다음 적용 단계

확인 완료: 원본 해시, 축·배열 크기, 토크·출력 부호, 효율 0~100%, 엔진 연료의 g/s↔kg/h 변환, 가상 65 kW 계산점의 두 Full load 한계와 전력 수지. Excel/CSV의 숫자와 열 형식을 확인했다.

미완료: CRUISE M GUI import, 프로그램 실행, 엔진 Program 상세 열·단위 확인, 실제 1.5 L NA 80 kW 연료/WOT 실측, 실제 65 kW 순발전 연속 시험, 330 V 직접구동 맵, 실제 온도별 효율/디레이팅, 저속 시동 검증과 실제 관성·동특성. 가상 후보를 기존 모델의 확정값으로 바꾸지 않았다. 사용자가 후보 설계 가정을 채택하는 경우 별도 모델 사본에서 정속점·시동·전력수지를 검증한 뒤 제어 비교에 사용한다.
