# EREV Fuel Evidence B03 COMPLETE — 2026-11-10

B01:9f4a4309 B02:1b11a664
Newly secured Yadav2018 public faculty PDF: BSFC Fig4.9; MGA406V Fig3.14; TPIM-A406V Fig3.16; startup/transient evidence. OEM raw grids not acquired. Existing candidate maps and PROJ/FMU unchanged. No actual CRUISE execution.

Persistent files:
Report libfile_dcdecd49140c8191af2c1a0559446d6d
Source PDFs libfile_fff7c78f2f0481919d6357a34d883c70 SHA256 2b29fdf39a0f934e47a56149ec9d4e270b23877f442ebe2c8fc76c3be606e54e
Data libfile_6d7ffba47188819199be23ce7f4e22a9 SHA256 9e474550493357004f3a005919d763c2c29f307bfa9f71770059866125df4990

# Volt Gen2 발전원: 연료맵·효율·26 kW 운전점 근거 확보

2026-11-10 | 기존 Bolt EV 기반 가상 직렬 EREV 연구의 입력 근거 보강

## 1. 확보 결과

**공개 원문과 도표 수준의 근거는 확보했다. OEM 원시 연료·발전·인버터 수치 배열을 확보한 상태는 아니다.** 이번에는 기존 프로젝트와 맵을 바꾸지 않았다. 실행 중인 요청형 DC FMU에도 연료모델을 설치하지 않았다.

가장 중요한 추가 자료는 지도교수의 대학 공개 서버에서 내려받은 **Yadav(2018) 학위논문**이다. 저장소의 서지 분류는 Campus Access지만 대학 교수 공개 PDF에 접근할 수 있었다. 접근 제한을 우회하지 않았다. 원문 위치와 확인 범위는 다음과 같다.

| 필요한 근거 | 확보 위치 | 적용 판단 |
|---|---|---|
| 엔진 BSFC 도표 및 실차 운전점 | Yadav, 인쇄 p.91 / PDF p.125, Fig.4.9; 원출처 Conlon SAE2015-01-1152 | 도표 확보. 빨간 실차 운전점이 겹쳐 정확한 수치 판독에 한계. 원시 배열 아님 |
| MGA 효율맵 | 인쇄 p.48 / PDF p.82, Fig.3.14 | **406 V** 표기. 4사분면 그림이 있으나 각 사분면 독립 실측 여부는 확인되지 않음 |
| TPIM-A 효율맵 | 인쇄 p.49 / PDF p.83, Fig.3.16 | **406 V**, 전기기와 별도 맵. 고정 98% 가정을 대체할 후보 도표 |
| 시동·과도 연료 손실 | §3.2.1.6, §4.2, Fig.4.12, Fig.4.16 | 온도·운전점 변화에 따른 추가 연료 모델의 필요성 근거. 현재 0.5초 기동지연을 검증하지 않음 |
| 원시 자료 추적 | Appendix B, Table B.6 | `DataToLoad JCT 071417.mat` 등 파일명이 기재돼 있으나 해당 파일 자체는 미확보 |

위 도표의 계보는 전기기 SAE2015-01-1208, 인버터 SAE2015-01-1201로 이어진다. 따라서 기존 전기기 단일 360 V 가정과 새 406 V 도표를 동일 조건으로 취급하면 안 된다. 현재 버스 약381–386 V에 대한 전압 보간도 단일 전압 도표만으로 검증할 수 없다. 별도 맵 사용은 모델 경계 설정을 뒷받침하지만 원 제조사의 시험 경계 확인을 대신하지 않는다.

원문: https://pages.mtu.edu/~mahdish/Docs/R_Yadav_MScThesis.pdf

## 2. 출처별 역할과 선정 근거

