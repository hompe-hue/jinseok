# Range energy definition checkpoint

BMS Monitor Energy connects to Range/Energy Left (y[1]). User-supplied code: e_min = e * min(soc_warning / max(soc, 0.01), 1); e_left = e - e_min. This is reserve-adjusted range-estimation energy, not terminal work integral. Do not interpret its decrease minus terminal discharge as battery loss.

Screen 20261011-130043 confirms inputs: a[0] Energy kWh; a[2] SoC Actual %; a[3] SoC Minimum % default 0.05; a[5] Energy Left Previous kWh default 8.69; a[6] Work Total Previous kWh default 4.4; a[7] Distance Previous km default 30; a[8] Range Max km default 70. Defaults are not confirmed effective values when connected. 0.05 percent is not 5 percent; do not change before inspecting source connection.

Initial battery.csv consumption 14.6666667 kWh/100km equals 100*4.4/30, and reported range 70 km matches cap. These are template estimator quantities, not Bolt measured range or independent simulation-only consumption.

No model changes requested. Next: Range Data Bus Connections, select Energy a[0], inspect source component/channel; then SoC Minimum a[3] source/effective value. Full WLTC and independent validation remain pending. User explicitly approved continued research checkpoints in hompe-hue/jinseok on 2026-10-11.
