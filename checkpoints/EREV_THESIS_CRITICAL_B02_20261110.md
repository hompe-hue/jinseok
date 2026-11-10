# B02 Physical screening COMPLETE — 2026-11-10
B01 32b19ed0. New analytical calculation only; no CRUISE run/model changes. Existing ANL ABC in km/h units +0.4kW accessories; zero incremental EDU loss. 26kW SOC-neutral speed upper bound126.2479669km/h; at150km/h DC demand lower bound40.5150814kW and battery discharge at least14.5150814kW. These are not official top speed or thermal continuous capability. A1.8s minimum lead derives from 0.5s+26/20 under no restart lockout/derating.
Unit crosscheck, monotonicity and root residual PASS. Next B03: final critical review, concrete experiment and inference protocol, artifacts and persistent source downloads.

```json
{
  "method": "analytic bound, not CRUISE test or official top speed",
  "input_source": "current meeting brief v2, ANL-derived Target ABC; existing 0.4kW auxiliary and 26kW virtual source",
  "parameters": {
    "A_N": 126.329494,
    "B_N_per_kmh": 0.557775,
    "C_N_per_kmh2": 0.033456276,
    "aux_kW": 0.4,
    "net_gen_kW": 26.0
  },
  "lossless_SOC_neutral_speed_upper_bound_kmh": 126.24796694180148,
  "illustrative_speeds": [
    {
      "speed_kmh": 80,
      "road_load_kW": 8.55714800888889,
      "DC_demand_lower_bound_kW": 8.95714800888889,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 0,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 100,
      "road_load_kW": 14.351937611111111,
      "DC_demand_lower_bound_kW": 14.751937611111112,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 0,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 120,
      "road_load_kW": 22.501095613333334,
      "DC_demand_lower_bound_kW": 22.901095613333332,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 0,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 130,
      "road_load_kW": 27.597963914444446,
      "DC_demand_lower_bound_kW": 27.997963914444444,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 1.997963914444444,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 140,
      "road_load_kW": 33.450705695555556,
      "DC_demand_lower_bound_kW": 33.850705695555554,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 7.850705695555554,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 150,
      "road_load_kW": 40.11508141666667,
      "DC_demand_lower_bound_kW": 40.51508141666667,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 14.515081416666668,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    },
    {
      "speed_kmh": 160,
      "road_load_kW": 47.646851537777785,
      "DC_demand_lower_bound_kW": 48.04685153777778,
      "net_generator_cap_kW": 26.0,
      "battery_discharge_min_kW": 22.046851537777783,
      "status": "analytic_flat_windless_no_added_mass_no_EDU_loss_not_vehicle_test"
    }
  ],
  "ABC_diagnostic_not_measured_uncertainty": [
    {
      "scale": 0.9,
      "bound_kmh": 131.53246661970752
    },
    {
      "scale": 1.0,
      "bound_kmh": 126.24796694180148
    },
    {
      "scale": 1.1,
      "bound_kmh": 121.6095435964339
    }
  ],
  "minimum_full_power_lead_s": 1.8,
  "checks": {
    "SI_units_crosscheck": true,
    "positive_monotonic_roadload": true,
    "bisection_residual": true
  },
  "limitations": [
    "EDU loss not included: actual predicted SOC-neutral speed is no greater under same boundary",
    "no motor torque/speed, battery voltage, thermal/continuous rating, actual speed limiter or added genset mass constraint evaluated",
    "speed grid 0-180 is illustration, not an official Bolt speed claim",
    "total DC demand includes 0.4kW accessory; 26kW already net source output",
    "grade/wind/mass sensitivity needs consistent road-load model; no new physical parameter adopted"
  ]
}
```
