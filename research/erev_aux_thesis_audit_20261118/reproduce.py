"""Reproduce the auxiliary load evidence from the archived Bolt EV data."""
import csv
import hashlib
import json
import statistics
from argparse import ArgumentParser
from bisect import bisect_left
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


def records(path):
    with path.open(newline='', encoding='utf-8-sig') as file:
        return [{key: float(value) for key, value in row.items()} for row in csv.DictReader(file)]


def average_in_window(rows, clock, channel, start, end):
    times = [row[clock] for row in rows]
    values = [row[channel] for row in rows]
    assert times[0] <= start < end <= times[-1]
    assert max(right - left for left, right in zip(times, times[1:])) <= 0.2
    assert all(right > left for left, right in zip(times, times[1:]))

    def at(time):
        right = bisect_left(times, time)
        if times[right] == time:
            return values[right]
        left = right - 1
        fraction = (time - times[left]) / (times[right] - times[left])
        return values[left] + fraction * (values[right] - values[left])

    points = [(start, at(start))]
    points.extend((t, v) for t, v in zip(times, values) if start < t < end)
    points.append((end, at(end)))
    energy_ws = sum((t1 - t0) * (v0 + v1) / 2
                    for (t0, v0), (t1, v1) in zip(points, points[1:]))
    return energy_ws / (end - start), energy_ws / 3_600_000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_fields(node):
    data = node.find('dict')
    return {key.text: value for key, value in zip(data[::2], data[1::2])}


def verify_project(path):
    project_hash = sha(path)
    assert project_hash == '4048cfc65ce59ea3a708d304bd8623257cd8e9bae62dd60a50b8a90cf3e6b67a'
    with ZipFile(path) as project:
        assert project.testzip() is None
        root = ET.fromstring(project.read('project.xml'))
    consumers = root.findall(".//object[@type='cruise.props.basic_electric_components.PowerConsumerGeneral']")
    assert len(consumers) == 1
    amount = object_fields(object_fields(consumers[0])['power'])
    setting = float(amount['value'].text)
    assert setting == 0.4 and amount['unit'].findtext('str') == 'power~kW'
    expected_ports = ('Vehicle Monitor', 'Consumer Power', 'Power Consumer', 'Power demand')
    ports = ('role1', 'port1', 'role2', 'port2')
    connections = []
    for node in root.findall(".//object[@type='act.topo.Connection']"):
        fields = object_fields(node)
        if tuple(fields[key].text for key in ports) == expected_ports:
            connections.append(node.get('id'))
    assert len(connections) == 2
    return {'file': path.name, 'sha256': project_hash, 'configured_kW': setting,
            'connection_ids': connections, 'cruise_m_runtime_status': 'pending'}


