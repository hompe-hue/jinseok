# EREV 요청형 26 kW 전원 연결 시험

## 실행 파일

EREV_Request26_Connected.proj는 기존 2 ms·16 s 정차 시험을 복제한 연결본이다. EREV_Request26.fmu의 실제 공급을 기존 HV Bus와 Ground에 주입한다. 새 Request Interface가 ON/OFF 요청과 실제 부하·충전수용 값을 전달하고 Generator Monitor가 13개 신호를 기록한다.

1. 동봉 EREV_Request26.fmu를 C:/CRUISEM/EREV_Request26.fmu에 복사한다. 폴더가 없으면 만든다. 프로젝트에 저장된 경로다. 다른 위치를 사용하려면 Electrical FMU 1 → File에서 이 FMU를 선택한다.
2. EREV_Request26_Connected.proj를 열고 REEV_MBE → Cycle Run → ANL61905060을 실행한다.
3. 방금 완료된 결과의 Generator Monitor, Electrical FMU 1 Plus, BMS Monitor, Vehicle Monitor를 CSV로 내보낸다. 첫 확인은 Generator Monitor CSV다. 출력은 기존과 같은 2 ms, 0–16 s다.

## 연결 내용

Request Interface는 1 s에 ON 요청을 주고 2 s에 OFF 요청을 준다. 발전원 상태기는 최소 ON 10 s 때문에 약 11 s까지 운전한 뒤 정상 정지한다. 지연 0.5 s, 상승 20 kW/s, 하강 50 kW/s를 적용하므로 대략 1.5 s 상승 시작, 2.8 s에 26 kW, 11.52 s 공급 0을 기대한다. 요청·상태 전이는 통신 스텝으로 양자화된다. 정확한 시각과 파형 오차는 이번 실제 CSV로 확인한다.

실제 부하는 E-Motor Electric power와 Power Consumer Power loss를 합산한다. 충전허용전력은 BMS ECM Max. Power Charge의 절댓값과 기존 160 A 한도의 버스전압 환산값 중 작은 값이다. 버스전압은 기존 차량 전류 분석과 같은 HV Battery Voltage Out에서 받는다. 보호 OFF 요청은 이번 정차 인터페이스에서 0이며, FMU의 기존 수치 전압창 100–500 V 보호가 동작한다. 차량 보호 연동은 이 시험 이후 확장 대상이다.

이 시험은 26 kW 공급원 동특성 가정과 요청 인터페이스의 연결을 확인한다. 실차 엔진 연료맵이나 물리 기동 모델은 아직 적용하지 않았다. 기존 native 엔진·발전기는 OFF다. 배터리·모터·차량 제원은 출발 프로젝트를 유지했다.

## 전력 부호와 집계

공급할 때 I_terminal_A와 P_terminal_W는 음수다. P_generated_W와 E_generated_J는 공급 양수다. 기존 BMS ECM의 Generator Work 함수는 -min(0,입력전력)을 적분하므로 P_terminal_W를 연결했다. Vehicle Current Analysis의 Generator Current에는 I_terminal_A를 연결했다. 두 집계의 기존 native Generator 입력선을 교체했다.

Generator Monitor에는 요청, 실제 부하, 충전허용, 허용 목표, 실제 발전전력, 단자 전력/전류, 상태, 기동횟수, ON/OFF 경과시간, 보호상태, 생성에너지가 기록된다. Target W는 수용성으로 정한 허용 목표이므로 OFF 중에도 값이 있을 수 있다. 실제 공급 판단에는 Generated W와 Plus 단자 전력을 사용한다.

상태 번호는 OFF 0, STARTING 1, RAMP 2, RUN 3, STOPPING 4다. 이번 요청 시험의 기대 기동횟수는 1이다. 요청은 2 s부터 OFF이지만 최소 ON이 끝날 때까지 상태와 실제 출력이 유지되는지 확인한다.

## 확인 완료 및 실행 범위

- 요청형 FMU의 Linux 바이너리와 기존 참조 규칙을 여섯 시나리오·각 10,000 스텝에서 대조했다.
- reset, 독립 인스턴스, 잘못된 입력 갱신의 원자성을 확인했다.
- Windows x64 DLL을 실제 크로스 컴파일하고 PE 형식·FMI export 및 import/TLS 부재를 검사했다.
- 공식 FMI 2.0.5 XSD 검증을 통과했다.
- 프로젝트 XML, ID 중복·누락 참조, 새 신호 및 집계 연결 23개의 실제 포트 존재와 방향을 검사했다.
- Request Interface의 C 코드를 별도로 컴파일해 요청 경계와 부하 합산·충전전류 한도 환산을 확인했다.

