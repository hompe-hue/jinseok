# Energy signal definition checkpoint — 2026-10-11 22:10 KST

Evidence: user supplied Performance C code and screenshots 130710, 130840, 130924, 131036.

- Range Energy a[0] is connected to BMS ECM / Performance / Energy Total.
- Range SoC Minimum a[3] is connected to E-Drive Control / Parameters / SoC Warning, whose configured value is 5 %.
- Performance a[6], a[7] are Voltage OC Module 1/2 in V; a[8], a[9] are Charge Module 1/2 in A.h.
- Performance y[3] Energy Total is explicitly W.h. Formula: e_tot=ocv_01*ch_01+ocv_02*ch_02. V*A.h yields W.h; no extra factor belongs in this formula.
- Range Energy input is kWh per previously inspected definition, so the connected Wh output requires unit conversion by the data bus. The observed magnitude is consistent with conversion, but internal conversion implementation has not been independently inspected.
- BMS Monitor Energy is Range Energy Left, not integrated terminal energy. Range subtracts an SOC-warning reserve from the OCV-times-charge proxy. Its decrease cannot be interpreted as terminal work or used to infer battery heat from the difference with terminal power integral.
- At initial SOC 60%, 168 Ah, pack OCV 364.7252 V: proxy total 36.76430016 kWh; applying 5% warning yields 33.70060848 kWh, matching the exported initial Energy 33.700608479970434 kWh.
- Remaining: full-cycle run and independent terminal-power-based consumption evaluation. No real-vehicle energy/range validation claimed.
