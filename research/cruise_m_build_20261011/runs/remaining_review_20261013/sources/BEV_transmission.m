
if exist('REVS','var') && REVS.verbose  disp(['Loading ' mfilename]); end

transmission.type = enum_transmission_type.no_transmission;
transmission.variant = 'placeholder transmission system';
transmission.gear.number  = [0, 1];
transmission.gear.ratio   = [0, 1];