이 환경에서 CRUISE M을 실행하지 않았으므로 연결본의 실제 모델 로드·수렴·CSV 출력은 사용자 PC 확인이 남아 있다. PROJECT_QA.json, FMU_BUILD_TESTS.json, SOURCES 및 build/check 스크립트에 검증 기록을 보존했다. 기존 T1 완료 기록은 그대로 보존한다.

## 재현

inputs/Explicit2ms.proj가 출발 저장본이다. python build_project.py 및 python check_project.py로 연결본과 구조 검사를 재현할 수 있다. FMU 구현은 SOURCES/EREV_Request26.c에 있다. Linux gcc 및 Zig 0.13.0을 사용하는 바이너리 재현 절차와 여섯 시나리오 전체 trace는 별도 EREV_Request26_FMU_Build.zip에 보존했다.

다음 시작점은 이 연결본의 Generator Monitor와 동일 실행 Plus/BMS/Vehicle CSV를 받아 외부 요청·최소 유지시간·실제 집계 및 공통 버스 수지를 확인하는 것이다.
{
  "status": "STATIC_CONNECTED_PROJECT_READY",
  "source_sha256": "3a9b59154485708945147bed4834bc3bf0f37817ba68105452b177162f82fec4",
  "output_sha256": "c2ceb83726d921ba9f3340eb5fe86a4480df6e351eb91e23f2f80640ea9553de",
  "new_connections": [
    [
      "E-Motor",
      "Electric power",
      "Request Interface",
      "Motor Power"
    ],
    [
      "Power Consumer",
      "Power loss",
      "Request Interface",
      "Consumer Power"
    ],
    [
      "BMS ECM",
      "Max. Power Charge",
      "Request Interface",
      "Charge Acceptance"
    ],
    [
      "HV Battery",
      "Voltage Out",
      "Request Interface",
      "Bus Voltage"
    ],
    [
      "Request Interface",
      "Request ON",
      "Electrical FMU 1",
      "request_on"
    ],
    [
      "Request Interface",
      "Load W",
      "Electrical FMU 1",
      "P_load_W"
    ],
    [
      "Request Interface",
      "Charge Available W",
      "Electrical FMU 1",
      "P_charge_available_W"
    ],
    [
      "Request Interface",
      "Protection OFF",
      "Electrical FMU 1",
      "protection_off"
    ],
    [
      "Request Interface",
      "Request ON",
      "Generator Monitor",
      "Request ON"
    ],
    [
      "Request Interface",
      "Load W",
      "Generator Monitor",
      "Load W"
    ],
    [
      "Request Interface",
      "Charge Available W",
      "Generator Monitor",
      "Charge Available W"
    ],
    [
      "Electrical FMU 1",
      "P_target_W",
      "Generator Monitor",
      "Target W"
    ],
    [
      "Electrical FMU 1",
      "P_generated_W",
      "Generator Monitor",
      "Generated W"
    ],
    [
      "Electrical FMU 1",
      "P_terminal_W",
      "Generator Monitor",
      "Terminal Power W"
    ],
    [
      "Electrical FMU 1",
      "I_terminal_A",
      "Generator Monitor",
      "Terminal Current A"
    ],
    [
      "Electrical FMU 1",
      "state",
      "Generator Monitor",
      "State"
    ],
    [
      "Electrical FMU 1",
      "start_count",
      "Generator Monitor",
      "Start Count"
    ],
    [
      "Electrical FMU 1",
      "on_elapsed_s",
      "Generator Monitor",
      "ON Elapsed s"
    ],
    [
      "Electrical FMU 1",
      "off_elapsed_s",
      "Generator Monitor",
      "OFF Elapsed s"
    ],
    [
      "Electrical FMU 1",
      "protection_active",
      "Generator Monitor",
      "Protection Active"
    ],
    [
      "Electrical FMU 1",
      "E_generated_J",
      "Generator Monitor",
      "Generated Energy J"
    ]
  ],
  "rewired_aggregation": [
    "I_terminal_A to Vehicle Current Analysis",
    "P_terminal_W to BMS ECM Generator Power"
  ],
  "CRUISE_runs": 0,
  "new_component": "Request Interface",
  "test_request": "ON 1 s, OFF request 2 s, 16 s stationary bench",
  "immutable_scope": "Physical DC wiring and validated 2 ms solver retained; native engine/generator OFF",
  "windows_execution": "Pending user CRUISE M run",
  "endpoint_direction_checks": 23,
  "all_added_ports_and_directions": "PASS",
  "protocol_monitor": "Generator Monitor, 13 explicitly wired channels",
  "monitor_port_names": [
    "Charge Available W",
    "Generated Energy J",
    "Generated W",
    "Load W",
    "OFF Elapsed s",
    "ON Elapsed s",
    "Protection Active",
    "Request ON",
    "Start Count",
    "State",
    "Target W",
    "Terminal Current A",
    "Terminal Power W"
  ],
  "request_interface_compiled_check": "PASS: independently compiled C, ON edges and 160 A charging cap checked",
  "implementation_commit": "ebb233f049fb4c638957a1249b018689041912d2"
}
"""Build the isolated request-interface bench from the verified Explicit2ms project."""
from copy import deepcopy, copy
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import base64
import hashlib
import json
import re
import struct

