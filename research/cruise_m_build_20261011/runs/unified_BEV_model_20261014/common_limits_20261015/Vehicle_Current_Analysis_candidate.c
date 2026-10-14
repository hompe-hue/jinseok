#define pwr_dis a[0]
#define pwr_cha a[1]
#define v a[2]
#define i_batt a[3]
#define i_gen a[4]
#define i_cons_1 a[5]
#define i_cons_2 a[6]
#define i_cons_3 a[7]
#define i_cons_4 a[8]
#define i_cons_5 a[9]
#define i_lim_mot y[0]
#define i_lim_gen y[1]
#define i_cons y[2]
#define pwr_cons y[3]
/* Warm static surrogate candidate. These are modelling assumptions, not OEM BMS values.
   pwr_dis/pwr_cha ports convert their kW map outputs to W here.
   Generator current is negative when delivering to the DC bus. */
double den = max(1.0, v);
double dis_cap = min(530.0, max(0.0, pwr_dis / den));
double cha_cap = min(160.0, max(0.0, pwr_cha / den));
i_cons = i_cons_1 + i_cons_2 + i_cons_3 + i_cons_4 + i_cons_5;
pwr_cons = i_cons * v;
/* Voltage bounds are already used in the SOC power maps.
   Do not add a discontinuous voltage trip to this algebraic current loop. */
i_lim_mot = max(0.0, dis_cap - i_gen - i_cons);
/* Preserve the calibrated vehicle regen battery-power cap (40 kW).
   Battery charge acceptance remains separate for future range-extender control.
   Account for generator delivery so two sources cannot independently spend the charge budget. */
i_lim_gen = max(0.0, min(40000.0 / den, cha_cap + i_gen) + i_cons);
