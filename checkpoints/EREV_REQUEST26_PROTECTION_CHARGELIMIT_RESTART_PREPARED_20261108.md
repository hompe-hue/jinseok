# Checkpoint: remaining request-source scenarios prepared, 2026-11-08

Prior completed stage: request-driven T1 bus 10/10 PASS, commit 89c99705f607836126b50dcb38f64f8c1a8bd4b3.
This stage: 3 isolated projects prepared and checked; zero actual CRUISE runs.
Next action: run EREV_Request26_Protection.proj, ANL61905060, 16 seconds; obtain same-run Generator Monitor, Plus, BMS Monitor and Vehicle Monitor CSVs. Save executed project and Job Log if available. Do not rerun completed baseline or mark scenarios actual PASS from reference fixtures.

Archive: EREV_Request26_Protection_ChargeLimit_Restart_Package.zip
SHA256: cab9deaeea888aa37fb3785657e412f6cc2103622b1aa96b09d47e6b0351f687
Library ID: libfile_08a42c22f2348191bead7ee1e7b95535
Download: https://chatgpt.com/library?file_id=libfile_08a42c22f2348191bead7ee1e7b95535&account_id=personal

# 다음 실행: 요청형 발전원 보호정지 → 충전 제한 → 재기동

## 시작 위치
직전 완료는 요청형 26 kW 발전원 공통 DC 버스 검증 10/10 통과다. 완료 커밋은 89c99705f607836126b50dcb38f64f8c1a8bd4b3이다. 정상 요청 펄스 시험을 다시 할 필요가 없다.

이번 묶음은 시험 준비 완료이며, CRUISE M 실제 실행 완료가 아니다. 세 시험은 서로 독립된 R1 복사본이다. 기존 엔진/발전기는 OFF 상태이며 26 kW 가상 DC 발전원 FMU를 사용한다. 차속 0 km/h와 부하 10 kW를 유지한다. 제어 규칙과 배선·포트·단위·FMU 바이너리는 변경하지 않았다. 보호 입력·충전 수용량·재요청의 시험 자극만 달리했다. 재기동 시험만 프로젝트 종료시간을 20초로 늘렸다.

## 지금 실행할 파일
1. 압축을 해제한다.
2. 포함된 `EREV_Request26.fmu`를 `C:\CRUISEM\EREV_Request26.fmu`에 둔다. 직전 R1과 동일한 FMU다. 프로젝트는 이 경로를 참조한다.
3. `EREV_Request26_Protection.proj`를 연다.
4. Cycle Run의 `ANL61905060`을 선택한다. Simulations의 End time이 16 s인지 확인하고 Run한다.
5. 같은 실행 결과에서 `Generator Monitor`, `Electrical FMU 1 / Plus`, `BMS Monitor`, `Vehicle Monitor`를 각각 CSV로 내보낸다. 각 CSV는 원래 헤더와 단위 행을 유지한다. 보호 시험이라고 구분해서 전달한다.
6. 가능하면 실행 후 저장한 프로젝트와 Job Log도 같이 보존한다. CSV만으로 실행 프로젝트 해시와 동일 Job 식별을 독립 입증할 수는 없다.

실행 오류가 나면 화면과 생성된 .debug 파일을 보존한다. 원래 R1 프로젝트는 `inputs/`에 수정 없이 함께 보존했다.

## 각 시험의 입력과 예상 반응

| 순서·파일 | 시험 입력 | 종료 | 확인할 반응 |
|---|---|---:|---|
| 보호정지 `EREV_Request26_Protection.proj` | 1초 이후 ON 요청 유지, 6.0–6.1초 보호 입력 ON | 16 s | 약 6초 출력 0, 최소 ON 시간보다 보호정지가 우선. 약 11초 재기동 시작, 약 12.8초 26 kW 회복 |
| 충전 제한 `EREV_Request26_ChargeLimit.proj` | 1초 이후 ON 요청 유지, 6초부터 발전원에 전달하는 충전 수용량 0 W | 16 s | 26 kW에서 부하를 충당하는 10 kW로 제한, 배터리 순충전 약 0 kW |
| 재기동 `EREV_Request26_Restart.proj` | 1–2초 ON 요청, 12초 이후 다시 ON 요청 | 20 s | 첫 정지 약 11.52초, 12초 즉시 재기동하지 않음. OFF 5초 충족 뒤 약 16.52초 기동, 약 18.32초 26 kW 도달 |

FMU가 통신 구간 끝에 입력을 반영하므로, 직전 실제 시험과 같이 상태 전이는 이론값보다 약 2 ms 늦게 기록될 수 있다. 보호/충전 제한은 정상 하강률 50 kW/s보다 우선하는 즉시 제한이다. 6초의 급격한 변화 자체가 이번 시험 대상이다. 충전 제한 시험은 수용량을 소프트웨어 입력에서 제한하는 시험이며 배터리 물리 충전 한계를 0으로 수정한 모델이 아니다. 보호정지는 외부 보호 신호를 시험하며 실제 버스 과전압/저전압이나 하드웨어 고장 검증이 아니다.

