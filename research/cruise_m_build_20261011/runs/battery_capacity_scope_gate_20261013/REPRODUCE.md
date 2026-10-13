# Reproducing the battery diagnostic analysis

Dependencies: Python, numpy, pandas, scipy, nptdms.
Run replay_battery_current.py and compare_literature_capacity.py from research/cruise_m_build_20261011/scripts. The included reference_native.csv and minimal checkpoints are scientific initialization inputs, not independent confirmation of chemical SOC.

For assess_battery_identification_data.py, the retained original environment expects ANL_61905064_selected_native_rows.csv under ../map_original/datakit/Bolt_CRUISE_M_DataKit/data/ (relative to the repository parent), and the 61905067 TDMS under ../source_work/ANL61905067_Raw_Source/. Copy the included scientific CSV from research/battery_replay_sources_20261013/ into that first location.

The original 61905067 TDMS can be acquired from the public Argonne link below. Its metadata includes original laboratory identifiers; it is not republished in this update. The scientific derivative containing only aligned voltage/current/speed/SOC/temperature is included in the feasibility results.

https://anl.app.box.com/index.php?rm=box_download_shared_file&shared_name=rpx3ss7ceabzrhgd9k644vka67rx9ce2&file_id=f_1620740631815

The source SHA256 for the TDMS is fd0f662a44cfa95036b2994fccd52c2f49e0fad105022bab5921d610dc06856c. Do not treat short-window resistance or short-stop voltage as validated R0/OCV.
