# CRUISE M Bolt BEV 모델 구축 작업 기록 — 2026-10-11

현재 단계는 **입력자료 연결 및 첫 BEV 실행 준비**이다. 모터 손실맵과 배터리 참조표 import 성공을 화면에서 확인했고, 마지막 `REEV_MBE` 화면의 Data Checks는 `No data check messages`였다. **주행 시뮬레이션 결과 및 실측 대비 검증은 아직 없다.** 사용자가 Windows에서 작업했으며 이 기록은 화면 확인과 입력 안내를 구분한다. 실제 CRUISE M 프로젝트 파일은 전달받지 않아 백업에 포함되지 않았다.

## 연구 범위와 기존 자료

- 중간보고: Bolt BEV를 먼저 구성하여 정의된 시험 조건에서 공개 실험 데이터와 속도·배터리 전압/전류·SOC·에너지 소비를 비교한다. 공식 주행거리는 시험 절차, 온도, 부하, SOC 경계, 사용 가능 에너지 조건이 갖춰진 뒤 비교한다. 이 결과는 해당 모델/조건의 적합성 평가이며 CRUISE M 전체의 신뢰성 인증이 아니다.
- 이후: Bolt 차체/구동계를 유지하고 Volt Gen2 엔진·발전기 자료로 **가상 직렬 EREV**를 설계하여 EMS를 비교한다. 실제 Volt의 복합 동력분기 구조를 그대로 복제하는 모델은 아니다. i3는 대상에서 제외한다.
- 기존 자료: [검증 보완](../validation_fix_20261006/README_검증보완.md), [Bolt + Volt 가상 EREV](../bolt_volt_genset_20261006/README_가상EREV.md), [이전 Range Extender 입력자료](../range_extender_20261006/RESUME.md).
- 이전 65 kW 후보표는 스케일링 기반 예비 계산이다. 6000 rpm 축출력 약 73.26 kW, 발전 토크 −116.59 Nm 정속 후보를 얻었지만 실제 연속 정격이 검증된 것이 아니다. 650 V 원자료를 330 V 링크에 직접 적용하거나 1000 rpm 미만 시동 영역에 사용하는 것도 미해결이다.
- Volt Gen2 후보 제원은 L3A 1.5 L, 75 kW/140 Nm, MGA 48 kW/118 Nm 및 MGB 87 kW/280 Nm이며 기존 출처/가정을 따른다. 발전기 맵은 공개 그림을 재구성한 자료를 포함하고 OEM 원본 실측 맵으로 표시하지 않는다. 약 26 kW 순발전 정속 후보와 65 kW 후보를 혼동하지 않는다.

## 기록 상태의 정의

`확인`은 화면 또는 사용자의 명시적 완료 답변으로 확인한 상태이다. `안내/미확인`은 입력을 안내했으나 최종 화면을 받지 못한 상태이다. `템플릿/가정`은 값이 존재해도 Bolt 실측값으로 확정하지 못한 상태이다. 서로 연결된 `REEV_MBE`/`REEV_PhysE`는 입력이 전파될 수 있지만 두 모델의 모든 옵션이 동일하다고 검증한 것은 아니다.

## 차량·휠·구동계