## 유지한 원래 규칙
최대 26 kW, 기동 지연 0.5초, 상승 20 kW/s, 정상 하강 50 kW/s, 최소 ON 10초(STARTING 진입부터), 최소 OFF 5초(출력 0 및 OFF 진입부터). BMS 충전 전류 상한 160 A를 유지한다. 각 시험의 초기 OFF 상태는 기동 가능 시간만큼 이미 경과한 원래 초기화를 그대로 쓴다. 기존 FMU의 100–500 V 수치 가드도 그대로이며 하드웨어 운전 한계로 주장하지 않는다.

## 검증 상태
- 프로젝트 ZIP 및 XML 구조, 원본과 항목 목록 일치: 통과.
- 새 객체 ID·배선·포트·단위 추가 없음, 참조 순서·고유 ID: 통과.
- 원본 대비 바뀐 XML 텍스트: 보호 1개, 충전 제한 1개, 재기동 3개(C 코드 + 종료시간 두 필드).
- 세 C 함수의 GCC 문법 검사: 통과. CRUISE M 컴파일/로드를 대신하지 않는다.
- 수정하지 않은 참조 제어기의 이벤트 시점·제한 동작: 통과.
- 판정기 합성 예시: 정상 3건 통과, 버스 1 kW 오류 3건 실패, 보호/충전 제한/재기동 신호 오류 3건 실패.
- 세 프로젝트의 CRUISE M 실제 실행: 미수행. 실제 출력 CSV 수신 후 판정한다.

## 실제 결과 평가
`python3 evaluate_scenario.py --case Protection --generator generator.csv --plus plus.csv --bms bms.csv --vehicle vehicle.csv --output actual_protection_result`

다른 시험의 `--case`는 `ChargeLimit`, `Restart`다. Python 3, numpy, pandas가 필요하다. 공통 버스 잔차 최대 0.1 kW, 실제 부하 오차 0.1 kW, 전압에 따른 전류 오차 0.5 A 조건을 유지한다. 새로운 시험의 이벤트 시각은 절대 이론값 ±6 ms로 확인하고 시간축을 이동하지 않는다. 급변 후 정착 판정은 입력 변경 6 ms 뒤부터 적용하지만, 버스 잔차는 급변 시점을 포함해 전 구간 검사한다. 기존 정상 펄스 시험의 10개 평가 조건이나 결과는 변경하지 않는다.

`*_REFERENCE_ONLY.csv`는 참조 제어기 계산값이며 실제 실행 자료가 아니다. `QA_SYNTHETIC_ONLY/`의 CSV와 판정 결과는 판정기 검사에 사용한 합성 예시다. 이 파일들을 실제 시뮬레이션 출력으로 사용하거나 논문의 실측/실행 결과로 인용하면 안 된다.

## 다음 완료 조건
보호 시험 실제 4 CSV를 판정·저장·커밋한 뒤 충전 제한 시험으로 진행한다. 세 시험의 실제 통과 전 EMS 성능/연료 검증을 완료 처리하지 않는다. 이후 기존 계획의 수요 사전제한/배터리 가용출력 스크리닝과 S0–S4 비교로 이어간다.


## BUILD_QA.json

