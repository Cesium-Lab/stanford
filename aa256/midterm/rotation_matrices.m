function [Rx, Ry, Rz, Tx, Ty, Tz, Tx_eps, Ty_eps, Tz_eps] = rotation_matrices(theta_x, theta_y, theta_z)
% Angles in radians; passive rotations, as in HW1.
% Stress order [11; 22; 33; 23; 13; 12]. Strain uses engineering shears.
c = cos(theta_x); s = sin(theta_x);
Rx = [1 0 0; 0 c s; 0 -s c];
Tx = [1 0 0 0 0 0;
      0 c*c s*s 2*c*s 0 0;
      0 s*s c*c -2*c*s 0 0;
      0 -c*s c*s c*c-s*s 0 0;
      0 0 0 0 c -s;
      0 0 0 0 s c];

c = cos(theta_y); s = sin(theta_y);
Ry = [c 0 -s; 0 1 0; s 0 c];
Ty = [c*c 0 s*s 0 -2*c*s 0;
      0 1 0 0 0 0;
      s*s 0 c*c 0 2*c*s 0;
      0 0 0 c 0 s;
      c*s 0 -c*s 0 c*c-s*s 0;
      0 0 0 -s 0 c];

c = cos(theta_z); s = sin(theta_z);
Rz = [c s 0; -s c 0; 0 0 1];
Tz = [c*c s*s 0 0 0 2*c*s;
      s*s c*c 0 0 0 -2*c*s;
      0 0 1 0 0 0;
      0 0 0 c -s 0;
      0 0 0 s c 0;
      -c*s c*s 0 0 0 c*c-s*s];

R = diag([1 1 1 2 2 2]);
Tx_eps = R * Tx / R;
Ty_eps = R * Ty / R;
Tz_eps = R * Tz / R;
% Successive x,y,z rotations: rotation = Rz*Ry*Rx, T = Tz*Ty*Tx.
end
