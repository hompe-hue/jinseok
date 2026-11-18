# 석사학위논문 연구계획서

국문 연구과제  배터리와 발전계 제약을 고려한 가상 직렬형 EREV의 주행성능 유지 경계와 발전 개입 전략 비교

영문 연구과제  Sustained Driving Performance Limits and Comparison of Range Extender Control Strategies in a Virtual Series EREV

## 1. 연구개요

### 연구배경 및 필요성

직렬형 주행거리 연장 전기차(EREV)는 배터리와 발전원이 공통 직류(DC) 버스를 통해 구동모터에 전력을 공급한다. 고속 정속이나 장등판에서 요구전력이 발전원의 지속 공급능력을 넘으면 배터리가 차이를 공급하고 충전상태(SOC)가 낮아진다. 목표 차속을 유지할 수 있는 시간과 주행을 완료하는 데 필요한 SOC 여유는 부하의 크기와 지속시간, 배터리 가용에너지 및 발전 개입 조건에 따라 달라진다.

요구전력 추세에 따른 선제 기동과 구배 정보를 활용한 사전 충전은 선행연구에서 다루어졌다[1–3]. 본 연구에서는 지속 고부하를 중심으로 목표 성능을 유지할 수 있는 범위를 분석하고, 부하가 급변할 때 나타나는 순간 출력 미달도 함께 살펴본다.

### 연구목적 및 범위

배터리의 가용출력과 사용 가능 에너지, 가상 발전원의 순 DC 출력과 응답이 주어졌을 때 고속 정속과 지속 등판의 목표 차속을 유지할 수 있는 조건을 정량화한다. SOC 기준, 현재 휠 파워 반응, SOC 여유 확보, 단기 요구전력 예측을 적용한 전략군(S0~S4)을 동일한 차량 조건에서 비교한다. 발전 개입 전략에 따라 목표 차속 유지 시간, 필요한 초기 SOC 여유, 발전 에너지와 기동 횟수가 얼마나 달라지는지 분석한다.

Chevrolet Bolt EV 시험 자료로 차량 모델의 에너지 소비를 비교하였으며, 가상 발전원의 출력과 보호 동작은 정차 상태에서 확인하였다. 결과는 해당 차량 모델과 발전계 설정을 적용한 시뮬레이션 범위에서 해석한다.

### 기대효과

지속 고부하에서 배터리 여유를 늘리거나 발전 개입 시점을 앞당겼을 때 목표 주행을 유지할 수 있는 범위를 제시한다. 발전용량, 배터리 가용에너지와 제어전략의 효과를 비교하여 초기 설계에서 필요한 공급 여유를 판단하는 근거를 마련한다.

## 2. 연구(실험, 조사) 재료 및 방법

### 차량과 가상 발전원 모델

AVL CRUISE M에 ANL의 2017 Chevrolet Bolt EV 차대동력계 자료, EPA의 2018 Bolt 구동계 손실맵, NREL 공동연구 보고서의 배터리 개방회로 전압과 내부저항 자료를 적용한다[4–6]. 기존 4개 주행 조건에서 배터리 단자 순 DC 소비에너지 상대오차는 +5.98~+8.85%로 검토 기준인 절댓값 15% 이내였다. 도로부하와 구동계 손실의 중복 가능성은 가설로 두고, 원본 모델과 손실 경계 조정 후보를 별도 시험으로 비교한다.

가상 발전원의 기준 순 DC 출력은 26 kW이며 정차 조건에서 지령 추종, 보호 정지, 충전 한계와 재기동을 확인하였다. 발전 용량의 적정성은 평지 고속 정속에서 계산한 SOC 유지 요구전력으로 검토한다. Volt 2세대 공개 도표를 사용한 연료 환산은 근거가 확보된 온간 정상운전 구간에 한정한다[7, 8].

### 지속 고부하와 순간 출력의 평가

정속 등판 등 지속 부하에서 제한 전 DC 요구전력과 발전원의 순 DC 출력 차이를 구한다. 요구전력이 발전 출력보다 큰 정속 구간에서는 하한 SOC까지 배터리 단자에서 쓸 수 있는 에너지를 그 순부족전력으로 나누어 유지 시간을 예측한다. 이를 CRUISE M의 목표 차속 유지 시간과 하한 SOC 도달 시점에 비교하고, 목표 구간을 완주하는 데 필요한 초기 SOC 여유를 산출한다.