```
{
  "base_sha256": "0754f46a6df5e888903106d5c8128d47e46a5d99049b38a2bfe47219f6582db2",
  "fmu_sha256": "6cca9fd6f20595387df9924d27dfccc9540efa712409664667477002571d6294",
  "source_policies": {
    "maximum_W": 26000,
    "start_delay_s": 0.5,
    "rise_W_s": 20000,
    "fall_W_s": 50000,
    "min_ON_s": 10,
    "min_OFF_s": 5
  },
  "status": "PREPARED_NOT_CRUISE_EXECUTED",
  "cases": {
    "Protection": {
      "project": "EREV_Request26_Protection.proj",
      "project_sha256": "8b87fc92263fe90cb8a7e6cdb27e7b2d6d118fc36f9a737a3638d84d6248187f",
      "end_s": 16.0,
      "scenario": "emergency",
      "changed_text_nodes": [
        {
          "tag": "str",
          "before": "/* Request-interface bench. Powers are W. Positive load means consumption. */\ny[0] = (realTime >= 1.0 && realTime < 2.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\n/* Preserve the existing research BMS 160 A charging-current ceiling. */\ny[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = 0.0; /* Bench protection request. FMU voltage guard remains active. */\n",
          "after": "/* Isolated request-source Protection bench. Powers in W. */\ny[0] = (realTime >= 1.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\ny[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = (realTime >= 6.0 && realTime < 6.1) ? 1.0 : 0.0;\n"
        }
      ],
      "reference_start_events_s": [
        1.0,
        11.0
      ],
      "reference_samples": 8001,
      "graph_ids_connections_ports_units_unchanged": true,
      "forward_references": 0,
      "duplicate_ids": 0,
      "CRUISE_execution": "PENDING"
    },
    "ChargeLimit": {
      "project": "EREV_Request26_ChargeLimit.proj",
      "project_sha256": "5a8574940fb83402edd1b11927519b99a73f8105d4e09c5d1e497723ec0bb1d0",
      "end_s": 16.0,
      "scenario": "charge_curtail",
      "changed_text_nodes": [
        {
          "tag": "str",
          "before": "/* Request-interface bench. Powers are W. Positive load means consumption. */\ny[0] = (realTime >= 1.0 && realTime < 2.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\n/* Preserve the existing research BMS 160 A charging-current ceiling. */\ny[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = 0.0; /* Bench protection request. FMU voltage guard remains active. */\n",
          "after": "/* Isolated request-source ChargeLimit bench. Powers in W. */\ny[0] = (realTime >= 1.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\ny[2] = (realTime >= 6.0) ? 0.0 : min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = 0.0;\n"
        }
      ],
      "reference_start_events_s": [
        1.0
      ],
      "reference_samples": 8001,
      "graph_ids_connections_ports_units_unchanged": true,
      "forward_references": 0,
      "duplicate_ids": 0,
      "CRUISE_execution": "PENDING"
    },
    "Restart": {
      "project": "EREV_Request26_Restart.proj",
      "project_sha256": "07d807687022a96d5d2e75f963e7c4ef412c4ca21d75fbb55af03529b0780d5e",
      "end_s": 20.0,
      "scenario": "restart_dwell",
      "changed_text_nodes": [
        {
          "tag": "num",
          "before": "16.0",
          "after": "20.0"
        },
        {
          "tag": "str",
          "before": "/* Request-interface bench. Powers are W. Positive load means consumption. */\ny[0] = (realTime >= 1.0 && realTime < 2.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\n/* Preserve the existing research BMS 160 A charging-current ceiling. */\ny[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = 0.0; /* Bench protection request. FMU voltage guard remains active. */\n",
          "after": "/* Isolated request-source Restart bench. Powers in W. */\ny[0] = ((realTime >= 1.0 && realTime < 2.0) || realTime >= 12.0) ? 1.0 : 0.0;\ny[1] = a[0] + a[1];\ny[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));\ny[3] = 0.0;\n"
        },
        {
          "tag": "num",
          "before": "16.0",
          "after": "20.0"
        }
      ],
      "reference_start_events_s": [
        1.0,
        16.52
      ],
      "reference_samples": 10001,
      "graph_ids_connections_ports_units_unchanged": true,
      "forward_references": 0,
      "duplicate_ids": 0,
      "CRUISE_execution": "PENDING"
    }
  }
}

```


## C_SYNTAX_QA.json

```
{
  "Protection": {
    "C_syntax": "PASS"
  },
  "ChargeLimit": {
    "C_syntax": "PASS"
  },
  "Restart": {
    "C_syntax": "PASS"
  }
}

```


## EVALUATOR_QA.json

```
{
  "Protection": {
    "reference_fixture_accepted": true,
    "1kW_bus_fault_rejected": true,
    "protocol_fault_rejected": true,
    "CRUISE_execution": false
  },
  "ChargeLimit": {
    "reference_fixture_accepted": true,
    "1kW_bus_fault_rejected": true,
    "protocol_fault_rejected": true,
    "CRUISE_execution": false
  },
  "Restart": {
    "reference_fixture_accepted": true,
    "1kW_bus_fault_rejected": true,
    "protocol_fault_rejected": true,
    "CRUISE_execution": false
  }
}

```


## VERIFICATION.log

```
Builder: python3 build_scenarios.py -> PASS after scoped scalar replacement correction.
C syntax: gcc -std=c99 -Wall -Wextra -Werror -fsyntax-only, three cases -> PASS.
Evaluator: python3 check_evaluator.py -> PASS after exclusive protection-OFF endpoint correction at theoretical restart time.
Actual CRUISE execution: PENDING.
No earlier results changed.

```


## build_scenarios.py

