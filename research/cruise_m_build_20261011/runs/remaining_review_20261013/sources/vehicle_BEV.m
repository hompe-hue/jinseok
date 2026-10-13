if exist('REVS','var') && REVS.verbose  disp(['Loading ' mfilename]); end

vehicle = class_REVS_vehicle(enum_powertrain_type.battery_electric);

vehicle.class = 'car';

%% Define Final Drive Ratio 
vehicle.drive_axle1.final_drive.gear_ratio      = 9.50;
vehicle.drive_axle1.final_drive.efficiency_norm = 1.00; % losses accounted for in EDU map

%% Define Loaded Tire Radius (m)
vehicle.drive_axle1.tire.radius_m = 0.32; 

vehicle.use_abc_roadload = true;