| 항목 | 값/설정 | 상태와 해석 |
|---|---|---|
| Driving resistance | Function without reference vehicle | 확인; ABC 사용 시 CdA/구름저항 중복 방지 |
| Curb weight | 1625 kg | 사용자 확인 |
| Additional load | 132.6704 kg | 안내/미확인; 이전 화면은 0 |
| 목표 시험 질량 | 1757.6704 kg | 목표값; Gross weight 표시만으로 동역학 질량 반영을 확정하지 않음; 실제 GVWR 아님 |
| Load state / 승객 | Empty / 0 | 확인 |
| ABC | 126.329494 N; 0.557775 N·h/km; 0.033456276 N·h²/km² | 속도 km/h 기준; F(100)=516.669754 N |
| Wheelbase / CG / 전면면적 | 2777 mm / 1100 mm·500 mm / 1.97 m² | 템플릿, Bolt 출처 미확정; Bolt wheelbase 2600 mm 적용 여부 재확인 |
| Vehicle 옵션 | front axle load limited, lifting, cornering, road gradient data bus, PFA, hitch forces 해제; velocity prescription None | 확인 |
| 4개 휠 dynamic rolling radius | 323 mm | 사용자 “네 휠 수정했어” 확인 |
| Static radius | 287 mm | 템플릿; dynamic 값으로 자동 대체하지 않음 |
| 휠 설정 | constant dynamic radius, Slip Deactivated, Rolling Resistance Standard, 속도 의존 해제 | 확인; ABC와 별도 저항의 중복 여부 결과에서 확인 |
| 휠 관성 / friction / 기준하중 | 1.75 kgm² / 1 / 3260 N | 템플릿, load correction 0 |
| Final Drive | ratio 7.05, efficiency 1, speed-dependent torque loss 해제 | 확인; 효율 1은 EDU 맵에 기어손실 포함하기 위한 등가화 가정 |
| Final Drive 관성 | input 0 / output 0.15 kgm² | 템플릿 |
| Differential | Unlocked; loss Deactivated; input/out1/out2 inertia 각 0.15 kgm² | 확인/템플릿; 관성 중복 계산 후속 점검 |
| Torque split factor | 1 | 기존 값 유지; 임의로 0.5로 변경하지 않음 |

## E-Motor: 완성 EDU 손실맵 입력

`Electric motor with inverter`에서 `Electric motor`로 변경했다. PMSM, Global losses map, Torque 입력, Torque 의존, Power loss, Mechanical load 제어, Q1 Motor/Q4 Generator 활성 및 Q2/Q3 비활성을 사용한다. EDU 전체 손실(모터/인버터/기어)이 포함된 맵이므로 별도 인버터/기어 손실을 다시 더하지 않는다. `REEV_PhysE`의 element tree에서 Inverter Power Losses가 이후에도 보였으므로 실제 활성 옵션과 모델 연결 상태는 추가 확인한다.

- 관성 0.04 kgm²는 템플릿이다. 최대속도 8250 rpm은 현재 맵 운용 경계이며 실제 하드웨어 최고속도 확정값이 아니다.
- Layout temperature 25°C는 안내했으나 최종 확인이 없다. 기존 화면은 0°C였다. remanence 온도계수 0을 초기 사용한다.
- 온도 입력 미연결 오류는 Environment ambient temperature → E-Motor Temperature input 연결 후 사라졌다. Environment 기존 표는 20°C였으며 25°C 변경은 안내/미확인이다. humidity 0.65, distance 0의 기존 조건을 사용한다.
- Drag torque 초기 0은 손실 중복을 방지하기 위한 설정이다.

### Full load

400 V에서 아래 Q1 토크를 사용하고 Q4는 음의 대칭값을 사용했다. Q4 대칭 한계는 초기 가정이다. 4441.750762 rpm의 233.484211 오입력을 322.484211 Nm로 양쪽 곡선에서 수정한 것을 확인했다.

| Speed rpm | Q1 Nm | Q4 Nm |
|---:|---:|---:|
| 0 | 360 | -360 |
| 3978.873577 | 360 | -360 |
| 4197.590115 | 341.242105 | -341.242105 |
| 4441.750762 | 322.484211 | -322.484211 |
| 4716.069742 | 303.726316 | -303.726316 |
| 5026.502525 | 284.968421 | -284.968421 |
| 5380.683129 | 266.210526 | -266.210526 |
| 5788.560335 | 247.452632 | -247.452632 |
| 6263.346973 | 228.694737 | -228.694737 |
| 6822.978156 | 209.936842 | -209.936842 |
| 7492.427945 | 191.178947 | -191.178947 |
| 8250 | 173.623574 | -173.623574 |

