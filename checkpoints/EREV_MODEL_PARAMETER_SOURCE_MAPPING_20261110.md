# Modeling parameter source mapping added to professor meeting brief

Date: 2026-11-10 KST
Prior meeting checkpoint: 90772962e712b3cdda29c7a9bd9b6c0f57f27f8a
Research inputs and original rules unchanged; no new CRUISE runs.

Updated existing brief: https://chatgpt.com/library?file_id=libfile_677a626b717481919a578985a83579a9&account_id=personal
Source archive: https://chatgpt.com/library?file_id=libfile_0357948a24ac8191a0936d263130828f&account_id=personal
Source archive SHA256: bc770829abf80617373a69149fb32ecbce80c12f0580554182d26f64fe57cbff

# 모델링 제원 출처 및 적용 구분

교수님께는 다음과 같이 설명한다.

“차량의 기본 구성은 GM의 Bolt EV 기술자료를 참고했고, 시험질량과 도로부하 및 검증용 주행 데이터는 ANL 자료를 대조했습니다. 구동계 손실은 EPA의 Bolt EDU 공개맵을 CRUISE M 형식으로 변환했습니다. 배터리 OCV와 내부저항은 NREL 공동연구 보고서에 제시된 Bolt 팩 참조식을 셀 단위로 환산했습니다. 발전원 출력과 기동응답, 보조부하 등은 별도의 연구 가정으로 구분했습니다.”

| 모델링 항목 | 출처 및 적용 내용 | 공개자료·가정의 구분 |
|---|---|---|
| 차량 기본 구성 | GM, *2017 Chevrolet Bolt EV New Model Features*, Bulletin 16-NA-393. PDF 3쪽의 150 kW 구동모터·60 kWh 팩, 4쪽의 96직렬 셀 그룹·그룹당 3병렬 구성 | 제조사 공개 제원. 모든 차량 치수·관성·제어한계까지 이 자료에서 확보한 것은 아님 |
| 시험질량 | ANL 61905060/61 원본 TDMS `TestInfo_Dyno_Test_Weight_lb`: 3,875 lb → 1,757.6704 kg | 해당 시험의 기록값을 환산. 공차중량이나 차량총중량 등급과 혼동하지 않음 |
| 도로부하 | 같은 ANL 원본의 Target ABC 28.4 / 0.2018 / 0.01948을 기존 lbf·mph 관례에 따라 환산. 현재 입력 A=126.329494 N, B=0.557775 N/(km/h), C=0.033456276 N/(km/h)² | 원본 시험 설정과 단위변환 대응 확인. Set ABC는 다이나모 설정 단계가 달라 그대로 대체하지 않음 |
| 구동계 손실맵·감속비 | US EPA, *2018 Chevrolet Bolt 150kW 400V FWD EDU – ALPHA Map Package*, 2023-09-25 배포본. SwRI 허브 다이나모 자료 기반 완성맵, 감속비 7.05 | 인버터·모터·감속기 포함. 실측 기반이나 전체 격자가 직접 실측점인 것은 아님. CRUISE DAT 변환·보간을 별도로 확인 |
| 회생 손실 | 위 EPA 패키지의 회생 영역 생성 규칙을 승계 | 독립 회생 실측맵이 아니라 구동 손실을 1.05배로 미러링한 추정 영역 |
| 배터리 OCV·내부저항 | ANL·NREL·ORNL 공동연구 보고서 *Development and Evaluation of Distributed Energy Resource Device Models*, NREL/TP-5500-75323, July 2020, §1.5.1.3 / Figure 12 / PDF 26쪽(인쇄 1.20쪽) | Bolt 팩의 OCV/R 다항식 계수를 사용. 전압÷96, 저항×3÷96으로 셀 입력 환산. 충전 목적의 단순 모델을 주행 충방전에 적용한 추가 가정과 SOC 좌표 한계를 명시 |
| 배터리 용량·온도 등 | 현재 공개입력/R1 저장본은 셀 60 Ah, 96S3P 등가 구성, 단일 25°C OCV/R 입력을 사용. ANL CAFE 보고서 Table 38/39의 60 Ah와 55.9 Ah는 서로 다른 설계 맥락 | 60 kWh 팩 제원과 셀 60 Ah는 다른 양이다. 현 설정을 해당 ANL 시험 팩의 실측 용량으로 확정하지 않음. CRUISE의 48S3P 모듈 두 개는 전기적 등가 구성으로 실제 10모듈 배치와 구분 |
| BEV 검증 데이터 | ANL Downloadable Dynamometer Database(D3)의 2017 Bolt EV 원본 TDMS. 차속·팩 전압·전류·전력과 시험 메타데이터 사용 | 비교용 실측 자료. OCV/R 참조식의 직접 출처와 구분하며, 주행 데이터 자체를 평형 OCV/HPPC 수치표라고 부르지 않음 |
| 보조부하·가상 발전원 | BEV 보조부하 0.4 kW. 가상 DC 발전 상한 26 kW, 지연 0.5초, 상승 20 kW/s, 정상 하강 50 kW/s, 최소 ON/OFF 10초/5초 | 연구 가정 및 구현값. 현재 정지 시험의 10 kW 부하는 연결 검증용 임시 부하이며 BEV 주행 보조부하와 다름. 특정 양산 발전계 실측값으로 인용하지 않음 |

