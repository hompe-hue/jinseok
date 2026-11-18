# 석사학위논문 연구계획서

국문 연구과제  발전기 기동 지연을 고려한 직렬형 EREV의 구동 출력 미달 분석

영문 연구과제  Analysis of Traction Power Shortfall in a Series Range-Extended Electric Vehicle Considering Generator Start-Up Delay

## 1. 연구개요

### 연구배경 및 필요성

직렬형 주행거리 연장 전기자동차(Extended-Range Electric Vehicle, EREV)는 배터리와 엔진·발전기가 공통 직류(DC) 버스에 전력을 공급하고, 구동모터가 차량을 구동한다. 급가속이나 등판 등으로 요구출력이 급증하면 배터리 가용출력만으로 이를 충족하기 어려울 수 있다. 이때 발전기를 기동해도 지령부터 발전 시작까지 시간이 걸리고 이후 출력이 점진적으로 상승하므로, 구동축에서 일시적으로 요구출력에 못 미칠 수 있다.

요구출력의 변화율과 기동시간을 이용한 선제 기동, 주행정보를 이용한 발전기 운전 제어는 선행연구에서 다루어졌다[1–3]. 직렬형 EREV에서 선제 기동의 효과를 판단하려면 배터리의 순간 공급 여유, 발전기의 응답, 구동모터의 출력 제약을 같은 주행 사건에서 비교해야 한다.

### 연구목적 및 범위

본 연구의 목적은 가상 직렬형 EREV에서 발전기 선제 기동이 구동 출력 미달을 줄이는 조건과 그 한계를 정량화하는 데 있다. 배터리 충전상태(SOC) 기준 제어, 현재 요구출력에 반응하는 제어, 단기 요구전력 예측을 이용한 선제 기동 제어를 동일한 차량 및 주행 조건에서 비교한다. 배터리만으로 요구를 충족하는 조건, 발전기 응답에 따라 미달을 줄일 수 있는 조건, 가용 출력을 합해도 요구를 충족하기 어려운 조건을 구분한다.

Chevrolet Bolt EV 공개 차대동력계 계측자료로 차량 모델의 배터리 단자 순 DC 소비에너지를 검토하였고, 가상 발전계는 정차 상태에서 지령에 따른 출력과 제약 동작을 확인하였다. 연구 결과는 설정한 배터리·발전계와 시뮬레이션 검증 범위에서 해석한다.

### 기대효과

출력 미달 시간·에너지와 차속 추종 결과를 기동 횟수 및 배터리 사용량과 함께 제시한다. 이를 바탕으로 선제 기동이 필요한 조건과 발전용량 또는 구동계 한계가 지배적인 조건을 구분해, 초기 EREV 설계 단계의 제어전략 검토에 활용할 수 있는 판단 근거를 마련한다.

## 2. 연구(실험, 조사) 재료 및 방법

### 연구 재료와 차량 모델

차량 모델은 AVL CRUISE M에서 구축한다. Argonne National Laboratory의 2017 Chevrolet Bolt EV 차대동력계 시험에서 주행속도와 배터리 단자 전압·전류·전력을 사용한다[4]. 미 환경보호청(EPA)의 2018 Bolt EV용 구동계 손실맵과 NREL 공동연구 보고서의 배터리 개방회로 전압 및 내부저항 자료를 적용한다[5, 6]. 보조부하 0.40 kW는 별도 Bolt EV 시험의 저전압 계측 출력과 정지 구간 전력비를 이용해 환산한 등가값이다. 기존 4개 주행 조건에서 배터리 단자 순 DC 소비에너지 상대오차는 +5.98~+8.85%로 검토 기준인 절댓값 15% 이내였다.

### 발전계 구성 및 단품 검증

공통 DC 버스에 연구용 순 DC 정격 26 kW의 발전기 모델을 연결한다. 기동 지연 0.5초와 초기 출력 상승률 20 kW/s를 기본 설정으로 적용한다. 정차 조건에서 발전 지령 추종, 보호 정지, 배터리 충전 한계 및 재기동 동작을 점검하였다. Chevrolet Volt 2세대의 엔진 효율과 전기기계·인버터 공개 도표를 수치화하여 운전점과 온간 정상상태 효율의 근거로 활용한다[7, 8]. 시동·과도·냉간 등 자료가 부족한 구간은 연료량 산정에서 별도로 표시한다.

### 주행 실험과 분석 방법

30초 예비 실행에서 제한 전 구동 요구, 배터리 가용전력, 발전기 단자출력 및 휠 토크·회전속도의 시간축과 단위를 확인한다. 대표 주행 조건 3개를 선정해 SOC 기준, 현재 요구출력 반응, 단기 예측과 SOC 예비 여유의 조합으로 구성한 5개 제어전략을 비교한다. 각 비교에는 같은 초기 SOC, 차량 제원, 출력 제한 및 주행 프로파일을 적용한다. 단기 예측에는 현재와 과거 신호를 사용한다.

요구 휠출력과 실제 휠출력의 양의 차이로 미달 시간과 미달 에너지를 산출하고, DC 버스 전력수지와 모터 제한 신호로 원인을 구분한다. 목표 차속 추종오차, 발전에너지, 기동 횟수 및 종료 SOC도 함께 비교한다. 휠 출력 신호가 확보되는 범위에서 휠 지표를 평가하며, 전력수지 결과는 DC 버스 경계에서 별도로 보고한다.

### 자료 공급수단 및 실험시설 이용방법

차대동력계 계측자료와 구동계·배터리·발전계 문헌은 ANL, EPA, 연구기관 및 학술 출처에서 확보한다. 사용 자료의 출처, 시험조건과 도표 수치화 절차를 기록한다. 시뮬레이션은 AVL CRUISE M이 설치된 전산 환경에서 수행하고, 출력 로그는 Python으로 시간축을 정렬하여 적분·비교한다.

## 3. 연구(실험, 조사) 진행 예정표

2026년 3~12월 및 2027년 1~2월. ● 완료 단계  ○ 예정 단계. 일정은 연구 진행 및 지도 일정에 따라 조정한다.

| 연구내용 | 3월 | 4월 | 5월 | 6월 | 7월 | 8월 | 9월 | 10월 | 11월 | 12월 | 1월 | 2월 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 선행연구 및 자료 정리 | | | | | | | | ● | ● | | | |
| 차량 모델 및 실측 대조 | | | | | | | | ● | ● | | | |
| 가상 발전계 정차 검증 | | | | | | | | | ● | | | |
| 주행 신호 확인 및 미션 선정 | | | | | | | | | ○ | | | |
| 주행 제어전략 비교 | | | | | | | | | ○ | ○ | | |
| 결과 및 적용 한계 분석 | | | | | | | | | | ○ | | |
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