Linear Voltage/Speed interpolation 확인. Constant extrapolation은 안내/미확인이다. 쌍곡선 토크를 선형 보간하면 중간점에서 150 kW를 약간 초과할 수 있으므로 제어에서 |T|≤360 Nm, |Pshaft|≤150 kW, n≤8250 rpm 제한을 확인/구현해야 한다. 효율/손실표의 Full load 바깥 값을 운전 가능점으로 사용하지 않는다.

### Import 실패와 해결

헤더 없는 TAB DAT는 `Invalid number value ... line 1`로 실패했다. 사용자 export `AVL_sample.dat`에서 AVL regular map 문법과 축 배치를 확인하여 다시 작성했다. **작동 파일은 [Bolt_EDU_Loss_400V_AVL_RegularMap.dat](inputs/Bolt_EDU_Loss_400V_AVL_RegularMap.dat)** 및 [ZIP](inputs/Bolt_EDU_AVL_RegularMap_Import.zip)이다. 기존 `Bolt_EDU_Loss_400V_rad_s_W.dat`는 실패한 형식이므로 재사용하지 않는다.

- All Quadrants import 조건: Temperature **298.15 K**, Voltage **400 V**, speed **rad/s**, torque **Nm**, loss **W**. 상위 표에서 25°C/rpm/kW로 표시될 수 있다. 양쪽 단위를 혼동하지 않는다.
- DAT `# dimensions`, `moment~Nm`, `ang_vel~rad_s`, `power~W`; 저장 배열은 torque rows × speed columns이다. 17×17 표이며 원래 12속도×17토크 204점을 모두 유지하고 최초 5개 속도 간격의 중간값을 선형 보간해 85점 추가, 총 289점이다. 추가 노드는 외삽이 아니다.
- 원자료 끝점 8251 rpm은 보존하고 실제 운용을 8250 rpm으로 제한한다. import 후 부모 표에서는 0속도 음토크 8점이 제외되어 281점(Q1 153/Q4 128)으로 나타나는 것을 기준으로 점검한다.
- 084832 화면에서 0 rad/s, −363.1 Nm의 loss 11855.100013 W와 500 rpm=52.359878 rad/s 등을 확인하여 import 성공을 판단했다.
- 출처/한계: 원측정 252점으로부터 완성 표를 만들었으며 회생 영역은 EPA 추정(손실 1.05 배)이다. 204 원표 중 운용 경계 내 151점은 실측점 볼록껍질 안의 완성맵 63점, 볼록껍질 밖의 구동 완성맵 18점, 회생 추정 70점이다. 볼록껍질 안 63점도 직접 실측 격자점이라는 뜻은 아니다. 전체 204점의 분류는 각각 64/44/96점이다. 2026-10-11 재검토에서 이전 요약의 분류 오류를 정정했다. 400 V 단일 전압 자료와 25°C 초기 가정을 다른 조건의 실측 맵으로 확대하지 않는다. 자세한 플래그는 기존 검증 보완 자료 및 첨부 source tables를 따른다.

## 배터리 등가 Rint 모델

내부 연결은 `Main Connector → Module 1 → Connection 1 → Module 2` 직렬이며 전압계는 팩 양단, 전류계는 양극 직렬이다. 각 모듈에 같은 셀 OCV와 저항표를 적용한다.