def read_avl(path, signal_columns):
    with path.open(newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        headers, units = next(reader), next(reader)
        cols = [headers.index(name) for name, _ in signal_columns]
        assert all(units[col] == unit for col, (_, unit) in zip(cols, signal_columns))
        return [tuple(float(row[c]) for c in cols) for row in reader if row]


def verify_runtime(bms, vehicle):
    bms_rows = read_avl(bms, [('Time', 's'), ('In/Voltage (BMS Monitor)', 'V'),
                             ('In/Power (BMS Monitor)', 'kW'), ('In/Motor DC Actual (BMS Monitor)', 'kW')])
    vehicle_rows = read_avl(vehicle, [('Time', 's'), ('In/E-Consumer Current (Vehicle Monitor)', 'A')])
    assert len(bms_rows) == len(vehicle_rows) == 7631
    vi, dc = [], []
    for (t_bms, voltage, battery_power, motor_power), (t_veh, aux_current) in zip(bms_rows, vehicle_rows):
        assert t_bms == t_veh
        vi.append(voltage * aux_current / 1000)
        dc.append(-battery_power - motor_power)
    assert max(abs(value - 0.4) for value in vi + dc) < 1e-5
    return {'case': 'PUBLIC_066 logged ancestor of the 30 s project', 'rows': len(vi),
            'aux_from_current_voltage_kW_min_mean_max': [min(vi), statistics.mean(vi), max(vi)],
            'aux_from_DC_balance_kW_min_mean_max': [min(dc), statistics.mean(dc), max(dc)],
            'bms_csv_sha256': sha(bms), 'vehicle_csv_sha256': sha(vehicle)}


def main():
    parser = ArgumentParser()
    for arg in ('repo', 'project', 'bms', 'vehicle', 'output'):
        parser.add_argument('--' + arg, type=Path, required=True)
    a = parser.parse_args()

    build = a.repo / 'research/cruise_m_build_20261011'
    original_dir = build / 'empirical_alignment_20261013/ANL_61905054_phase1'
    original = original_dir / 'ANL_61905054_Phase1_reference_native.csv'
    rec = records(original)
    t054 = 'phase_time_s'
    end054 = rec[-1][t054]
    startup = [row for row in rec if 0 <= row[t054] <= 20]
    assert max(abs(row['measured_speed_kmh']) for row in startup) < 0.001
    assert {row['HVAC_CAN_kW'] for row in rec} == {0.0}
    lv = 'LV_DCDC_output_W'
    factor = statistics.median(row['meter_pack_voltage_V'] *
                               row['meter_pack_current_A_discharge_positive'] / row[lv] for row in startup)
    can_path = build / 'runs/core_evidence_20261013/CAN_boundary_summary.json'
    can = {x['test']: x for x in json.loads(can_path.read_text())}
    harness = a.repo / 'research/erev_harness_20261102/harness'
    registry = json.loads((harness / 'registry.json').read_text())['runs']
    source060 = harness / registry['R0_BASE']['reference']
    source066 = harness / registry['PUBLIC_066']['reference']
    comparisons = [
        ('61905054', original, rec, t054, 0, end054, 'archived HVAC_CAN_kW == 0', 'selection'),
        ('61905060', source060, records(source060), 'phase_time_s', 20, 3150,
         'A/C compressor and pack-heater-request CAN summary', 'cross-check'),
        ('61905066', source066, records(source066), 'time_s', 20, 7630,
         'HVAC channels unavailable in selected reference', 'cross-check'),
    ]
    aux_rows = []
    for test, source, data, clock, start, end, hvac, purpose in comparisons:
        mean, total = average_in_window(data, clock, lv, start, end)
        temperature = 'battery_temperature_CAN_degC' if test == '61905054' else 'battery_temperature_C'
        temperatures = [r[temperature] for r in data if start <= r[clock] <= end]
        aux_rows.append({'ANL_test': test, 'role': purpose, 'start_s': start, 'end_s': end,
                         'LV_DC_DC_mean_W': mean, 'LV_DC_DC_kWh': total,
                         'scaled_HV_proxy_W': mean * factor, 'model_HV_aux_W': 400,
                         'model_HV_aux_kWh': 0.4 * (end - start) / 3600,
                         'battery_C_min': min(temperatures), 'battery_C_max': max(temperatures),
                         'HVAC_evidence': hvac, 'reference_name': source.name, 'sha256': sha(source)})
    assert abs(aux_rows[0]['scaled_HV_proxy_W'] - 392.58771928) < 1e-6
    checked_can = can['61905060']['HV_accessory_reported_channels']
    assert all(x['min'] == x['max'] == 0 for x in checked_can.values())
    state = json.loads((harness / 'reports/state.json').read_text())['runs']
    cases = ('PUBLIC_058', 'PUBLIC_059', 'R0_BASE', 'PUBLIC_066')
    sensitivity_rows = []
    for case in cases:
        metrics = state[case]['metrics']
        end = registry[case]['end_s']
        ref = metrics['reference_net_kWh']
        model = metrics['battery_net_kWh']
        assert abs(metrics['auxiliary_mean_kW'] - 0.4) < 1e-10
        assert metrics['generator_OFF']
        for aux in (0.35, 0.40, 0.45):
            e = (aux - 0.4) * (end - 20) / 3600
            sensitivity_rows.append({'case': case, 'test': registry[case]['test'], 'start_s': 20,
                                     'end_s': end, 'analytical_aux_kW': aux, 'reference_net_kWh': ref,
                                     'base_net_kWh': model, 'direct_aux_delta_kWh': e,
                                     'direct_corrected_error_pct': 100 * (model + e - ref) / ref})
    historical = {}
    for case in ['R3_AUX_M10', 'R0_BASE', 'R4_AUX_P10']:
        m = state[case]['metrics']
        keys = ('battery_net_kWh', 'reference_net_kWh', 'energy_error_percent', 'auxiliary_mean_kW')
        historical[case] = {k: m[k] for k in keys}
    details = {'choice': 'retain data-derived equivalent HV auxiliary power 0.40 kW',
               'identification_window_s': [0, 20], 'stationary_ratio_samples': len(startup),
               'stationary_effective_HV_over_LV_median': factor,
               'test_cell_C_61905054': 23.34,
               'test054_hvac_CAN_kW_min_max': [0.0, 0.0],
               'test060_can_accessories': checked_can,
               'project': verify_project(a.project), 'existing_runtime': verify_runtime(a.bms, a.vehicle),
               'historical_R0_aux_sensitivity': historical,
               'additional_Cruise_M_runs': 0}
    a.output.mkdir(parents=True, exist_ok=True)
    for filename, rows in [('AUX_EVIDENCE.csv', aux_rows), ('AUX_DIRECT_SENSITIVITY.csv', sensitivity_rows)]:
        with (a.output / filename).open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    (a.output / 'AUX_QA.json').write_text(json.dumps(details, indent=2) + '\n')
    print('PASS: reproduced 054 auxiliary estimate, checked 060 CAN, archived 066 runtime and exact 30 s project')


if __name__ == '__main__':
    main()