```
"""Create three isolated tests by changing only existing C text/end-time values.
No serialization IDs, ports, connections, FMU bytes or plant values are changed.
"""
from copy import copy
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
import hashlib
import json
import re
import numpy as np
import pandas as pd
from source_reference import Source

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'inputs/EREV_Request26_Connected_R1.proj'
BASE_HASH='0754f46a6df5e888903106d5c8128d47e46a5d99049b38a2bfe47219f6582db2'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_HASH
CASES={
 'Protection':dict(scenario='emergency',end_s=16.,request='realTime >= 1.0',
   charge='min(fabs(a[2]), 160.0 * max(0.0, a[3]))',
   protection='(realTime >= 6.0 && realTime < 6.1) ? 1.0 : 0.0'),
 'ChargeLimit':dict(scenario='charge_curtail',end_s=16.,request='realTime >= 1.0',
   charge='(realTime >= 6.0) ? 0.0 : min(fabs(a[2]), 160.0 * max(0.0, a[3]))',
   protection='0.0'),
 'Restart':dict(scenario='restart_dwell',end_s=20.,
   request='(realTime >= 1.0 && realTime < 2.0) || realTime >= 12.0',
   charge='min(fabs(a[2]), 160.0 * max(0.0, a[3]))',protection='0.0'),
}

def patch_scalar(xml,object_id,key,tag,value):
    # Scalar-only patch preserves original stream ordering and reference graph.
    pattern=r'<object\b[^>]*\bid="'+object_id+r'"[^>]*>\s*<dict>.*?</dict>\s*</object>'
    match=re.search(pattern,xml,re.S)
    assert match,object_id
    scoped,n=re.subn(r'(<str>'+key+r'</str>\s*<'+tag+r'>).*?(</'+tag+r'>)',
        lambda m:m[1]+value+m[2],match.group(),count=1,flags=re.S)
    assert n==1,(object_id,key)
    return xml[:match.start()]+scoped+xml[match.end():]

manifest=dict(base_sha256=BASE_HASH,fmu_sha256=hashlib.sha256((ROOT/'EREV_Request26.fmu').read_bytes()).hexdigest(),
 source_policies=dict(maximum_W=26000,start_delay_s=.5,rise_W_s=20000,fall_W_s=50000,min_ON_s=10,min_OFF_s=5),
 status='PREPARED_NOT_CRUISE_EXECUTED',cases={})
with ZipFile(BASE) as original:
    xml=original.read('project.xml').decode()
    base_tree=E.fromstring(xml)
    codes=[n.text for n in base_tree.iter('str') if n.text and n.text.startswith('/* Request-interface bench.')]
    assert len(codes)==1
    old_code=codes[0]
    for label,case in CASES.items():
        code='/* Isolated request-source '+label+' bench. Powers in W. */\n'
        code+='y[0] = ('+case['request']+') ? 1.0 : 0.0;\n'
        code+='y[1] = a[0] + a[1];\n'
        code+='y[2] = '+case['charge']+';\n'
        code+='y[3] = '+case['protection']+';\n'
        # Let ElementTree perform escaping of the C operators only.
        node=E.Element('str');node.text=code
        new_code=E.tostring(node,encoding='unicode')[5:-6]
        node.text=old_code
        old_encoded=E.tostring(node,encoding='unicode')[5:-6]
        assert xml.count(old_encoded)==1
        changed=xml.replace(old_encoded,new_code)
        if case['end_s']!=16:
            changed=patch_scalar(changed,'79884','value','num',str(case['end_s']))
            changed=patch_scalar(changed,'76831','stop_time','num',str(case['end_s']))
        path=ROOT/f'EREV_Request26_{label}.proj'
        with ZipFile(path,'w') as archive:
            archive.comment=original.comment
            for entry in original.infolist():
                archive.writestr(copy(entry),changed.encode() if entry.filename=='project.xml' else original.read(entry))
        with ZipFile(path) as check:
            assert check.testzip() is None
            assert check.namelist()==original.namelist()
            assert [name for name in check.namelist() if check.read(name)!=original.read(name)]==['project.xml']
            tree=E.fromstring(check.read('project.xml'))
        differences=[]
        a,b=list(base_tree.iter()),list(tree.iter())
        assert len(a)==len(b)
        for n,m in zip(a,b):
            assert n.tag==m.tag and n.attrib==m.attrib and n.tail==m.tail
            if n.text!=m.text:differences.append(dict(tag=n.tag,before=n.text,after=m.text))
        assert len(differences)==(3 if label=='Restart' else 1)
        seen=set()
        for node in tree.iter():
            if node.tag=='ref':assert node.get('id') in seen
            elif node.get('id'):
                assert node.get('id') not in seen
                seen.add(node.get('id'))
        (ROOT/f'{label}_Request_Interface.c').write_text(code)
        source=Source();records=[]
        for tick in range(round(case['end_s']/.002)+1):
            t=tick*.002
            request=(1<=t<2 or t>=12) if label=='Restart' else t>=1
            charge=0 if label=='ChargeLimit' and t>=6 else 50
            emergency=label=='Protection' and 6<=t<6.1
            records.append(source.step(t,request,10,charge,380,emergency))
        frame=pd.DataFrame(records)
        frame.to_csv(ROOT/f'{label}_REFERENCE_ONLY.csv',index=False)
        events=frame.loc[frame.start_event==1,'time_s'].tolist()
        expected=[1,11] if label=='Protection' else [1,16.52] if label=='Restart' else [1]
        np.testing.assert_allclose(events,expected,atol=1e-9,rtol=0)
        if label=='ChargeLimit':assert frame.loc[frame.time_s>=6,'Pgen_actual_kW'].max()<=10+1e-9
        if label=='Protection':assert frame.loc[(frame.time_s>=6)&(frame.time_s<11),'Pgen_actual_kW'].max()==0
        manifest['cases'][label]=dict(project=path.name,project_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            end_s=case['end_s'],scenario=case['scenario'],changed_text_nodes=differences,
            reference_start_events_s=events,reference_samples=len(frame),
            graph_ids_connections_ports_units_unchanged=True,forward_references=0,duplicate_ids=0,
            CRUISE_execution='PENDING')
(ROOT/'BUILD_QA.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'projects':list(manifest['cases']),
                  'graph_and_archive_QA':'PASS','reference_events':'PASS'},indent=2))

```


## evaluate_scenario.py