| 출처 | 선정 이유 | 확보 수준 / 제한 |
|---|---|---|
| GM, 2016 Volt Drive Unit 자료 | 실제 donor 시스템 식별 | 제조사 PDF. 제원 소개이며 연료맵 파일은 아님 |
| Conlon et al., SAE2015-01-1152 | Volt Gen2 시스템 및 엔진 도표의 원계보 | 공식 초록·서지 확인. 유료 본문/원시 배열 미확보 |
| Jurkovic et al., SAE2015-01-1208 | GM PMAC 전기기 설계·성능 원문 | 공식 초록·서지 확인. MGA Q4 원시 시험배열 미확보 |
| Anwar et al., SAE2015-01-1201 | TPIM 손실을 별도로 다룰 원문 | 공식 초록·서지 확인. 원시 효율 배열 미확보 |
| Jocsak et al., SAE2015-01-1272 | 1.5 L 엔진의 연소·효율 설계 근거 | DI/EGR/압축비12.5:1의 제조사 연구. 특정 2950rpm98Nm 효율을 초록으로 확정할 수 없음 |
| Castellano & Cammalleri, Applied Sciences2021,11,7779 | 기존 수치맵의 직접 도표 출처 | Fig.4/5를 재구성한 기존 CSV를 그대로 보존. 2차 도표이며 OEM 실측 표와 구분 |
| Yadav2018 | 엔진·전기기·TPIM·동특성의 모델 경계와 자료 계보 | 이번 추가 확보 핵심. 부록 파일 목록은 데이터 다운로드가 아님 |
| Bhasme et al., ICAVP2019 | 실차 기반 모델에서 전기기/TPIM/시동연료를 구분하는 방법 | PDF pp.5–6. 해당 연구의 검증 성과를 우리 모델의 정확도로 전용하지 않음 |
| ANL, EVS30 2017 / WEVJ2018,9,29 | 실차 엔진 운전·제어의 물리적 맥락 | 공개 학회 PDF 확보. 실제 power-split 운전점은 새 직렬 발전계의 최적점이 아님 |
| Doshi2019 | 온도 모델 및 연료 발열량 가정 비교 | PDF p.27에 LHV43.420MJ/kg. 우리 시험 연료의 실측 발열량 아님 |
| EPA ALPHA complete-engine 목록 | 독립 공개 수치맵 대체 가능성 조사 | 이번 확인 목록에 L3A 없음. 다른 제조사/배기량 맵을 L3A 실측맵으로 바꾸지 않음 |

SAE DOI: https://doi.org/10.4271/2015-01-1152 ; https://doi.org/10.4271/2015-01-1208 ; https://doi.org/10.4271/2015-01-1201 ; https://doi.org/10.4271/2015-01-1272

기존 도표: https://doi.org/10.3390/app11177779

ANL: https://doi.org/10.3390/wevj9020029

MTU2019: https://sites.ualberta.ca/~mahdi/Docs/ICAVP19_MichiganTech_ChevyVoltModeling.pdf

Doshi: https://sites.ualberta.ca/~mahdi/Docs/N_Doshi_MScThesis.pdf

EPA: https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-engine-alpha-maps

## 3. 기존 26 kW 후보 운전점의 정확한 의미

기존 탐색 코드는 엔진속도1200–5800rpm(50rpm 간격), 토크25–140Nm(1Nm 간격), 고정 속도비0.45/0.5/0.6/0.75/1/1.25/1.5/2를 탐색했다. 전부하 곡선의97% 안쪽과 도표 보간영역 안에서 순전력26kW±0.15kW 후보의 순발전량당 연료가 작은 점을 골랐다. **2950rpm98Nm는 이 유한 격자·가정에서 나온 후보이며 연속영역 전역최적점 또는 실제 Volt ECU 지령이 아니다.** 26kW 자체는 유지 중인 연구 목표다.