root = Path(__file__).resolve().parent
source = root/'inputs/Explicit2ms.proj'
target = root/'EREV_Request26_Connected.proj'
with ZipFile(source) as archive:
    original = archive.read('project.xml').decode()
tree = ET.fromstring(original)
definitions = {n.get('id'):n for n in tree.iter() if n.get('id') and n.tag != 'ref'}
next_id = max(int(key) for key in definitions) + 1

def resolve(node):
    return definitions[node.get('id')] if node.tag == 'ref' else node

def fields(node):
    data = resolve(node).find('dict')
    return {data[i].text:data[i+1] for i in range(0,len(data)-1,2)}

def set_scalar(obj, key, text):
    node = fields(obj)[key]
    node.text = text

def clone(node):
    global next_id
    result = deepcopy(resolve(node))
    ids = {}
    for item in result.iter():
        old_id = item.get('id')
        if old_id and item.tag != 'ref':
            ids[old_id] = str(next_id)
            next_id += 1
    for item in result.iter():
        if item.get('id') in ids:
            item.set('id',ids[item.get('id')])
    return result

def object_span(text, object_id):
    match = re.search(r'<(object|dict|list|set|tuple)\b[^>]*\bid="' + str(object_id) + r'"[^>]*>',text)
    assert match
    depth = 1
    for tag in re.finditer(r'</?' + match.group(1) + r'\b[^>]*>',text[match.end():]):
        token = tag.group()
        depth += -1 if token.startswith('</') else (0 if token.endswith('/>') else 1)
        if depth == 0:
            return match.start(),match.end()+tag.end()
    raise ValueError('Object end not found')

def replace_object(text, object_id, node):
    start,end = object_span(text,object_id)
    return text[:start]+ET.tostring(node,encoding='unicode')+text[end:]

def dictionary_append(container, name, node):
    label=ET.Element('str')
    label.text=name
    container.extend([label,node])

def port_entries(topology):
    container=fields(topology)['_ports']
    return container,{container[i].text:container[i+1] for i in range(0,len(container)-1,2)}

# Clone an existing C Function, retaining its component type and serialization layout.
function = clone(definitions['35921'])
props=fields(function)['_props']
properties={props[i].text:props[i+1] for i in range(0,len(props)-1,2)}
code=fields(properties['c_function'])['function_editor']
code.attrib.pop('coding',None)
code.text = """/* Request-interface bench. Powers are W. Positive load means consumption. */
y[0] = (realTime >= 1.0 && realTime < 2.0) ? 1.0 : 0.0;
y[1] = a[0] + a[1];
/* Preserve the existing research BMS 160 A charging-current ceiling. */
y[2] = min(fabs(a[2]), 160.0 * max(0.0, a[3]));
y[3] = 0.0; /* Bench protection request. FMU voltage guard remains active. */
"""
step=fields(properties['cosimulation_settings'])['component_step_size']
set_scalar(step,'active','const')
amount=fields(step)['const']
set_scalar(amount,'value','0.002')
out_settings=fields(properties['output_settings'])
out_settings['data_buses_as_results'].tag='true'
topology=list(fields(function)['_topos'])[0]
function_ports, entries = port_entries(topology)
in_template = next(value for value in entries.values()
                   if 'CFunctionDatabusIn' in ET.tostring(value,encoding='unicode'))
out_template = next(value for value in entries.values()
                    if 'CFunctionDatabusOut' in ET.tostring(value,encoding='unicode'))