```
"""Evaluate future actual four-monitor CSVs; reference files are never actual runs.
Usage: python3 evaluate_scenario.py --case Protection --generator g.csv
       --plus p.csv --bms b.csv --vehicle v.csv --output result_directory
The original T1 evaluator remains unchanged in its completed checkpoint.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

def evaluate(case, paths, output):
    frames={k:pd.read_csv(p,skiprows=[1]) for k,p in paths.items()}
    g,p,b,v=(frames[k] for k in ('generator','plus','bms','vehicle'))
    t=g.Time.to_numpy();end=20 if case=='Restart' else 16
    for frame in frames.values():
        assert np.isfinite(frame.to_numpy(float)).all()
        np.testing.assert_array_equal(t,frame.Time)
    assert len(t)==round(end/.002)+1
    np.testing.assert_allclose(np.diff(t),.002,atol=2e-12,rtol=0)
    def channel(name):return g[f'In/{name} (Generator Monitor)'].to_numpy()
    def maxabs(x):return float(np.max(np.abs(x))) if len(x) else float('inf')
    def interval(a,z):return (t>=a)&(t<=z)
    def transitions(x):return [(float(t[i]),float(x[i])) for i in np.r_[0,np.flatnonzero(np.diff(x)!=0)+1]]
    voltage=p['Plus/Potential (Electrical FMU 1)'].to_numpy()
    pg=-p['Plus/Power (Electrical FMU 1)'].to_numpy()/1000
    pb=-b['In/Power (BMS Monitor)'].to_numpy()
    load=voltage*(v['In/E-Consumer Current (Vehicle Monitor)']+v['In/E-Motor Current (Vehicle Monitor)']).to_numpy()/1000
    gm=channel('Generated W')/1000
    starts=channel('Start Count');state=channel('State')
    edges=transitions(starts)
    actual_starts=[tt for tt,value in edges[1:] if value>0]
    expected=[1,11] if case=='Protection' else [1,16.52] if case=='Restart' else [1]
    checks=dict(window=abs(t[0])<=1e-6 and abs(t[-1]-end)<=1e-6,
        voltage_agreement=maxabs(voltage-b['In/Voltage (BMS Monitor)'])<=1e-8,
        actual_load_10kW=maxabs(load-10)<=.1,
        bus_balance_max_0p1kW=maxabs(pb+pg-load)<=.1,
        current_from_bus_voltage=maxabs(-p['Plus/Current (Electrical FMU 1)']-pg*1000/voltage)<=.5,
        stationary_actual=maxabs(v['In/Actual Velocity (Vehicle Monitor)'])<=1e-10,
        stationary_desired=maxabs(v['In/Desired Velocity (Vehicle Monitor)'])<=1e-10,
        monitor_load=maxabs(channel('Load W')-load*1000)<=100,
        initial_generation_26kW=maxabs(pg[interval(3,5.9)]-26)<=.1,
        expected_start_count_and_times=len(actual_starts)==len(expected) and all(abs(a-e)<=.006 for a,e in zip(actual_starts,expected)))
    if case=='Protection':
        checks.update(protection_asserted=np.all(channel('Protection Active')[interval(6.006,6.09)]==1),
            protected_monitor_zero=maxabs(gm[interval(6.006,11)])<=.05,
            protected_terminal_zero=maxabs(pg[interval(6.006,11)])<=.05,
            protected_state_off=np.all(state[(t>=6.006)&(t<11)]==0),
            recovered_26kW=maxabs(pg[interval(13,15.9)]-26)<=.1)
    elif case=='ChargeLimit':
        checks.update(charge_limit_zero=maxabs(channel('Charge Available W')[t>=6.006])<=1e-6,
            curtailed_monitor_10kW=maxabs(gm[t>=6.006]-10)<=.1,
            curtailed_terminal_10kW=maxabs(pg[t>=6.006]-10)<=.1,
            no_excess_battery_charge=maxabs(pb[t>=6.006])<=.1,
            no_protection=np.all(channel('Protection Active')[t>=.006]==0))
    else:
        off_edges=[tt for tt,value in transitions(state)[1:] if value==0 and tt>2]
        checks.update(off_interval_observed=len(off_edges)==1,
            no_early_restart=len(off_edges)==1 and len(actual_starts)==2 and actual_starts[1]-off_edges[0]>=5-1e-9,
            off_generation_zero=maxabs(pg[interval(11.54,16.52)])<=.05,
            second_run_26kW=maxabs(pg[interval(18.4,19.9)]-26)<=.1,
            no_protection=np.all(channel('Protection Active')[t>=.006]==0))
    checks={k:bool(value) for k,value in checks.items()}
    output.mkdir(parents=True,exist_ok=True)
    result=dict(status='SCENARIO_NUMERIC_PASS' if all(checks.values()) else 'SCENARIO_NUMERIC_FAIL',
        case=case,checks=checks,start_events_s=actual_starts,state_transitions=transitions(state),
        maximum_bus_residual_kW=maxabs(pb+pg-load),
        source_hashes={k:hashlib.sha256(Path(path).read_bytes()).hexdigest() for k,path in paths.items()},
        temporal_policy='2 ms, absolute reference event times within 6 ms. No trace shift. Abrupt-edge settling windows start 6 ms after stimulus; full bus residual checked at all samples.',
        scope='Request-source scenario only; saved executed project and Job Log identity require separate review.')
    pd.DataFrame(dict(time_s=t,Pgen_kW=pg,Pload_kW=load,Pbat_discharge_kW=pb,residual_kW=pb+pg-load)).to_csv(output/'NORMALIZED.csv',index=False)
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',choices=['Protection','ChargeLimit','Restart'],required=True)
    for name in ('generator','plus','bms','vehicle'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=evaluate(args.case,{name:getattr(args,name) for name in ('generator','plus','bms','vehicle')},args.output)
    print(result['status'])
    raise SystemExit(0 if all(result['checks'].values()) else 1)

```