| 항목 | 목표/현재 | 확인 상태 |
|---|---|---|
| 각 모듈 구성 | 48S3P → 총 96S3P | Module 1 화면 확인; Module 2 기본 설정 최종 확인 필요 |
| Cell capacity | Constant 56 Ah → pack 168 Ah | 안내/미확인; 실측 용량 확정값 아님 |
| Initial SOC | 각 60% | Module 1 확인; Module 2 재확인 |
| Defined temperature | 25°C | 두 모듈 화면 관찰 |
| Cell connection resistance | 0 | 기존 화면 관찰 |
| Main Connector / Connection 1 R | 각 0 Ω | 기존 각 0.01 Ω를 0으로 변경 안내/미확인; 참조 팩 R 중복 방지 가정 |
| Cell min/max voltage | 기존 2.5 / 5 V | 템플릿; 실제 Bolt BMS 한계 아님; 매뉴얼상 상태 출력이며 자동 차단을 보장하지 않음 |
| RC network | 비움 | 초기 Rint 가정 |
| 옵션 | Current dependent R, Coulomb efficiency, OCV charge/discharge 분리, reversible heat 해제 | 초기 화면 기준, 후속 점검 |
| Multiplier | OCV/R 각 1 | 관찰한 표에서 확인 |

사용자 export 헤더에 맞춘 두 파일과 설명서/ZIP을 `inputs/battery/`에 보관했다. OCV SOC는 **0~100 %**, Resistance SOC는 **0~1 [-]**이다. 온도 각 25°C, SOC 1% 간격 101점, CRLF. 충전/방전 저항에 같은 파일을 쓰는 것은 대칭 저항 가정이다.

- `091326`: Module 2 OCV import 확인(0%=3.358302 V 등).
- `091332`: Module 2 Charge R import 확인(0.01=0.002513 Ω 등).
- `091503`: Module 1 Discharge R import 확인.
- `091641`: Module 1 OCV import, Linear SOC/temperature interpolation, Constant extrapolation 확인.
- **Module 1 Charge R / Module 2 Discharge R**, 나머지 표의 interpolation/extrapolation은 입력 안내했으나 최종 화면 확인이 없다. 다음 세션에서 대조한다.

참조식: NREL/TP-5500-75323 Figure 12, https://www.nrel.gov/docs/fy20osti/75323.pdf . s=SOC[%].

```
U_pack = 322.397 + 1.29836*s - 0.0184756*s² + 0.000143235*s³ [V]
R_pack = 0.0806969 - 0.000281326*s + 0.00000166726*s² [ohm]
U_cell = U_pack/96
R_cell = R_pack*3/96
```

SOC 60%에서 Ucell=3.799220833333 V, Rcell=0.002181858625 Ω; 각 모듈 182.3626 V/0.034909738 Ω; 팩 무부하 OCV **364.7252 V**, R **0.069819476 Ω**이다. 부하 단자전압과 OCV는 구분한다.

파일 생성 범위 0~100%는 실험 검증 범위가 아니다. 5~95%는 후속 검사 우선 범위이다. CAN 참조 SOC와 표시 SOC, 내부 SOC, 모델 적산 SOC의 정의 대응이 미완료이며 25°C는 등온 모델 가정이다. 100% 식 값 410.712 V는 가정 상한 403.2 V와 충돌한다. 수학적 교점 약 95.828%를 실제 BMS 한계로 채택하지 않는다. 초기 60% 짧은 사이클부터 확인하며 완전 충전/고갈 주행거리 검증은 뒤로 둔다.

기존 오프라인 검사에서는 ANL 61905065 충전 표시 SOC 5~95% RMSE 1.839 V, 61905064 방전 약 5~80.77% RMSE 7.413 V, HPCM2 약 5~79.97% RMSE 10.025 V 및 저 SOC 5~10% RMSE 21.30 V, 61905054 고 SOC 98~99.985% RMSE 13.829 V였다. 이는 CRUISE M 검증 완료가 아니며 저 SOC/고 SOC에 제한이 있음을 보여준다. 충전 기반 참조를 방전 검증 완료라고 표시하지 않는다.

## 마지막 화면과 Range Extender

`091652`의 활성 `REEV_MBE` 화면에서 HV bus에 Range Extender, HV Battery, Power Consumer, E-Motor가 연결되어 있다. Data Checks는 녹색 `No data check messages`였다. Range Extender가 연결된 상태이므로 BEV 비교를 하기 전에 발전 정지 제어와 정지 시 소비/손실을 확인해야 한다.