| 항목 | 기존 후보 값 | 근거 등급 |
|---|---:|---|
| 엔진 회전속도 / 토크 | 2950rpm / 98Nm | 기존 탐색 결과 |
| 발전기 회전속도 / 토크 | 5900rpm / −48.02Nm | 신규 결합비2와 커플링효율98%로 계산 |
| 엔진 / MGA 효율 | 36% / 93% | 도표 재구성·보간 결과, 단일점 실측값 아님 |
| 엔진 축출력 | 30.274481kW | 회전속도×토크 |
| 발전기 축입력 | 29.668992kW | 커플링효율 가정 적용 |
| 최종 DC 순공급 | 25.999513kW | 전기기·인버터·DC/DC·보조손실 포함 |
| 엔진 BSFC | 232.558140g/kWh(축출력 기준) | 효율36%, LHV43MJ/kg 가정 |
| 연료율 | 1.955716g/s = 7.040577kg/h | 온간 정상상태 환산 |
| 순 DC 발전량당 연료 | 270.796501g/kWh | 버스 순공급 기준 |
| 연료→버스 순효율 | 30.916548% | 위 동일 가정의 계산값 |

계산식(출력kW, LHV MJ/kg, 연료g/s):

`P_engine = rpm × torque × 2π / 60000`

`P_bus = P_engine × η_coupling × η_generator × η_inverter × η_DCDC − P_aux`

`fuel_g_s = P_engine / (η_engine × LHV)`

`BSFC_engine = 3600 / (η_engine × LHV)`

`specific_fuel_bus = 3600 × fuel_g_s / P_bus`

커플링·인버터·DC/DC 각각98%, 발전계 보조0.5kW는 가정이다. 특히 기존 재구성 코드의 엔진 고효율 섬은 최고 채택 등고선36%를 이용하며 내부 정보가 없는 부분을 실제 최고효율 형상으로 복원한 것이 아니다. MGA93% 역시 원시 단일점 데이터가 아니다. 결합비2도 Volt 행성기어의 실제 기어비를 그대로 가져온 값이 아니다.

기존 후보의 생성 코드는 보존만 했다. 새 PDF v2와 과거 추출 PDF의 해시가 다르므로 재추출해 기존 표를 덮어쓰지 않았다. 원 추출 PDF는 이번 묶음에 없어 벡터 맵 생성 전체의 독립 재현은 아직 제한된다. 이번 검산은 저장된 후보와 변환식의 일관성 검산이다.

## 4. 연료 비교에 바로 적용 가능한 범위

현재 확보 수준으로 가능한 것은 **가정이 명시된 온간 정상상태 후보 연료모델**이다. `unchanged_candidate_maps`에는 엔진 연료528점, MGA 양방향 효율1314행의 기존 CSV와 전부하 표를 보존했다. 원시 실측자료로 명명하지 않았다. `26kW_existing_ratio_candidates.csv`는 기존26kW 후보만 추린 표이고, `26kW_power_boundary.csv`는 손실 경계별 계산이다.

단일26kW 정상점의 연료를 출력비로 비례 축소하면 저출력·기동 연료를 검증한 것이 아니다. 충전 제한으로10kW까지 내려가는 경우에는 별도 속도·토크 운전점 또는 명시적인 축소 가정이 필요하다. STARTING에서도 공급전력이0이라고 연료가0이라고 둘 근거는 없다. 정지 시 연료차단과 기계 회전 지속도 구분해야 한다.

`fuel_assumption_sensitivity.csv`는 엔진효율34/35/36/37/38%와 LHV43/43.42의 조합을 계산한다. **설계 민감도이며 측정 오차범위나95% 신뢰구간이 아니다.** 기존값36%/43은 변경하지 않았다. 발열량만43.42로 바꾸는 비교는 동일효율 가정의 연료환산 영향이며, 원시BSFC가 있으면 그 BSFC를 우선하고 발열량 변화로 측정 연료를 재조정하지 않는다.

현재 온간 정적 비교와 기동횟수를 별도로 보고할 수 있다. 기동횟수가 다른 EMS 간 총연료 절감률은 시동·촉매·과도 추가연료가 확보될 때까지 제한적으로 해석해야 한다. 0.5초/20kW·s⁻¹/50kW·s⁻¹/최소ON10초/OFF5초는 현행 연구가정이며 이번 문헌으로 실측값이 되지 않는다.

## 5. 채택 전 남은 조건과 다음 시작점