function_ports[:] = []
function_inputs = [('Motor Power','power~W'),('Consumer Power','power~W'),
                   ('Charge Acceptance','power~W'),('Bus Voltage','voltage~V')]
function_outputs = [('Request ON','no_unit~none'),('Load W','power~W'),
                    ('Charge Available W','power~W'),('Protection OFF','no_unit~none')]
for direction,port_list,template in [('IN',function_inputs,in_template),('OUT',function_outputs,out_template)]:
    for index,(name,unit) in enumerate(port_list):
        new=clone(template)
        data=fields(new)['data']
        fields(data)['unit'].find('str').text=unit
        set_scalar(data,'stc_name',f'{direction}_PORT_{index}')
        dictionary_append(function_ports,name,new)

# Preserve the physical electrical terminals and replace/add only FMU data ports.
fmu=deepcopy(definitions['76793'])
fmu_props=fields(fmu)['_props']
fp={fmu_props[i].text:fmu_props[i+1] for i in range(0,len(fmu_props)-1,2)}
for value in fmu.iter('str'):
    if value.text=='C:/CRUISEM/EREV_T1_26kW.fmu':
        value.text='C:/CRUISEM/EREV_Request26.fmu'
info=fp['fmu_info']
for key,val in [('name','EREV_Request26'),('cosim_model_identifier','EREV_Request26'),
                ('guid','{c98a6c50-5372-4fab-bf13-31f268e159d0}'),
                ('description','Request-driven 26 kW research source')]:
    set_scalar(info,key,val)
set_scalar(fields(info)['default_experiment'],'step_size','0.002')
fmu_top=list(fields(fmu)['_topos'])[0]
ports,entries=port_entries(fmu_top)
input_template=entries['V_bus_V']
output_template=entries['P_command_W']
ports[:] = list(ports)[:0]
for name in ('Plus','Minus','V_bus_V','I_terminal_A'):
    dictionary_append(ports,name,entries[name])
manifest=json.loads((root/'BUILD_MANIFEST.json').read_text())
for item in manifest['variables']:
    name,vr,direction=item['name'],item['VR'],item['causality']
    if direction=='parameter' or name in ('V_bus_V','I_terminal_A'):
        continue
    new=clone(input_template if direction=='input' else output_template)
    data=fields(new)['data']
    set_scalar(data,'name_in_fmu',name)
    set_scalar(data,'varref',str(vr))
    inputs=['V_bus_V','request_on','P_load_W','P_charge_available_W','protection_off']
    outputs=['I_terminal_A']+[v['name'] for v in manifest['variables']
                              if v['causality']=='output' and v['name']!='I_terminal_A']
    index=(inputs if direction=='input' else outputs).index(name)
    set_scalar(data,'stc_name',('IN' if direction=='input' else 'OUT')+f'_PORT_{index}')
    unit={'V':'voltage~V','A':'amperage~A','W':'power~W','J':'energy~J','s':'time~s',None:'no_unit~none'}[item['unit']]
    fields(data)['unit'].find('str').text=unit
    dictionary_append(ports,name,new)

# Use the existing monitor component type so protocol channels have a dedicated CSV entry.
monitor = clone(definitions['69264'])
monitor_top = next(node for node in fields(monitor)['_topos']
                   if node.get('type') == 'cruise.elements.monitor.Topology')
monitor_ports, monitor_entries = port_entries(monitor_top)
monitor_template = monitor_entries['Voltage']
monitor_ports[:] = []
monitor_signals = [
    ('Request ON','Request Interface','Request ON','no_unit~none'),
    ('Load W','Request Interface','Load W','power~W'),
    ('Charge Available W','Request Interface','Charge Available W','power~W'),
    ('Target W','Electrical FMU 1','P_target_W','power~W'),
    ('Generated W','Electrical FMU 1','P_generated_W','power~W'),
    ('Terminal Power W','Electrical FMU 1','P_terminal_W','power~W'),
    ('Terminal Current A','Electrical FMU 1','I_terminal_A','amperage~A'),
    ('State','Electrical FMU 1','state','no_unit~none'),
    ('Start Count','Electrical FMU 1','start_count','no_unit~none'),
    ('ON Elapsed s','Electrical FMU 1','on_elapsed_s','time~s'),
    ('OFF Elapsed s','Electrical FMU 1','off_elapsed_s','time~s'),
    ('Protection Active','Electrical FMU 1','protection_active','no_unit~none'),
    ('Generated Energy J','Electrical FMU 1','E_generated_J','energy~J'),
]
for index,(name,_,_,unit) in enumerate(monitor_signals):
    new = clone(monitor_template)
    data = fields(new)['data']
    fields(data)['unit'].find('str').text = unit
    set_scalar(data,'stc_name',f'IN_PORT_{index}')
    dictionary_append(monitor_ports,name,new)