자료의 연식과 경계도 명시한다. 검증 차량은 ANL 2017 Bolt이며 EDU 맵은 EPA 2018 Bolt 자료다. 400 V 단일 전압 맵과 25°C 단일 온도 입력을 전압·온도별 실측 다차원 맵으로 표현하지 않는다. 차량 템플릿에 남은 휠 관성·무게중심 등 출처 미확정 항목은 GM 공개 제원이라고 묶어 설명하지 않는다. 현재 R1의 네 휠 반경은 323 mm로, 과거 313.5 mm 보정 후보와 구분한다. 이 값들을 이번 미팅 자료 작성 중 변경하지 않았다.

출처와 연구 가정을 구분한 목록을 교수님께 제시하고, 가상 발전원 가정과 배터리 저SOC 적용 범위를 어디까지 허용할지 자문받는다.

### 원문 링크

- GM 기술자료: https://static.nhtsa.gov/odi/tsbs/2016/MC-10138000-9999.pdf
- EPA EDU 공개맵 목록: https://www.epa.gov/vehicle-and-fuel-emissions-testing/combining-data-complete-emotor-alpha-maps
- EPA 실제 사용 패키지: https://www.epa.gov/system/files/other-files/2023-09/2018-chevrolet-bolt-150kw-400v-fwd-edu-alpha-map-package-dated-09-25-23.zip
- 배터리 공동연구 보고서 DOI: https://doi.org/10.2172/1660063
- 동일 보고서 ORNL 보관 원문: https://info.ornl.gov/sites/publications/Files/Pub133138.pdf
- ANL D3: https://www.anl.gov/taps/downloadable-dynamometer-database
- ANL CAFE 설계보고서: https://publications.anl.gov/anlpubs/2020/04/159142.pdf

2026-11-10 원문 재확인에서는 GM PDF, EPA 원본 ZIP, ORNL 보관 PDF를 내려받았다. ORNL PDF의 표지에 NREL/TP-5500-75323과 공동기관을 확인하고 Figure 12의 Bolt OCV/R 계수를 시각 대조했다. NREL/NLR 및 OSTI의 일부 직접 다운로드 주소는 이번 접근에서 실패했으며 이력을 함께 보존했다. ANL 시험질량/ABC 대응은 앞서 보존한 원본 TDMS 감사 기록을 승계했고 대용량 TDMS를 재다운로드하지 않았다.



## SOURCE_MAPPING_QA.json

