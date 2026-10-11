Bolt 배터리 셀 기준 CRUISE M 입력 파일 — 2026-10-11

이 파일은 NREL 참조식의 초기 모델 입력용이며 실측 방전 검증 완료 맵이 아니다.
사용자가 내보낸 OCV_sample.dat와 ]Resistance_sample.dat의 첫 두 행, 단위,
숫자 2열 및 CRLF 줄바꿈을 그대로 사용했다. 실제 CRUISE M import 실행은 사용자 PC에서 확인해야 한다.

파일 / 적용 위치
- Bolt_Cell_OCV_25C.dat: Module 1, Module 2 각각 Open Circuit Voltage의 25°C 표
  헤더: "State of Charge" Voltage / % V
  SOC는 0~100%; Multiplier=1.
- Bolt_Cell_Resistance_25C.dat: Module 1, Module 2 각각 Ohmic Resistance의 25°C 표
  헤더: "State of Charge" Resistance / [-] Ohm
  SOC는 0~1 분율; Multiplier=1.
  충전/방전 별도 표가 보이면 같은 참조표를 각각 적용하는 것은 초기 대칭 저항 가정이다.
  이는 방전 검증 완료를 뜻하지 않는다. 기존 0.002Ω 표를 대체하고 추가하지 않는다.

설정
두 모듈은 직렬이며 각각 48S3P. 셀 용량 Constant 56Ah => 팩 168Ah.
56Ah는 연구 초기 가정이며 실측 용량 확정값이 아니다.
초기 SOC 두 모듈 각각 60%, 온도 Defined temperature 25°C.
OCV charge and discharge 옵션은 해제(공통 OCV), RC networks는 비움(초기 Rint 모델).
셀 Connection resistance=0. 참조 팩 저항을 셀 표에 모두 배분하므로
별도 Main Connector / Connection 1의 기존 각 0.01Ω도 초기 등가 모델에서 0Ω로 설정한다.
이는 접속 손실이 실제 0이라는 뜻이 아니라 별도 저항을 추가 식별하지 않았다는 모델 가정이다.
0Ω가 Data Checks에서 허용되지 않으면 임의로 작은 값을 넣지 말고 오류 내용을 확인한다.
최소/최대 전압은 이번 파일에서 지정하지 않는다. 실제 BMS 한계는 미확정이다.
현재 템플릿 2.5/5V는 Bolt 보호 한계로 인용하지 않는다.
매뉴얼상 최소/최대 전압은 상태 출력용이며 실제 차단은 제어 로직 확인이 필요하다.

참조식 (s는 SOC %)
U_pack=322.397+1.29836s-0.0184756s²+0.000143235s³ [V]
R_pack=0.0806969-0.000281326s+0.00000166726s² [Ω]
U_cell=U_pack/96; R_cell=R_pack*3/96.
각 표는 1% 간격 101점이며 계수를 변경하거나 끝점을 잘라내지 않았다.
SOC 60%: 셀 OCV=3.79922083333V, 셀 R=0.002181858625Ω.
각 48S3P 모듈 OCV=182.3626V, R=0.034909738Ω.
두 모듈 직렬 팩 무부하 OCV=364.7252V, R=0.069819476Ω.
부하 중 단자전압은 이 OCV와 다르다.

적용 범위와 한계
0~100%는 파일 작성 범위이며 검증된 전 SOC 운전 범위가 아니다.
첫 실행은 초기 60%에서 짧은 사이클의 연결/단위/에너지 계산 점검용이다.
5~95%는 후속 검사 우선 범위이며 NREL 인증 유효 범위가 아니다.
CAN SOC와 표시 SOC/내부 SOC/모델 적산 SOC의 일치가 아직 확정되지 않았다.
25°C는 고정 온도 모델 설정이며 참조식의 전체 온도 유효성 확인이 아니다.
공통 OCV/R, RC 생략 가정은 저 SOC 방전, 최고 SOC, 과도 부하 검증에 충분하지 않다.
U_pack(100%)=410.712V로 가정 한계 403.2V와 충돌한다.
그래서 초기 SOC 100% 및 고갈 주행거리 검증에는 그대로 사용하지 않는다.
보간은 SOC Linear, 표 밖 외삽은 제공되면 Constant로 설정하되
Constant 외삽은 운전 허용/검증 판정이 아니다. 실제 SOC 경계 제어는 별도 점검한다.

출처
NREL/TP-5500-75323 Figure 12, https://www.nrel.gov/docs/fy20osti/75323.pdf
기존 검산 입력: validation_fix_20261006/inputs/battery_reference_with_validity.csv
기존 적용 한계: validation_fix_20261006/README_검증보완.md
AVL 사용자 제공 매뉴얼: Battery (Equivalent Circuit Model), Open Circuit Voltage.