30초 계측으로 신호와 단위를 확인한 뒤, 발전원을 끈 상태에서 조건별로 미달이 나타나는 범위를 파악한다. 대표 평가 조건 3종에서 S0~S4를 같은 초기 SOC, 질량 및 부하 조건으로 비교한다. 발전 에너지, 기동 횟수와 종료 SOC를 함께 기록한다. 급가속과 계단 부하에서는 기동 지연과 출력 상승률에 따른 순간 휠 파워 미달을 보조 지표로 확인한다. 발전 용량과 배터리 가용에너지·출력의 가정이 성능 유지 경계에 미치는 영향도 살펴본다.

### 자료 공급수단 및 실험시설 이용방법

ANL·EPA 공개 자료와 관련 문헌으로 입력을 구성한다. AVL CRUISE M이 설치된 전산 환경에서 시뮬레이션을 실행하고, Python으로 주행 로그를 정렬·적분하여 경계식 예측 결과 및 제어전략별 결과를 비교한다.

## 3. 연구(실험, 조사) 진행 예정표

2026년 3~12월 및 2027년 1~2월. ● 완료 단계  ○ 예정 단계. 일정은 연구 진행 및 지도 일정에 따라 조정한다.

| 연구내용 | 3월 | 4월 | 5월 | 6월 | 7월 | 8월 | 9월 | 10월 | 11월 | 12월 | 1월 | 2월 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 선행연구 및 자료 정리 | | | | | | | | ● | ● | | | |
| 차량 모델 및 실측 대조 | | | | | | | | ● | ● | | | |
| 가상 발전원 정차 검증 | | | | | | | | | ● | | | |
| 주행 계측 확인 및 조건 선별 | | | | | | | | | ○ | | | |
| 지속 고부하 경계식 검증 | | | | | | | | | ○ | ○ | | |
| 발전 개입 전략 비교 | | | | | | | | | | ○ | | |
| 손실 경계 및 민감도 검토 | | | | | | | | | | ○ | | |
| 논문 작성 및 지도 반영 | | | | | | | | | | ○ | ○ | |

## 4. 참고문헌

[1] Tamor, M. (2008). Control system for a hybrid electric vehicle to anticipate the need for a mode change. U.S. Patent No. 7,407,026 B2. https://patents.google.com/patent/US7407026B2/en

[2] Lin, W., Zhao, H., Zhang, B., Wang, Y., Xiao, Y., Xu, K., & Zhao, R. (2022). Predictive energy management strategy for range-extended electric vehicles based on ITS information and start–stop optimization with vehicle velocity forecast. Energies, 15(20), 7774. doi:10.3390/en15207774

[3] 김수현. (2026). 도로 구배를 고려한 주행거리 연장형 전기자동차의 가상 시뮬레이션 환경 구축 및 에너지 관리 전략 연구. 단국대학교 대학원 석사학위논문.

[4] Argonne National Laboratory. (연도 미상). Downloadable Dynamometer Database (D³). 2017 Chevrolet Bolt EV 시험 자료, 시험번호 61905054, 61905058, 61905059, 61905060, 61905066. https://www.anl.gov/taps/downloadable-dynamometer-database

[5] U.S. Environmental Protection Agency. (2023). 2018 Chevrolet Bolt 150 kW 400 V FWD EDU – ALPHA Map Package (2023-09-25 배포본). https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-emotor-alpha-maps

[6] Booten, C., Sparn, B., Maguire, J., Balamurugan, S., Duoba, M., Canosa, A., Munk, J., Kuruganti, T., Sun, J., Cui, B., & Dong, J. (2020). Development and evaluation of distributed energy resource device models: Electric vehicles, electric water heaters, and commercial refrigeration systems. NREL/TP-5500-75323. doi:10.2172/1660063

[7] Castellano, A., & Cammalleri, M. (2021). Power losses minimization for optimal operating maps in power-split HEVs: A case study on the Chevrolet Volt. Applied Sciences, 11(17), 7779. doi:10.3390/app11177779

[8] Yadav, R. (2018). Modeling and analysis of energy consumption in Chevrolet Volt Gen II hybrid electric vehicle. Michigan Technological University, Master's thesis. https://digitalcommons.mtu.edu/etdr/633/
