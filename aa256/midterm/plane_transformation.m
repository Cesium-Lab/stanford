function [T, T_eps] = plane_transformation(theta)
% theta in radians. Both matrices transform GLOBAL -> LOCAL.
c = cos(theta);
s = sin(theta);
T = [c*c s*s 2*c*s;
     s*s c*c -2*c*s;
     -c*s c*s c*c-s*s];
R = diag([1 1 2]);
T_eps = R * T / R; % Also T_eps = inv(T').
end
