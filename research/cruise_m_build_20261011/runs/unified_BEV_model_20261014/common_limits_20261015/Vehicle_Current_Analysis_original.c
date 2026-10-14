#define pwr_dis   a[0]
#define pwr_cha   a[1]
#define v         a[2]
#define i_batt    a[3]
#define i_gen     a[4]
#define i_cons_1  a[5]
#define i_cons_2  a[6]
#define i_cons_3  a[7]
#define i_cons_4  a[8]
#define i_cons_5  a[9]

#define i_lim_mot  y[0]
#define i_lim_gen  y[1]
#define i_cons     y[2]
#define pwr_cons   y[3]

double v_min=350; // [V] please adapt this value depending on the battery pack

/*
Total consumer current, without the e-motor(s) contribution.
*/
i_cons = i_cons_1 + i_cons_2 + i_cons_3 + i_cons_4 + i_cons_5;
pwr_cons = i_cons * v;

/*
In motor mode, the maximum current for the traction motor is defined by the maximum power delivery of the battery
and from any power generator minus the consumers request, which is always covered and the battery current when it is charged.
If the power generator requires current, for instance to crank a combustion engine, the current limit is reduced.
*/
i_lim_mot = max( 0, pwr_dis / max(v_min, v) - i_gen - i_cons );

/*
In generator mode, the maximum current from the traction motor is defined by the maximum power acceptance of the battery and the consumers request.
*/
i_lim_gen = max(0, pwr_cha / max(v_min, v) + i_cons);