1. 새 BSFC·MGA406V·TPIM-A406V 도표를 **별도 후보 버전**으로 수치화하고 원도표 재투영·단위·경계·등고선 오차를 확인한다. 겹친 실차 점 때문에 엔진 도표 판독이 불가능한 영역은 결측 처리한다. 기계 효율과 TPIM 효율을 중복 적용하지 않는다.
2. 발전 Q4의 도표값과 대칭 가정을 구분한다. 실제381–386V와406V 차이를 민감도로 처리하거나 추가 전압 자료를 확보한다. 한 전압 맵으로 전압 의존 검증을 주장하지 않는다.
3. OEM 원시 배열은 SAE 본문/부록 또는 MTU 연구진의 파라미터 파일 제공 가능성을 통해 확인할 필요가 있다. 요청 대상은 `DataToLoad JCT 071417.mat`, 엔진 fuel/BSFC grid와WOT, MGA Q4·TPIM-A 전압/온도별 표, 시동 연료와 열 연속출력 한도다. 이번에 외부 연락은 보내지 않았다.
4. 모델 채택 이후에는 단일점→출력변화→기동·정지→주행 순으로 검증한다. 기존 요청형 DC 전원의 보호/충전허용/재기동 시험 순서는 유지한다. 본 문헌 확보가 그 실행시험의 통과를 뜻하지 않는다.

교수님께 설명할 문장: “Bolt EV를 차량 기반으로 하고 별도 차량인 Volt Gen2의 L3A·MGA를 발전계 후보로 참고했습니다. 연료·전기기·인버터 도표와 시동 손실 연구는 확보했고,26kW점은 이를 바탕으로 한 가상 결합계 후보입니다. OEM 원시 배열 및 실제 발전 운전의 검증은 아직 확보하지 못했으므로 우선 온간 정적 비교 범위로 한정하겠습니다.”

## 6. 파일과 검증 상태

- `DOWNLOAD_LOG.json`: 성공·실패·대체 다운로드 URL/크기/SHA256.
- `CALCULATION_QA.json`: 기존파일 불변 해시와26kW/연료 검산.
- `build_evidence.py`: 저장된 기존 후보의 경계 계산과 민감도 표 생성. 프로젝트 변경 없음.
- `YADAV_PAGE_INDEX.json`: 확인한 도표 위치. 원문 PDF는 별도 Source Documents 압축파일.
- `README_NEXT.md`: 다음 시작점과 채택 금지 조건.

완료: 공개 근거 수집, 계보·경계 확인, 후보 보존, 정상점 수치검산, 적용 한계 정리. 미완료: OEM 원시맵 확보, 새 도표 수치화, 프로젝트 연료모델 통합 및 실제 시뮬레이션 검증.