## check_evaluator.py

```
"""Synthetic acceptance/rejection fixtures only. Never a CRUISE result."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
from evaluate_scenario import evaluate

root=Path(__file__).resolve().parent
summary={}
def write(frame,path):
    # Mimic only the CSV header/unit layout, explicitly under synthetic directory.
    path.write_text(frame.to_csv(index=False).split('\n',1)[0]+'\n'+','.join(['synthetic']*len(frame.columns))+'\n'+frame.to_csv(index=False,header=False))

for case in ('Protection','ChargeLimit','Restart'):
    f=pd.read_csv(root/f'{case}_REFERENCE_ONLY.csv');t=f.time_s.to_numpy()
    directory=root/'QA_SYNTHETIC_ONLY'/case;directory.mkdir(parents=True,exist_ok=True)
    g=pd.DataFrame({'Time':t})
    for name,values in {
        'Generated W':f.Pgen_actual_kW*1000,'Load W':f.Pdem_DC_kW*1000,
        'Charge Available W':np.where(t>=6,0,50000) if case=='ChargeLimit' else 50000,
        'Start Count':f.start_count,'State':f.state,'Protection Active':f.protection_active
    }.items():g[f'In/{name} (Generator Monitor)']=values
    p=pd.DataFrame({'Time':t,'Plus/Potential (Electrical FMU 1)':380,
        'Plus/Power (Electrical FMU 1)':-f.Pgen_actual_kW*1000,
        'Plus/Current (Electrical FMU 1)':-f.Pgen_actual_kW*1000/380})
    b=pd.DataFrame({'Time':t,'In/Voltage (BMS Monitor)':380,
        'In/Power (BMS Monitor)':-f.Pbat_discharge_positive_kW})
    v=pd.DataFrame({'Time':t,'In/E-Consumer Current (Vehicle Monitor)':10000/380,
        'In/E-Motor Current (Vehicle Monitor)':0,'In/Actual Velocity (Vehicle Monitor)':0,
        'In/Desired Velocity (Vehicle Monitor)':0})
    paths={}
    for key,frame in zip(('generator','plus','bms','vehicle'),(g,p,b,v)):
        paths[key]=directory/f'{key}_SYNTHETIC.csv';write(frame,paths[key])
    nominal=evaluate(case,paths,directory/'NOMINAL_SYNTHETIC')
    assert nominal['status']=='SCENARIO_NUMERIC_PASS',nominal
    b['In/Power (BMS Monitor)']+=1
    bad=directory/'bms_CORRUPTED_SYNTHETIC.csv';write(b,bad)
    faults=evaluate(case,{**paths,'bms':bad},directory/'CORRUPTED_SYNTHETIC')
    assert faults['status']=='SCENARIO_NUMERIC_FAIL' and not faults['checks']['bus_balance_max_0p1kW']
    # Corrupt source protocol while keeping physical channels identical.
    if case=='Protection':g['In/Protection Active (Generator Monitor)']=0
    elif case=='ChargeLimit':g['In/Charge Available W (Generator Monitor)']=50000
    else:g.loc[t>=12,'In/Start Count (Generator Monitor)']=2
    badg=directory/'generator_CORRUPTED_SYNTHETIC.csv';write(g,badg)
    protocol=evaluate(case,{**paths,'generator':badg},directory/'CORRUPTED_PROTOCOL_SYNTHETIC')
    assert protocol['status']=='SCENARIO_NUMERIC_FAIL'
    summary[case]={'reference_fixture_accepted':True,'1kW_bus_fault_rejected':True,
                   'protocol_fault_rejected':True,'CRUISE_execution':False}
(root/'EVALUATOR_QA.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Synthetic checks: 3 nominal accepted; 3 bus faults and 3 protocol faults rejected. No actual CRUISE execution.')

```


## SHA256SUMS.txt