마지막 6장 `091739/091751/091756/091801/091808/091813`는 **Range Extender 내부 ICE 설정**이었다. `Range Extender Control` 화면이 아니다. 엔진은 Map based/Torque controlled, gasoline.bgp(LHV 43500 kJ/kg, density 748 kg/m³), mass flow kg/s 표를 사용하고 있었다. full load 약 266 Nm와 최소 BSFC 약 161.4 g/kWh 등의 기존 템플릿 곡선은 선택한 Volt 맵으로 확인되지 않았다. Motoring torque(0 rpm −5 Nm), aspiration delay 0.1 s 등도 템플릿이다. **이번 세션에서 엔진/발전기 맵을 Volt 자료로 교체했다고 기록하지 않는다.**

## 다음 세션: 여기서 재개

1. Windows의 현재 CRUISE M 프로젝트를 저장하고 BEV 기준용 사본을 만든다. 이 GitHub 기록에는 원본 프로젝트 파일이 없으므로 별도 보관한다.
2. 내부 ICE 창을 닫고 메인 화면의 `Range Extender Control`(Range Extender Monitor 옆) Parameters를 확인한다. 첫 BEV 실행에는 발전 출력 0, 엔진 start/fuel 0을 보장하고 결과에서도 확인한다. 엔진 맵을 0으로 덮어쓰는 방식으로 비활성화하지 않는다.
3. Battery와 E-Motor 사이의 `Power Consumer` 설정을 확인하고 공개 실험과 맞는 보조부하 조건을 정의한다. 수치를 아직 확정하지 않았다.
4. 안내/미확인 설정을 확인: 추가 질량, 두 모듈 48S3P/56Ah/60%, 두 커넥터 R, 6개 배터리 표, Environment/Layout 온도, 연결된 모델의 인버터 손실/외삽 설정.
5. 제어의 회생/모터 토크·150 kW·8250 rpm 한계와 Full load 경계를 확인한다. 첫 평지/등온 25°C/초기60% 짧은 사이클을 정의한다.
6. Data Checks 후 첫 실행. target/actual speed, distance, shaft speed/torque/power, battery voltage/current/SOC/DC energy, auxiliary power, Range Extender DC power와 fuel을 export한다. 시간 정렬, 전류·토크 부호, Wh/kWh 및 에너지 수지부터 점검한다.
7. 동일 조건 ANL trace와 비교하고 차이를 기록한다. 단일 연비/주행거리 숫자에 맞추기 위해 SOC 경계와 모터 손실을 함께 조정하고 이를 독립 검증이라고 부르지 않는다. 연료소비·총 주행거리/EMS 확장은 연료맵, 발전 한계, SOC 경계와 비교 조건을 갖춘 뒤 진행한다.

## 파일과 검산

`inputs/`: 실제 작동한 motor regular map, import ZIP, battery DAT/ZIP, 원본 export 문법 sample, 모터 원표 및 출처 플래그. `evidence/`: 주요 import/Data Checks 원본 화면과 전체 화면 파일명/SHA256 인덱스. 인덱스에 있는 모든 화면이 저장소에 첨부된 것은 아니며 저장된 화면은 별도 표시한다. `scripts/verify_inputs.py`: 헤더/차원/단위/원점 보존/배터리 참조식/ZIP byte一致 검사. 이 검사는 파일 검산이며 CRUISE M 실행을 대체하지 않는다.

과거 GitHub 자동 승인 거절은 이전 시도 기록이며 현재 권한 차단으로 간주하지 않는다. 2026-10-06 동기화 완료 이후 이 세션의 기록은 새 커밋으로 보관한다. 별도 기록 제외를 요청한 방법론 상담 대화는 옮기지 않았다.