# Add the input block to the existing System child dictionary by a reference to its own definition.
children=deepcopy(definitions['35581'])
dictionary_append(children,'Request Interface',function)
dictionary_append(children,'Generator Monitor',monitor)

# Add a visible role using the existing C Function's layout.
system_top=deepcopy(definitions['76957'])
visible=fields(system_top)['_visroles']
visible_entries={visible[i].text:visible[i+1] for i in range(0,len(visible)-1,2)}
role=clone(visible_entries['Vehicle Current Analysis'])
for obj in role.findall(".//object[@type='AVBlockModeller.block_editor_data.RoleInfoData;v=5']"):
    p=fields(obj)
    for field,val in [('pos',(5.0,-3.0,0.0)),('pos_name',(0.0,-.25,0.0))]:
        if field in p:
            p[field].text=base64.b64encode(struct.pack('<ddd',*val)).decode()
dictionary_append(visible,'Request Interface',role)
monitor_role = clone(visible_entries['BMS Monitor'])
for obj in monitor_role.findall(".//object[@type='AVBlockModeller.block_editor_data.RoleInfoData;v=5']"):
    p = fields(obj)
    if 'pos' in p:
        p['pos'].text = base64.b64encode(struct.pack('<ddd',8.0,-3.0,0.0)).decode()
dictionary_append(visible,'Generator Monitor',monitor_role)

connections=fields(system_top)['_conn_list']
if connections.tag=='ref':
    connections=deepcopy(resolve(connections))
    old=fields(system_top)['_conn_list']
    parent=system_top.find('dict')
    parent[list(parent).index(old)]=connections
existing=[n for n in connections if n.tag=='object']
assert any(n.get('id')=='78047' for n in existing)
assert any(n.get('id')=='78693' for n in existing)
for obj,port in [('78047','I_terminal_A'),('78693','P_terminal_W')]:
    node=next(n for n in existing if n.get('id')==obj)
    set_scalar(node,'role1','Electrical FMU 1')
    set_scalar(node,'port1',port)

wire_template=definitions['78047']
new_wires=[
    ('E-Motor','Electric power','Request Interface','Motor Power'),
    ('Power Consumer','Power loss','Request Interface','Consumer Power'),
    ('BMS ECM','Max. Power Charge','Request Interface','Charge Acceptance'),
    ('HV Battery','Voltage Out','Request Interface','Bus Voltage'),
    ('Request Interface','Request ON','Electrical FMU 1','request_on'),
    ('Request Interface','Load W','Electrical FMU 1','P_load_W'),
    ('Request Interface','Charge Available W','Electrical FMU 1','P_charge_available_W'),
    ('Request Interface','Protection OFF','Electrical FMU 1','protection_off'),
]
new_wires += [(role,port,'Generator Monitor',name) for name,role,port,_ in monitor_signals]
for start,port1,end,port2 in new_wires:
    wire=clone(wire_template)
    for key,val in [('role1',start),('port1',port1),('role2',end),('port2',port2)]:
        set_scalar(wire,key,val)
    connections.append(wire)

# Replace only the three affected serialized objects. Their definitions remain in their original location.
patched=original
patched=replace_object(patched,'76793',fmu)
patched=replace_object(patched,'35581',children)
# The children dictionary includes the old FMU copy, so apply its updated object after insertion.
patched=replace_object(patched,'76793',fmu)
patched=replace_object(patched,'76957',system_top)
modified=ET.fromstring(patched)
ids=[n.get('id') for n in modified.iter() if n.get('id') and n.tag!='ref']
id_set = set(ids)
assert len(ids)==len(id_set), 'Duplicate serialization ID'
assert all(n.get('id') in id_set for n in modified.iter('ref')), 'Dangling reference'
for name in ['request_on','P_load_W','P_charge_available_W','protection_off']:
    assert sum(fields(n).get('port2') is not None and fields(n)['port2'].text==name
               for n in modified.findall(".//object[@type='act.topo.Connection']"))==1