```
1d8c42fe71dca0d3ac8354b8c0d15124899a00cf5eb5363fe8f74bb7dce5a8e8  BUILD_QA.json
13c0c6998936f71d58b9848c0fd94bc4a45870ab96232b904c8f1684cd037fb9  C_SYNTAX_QA.json
2bfbd13e3b3ec52cafe870b01a0abd3cc7ee0b16ef4fac1b42ff66a8939293b9  ChargeLimit_REFERENCE_ONLY.csv
ea6465f87607b33cc4b0c7585dba86f6fadc8fe378b50feedcecebca3171a6ec  ChargeLimit_Request_Interface.c
6cca9fd6f20595387df9924d27dfccc9540efa712409664667477002571d6294  EREV_Request26.fmu
5a8574940fb83402edd1b11927519b99a73f8105d4e09c5d1e497723ec0bb1d0  EREV_Request26_ChargeLimit.proj
8b87fc92263fe90cb8a7e6cdb27e7b2d6d118fc36f9a737a3638d84d6248187f  EREV_Request26_Protection.proj
07d807687022a96d5d2e75f963e7c4ef412c4ca21d75fbb55af03529b0780d5e  EREV_Request26_Restart.proj
e5573526f462e2f72d5703a6942e5c30e625d20759cb74e39bddcec1c7402995  EVALUATOR_QA.json
c1d864729d529ede959341ffb7ca144461731af0f153a79d2622fe18848c72c3  Protection_REFERENCE_ONLY.csv
eb81700190d3291a0a6b3ed3b317004bf435194e6fe97cd97198a0567cd09eff  Protection_Request_Interface.c
7b9c3b01807e001d810f15841d3f747a6ef340cee3cf59568c1f43667a1f289a  QA_SYNTHETIC_ONLY/ChargeLimit/CORRUPTED_PROTOCOL_SYNTHETIC/NORMALIZED.csv
c269cfcc5bb6d0da1e99900bc851c0ab39eb880ab63a9535efffd5d5dbbbcfd0  QA_SYNTHETIC_ONLY/ChargeLimit/CORRUPTED_PROTOCOL_SYNTHETIC/RESULT.json
7e9a4ba2423b5c6d82c9714bd7891a6937348e1051f5fdb27720a912a0b2a206  QA_SYNTHETIC_ONLY/ChargeLimit/CORRUPTED_SYNTHETIC/NORMALIZED.csv
2ac0ddb7c095b6afad1b7caa3fd643cffe6c1a548c47863529ed2b92facf5a54  QA_SYNTHETIC_ONLY/ChargeLimit/CORRUPTED_SYNTHETIC/RESULT.json
7b9c3b01807e001d810f15841d3f747a6ef340cee3cf59568c1f43667a1f289a  QA_SYNTHETIC_ONLY/ChargeLimit/NOMINAL_SYNTHETIC/NORMALIZED.csv
de94d82635596110d472e0146ce2a4b20ba2bfb840ef2f8d2330c8ae3c9d7600  QA_SYNTHETIC_ONLY/ChargeLimit/NOMINAL_SYNTHETIC/RESULT.json
622bf04f3e9cf1439831978170b3c68482cad47107b26254f364a775d2ec8ce9  QA_SYNTHETIC_ONLY/ChargeLimit/bms_CORRUPTED_SYNTHETIC.csv
2dae47f4b7eba4ef610870fb2fe5ba4f8375216e92bd75f0c0d80b260f4003b1  QA_SYNTHETIC_ONLY/ChargeLimit/bms_SYNTHETIC.csv
afb46d28ca172bc64992d4879f21f1e47baee2aeb7658ac6a2b522973f223120  QA_SYNTHETIC_ONLY/ChargeLimit/generator_CORRUPTED_SYNTHETIC.csv
8757f7eae0d3f40e9ba1a767790842beed6936d2df2219e9ac56613c8364b74b  QA_SYNTHETIC_ONLY/ChargeLimit/generator_SYNTHETIC.csv
e10c34bb8e67e2f2bc6de28a6061616a672b262eef0209757d7fe91ca2e7fc81  QA_SYNTHETIC_ONLY/ChargeLimit/plus_SYNTHETIC.csv
366374841335c591f16ba1277d299234b8f151ddd99170d89fcf0be137117028  QA_SYNTHETIC_ONLY/ChargeLimit/vehicle_SYNTHETIC.csv
0b09d35d61a5b617505f389c2d8147e30bc73ebe34d73cd873e96a069e8bb069  QA_SYNTHETIC_ONLY/Protection/CORRUPTED_PROTOCOL_SYNTHETIC/NORMALIZED.csv
be8ef53417d8f3c815859c609c2f47ff05216cf8c096e958c4e369d56ab15b50  QA_SYNTHETIC_ONLY/Protection/CORRUPTED_PROTOCOL_SYNTHETIC/RESULT.json
c945f6283e984ce6f3a8ce4187dda68228005b92f504fede2b52929d91fe4ca4  QA_SYNTHETIC_ONLY/Protection/CORRUPTED_SYNTHETIC/NORMALIZED.csv
a1170644e146aa210605df09e494fe9f7218f8929b554c7bbf8099ec2ecba85c  QA_SYNTHETIC_ONLY/Protection/CORRUPTED_SYNTHETIC/RESULT.json
0b09d35d61a5b617505f389c2d8147e30bc73ebe34d73cd873e96a069e8bb069  QA_SYNTHETIC_ONLY/Protection/NOMINAL_SYNTHETIC/NORMALIZED.csv
bdf6ee0404bf5448b7118001ce7ddc2be354dddef7f451f297ed15f8af0b10fe  QA_SYNTHETIC_ONLY/Protection/NOMINAL_SYNTHETIC/RESULT.json
4c353bb808ce84e57d4ef7c56828cb8ce1795e139e5108644ca5cea2a00aec46  QA_SYNTHETIC_ONLY/Protection/bms_CORRUPTED_SYNTHETIC.csv
7fa7209abde73f79910264788d6ad57bd33055a44f2330f600277cc3d0d13d8e  QA_SYNTHETIC_ONLY/Protection/bms_SYNTHETIC.csv
551f5a9bf10ca18dce0da75d532e0861ba388342291714ff3883dfd320031e32  QA_SYNTHETIC_ONLY/Protection/generator_CORRUPTED_SYNTHETIC.csv
10a3e5124ecd2915be19755163c6cd263cf9a216b019d9ab73a859d729c41d86  QA_SYNTHETIC_ONLY/Protection/generator_SYNTHETIC.csv
3f6676c7aa6960fbca5b298d408326bb66bacfe94802e2ea155f0048c9ffffc6  QA_SYNTHETIC_ONLY/Protection/plus_SYNTHETIC.csv
366374841335c591f16ba1277d299234b8f151ddd99170d89fcf0be137117028  QA_SYNTHETIC_ONLY/Protection/vehicle_SYNTHETIC.csv
483fa8b61355bd6bcba4359d71c51a6c48e0c90b5cd5baa1fe28f4928f66fbfe  QA_SYNTHETIC_ONLY/README.txt
d99e642d8079e8a3d3450f1c7358baa5c380e63e4ce88bd22a002a88d5f5a0f2  QA_SYNTHETIC_ONLY/Restart/CORRUPTED_PROTOCOL_SYNTHETIC/NORMALIZED.csv
5b20378a9d48cee60d421274084ae232cb4444419862e95bea8be951b2ebf8bc  QA_SYNTHETIC_ONLY/Restart/CORRUPTED_PROTOCOL_SYNTHETIC/RESULT.json
75b9635b69a3eb280d0b100de69b1363d7b366d7a63b2cca6c24f16fad797562  QA_SYNTHETIC_ONLY/Restart/CORRUPTED_SYNTHETIC/NORMALIZED.csv
7438e1b1d180e046b0413209872178cfaa165edd48f1236424d65ad8a2ab5fda  QA_SYNTHETIC_ONLY/Restart/CORRUPTED_SYNTHETIC/RESULT.json
d99e642d8079e8a3d3450f1c7358baa5c380e63e4ce88bd22a002a88d5f5a0f2  QA_SYNTHETIC_ONLY/Restart/NOMINAL_SYNTHETIC/NORMALIZED.csv
d1bb9d677f063d2a256e2da89e63e5358723b67823498d02f290e9c532a6b6ba  QA_SYNTHETIC_ONLY/Restart/NOMINAL_SYNTHETIC/RESULT.json
b56a429ef855634b9a9b5f55574af83b3e2f305364250248785291a92ca9bf54  QA_SYNTHETIC_ONLY/Restart/bms_CORRUPTED_SYNTHETIC.csv
480763c85c31cbf65bd3c14baefc1880bb21a5f4d2fcb03947bf10429fc0edac  QA_SYNTHETIC_ONLY/Restart/bms_SYNTHETIC.csv
e3cbfda41392ec0ff38b9d909bc0a5f82b5fe22aa3669ea2eb524e4ca8a44964  QA_SYNTHETIC_ONLY/Restart/generator_CORRUPTED_SYNTHETIC.csv
e29da174ea98c100c66a8cbb8ab78c2456678fb95ec178caa9311a04d7fdff88  QA_SYNTHETIC_ONLY/Restart/generator_SYNTHETIC.csv
e5e7149e3f6453fe459ae74ec991f11018accec14a5c49eaab6c1b235eaf36f9  QA_SYNTHETIC_ONLY/Restart/plus_SYNTHETIC.csv
0123c4bbde318b1b5f319ce58cba9b8e88ba8640a9f51f84d33870e0a482ab8c  QA_SYNTHETIC_ONLY/Restart/vehicle_SYNTHETIC.csv
c184d5ac78530e962a4137240b22dab412226b34da175f514e92cdf9b599e0ca  README_START_HERE_KO.md
cc6dc08d26d5cb8e0b4f5c882f1cf06af580352ecb97bc86f06953e9aed6dfd5  Restart_REFERENCE_ONLY.csv
b99ccc9d049e33e3dfbf01ccf0f2c1f1a9c21c6fc618c1cb4532a2b24b4cd274  Restart_Request_Interface.c
8aef0e5d74db255912cf52bc45f556feaf69803d0fb2172d2d9ed284be36902e  VERIFICATION.log
7295087f6660db92fe105ee53a2a4498cccd2819c0bc3405c73c4a18cb3f8c78  build_scenarios.py
d5c137be4a0f70e7b9b6272d1584801a9fdfcedbd89a6269086508acc9cd0d20  check_evaluator.py
a24e314a098e7acbeb0de382c748b66e163e7f58d59d29c43f58221697d1ba0b  evaluate_scenario.py
0754f46a6df5e888903106d5c8128d47e46a5d99049b38a2bfe47219f6582db2  inputs/EREV_Request26_Connected_R1.proj
4581670b762fc95083bc7014dfc015d0c76e9370ae5203d51b3f9a649a0a0d58  source_reference.py

```
