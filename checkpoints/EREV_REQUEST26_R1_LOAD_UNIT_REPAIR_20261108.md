# 요청형 발전원 프로젝트 로드 오류 수정본 R1

추가한 에너지 출력과 Generator Monitor 에너지 입력 두 곳에 CRUISE M 원본에서 사용되지 않는 energy~J 식별자가 들어 있었다. 원본 프로젝트에서 J 단위는 work~J로 저장된다. 해당 두 곳을 work~J로 수정했다. 오류 화면만으로 AVL 로더의 정확한 예외를 확인한 것은 아니므로, 이 수정이 실제 로드 실패를 해결했는지는 PC에서 확인해야 한다.

## 이번 변경과 검증

에너지 채널의 직렬화 단위 두 값만 수정했다. FMU 바이너리는 그대로이며 SHA-256과 바이트 일치를 확인했다. XML 파싱·압축 무결성, 중복 ID·선행 정의 없는 참조가 없음을 검사했다. 수정본에 사용된 단위 식별자는 모두 정상 로드된 출발 프로젝트에 존재한다. 신호 연결 23개의 포트 존재와 IN/OUT 방향도 재검사했다. 실제 CRUISE M 로드·실행은 확인 전이다.

## 실행

1. EREV_Request26_Connected_R1.proj를 연다. 동봉 EREV_Request26.fmu의 프로젝트 저장 경로는 C:/CRUISEM/EREV_Request26.fmu다. 이 위치에 복사하거나 Electrical FMU 1의 File에서 동봉 FMU를 선택한다.
2. 모델이 열리면 REEV_MBE → Cycle Run → ANL61905060을 실행한다.
3. 같은 Project Loading Failed 오류가 반복되면 오류 창의 파란 avl-error-report-*.debug 링크 또는 옆 폴더 아이콘으로 보고서를 찾아 첨부한다. 해당 파일의 실제 예외를 확인해야 추가 구조 오류를 식별할 수 있다.
4. 실행이 완료되면 새 Generator Monitor의 Request ON, Generated W, State, Start Count와 Plus/BMS/Vehicle 결과를 확인한다.

이 파일은 1 s ON, 2 s OFF 요청과 최소 운전시간을 확인하는 26 kW 정차 연결 시험이다. 기존 T1 수치 통과 기록은 그대로 보존한다.

## 재현 파일

REPAIR_CHECKPOINT.json에 수정 전후 해시와 정확한 두 필드를 기록했다. check_project.py는 연결 포트 검사를 재현한다. build_project.py는 동봉 inputs/Explicit2ms.proj에서 수정된 단위를 사용해 새 연결본을 생성한다. repair_project.py는 이전 EREV_Request26_Connected.proj 경로를 인수로 받아 두 단위 값만 수정하는 과정을 재현한다.
{
  "status": "UNIT_SERIALIZATION_DEFECT_CORRECTED",
  "changed_unit_values": [
    {
      "tag": "str",
      "before": "energy~J",
      "after": "work~J"
    },
    {
      "tag": "str",
      "before": "energy~J",
      "after": "work~J"
    }
  ],
  "source_sha256": "c2ceb83726d921ba9f3340eb5fe86a4480df6e351eb91e23f2f80640ea9553de",
  "corrected_sha256": "0754f46a6df5e888903106d5c8128d47e46a5d99049b38a2bfe47219f6582db2",
  "previously_unseen_units": [
    "energy~J"
  ],
  "remaining_unseen_units": [],
  "forward_references": 0,
  "duplicate_ids": 0,
  "fmu_changed": false,
  "exact_loader_exception": "Not received; screenshot identifies project-load failure only",
  "CRUISE_M_load_and_execution": "PENDING",
  "next_start": "Open R1 project and execute ANL61905060. If loading still fails, provide generated .debug error report."
}
"""Correct only the two newly introduced serialized joule-unit identifiers."""
from copy import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

workspace=Path(__file__).resolve().parents[2]
root=Path(__file__).resolve().parent
source=Path(sys.argv[1]) if len(sys.argv)>1 else workspace/'outputs/erev_request_connected/EREV_Request26_Connected.proj'
base=root/'inputs/Explicit2ms.proj'
target=root/'EREV_Request26_Connected_R1.proj'
before=b'<str>energy~J</str>'
after=b'<str>work~J</str>'
with ZipFile(source) as old:
    original=old.read('project.xml')
    assert original.count(before)==2
    modified=original.replace(before,after)
    with ZipFile(target,'w') as new:
        new.comment=old.comment
        for entry in old.infolist():
            new.writestr(copy(entry),modified if entry.filename=='project.xml' else old.read(entry))
    with ZipFile(target) as check:
        assert check.testzip() is None
        assert [name for name in old.namelist() if old.read(name)!=check.read(name)]==['project.xml']
        assert check.read('project.xml')==modified

original_tree,new_tree=ET.fromstring(original),ET.fromstring(modified)
base_tree=ET.fromstring(ZipFile(base).read('project.xml'))

def units(tree):
    return {''.join(node.itertext()).strip()
            for node in tree.findall(".//compose[@type='act.units.Unit']")}

assert units(new_tree).issubset(units(base_tree))
seen=set()
for node in new_tree.iter():
    if node.tag=='ref':
        assert node.get('id') in seen
    elif node.get('id'):
        assert node.get('id') not in seen
        seen.add(node.get('id'))
changes=[]
for old,new in zip(original_tree.iter(),new_tree.iter()):
    assert old.tag==new.tag and old.attrib==new.attrib
    if old.text!=new.text:
        changes.append(dict(tag=old.tag,before=old.text,after=new.text))
assert len(changes)==2
result=dict(
    status='UNIT_SERIALIZATION_DEFECT_CORRECTED',changed_unit_values=changes,
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    corrected_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
    previously_unseen_units=sorted(units(original_tree)-units(base_tree)),
    remaining_unseen_units=sorted(units(new_tree)-units(base_tree)),
    forward_references=0,duplicate_ids=0,fmu_changed=False,
    exact_loader_exception='Not received; screenshot identifies project-load failure only',
    CRUISE_M_load_and_execution='PENDING',
    next_start='Open R1 project and execute ANL61905060. If loading still fails, provide generated .debug error report.')
(root/'REPAIR_CHECKPOINT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