```
{
  "date_KST": "2026-11-10",
  "status": "SOURCE_MAPPING_ADDED_TO_EXISTING_MEETING_BRIEF",
  "underlying_research_status_unchanged": true,
  "new_simulations": 0,
  "project_inputs_modified": false,
  "battery_provenance": "NREL/TP-5500-75323 Figure12, verified on ORNL-hosted original PDF26",
  "verification": [
    "GM150kW60kWh96S3P primary source",
    "ANL61905060/61 mass and TargetABC archived source audit reused",
    "EPA2018Bolt400V EDU20230925 package downloaded",
    "ORNLPDF26 rendered; Figure12 polynomial coefficients visually match existing inputs",
    "R1 current radius323mm and cell60Ah read from saved project"
  ],
  "current_project_sha256": "0754f46a6df5e888903106d5c8128d47e46a5d99049b38a2bfe47219f6582db2",
  "brief_sha256": "c0dddf229a6dedfb2e6da1e05d887782caaa66d1c821dd027fa603b0002a7589",
  "next_research_action": "Professor scope advice and pending Protection actual run; no completed stage repeated"
}
```


## model_sources/DOWNLOAD_MANIFEST.json

```
[
  {
    "file": "NREL_TP_5500_75323.pdf",
    "url": "https://www.nlr.gov/docs/fy20osti/75323.pdf",
    "status": "FAILED",
    "error": "HTTP Error 404: Not Found"
  },
  {
    "file": "GM_2017_Bolt_New_Model_Features.pdf",
    "url": "https://static.nhtsa.gov/odi/tsbs/2016/MC-10138000-9999.pdf",
    "bytes": 5859770,
    "sha256": "e589e59e1b001139b5a1ea4407899c6da470f62cdbcc2b42a5865dc7c5056c7a",
    "status": "DOWNLOADED"
  },
  {
    "file": "EPA_Bolt_EDU_ALPHA_20230925.zip",
    "url": "https://www.epa.gov/system/files/other-files/2023-09/2018-chevrolet-bolt-150kw-400v-fwd-edu-alpha-map-package-dated-09-25-23.zip",
    "bytes": 869508,
    "sha256": "80900864a012558bed051eb0ca04ecd9e00acf69da814cac3aa72565819dda1d",
    "status": "DOWNLOADED"
  },
  {
    "file": "NREL_TP_5500_75323_OSTI.pdf",
    "url": "https://www.osti.gov/servlets/purl/1660063",
    "status": "FAILED",
    "error": "HTTP Error 404: Not Found"
  },
  {
    "file": "ORNL_Pub133138.pdf",
    "url": "https://info.ornl.gov/sites/publications/Files/Pub133138.pdf",
    "bytes": 10628723,
    "sha256": "6059168469c9608ac850acb4359fda34e49f9113591943599496d2a3d2752a62",
    "status": "DOWNLOADED"
  }
]
```


## model_sources/SHA256SUMS.txt

```
880fa0e2261d287f5b2d4cd1cb4045b7912f1d6b2c6228918569bcb744fc936d  ANL61905060_61_SELECTED_METADATA.json
e954d87a955c7ec9c5de1dcf87508a0932035a0cb69793d1cb1e0422c66cd1c3  ARCHIVED_SOURCE_REGISTER.json
0f20b09f1ab401d7d226f6c9a206219a40e79ac70fbe0385eb65e632479f8d23  DOWNLOAD_MANIFEST.json
80900864a012558bed051eb0ca04ecd9e00acf69da814cac3aa72565819dda1d  EPA_Bolt_EDU_ALPHA_20230925.zip
e589e59e1b001139b5a1ea4407899c6da470f62cdbcc2b42a5865dc7c5056c7a  GM_2017_Bolt_New_Model_Features.pdf
6059168469c9608ac850acb4359fda34e49f9113591943599496d2a3d2752a62  ORNL_Pub133138.pdf
5b8d48bcff34856727c5808fe355dc22f1e80fdbf457fc74962749815e4850bb  README_SOURCE_MAPPING_KO.md
```