# Preserve established solver and physical parameters.
newdefs={n.get('id'):n for n in modified.iter() if n.get('id') and n.tag!='ref'}
assert fields(newdefs['79908'])['time_step_type'].find('str').text=='fixed'
assert fields(newdefs['79909'])['value'].text=='0.002'
assert fields(newdefs['75557'])['value'].text=='2000.0'
# Find the decoded control body directly, because encoded strings may wrap across lines.
native_off_code = []
for node in tree.iter('str'):
    if node.get('coding') != 'base64':
        continue
    try:
        decoded = base64.b64decode(node.text or '').decode()
    except (ValueError, UnicodeDecodeError):
        continue
    if 'BEV baseline:' in decoded:
        native_off_code.append(decoded)
assert len(native_off_code) == 1 and 'operating_mode_out = mode_eDrive;' in native_off_code[0]
with ZipFile(source) as old,ZipFile(target,'w') as out:
    out.comment=old.comment
    for entry in old.infolist():
        out.writestr(copy(entry),patched.encode() if entry.filename=='project.xml' else old.read(entry))
with ZipFile(target) as out:
    assert out.testzip() is None
result=dict(status='STATIC_CONNECTED_PROJECT_READY',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            new_connections=new_wires,rewired_aggregation=['I_terminal_A to Vehicle Current Analysis',
                                                        'P_terminal_W to BMS ECM Generator Power'],
            CRUISE_runs=0,new_component='Request Interface',
            test_request='ON 1 s, OFF request 2 s, 16 s stationary bench',
            immutable_scope='Physical DC wiring and validated 2 ms solver retained; native engine/generator OFF',
            windows_execution='Pending user CRUISE M run')
(root/'PROJECT_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(root/'REQUEST_INTERFACE.c').write_text(code.text)
print(result['status'])
"""Resolve the serialized model graph and verify every added data connection."""
from pathlib import Path
from xml.etree import ElementTree as E
from zipfile import ZipFile
import json

root=Path(__file__).resolve().parent
path=root/'EREV_Request26_Connected.proj'
with ZipFile(path) as archive:
    assert archive.testzip() is None
    tree=E.fromstring(archive.read('project.xml'))
index={n.get('id'):n for n in tree.iter() if n.get('id') and n.tag!='ref'}

def resolve(node):
    return index[node.get('id')] if node.tag=='ref' else node

def fields(node):
    data=resolve(node).find('dict')
    return {data[i].text:data[i+1] for i in range(0,len(data)-1,2)}

children=fields(index['35580'])['_children']
portmap={}
for i in range(0,len(children)-1,2):
    ports={}
    child=resolve(children[i+1])
    for topology in fields(child).get('_topos',[]):
        properties=fields(topology)
        if '_ports' not in properties:
            continue
        data=resolve(properties['_ports'])
        for j in range(0,len(data)-1,2):
            port=fields(data[j+1])['data']
            direction=fields(port).get('direction')
            if direction is not None:
                ports[data[j].text]=direction.find('str').text
    portmap[children[i].text]=ports

connections=resolve(fields(index['76957'])['_conn_list'])
checked=[]
for connection in connections:
    if connection.tag!='object':
        continue
    values=fields(connection)
    start,port1,end,port2=(values[key].text for key in ['role1','port1','role2','port2'])
    relevant=('Request Interface' in (start,end) or 'Generator Monitor' in (start,end) or
              (start=='Electrical FMU 1' and end in ['BMS ECM','Vehicle Current Analysis']))
    if relevant:
        assert portmap[start][port1]=='OUT',(start,port1)
        assert portmap[end][port2]=='IN',(end,port2)
        checked.append([start,port1,end,port2])
assert len(checked)==23
manifest=json.loads((root/'BUILD_MANIFEST.json').read_text())
fmu_names={row['name'] for row in manifest['variables'] if row['causality']!='parameter'}
assert fmu_names.issubset(portmap['Electrical FMU 1'])
qa=root/'PROJECT_QA.json'
result=json.loads(qa.read_text())
result.update(endpoint_direction_checks=len(checked),all_added_ports_and_directions='PASS',
              protocol_monitor='Generator Monitor, 13 explicitly wired channels',
              monitor_port_names=sorted(portmap['Generator Monitor']))
qa.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('23 connected endpoint directions and all FMU variable ports PASS')
43c24e6258d2e33e135e2ca484ff0d217e2aedb66e490f3ef474328623d6e513  outputs/EREV_Request26_Connected_Package.zip