## Calculation script
```python
from pathlib import Path
import csv,json,math,shutil,hashlib,zipfile
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
old=ROOT/'repo/research/bolt_volt_genset_20261006'
(P/'unchanged_candidate_maps').mkdir(exist_ok=True)
names=['L3A_CRUISE_PREVIEW_assumed_axes.csv','MGA_CRUISE_PREVIEW_assumed_axes.csv','L3A_FullLoad_CRUISE_PREVIEW.csv','MGA_FullLoad_CRUISE_PREVIEW.csv','genset_target_candidates.csv','source_register.csv','contour_legend.csv']
hashes=[]
for name in names:
 src=old/'inputs'/name; dest=P/'unchanged_candidate_maps'/name
 shutil.copyfile(src,dest)
 assert src.read_bytes()==dest.read_bytes()
 hashes.append(dict(file=name,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),unchanged=True))
shutil.copyfile(old/'scripts/reconstruct_maps.py',P/'unchanged_candidate_maps/ARCHIVED_reconstruct_maps_NOT_RUN.py')
def writecsv(name,rows):
 with (P/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=list(csv.DictReader((old/'inputs/genset_target_candidates.csv').open()))
sel=[r for r in rows if r['generator']=='MGA' and r['target_net_kW']=='26' and r['engine_rpm']]
writecsv('26kW_existing_ratio_candidates.csv',sel)
r=next(r for r in sel if float(r['ratio_generator_over_engine'])==2)
pe=2950*98*2*math.pi/60000
pg=pe*.98; pac=pg*.93; pdc=pac*.98; pbus=pdc*.98-.5
fuel=pe/(.36*43)
assert abs(pbus-float(r['net_bus_kW']))<1e-10
assert abs(fuel-float(r['fuel_g_s']))<1e-10
writecsv('26kW_power_boundary.csv',[dict(boundary=n,power_kW=v,basis=b) for n,v,b in [
 ('engine_shaft',pe,'2950rpm 98Nm candidate'),('generator_shaft',pg,'coupling eta .98 assumption'),
 ('generator_AC',pac,'eta .93 reconstructed candidate'),('inverter_DC',pdc,'TPIM eta .98 assumption'),
 ('bus_net',pbus,'DC/DC eta .98 and auxiliary .5kW assumptions')]])
sens=[]
for eta in [.34,.35,.36,.37,.38]:
 for lhv in [43,43.42]:
  f=pe/(eta*lhv)
  sens.append(dict(engine_eta=eta,LHV_MJ_kg=lhv,shaft_kW=pe,net_kW=pbus,fuel_g_s=f,engine_BSFC_g_kWh=3600/(eta*lhv),net_fuel_g_kWh=f*3600/pbus,status='assumption_sensitivity_not_confidence_interval'))
writecsv('fuel_assumption_sensitivity.csv',sens)
qa=dict(candidate_reproduced=True,shaft_kW=pe,net_kW=pbus,fuel_g_s=fuel,engine_BSFC_g_kWh=3600/(.36*43),net_g_kWh=fuel*3600/pbus,fuel_kg_h=fuel*3.6,overall_net_efficiency=pbus/(fuel*43),original_inputs_unchanged=hashes,CRUISE_run=False,OEM_raw_fuel_array_obtained=False,new_voltage_evidence='Yadav2018 Figures3.14/3.16:406V; not verified voltage of old map',next='Digitize and cross-check new BSFC/MGA/TPIM figures as separate candidate; never overwrite existing baseline; fuel-model adoption conditional')
(P/'CALCULATION_QA.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in qa.items() if k!='original_inputs_unchanged'},ensure_ascii=False))

```
## Download log
```json
[
  {
    "file": "Doshi_2019_Thesis.pdf",
    "url": "https://sites.ualberta.ca/~mahdi/Docs/N_Doshi_MScThesis.pdf",
    "bytes": 10447874,
    "sha256": "8b59d452ad56506c2f26773d5110062ffc206978bec7625866202b013a288d27",
    "status": "downloaded"
  },
  {
    "file": "MTU_Volt_Controller_2019.pdf",
    "url": "https://sites.ualberta.ca/~mahdi/Docs/ICAVP19_MichiganTech_ChevyVoltModeling.pdf",
    "status": "HTTP Error 503: Service Unavailable"
  },
  {
    "file": "ANL_Voltec_Control_2018.pdf",
    "url": "https://mdpi-res.com/d_attachment/wevj/wevj-09-00029/article_deploy/wevj-09-00029.pdf",
    "status": "HTTP Error 403: Forbidden"
  },
  {
    "file": "EPA_engine_map_catalog.html",
    "url": "https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-engine-alpha-maps",
    "bytes": 71337,
    "sha256": "4ebd77443a88211195bbb7ad2d1e81c638c735bd6c9bb58b4fc874b808665e72",
    "status": "downloaded"
  },
  {
    "file": "ANL_Voltec_Control_EVS30_2017.pdf",
    "url": "https://www.citelec.org/EVS30/download.php?f=papers/EVS30-2460262.pdf",
    "bytes": 6207902,
    "sha256": "02209e640726c22dc66739a3d872b3231511979ac19b24c507bbd404c983df54",
    "status": "downloaded"
  },
  {
    "file": "MTU_Volt_Controller_2019.pdf",
    "url": "https://sites.ualberta.ca/~mahdi/Docs/ICAVP19_MichiganTech_ChevyVoltModeling.pdf",
    "bytes": 1941615,
    "sha256": "6d27b0376bea4cfb4cfec603c559e5e2dc18083f2f616d8ca255b52e3f7eb967",
    "status": "downloaded"
  },
  {
    "file": "AppliedSciences_2021_7779_v2.pdf",
    "source": "outputs/erev_genset_audit/sources/AppliedSciences_2021_7779_v2.pdf",
    "sha256": "6cedfa864498ffe3b5e0e994ef74d549fa8fca18c309e8db44315bdba4be8dd4",
    "status": "reused_prior_download_not_redigitized"
  },
  {
    "file": "GM_Volt2016_DriveUnit.pdf",
    "source": "outputs/erev_genset_audit/sources/GM_Volt2016_DriveUnit.pdf",
    "sha256": "995852b06d533aec7a1271e758ff8fc347d457d2988c35b4aae28994e381266a",
    "status": "reused_prior_download_not_redigitized"
  },
  {
    "file": "Yadav_2018_Thesis.pdf",
    "url": "https://pages.mtu.edu/~mahdish/Docs/R_Yadav_MScThesis.pdf",
    "bytes": 9086865,
    "sha256": "e1b2d5c783e2b2eba4f9be21f05eef5c8aa7fb0d1c450d00e9deca5554cde150",
    "status": "downloaded_public_faculty_host"
  }
]
```
## QA
```json
{
  "candidate_reproduced": true,
  "shaft_kW": 30.27448120509364,
  "net_kW": 25.999512548377577,
  "fuel_g_s": 1.9557158401223282,
  "engine_BSFC_g_kWh": 232.55813953488374,
  "net_g_kWh": 270.796500947466,
  "fuel_kg_h": 7.040577024440382,
  "overall_net_efficiency": 0.3091654801285628,
  "original_inputs_unchanged": [
    {
      "file": "L3A_CRUISE_PREVIEW_assumed_axes.csv",
      "sha256": "1bd6d7a0d58446e759a7736dc4e7d901b53af5b172d2830a9e3176e91279c0ee",
      "unchanged": true
    },
    {
      "file": "MGA_CRUISE_PREVIEW_assumed_axes.csv",
      "sha256": "95a4276feaf9f4e1f9adbc45f864569b75f851a3f8ed6a09d5d0436acd4885e0",
      "unchanged": true
    },
    {
      "file": "L3A_FullLoad_CRUISE_PREVIEW.csv",
      "sha256": "51056705c81d879a10fca06038492c2a60330683d41c5235f99a3e1d41c1fbd5",
      "unchanged": true
    },
    {
      "file": "MGA_FullLoad_CRUISE_PREVIEW.csv",
      "sha256": "8b716b46da6ebca8d86ead55d5b8847c504b7448944b983deb9bda4550cf290b",
      "unchanged": true
    },
    {
      "file": "genset_target_candidates.csv",
      "sha256": "d685b2b50c7a23d938f905a510c49ab6a5af43e7d23040c841752eada785719f",
      "unchanged": true
    },
    {
      "file": "source_register.csv",
      "sha256": "723a641908cb96ad556148b439a7dd78dc4cf8574a08e547e1584e1fd2715b3c",
      "unchanged": true
    },
    {
      "file": "contour_legend.csv",
      "sha256": "80de23be7a7cb5514fd4515059ae755e900cfee3003e5bd53d66ce789baee6e4",
      "unchanged": true
    }
  ],
  "CRUISE_run": false,
  "OEM_raw_fuel_array_obtained": false,
  "new_voltage_evidence": "Yadav2018 Figures3.14/3.16:406V; not verified voltage of old map",
  "next": "Digitize and cross-check new BSFC/MGA/TPIM figures as separate candidate; never overwrite existing baseline; fuel-model adoption conditional"
}
```